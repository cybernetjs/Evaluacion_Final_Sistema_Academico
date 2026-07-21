from datetime import datetime
from sqlalchemy.orm import joinedload
from app import db
from app.dominio.modelos.matriculas.matricula_detalle import MatriculaDetalle
from app.dominio.modelos.matriculas.matricula import Matricula
from app.dominio.modelos.estudiantes.estudiante import Estudiante
from app.dominio.modelos.docentes.docente import Docente
from app.dominio.modelos.ofertas.oferta_academica import OfertaAcademica
from app.dominio.modelos.ofertas.oferta_academica_docente import OfertaAcademicaDocente
from app.dominio.modelos.estudiantes.hito_academico import HitoAcademico
from app.dominio.modelos.notas.acta import Acta
from app.dominio.modelos.academico.estado_curso import EstadoCurso
from app.dominio.modelos.notas.expediente_semestral import ExpedienteSemestral
from app.dominio.modelos.estudiantes.progreso_estudiante import ProgresoEstudiante
from app.dominio.modelos.estudiantes.estado_permanencia_estudiante import EstadoPermanenciaEstudiante

UMBRAL_APROBACION = 10.5

CAMPOS_POR_TIPO = {
    "parcial1": "nota_parcial",
    "parcial2": "nota_parcial2",
    "practica": "nota_practica",
    "final": "nota_final",
}

PESOS_FORMULA_FINAL = {
    "nota_parcial": 0.3,
    "nota_parcial2": 0.3,
    "nota_practica": 0.4,
}


class NotasService:

    @staticmethod
    def registrar_nota(matricula_id, oferta_academica_id, nota_parcial=None, nota_final=None, estado_curso_id=None):
        detalle = MatriculaDetalle.query.filter_by(
            matricula_id=matricula_id,
            oferta_academica_id=oferta_academica_id
        ).first()

        if not detalle:
            return None, "Detalle de matrícula no encontrado"

        if nota_parcial is not None:
            detalle.nota_parcial = nota_parcial
        if nota_final is not None:
            detalle.nota_final = nota_final
        if estado_curso_id is not None:
            detalle.estado_curso_id = estado_curso_id

        db.session.commit()
        return detalle, None

    @staticmethod
    def _mapa_visibilidad_actas(oferta_academica_ids):
        if not oferta_academica_ids:
            return {}

        actas = Acta.query.filter(
            Acta.oferta_academica_id.in_(oferta_academica_ids)
        ).all()

        return {
            acta.oferta_academica_id: (acta.notas_publicadas or acta.estado == "Cerrada")
            for acta in actas
        }

    @staticmethod
    def hoja_de_notas_por_ciclo(usuario_id, periodo_academico_id=None, semestre_id=None):
        estudiante = Estudiante.query.filter_by(usuario_id=usuario_id).first()

        if not estudiante:
            return None, "No se encontró un estudiante asociado a este usuario"

        query = Matricula.query.options(
            joinedload(Matricula.detalle)
            .joinedload(MatriculaDetalle.oferta_academica)
            .joinedload(OfertaAcademica.curso)
        ).filter_by(estudiante_id=estudiante.id)
        if periodo_academico_id:
            query = query.filter_by(periodo_academico_id=periodo_academico_id)
        if semestre_id:
            query = query.filter_by(semestre_id=semestre_id)

        matriculas = query.all()

        ids_ofertas = [d.oferta_academica_id for m in matriculas for d in m.detalle]
        visibilidad = NotasService._mapa_visibilidad_actas(ids_ofertas)

        resultado = []
        for m in matriculas:
            for d in m.detalle:
                visible = visibilidad.get(d.oferta_academica_id, False)

                resultado.append({
                    "periodo_academico_id": m.periodo_academico_id,
                    "semestre_id": m.semestre_id,
                    "curso_id": d.oferta_academica.curso_id,
                    "curso_nombre": d.oferta_academica.curso.nombre,
                    "nota_parcial1": float(d.nota_parcial) if visible and d.nota_parcial is not None else None,
                    "nota_parcial2": float(d.nota_parcial2) if visible and d.nota_parcial2 is not None else None,
                    "nota_practica": float(d.nota_practica) if visible and d.nota_practica is not None else None,
                    "nota_final": float(d.nota_final) if visible and d.nota_final is not None else None,
                    "estado_curso_id": d.estado_curso_id,
                    "publicado": visible,
                })

        return resultado, None

    @staticmethod
    def ciclos_cursados(usuario_id):
        estudiante = Estudiante.query.filter_by(usuario_id=usuario_id).first()
        if not estudiante:
            return None, "No se encontró un estudiante asociado a este usuario"

        matriculas = Matricula.query.options(
            joinedload(Matricula.periodo_academico)
        ).filter_by(estudiante_id=estudiante.id).all()

        vistos = {}
        for m in matriculas:
            if m.periodo_academico_id not in vistos:
                vistos[m.periodo_academico_id] = m.periodo_academico.nombre if m.periodo_academico else None

        ciclos = [{"periodo_academico_id": pid, "nombre": nombre} for pid, nombre in vistos.items()]
        return ciclos, None

    @staticmethod
    def publicar_notas(usuario_id_docente, oferta_academica_id):
        docente = NotasService._docente_asignado(usuario_id_docente, oferta_academica_id)
        if not docente:
            return None, "No tienes asignada esta sección"

        acta = Acta.query.filter_by(oferta_academica_id=oferta_academica_id).first()
        if not acta:
            acta = Acta(oferta_academica_id=oferta_academica_id)
            db.session.add(acta)

        if acta.estado == "Cerrada":
            return None, "El acta ya está cerrada, las notas ya son oficiales"

        acta.notas_publicadas = True
        db.session.commit()

        return {"mensaje": "Notas publicadas a los estudiantes", "oferta_academica_id": oferta_academica_id}, None

    @staticmethod
    def _docente_asignado(usuario_id, oferta_academica_id):
        docente = Docente.query.filter_by(usuario_id=usuario_id).first()
        if not docente:
            return None

        asignacion = OfertaAcademicaDocente.query.filter_by(
            docente_id=docente.id, oferta_academica_id=oferta_academica_id
        ).first()

        return docente if asignacion else None

    @staticmethod
    def estado_cronograma(oferta_academica_id, tipo_nota):
        if tipo_nota not in CAMPOS_POR_TIPO:
            return None, "Tipo de nota inválido"

        oferta = OfertaAcademica.query.get(oferta_academica_id)
        if not oferta:
            return None, "Oferta académica no encontrada"

        hito = HitoAcademico.query.filter_by(
            periodo_academico_id=oferta.periodo_academico_id, tipo_nota=tipo_nota
        ).first()

        if not hito:
            return {"vigente": True, "fecha_limite": None}, None

        vigente = datetime.now() <= hito.fecha_limite
        return {"vigente": vigente, "fecha_limite": hito.fecha_limite.isoformat()}, None

    @staticmethod
    def obtener_planilla(oferta_academica_id, usuario_id_docente):
        docente = NotasService._docente_asignado(usuario_id_docente, oferta_academica_id)
        if not docente:
            return None, "No tienes asignada esta sección"

        oferta = OfertaAcademica.query.get(oferta_academica_id)
        if not oferta:
            return None, "Oferta académica no encontrada"

        detalles = MatriculaDetalle.query.options(
            joinedload(MatriculaDetalle.matricula).joinedload(Matricula.estudiante)
        ).filter_by(oferta_academica_id=oferta_academica_id).all()

        estudiantes = []
        for d in detalles:
            estudiante = d.matricula.estudiante
            estudiantes.append({
                "matricula_id": d.matricula_id,
                "estudiante_id": estudiante.id,
                "estudiante_nombre": f"{estudiante.nombres} {estudiante.apellido_paterno} {estudiante.apellido_materno}",
                "nota_parcial1": float(d.nota_parcial) if d.nota_parcial is not None else None,
                "nota_parcial2": float(d.nota_parcial2) if d.nota_parcial2 is not None else None,
                "nota_practica": float(d.nota_practica) if d.nota_practica is not None else None,
                "nota_final": float(d.nota_final) if d.nota_final is not None else None,
            })

        cronograma = {}
        for tipo in CAMPOS_POR_TIPO:
            estado, _ = NotasService.estado_cronograma(oferta_academica_id, tipo)
            cronograma[tipo] = estado

        return {
            "curso_nombre": oferta.curso.nombre,
            "estudiantes": estudiantes,
            "cronograma": cronograma,
        }, None

    @staticmethod
    def registrar_notas_planilla(usuario_id_docente, oferta_academica_id, tipo_nota, calificaciones):
        if tipo_nota not in CAMPOS_POR_TIPO:
            return None, "Tipo de nota inválido", 400

        if tipo_nota == "final":
            return None, (
                "La nota final se calcula automáticamente a partir de los parciales "
                "y la práctica, no puede registrarse manualmente"
            ), 400

        docente = NotasService._docente_asignado(usuario_id_docente, oferta_academica_id)
        if not docente:
            return None, "No tienes asignada esta sección", 403

        cronograma, error = NotasService.estado_cronograma(oferta_academica_id, tipo_nota)
        if error:
            return None, error, 400
        if not cronograma["vigente"]:
            return None, "Periodo de ingreso cerrado por la administración", 423

        if not calificaciones:
            return None, "Debes enviar al menos una calificación", 400

        for item in calificaciones:
            valor = item.get("calificacion")
            try:
                valor_numerico = float(valor)
            except (TypeError, ValueError):
                return None, f"La calificación '{valor}' no es un valor numérico válido", 400
            if valor_numerico < 0 or valor_numerico > 20:
                return None, f"La calificación {valor_numerico} está fuera del rango permitido (0-20)", 400

        campo = CAMPOS_POR_TIPO[tipo_nota]
        actualizados = 0

        for item in calificaciones:
            estudiante_id = item.get("estudiante_id")
            valor_numerico = float(item.get("calificacion"))

            detalle = (
                MatriculaDetalle.query.join(Matricula, MatriculaDetalle.matricula_id == Matricula.id)
                .filter(
                    Matricula.estudiante_id == estudiante_id,
                    MatriculaDetalle.oferta_academica_id == oferta_academica_id,
                )
                .first()
            )
            if not detalle:
                continue

            setattr(detalle, campo, valor_numerico)

            if tipo_nota != "final":
                componentes = [detalle.nota_parcial, detalle.nota_parcial2, detalle.nota_practica]
                if all(c is not None for c in componentes):
                    ponderado = sum(
                        float(getattr(detalle, nombre_campo)) * peso
                        for nombre_campo, peso in PESOS_FORMULA_FINAL.items()
                    )
                    detalle.nota_final = round(ponderado, 2)

            actualizados += 1

        db.session.commit()
        return {"mensaje": "Calificaciones registradas", "total_actualizados": actualizados}, None, 200

    @staticmethod
    def _porcentaje_notas_ingresadas(oferta_academica_id):
        detalles = MatriculaDetalle.query.filter_by(oferta_academica_id=oferta_academica_id).all()
        if not detalles:
            return 0, 0, 0

        total = len(detalles)
        con_nota = sum(1 for d in detalles if d.nota_final is not None)
        porcentaje = round((con_nota / total) * 100, 1)
        return porcentaje, con_nota, total

    @staticmethod
    def panel_actas():
        ofertas = OfertaAcademica.query.options(
            joinedload(OfertaAcademica.curso)
        ).all()
        if not ofertas:
            return [], None

        ids_ofertas = [o.id for o in ofertas]

        conteos = (
            db.session.query(
                MatriculaDetalle.oferta_academica_id,
                db.func.count(MatriculaDetalle.oferta_academica_id).label("total"),
                db.func.sum(
                    db.case((MatriculaDetalle.nota_final.isnot(None), 1), else_=0)
                ).label("con_nota"),
            )
            .filter(MatriculaDetalle.oferta_academica_id.in_(ids_ofertas))
            .group_by(MatriculaDetalle.oferta_academica_id)
            .all()
        )
        totales_por_oferta = {
            fila.oferta_academica_id: (int(fila.total), int(fila.con_nota or 0))
            for fila in conteos
        }

        actas_por_oferta = {
            a.oferta_academica_id: a
            for a in Acta.query.filter(Acta.oferta_academica_id.in_(ids_ofertas)).all()
        }

        asignaciones = (
            OfertaAcademicaDocente.query.options(joinedload(OfertaAcademicaDocente.docente))
            .filter(OfertaAcademicaDocente.oferta_academica_id.in_(ids_ofertas))
            .all()
        )
        docente_por_oferta = {}
        for asignacion in asignaciones:
            if asignacion.oferta_academica_id not in docente_por_oferta and asignacion.docente:
                d = asignacion.docente
                docente_por_oferta[asignacion.oferta_academica_id] = (
                    f"{d.nombres} {d.apellido_paterno} {d.apellido_materno}"
                )

        filas = []
        for oferta in ofertas:
            total, con_nota = totales_por_oferta.get(oferta.id, (0, 0))
            if total == 0:
                continue

            porcentaje = round((con_nota / total) * 100, 1)
            acta = actas_por_oferta.get(oferta.id)

            filas.append({
                "oferta_academica_id": oferta.id,
                "curso_codigo": oferta.curso.codigo,
                "curso_nombre": oferta.curso.nombre,
                "docente": docente_por_oferta.get(oferta.id),
                "porcentaje_notas_ingresadas": porcentaje,
                "estudiantes_con_nota": con_nota,
                "estudiantes_total": total,
                "estado_acta": acta.estado if acta else "Abierta",
                "puede_cerrar": porcentaje == 100 and (not acta or acta.estado != "Cerrada"),
            })

        return filas, None

    @staticmethod
    def alumnos_omisos(oferta_academica_id):
        detalles = (
            MatriculaDetalle.query.options(
                joinedload(MatriculaDetalle.matricula).joinedload(Matricula.estudiante)
            )
            .filter_by(oferta_academica_id=oferta_academica_id)
            .filter(MatriculaDetalle.nota_final.is_(None))
            .all()
        )

        omisos = []
        for d in detalles:
            estudiante = d.matricula.estudiante
            omisos.append({
                "estudiante_id": estudiante.id,
                "estudiante_nombre": f"{estudiante.nombres} {estudiante.apellido_paterno} {estudiante.apellido_materno}",
            })

        return omisos, None

    @staticmethod
    def cerrar_acta(oferta_academica_id):
        import hashlib

        oferta = OfertaAcademica.query.get(oferta_academica_id)
        if not oferta:
            return None, "Oferta académica no encontrada", 404

        detalles = MatriculaDetalle.query.filter_by(oferta_academica_id=oferta_academica_id).all()
        if not detalles:
            return None, "No hay estudiantes matriculados en esta sección", 400

        omisos, _ = NotasService.alumnos_omisos(oferta_academica_id)
        if omisos:
            return {"alumnos_omisos": omisos}, "Existen alumnos sin nota final registrada", 422

        acta = Acta.query.filter_by(oferta_academica_id=oferta_academica_id).first()
        if acta and acta.estado == "Cerrada":
            return None, "El acta de esta sección ya se encuentra cerrada", 400

        if not acta:
            acta = Acta(oferta_academica_id=oferta_academica_id)
            db.session.add(acta)

        for d in detalles:
            aprobado = float(d.nota_final) >= UMBRAL_APROBACION
            nombre_estado = "Aprobado" if aprobado else "Desaprobado"
            estado = EstadoCurso.query.filter_by(nombre=nombre_estado).first()
            if estado:
                d.estado_curso_id = estado.id

        notas_ordenadas = sorted(
            (d.matricula.estudiante_id, float(d.nota_final)) for d in detalles
        )
        base = f"{oferta_academica_id}|{notas_ordenadas}|{datetime.now().isoformat()}"
        hash_auditoria = hashlib.sha256(base.encode("utf-8")).hexdigest()

        acta.estado = "Cerrada"
        acta.notas_publicadas = True
        acta.hash_auditoria = hash_auditoria
        acta.fecha_cierre = datetime.now()

        db.session.commit()

        return {
            "mensaje": "Acta cerrada formalmente",
            "oferta_academica_id": oferta_academica_id,
            "estado": acta.estado,
            "hash_auditoria": hash_auditoria,
        }, None, 200

    @staticmethod
    def estado_periodo_para_consolidar(periodo_academico_id):
        ofertas_ids = (
            db.session.query(MatriculaDetalle.oferta_academica_id)
            .join(Matricula, MatriculaDetalle.matricula_id == Matricula.id)
            .filter(Matricula.periodo_academico_id == periodo_academico_id)
            .distinct()
            .all()
        )
        ofertas_ids = [o[0] for o in ofertas_ids]

        total_actas = len(ofertas_ids)
        secciones_pendientes = []
        actas_cerradas = 0

        for oferta_id in ofertas_ids:
            oferta = OfertaAcademica.query.get(oferta_id)
            acta = Acta.query.filter_by(oferta_academica_id=oferta_id).first()
            if acta and acta.estado == "Cerrada":
                actas_cerradas += 1
            else:
                secciones_pendientes.append({
                    "oferta_academica_id": oferta_id,
                    "curso_codigo": oferta.curso.codigo,
                    "curso_nombre": oferta.curso.nombre,
                })

        return {
            "total_actas": total_actas,
            "actas_cerradas": actas_cerradas,
            "todas_cerradas": len(secciones_pendientes) == 0 and total_actas > 0,
            "secciones_pendientes": secciones_pendientes,
        }, None

    @staticmethod
    def _calcular_promedio_ponderado(detalles):
        suma_ponderada = 0
        suma_creditos = 0
        for d in detalles:
            creditos = d.oferta_academica.curso.creditos
            if not creditos or d.nota_final is None:
                continue
            suma_ponderada += float(d.nota_final) * creditos
            suma_creditos += creditos

        if suma_creditos == 0:
            return None, 0
        return round(suma_ponderada / suma_creditos, 2), suma_creditos

    @staticmethod
    def consolidar_semestre(periodo_academico_id):
        estado, _ = NotasService.estado_periodo_para_consolidar(periodo_academico_id)

        if not estado["todas_cerradas"]:
            return None, "Existen actas abiertas, no se puede consolidar el periodo", 400, estado["secciones_pendientes"]

        matriculas = Matricula.query.filter_by(periodo_academico_id=periodo_academico_id).all()
        estudiantes_ids = list({m.estudiante_id for m in matriculas})

        actualizados = 0
        errores = []

        for estudiante_id in estudiantes_ids:
            try:
                detalles_semestre = (
                    MatriculaDetalle.query.join(Matricula, MatriculaDetalle.matricula_id == Matricula.id)
                    .filter(
                        Matricula.estudiante_id == estudiante_id,
                        Matricula.periodo_academico_id == periodo_academico_id,
                    )
                    .all()
                )

                pps, creditos_semestre = NotasService._calcular_promedio_ponderado(detalles_semestre)
                if pps is None:
                    errores.append({
                        "estudiante_id": estudiante_id,
                        "codigo_error": "SIN_CREDITOS_VALIDOS",
                        "detalle": "Inconsistencia de créditos: no se pudo calcular el promedio del semestre",
                    })
                    continue

                creditos_aprobados_semestre = sum(
                    d.oferta_academica.curso.creditos
                    for d in detalles_semestre
                    if d.estado_curso and d.estado_curso.nombre == "Aprobado" and d.oferta_academica.curso.creditos
                )

                expediente = ExpedienteSemestral.query.filter_by(
                    estudiante_id=estudiante_id, periodo_academico_id=periodo_academico_id
                ).first()
                if not expediente:
                    expediente = ExpedienteSemestral(
                        estudiante_id=estudiante_id, periodo_academico_id=periodo_academico_id
                    )
                    db.session.add(expediente)

                expediente.promedio_ponderado_semestral = pps
                expediente.creditos_aprobados_semestre = creditos_aprobados_semestre
                expediente.estado = "Consolidado"
                expediente.fecha_consolidacion = datetime.now()

                detalles_historicos = (
                    MatriculaDetalle.query.join(Matricula, MatriculaDetalle.matricula_id == Matricula.id)
                    .join(OfertaAcademica, MatriculaDetalle.oferta_academica_id == OfertaAcademica.id)
                    .join(Acta, Acta.oferta_academica_id == OfertaAcademica.id)
                    .filter(Matricula.estudiante_id == estudiante_id, Acta.estado == "Cerrada")
                    .all()
                )
                ppa, _ = NotasService._calcular_promedio_ponderado(detalles_historicos)
                creditos_acumulados = sum(
                    d.oferta_academica.curso.creditos
                    for d in detalles_historicos
                    if d.estado_curso and d.estado_curso.nombre == "Aprobado" and d.oferta_academica.curso.creditos
                )

                progreso = ProgresoEstudiante.query.filter_by(estudiante_id=estudiante_id).first()
                if not progreso:
                    estado_regular = EstadoPermanenciaEstudiante.query.filter_by(nombre="Regular").first()
                    progreso = ProgresoEstudiante(
                        estudiante_id=estudiante_id,
                        estado_permanencia_id=estado_regular.id if estado_regular else None,
                        creditos_aprobados_acumulados=0,
                        promedio_ponderado_acumulado=0,
                    )
                    db.session.add(progreso)

                progreso.promedio_ponderado_acumulado = ppa if ppa is not None else 0
                progreso.creditos_aprobados_acumulados = creditos_acumulados

                actualizados += 1
            except Exception as e:
                errores.append({
                    "estudiante_id": estudiante_id,
                    "codigo_error": "ERROR_COMPUTO",
                    "detalle": str(e),
                })

        db.session.commit()

        return {
            "mensaje": "Consolidación semestral finalizada",
            "total_expedientes_actualizados": actualizados,
            "errores": errores,
        }, None, 200, None

    @staticmethod
    def indicadores_direccion(periodo_academico_id=None, especialidad_id=None, plan_estudios_id=None):
        from app.dominio.modelos.academico.especialidad import Especialidad
        from app.dominio.modelos.estudiantes.plan_estudiante import PlanEstudiante

        consulta = (
            MatriculaDetalle.query.options(
                joinedload(MatriculaDetalle.oferta_academica).joinedload(OfertaAcademica.curso),
                joinedload(MatriculaDetalle.estado_curso),
                joinedload(MatriculaDetalle.matricula).joinedload(Matricula.estudiante),
            )
            .join(Matricula, MatriculaDetalle.matricula_id == Matricula.id)
            .join(OfertaAcademica, MatriculaDetalle.oferta_academica_id == OfertaAcademica.id)
            .join(Acta, Acta.oferta_academica_id == OfertaAcademica.id)
            .join(Estudiante, Matricula.estudiante_id == Estudiante.id)
            .filter(Acta.estado == "Cerrada")
        )
        if periodo_academico_id:
            consulta = consulta.filter(Matricula.periodo_academico_id == periodo_academico_id)
        if especialidad_id:
            consulta = consulta.filter(Estudiante.especialidad_id == especialidad_id)
        if plan_estudios_id:
            consulta = consulta.join(
                PlanEstudiante, PlanEstudiante.estudiante_id == Estudiante.id
            ).filter(PlanEstudiante.plan_estudios_id == plan_estudios_id)

        detalles = consulta.all()

        ids_ofertas = {d.oferta_academica_id for d in detalles}
        docente_por_oferta = {}
        if ids_ofertas:
            asignaciones = (
                OfertaAcademicaDocente.query.options(joinedload(OfertaAcademicaDocente.docente))
                .filter(OfertaAcademicaDocente.oferta_academica_id.in_(ids_ofertas))
                .all()
            )
            for asignacion in asignaciones:
                if asignacion.oferta_academica_id not in docente_por_oferta and asignacion.docente:
                    doc = asignacion.docente
                    docente_por_oferta[asignacion.oferta_academica_id] = (
                        f"{doc.nombres} {doc.apellido_paterno} {doc.apellido_materno}"
                    )

        por_oferta = {}
        for d in detalles:
            oferta_id = d.oferta_academica_id
            if oferta_id not in por_oferta:
                por_oferta[oferta_id] = {
                    "oferta_academica_id": oferta_id,
                    "curso_codigo": d.oferta_academica.curso.codigo,
                    "curso_nombre": d.oferta_academica.curso.nombre,
                    "docente": docente_por_oferta.get(oferta_id),
                    "aprobados": 0,
                    "desaprobados": 0,
                    "total": 0,
                }

            por_oferta[oferta_id]["total"] += 1
            if d.estado_curso and d.estado_curso.nombre == "Aprobado":
                por_oferta[oferta_id]["aprobados"] += 1
            elif d.estado_curso and d.estado_curso.nombre == "Desaprobado":
                por_oferta[oferta_id]["desaprobados"] += 1

        tasa_aprobacion_por_curso = []
        secciones_criticas = []
        for fila in por_oferta.values():
            tasa_aprobacion = round((fila["aprobados"] / fila["total"]) * 100, 1) if fila["total"] else 0
            tasa_desaprobacion = round((fila["desaprobados"] / fila["total"]) * 100, 1) if fila["total"] else 0

            registro = {
                "oferta_academica_id": fila["oferta_academica_id"],
                "curso_codigo": fila["curso_codigo"],
                "curso_nombre": fila["curso_nombre"],
                "docente": fila["docente"],
                "tasa_aprobacion_porcentaje": tasa_aprobacion,
                "tasa_desaprobacion_porcentaje": tasa_desaprobacion,
                "seccion_critica": tasa_desaprobacion > 40,
            }
            tasa_aprobacion_por_curso.append(registro)

            if registro["seccion_critica"]:
                secciones_criticas.append(registro)

        especialidades = Especialidad.query.all()
        desaprobacion_por_especialidad = []
        for especialidad in especialidades:
            detalles_especialidad = [d for d in detalles if d.matricula.estudiante.especialidad_id == especialidad.id]
            total_especialidad = len(detalles_especialidad)
            if total_especialidad == 0:
                continue
            desaprobados_especialidad = sum(
                1 for d in detalles_especialidad if d.estado_curso and d.estado_curso.nombre == "Desaprobado"
            )
            desaprobacion_por_especialidad.append({
                "especialidad": especialidad.nombre,
                "tasa_desaprobacion_porcentaje": round((desaprobados_especialidad / total_especialidad) * 100, 1),
            })

        matriculas_periodo = Matricula.query.options(joinedload(Matricula.estado))
        if periodo_academico_id:
            matriculas_periodo = matriculas_periodo.filter_by(periodo_academico_id=periodo_academico_id)
        matriculas_periodo = matriculas_periodo.all()

        total_matriculas = len(matriculas_periodo)
        retiradas = sum(1 for m in matriculas_periodo if m.estado and m.estado.nombre == "Retirado")
        porcentaje_desercion = round((retiradas / total_matriculas) * 100, 1) if total_matriculas else 0

        return {
            "tasa_aprobacion_por_curso": tasa_aprobacion_por_curso,
            "desaprobacion_por_especialidad": desaprobacion_por_especialidad,
            "porcentaje_desercion": porcentaje_desercion,
            "secciones_criticas": secciones_criticas,
        }, None