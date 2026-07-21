import os
import uuid
from datetime import datetime
from sqlalchemy.orm import joinedload
from app import db
from app.dominio.modelos.academico.silabo import Silabo
from app.dominio.modelos.docentes.docente import Docente
from app.dominio.modelos.academico.curso import Curso
from app.dominio.modelos.ofertas.oferta_academica import OfertaAcademica
from app.dominio.modelos.ofertas.oferta_academica_docente import OfertaAcademicaDocente
from app.dominio.modelos.ofertas.oferta_academica_horario import OfertaAcademicaHorario
from app.dominio.modelos.ofertas.periodo_academico import PeriodoAcademico
from app.dominio.modelos.academico.semestre import Semestre
from app.dominio.modelos.academico.plan_cursos_semestre import PlanCursosSemestre
from app.dominio.modelos.academico.plan_de_estudios import PlanDeEstudios
from app.dominio.modelos.academico.especialidad import Especialidad
from app.compartido.utilidades.seccion_oferta import etiqueta_seccion

CARPETA_SILABOS = os.path.join(os.getcwd(), "uploads", "silabos")
TAMANO_MAXIMO_SILABO_BYTES = 10 * 1024 * 1024
CARGA_MINIMA_SEMANAL = 8
CARGA_MAXIMA_SEMANAL = 20
FUNCIONES_VALIDAS = ("Teorico", "Practico")

DIAS_SEMANA = {
    1: "Lunes", 2: "Martes", 3: "Miercoles", 4: "Jueves",
    5: "Viernes", 6: "Sabado", 7: "Domingo",
}


class CursosDocentesService:

    @staticmethod
    def periodo_activo():
        hoy = datetime.utcnow()
        periodo = (
            PeriodoAcademico.query
            .filter(PeriodoAcademico.fecha_inicio <= hoy, PeriodoAcademico.fecha_fin >= hoy)
            .order_by(PeriodoAcademico.fecha_inicio.desc())
            .first()
        )
        if periodo:
            return periodo
        return PeriodoAcademico.query.order_by(PeriodoAcademico.fecha_inicio.desc()).first()

    @staticmethod
    def periodos_historicos_docente(usuario_id):
        docente = Docente.query.filter_by(usuario_id=usuario_id).first()
        if not docente:
            return [], "No se encontró un docente asociado a este usuario"

        periodos_ids = (
            db.session.query(OfertaAcademica.periodo_academico_id)
            .join(OfertaAcademicaDocente, OfertaAcademicaDocente.oferta_academica_id == OfertaAcademica.id)
            .filter(OfertaAcademicaDocente.docente_id == docente.id)
            .distinct()
            .all()
        )
        ids = [p[0] for p in periodos_ids]

        periodos = (
            PeriodoAcademico.query.filter(PeriodoAcademico.id.in_(ids))
            .order_by(PeriodoAcademico.fecha_inicio.desc())
            .all()
        )

        return [{
            "id": p.id,
            "nombre": p.nombre
        } for p in periodos
        ], None

    @staticmethod
    def crear_curso(nombre, codigo, creditos, horas_lectivas, horas_practicas):
        if not nombre or not str(nombre).strip():
            return None, "El nombre del curso es obligatorio", 400
        if not codigo or not str(codigo).strip():
            return None, "El código del curso es obligatorio", 400

        codigo_normalizado = str(codigo).strip().upper()
        if Curso.query.filter_by(codigo=codigo_normalizado).first():
            return None, f"Ya existe un curso registrado con el código {codigo_normalizado}", 409

        try:
            creditos = int(creditos)
            horas_lectivas = int(horas_lectivas)
            horas_practicas = int(horas_practicas)
        except (TypeError, ValueError):
            return None, "Créditos, horas lectivas y horas prácticas deben ser números enteros", 422

        if creditos <= 0:
            return None, "Los créditos deben ser un número entero positivo", 422
        if horas_lectivas < 0 or horas_practicas < 0:
            return None, "Las horas lectivas y prácticas no pueden ser negativas", 422
        if horas_lectivas + horas_practicas <= 0:
            return None, "El curso debe tener al menos una hora lectiva o práctica", 422

        curso = Curso(
            nombre=str(nombre).strip(),
            codigo=codigo_normalizado,
            creditos=creditos,
            horas_lectivas=horas_lectivas,
            horas_practicas=horas_practicas,
        )
        db.session.add(curso)
        db.session.commit()

        return {
            "id": curso.id,
            "nombre": curso.nombre,
            "codigo": curso.codigo,
            "creditos": curso.creditos,
            "horas_lectivas": curso.horas_lectivas,
            "horas_practicas": curso.horas_practicas,
        }, None, 201

    @staticmethod
    def crear_oferta_academica(curso_id, periodo_academico_id, semestre_id, cupos=None):
        if not curso_id or not periodo_academico_id or not semestre_id:
            return None, "Debes seleccionar el curso, el periodo académico y el semestre", 400

        curso = Curso.query.get(curso_id)
        if not curso:
            return None, "Curso no encontrado", 404

        periodo = PeriodoAcademico.query.get(periodo_academico_id)
        if not periodo:
            return None, "Periodo académico no encontrado", 404

        semestre = Semestre.query.get(semestre_id)
        if not semestre:
            return None, "Semestre no encontrado", 404

        existente = OfertaAcademica.query.filter_by(
            curso_id=curso_id,
            periodo_academico_id=periodo_academico_id,
            semestre_id=semestre_id,
        ).first()
        if existente:
            return None, (
                "Ya existe una sección abierta para este curso en el semestre y periodo seleccionados"
            ), 409

        if cupos is not None:
            try:
                cupos = int(cupos)
            except (TypeError, ValueError):
                return None, "Los cupos deben ser un número entero", 422
            if cupos <= 0:
                return None, "Los cupos deben ser un número entero positivo", 422

        oferta = OfertaAcademica(
            curso_id=curso_id,
            periodo_academico_id=periodo_academico_id,
            semestre_id=semestre_id,
            cupos=cupos or 40,
        )
        db.session.add(oferta)
        db.session.commit()

        return {
            "id": oferta.id,
            "curso_id": oferta.curso_id,
            "curso_nombre": curso.nombre,
            "periodo_academico_id": oferta.periodo_academico_id,
            "semestre_id": oferta.semestre_id,
            "semestre_codigo": semestre.codigo,
            "cupos": oferta.cupos,
        }, None, 201

    @staticmethod
    def asignaciones_oferta(oferta_academica_id):
        oferta = OfertaAcademica.query.get(oferta_academica_id)
        if not oferta:
            return None, "Oferta académica no encontrada"

        curso = oferta.curso
        horas_requeridas_curso = curso.horas_lectivas + curso.horas_practicas

        asignaciones = OfertaAcademicaDocente.query.options(
            joinedload(OfertaAcademicaDocente.docente)
        ).filter_by(
            oferta_academica_id=oferta_academica_id
        ).all()
        horarios = OfertaAcademicaHorario.query.filter_by(
            oferta_academica_id=oferta_academica_id
        ).all()

        funciones_cubiertas = {a.funcion_curso for a in asignaciones if a.funcion_curso}
        suma_horas_asignadas = sum(a.horas_asignadas or 0 for a in asignaciones)

        return {
            "oferta_academica_id": oferta.id,
            "curso_nombre": curso.nombre,
            "horas_requeridas_curso": horas_requeridas_curso,
            "suma_horas_asignadas": suma_horas_asignadas,
            "funciones_pendientes": [f for f in FUNCIONES_VALIDAS if f not in funciones_cubiertas],
            "plana_completa": (
                set(FUNCIONES_VALIDAS).issubset(funciones_cubiertas)
                and suma_horas_asignadas == horas_requeridas_curso
            ),
            "docentes_asignados": [
                {
                    "asignacion_id": a.id,
                    "docente_id": a.docente_id,
                    "docente_nombre": (
                        f"{a.docente.nombres} {a.docente.apellido_paterno}" if a.docente else None
                    ),
                    "funcion_curso": a.funcion_curso,
                    "horas_asignadas": a.horas_asignadas,
                }
                for a in asignaciones
            ],
            "horarios": [
                {
                    "id": h.id,
                    "dia": DIAS_SEMANA.get(h.dia, h.dia),
                    "hora_inicio": h.hora_inicio.strftime("%H:%M") if h.hora_inicio else None,
                    "hora_fin": h.hora_fin.strftime("%H:%M") if h.hora_fin else None,
                    "aula": h.aula,
                    "funcion_curso": h.funcion_curso,
                }
                for h in horarios
            ],
        }, None

    @staticmethod
    def mis_cursos(usuario_id, periodo_academico_id=None):
        docente = Docente.query.filter_by(usuario_id=usuario_id).first()
        if not docente:
            return None, "No se encontró un docente asociado a este usuario"

        if not periodo_academico_id:
            periodo = CursosDocentesService.periodo_activo()
            periodo_academico_id = periodo.id if periodo else None

        asignaciones = (
            OfertaAcademicaDocente.query.filter_by(docente_id=docente.id)
            .filter(OfertaAcademicaDocente.funcion_curso.isnot(None))
            .join(OfertaAcademica, OfertaAcademicaDocente.oferta_academica_id == OfertaAcademica.id)
            .filter(OfertaAcademica.periodo_academico_id == periodo_academico_id)
            .options(joinedload(OfertaAcademicaDocente.oferta_academica).joinedload(OfertaAcademica.curso))
            .all()
        )

        secciones_por_oferta = {}
        for a in asignaciones:
            oferta = a.oferta_academica
            if oferta.id not in secciones_por_oferta:
                secciones_por_oferta[oferta.id] = {"oferta": oferta, "horas_semanales": 0}
            secciones_por_oferta[oferta.id]["horas_semanales"] += a.horas_asignadas or 0

        oferta_ids = list(secciones_por_oferta.keys())

        horarios_por_oferta = {}
        if oferta_ids:
            horarios_todos = OfertaAcademicaHorario.query.filter(
                OfertaAcademicaHorario.oferta_academica_id.in_(oferta_ids)
            ).all()
            for h in horarios_todos:
                horarios_por_oferta.setdefault(h.oferta_academica_id, []).append(h)

        ofertas_con_silabo = set()
        if oferta_ids:
            silabos_todos = Silabo.query.filter(
                Silabo.oferta_academica_id.in_(oferta_ids)
            ).all()
            ofertas_con_silabo = {s.oferta_academica_id for s in silabos_todos}

        resultado = []
        for oferta_id, info in secciones_por_oferta.items():
            oferta = info["oferta"]
            curso = oferta.curso
            horarios = horarios_por_oferta.get(oferta_id, [])

            resultado.append({
                "oferta_academica_id": oferta.id,
                "codigo_curso": curso.codigo,
                "nombre_curso": curso.nombre,
                "creditos": curso.creditos,
                "seccion": etiqueta_seccion(oferta),
                "horas_semanales": info["horas_semanales"],
                "estado_silabo": "Silabo Cargado" if oferta_id in ofertas_con_silabo else "Silabo Pendiente",
                "horario": [
                    {
                        "dia": DIAS_SEMANA.get(h.dia, h.dia),
                        "dia_numero": h.dia,
                        "hora_inicio": h.hora_inicio.strftime("%H:%M") if h.hora_inicio else None,
                        "hora_fin": h.hora_fin.strftime("%H:%M") if h.hora_fin else None,
                        "aula": h.aula,
                        "funcion_curso": h.funcion_curso,
                    }
                    for h in horarios
                ],
            })

        resultado.sort(key=lambda r: r["oferta_academica_id"])
        return resultado, None

    @staticmethod
    def cargar_silabo(usuario_id, oferta_academica_id, nombre_archivo, archivo_stream):
        docente = Docente.query.filter_by(usuario_id=usuario_id).first()
        if not docente:
            return None, "No se encontró un docente asociado a este usuario", 404

        asignado = OfertaAcademicaDocente.query.filter_by(
            oferta_academica_id=oferta_academica_id,
            docente_id=docente.id
        ).first()
        if not asignado:
            return None, "No tienes asignado este curso, no puedes cargar el sílabo", 403

        extension = os.path.splitext(nombre_archivo)[1].lower()
        if extension != ".pdf":
            return None, "Formato no válido. Solo se permiten documentos en formato PDF", 400

        archivo_stream.seek(0, os.SEEK_END)
        tamano = archivo_stream.tell()
        archivo_stream.seek(0)
        if tamano > TAMANO_MAXIMO_SILABO_BYTES:
            return None, "El archivo supera el tamaño máximo permitido de 10 MB", 413

        os.makedirs(CARPETA_SILABOS, exist_ok=True)
        nombre_unico = f"silabo_{oferta_academica_id}_{uuid.uuid4()}{extension}"
        ruta_completa = os.path.join(CARPETA_SILABOS, nombre_unico)
        archivo_stream.save(ruta_completa)

        silabo = Silabo.query.filter_by(oferta_academica_id=oferta_academica_id).first()
        if silabo:
            silabo.nombre_archivo = nombre_archivo
            silabo.ruta_archivo = ruta_completa
            silabo.subido_en = datetime.utcnow()
        else:
            silabo = Silabo(
                oferta_academica_id=oferta_academica_id,
                nombre_archivo=nombre_archivo,
                ruta_archivo=ruta_completa
            )
            db.session.add(silabo)

        db.session.commit()
        return silabo, None, 201

    @staticmethod
    def obtener_silabo(oferta_academica_id):
        silabo = Silabo.query.filter_by(oferta_academica_id=oferta_academica_id).first()
        if not silabo:
            return None, "No hay sílabo cargado para este curso"
        return silabo, None

    @staticmethod
    def asignar_docente(oferta_academica_id, docente_id, funcion_curso, horas_asignadas, tipo_docente_id=None):
        oferta = OfertaAcademica.query.get(oferta_academica_id)
        if not oferta:
            return None, "Oferta académica no encontrada", 404

        if funcion_curso not in FUNCIONES_VALIDAS:
            return None, "El tipo de docente debe ser Teorico o Practico", 422

        if not isinstance(horas_asignadas, int) or horas_asignadas <= 0:
            return None, "Las horas asignadas deben ser un número entero positivo", 422

        asignaciones_actuales = OfertaAcademicaDocente.query.filter_by(
            oferta_academica_id=oferta_academica_id
        ).all()

        if any(a.funcion_curso == funcion_curso for a in asignaciones_actuales):
            return None, (
                f"La sección ya cuenta con un docente de tipo {funcion_curso} asignado. "
                f"Debe registrar un docente de tipo distinto para completar la carga horaria"
            ), 409

        curso = oferta.curso
        horas_requeridas_curso = curso.horas_lectivas + curso.horas_practicas
        suma_horas_actual = sum(a.horas_asignadas or 0 for a in asignaciones_actuales)
        suma_horas_nueva = suma_horas_actual + horas_asignadas

        funciones_despues = {a.funcion_curso for a in asignaciones_actuales} | {funcion_curso}
        plana_completa_por_funciones = set(FUNCIONES_VALIDAS).issubset(funciones_despues)

        if plana_completa_por_funciones and suma_horas_nueva != horas_requeridas_curso:
            return None, (
                f"Error en la asignación: La suma de horas de los docentes asignados "
                f"({suma_horas_nueva}) no coincide con las horas requeridas por el plan de estudios "
                f"({horas_requeridas_curso})"
            ), 422

        if not plana_completa_por_funciones and suma_horas_nueva > horas_requeridas_curso:
            return None, (
                f"Error en la asignación: La suma de horas de los docentes asignados "
                f"({suma_horas_nueva}) no coincide con las horas requeridas por el plan de estudios "
                f"({horas_requeridas_curso})"
            ), 422

        asignacion_existente = next(
            (a for a in asignaciones_actuales if a.docente_id == docente_id and a.funcion_curso is None),
            None,
        )

        if asignacion_existente:
            asignacion_existente.tipo_docente_id = tipo_docente_id
            asignacion_existente.funcion_curso = funcion_curso
            asignacion_existente.horas_asignadas = horas_asignadas
            asignacion = asignacion_existente
        else:
            asignacion = OfertaAcademicaDocente(
                oferta_academica_id=oferta_academica_id,
                docente_id=docente_id,
                tipo_docente_id=tipo_docente_id,
                funcion_curso=funcion_curso,
                horas_asignadas=horas_asignadas,
            )
            db.session.add(asignacion)

        db.session.commit()

        estado_seccion = (
            "Plana Docente Completa"
            if plana_completa_por_funciones and suma_horas_nueva == horas_requeridas_curso
            else "Plana Docente Incompleta"
        )

        return {
            "id": asignacion.id,
            "suma_horas_asignadas": suma_horas_nueva,
            "horas_requeridas_curso": horas_requeridas_curso,
            "estado_seccion": estado_seccion,
        }, None, 201

    @staticmethod
    def gestionar_horario(oferta_academica_id, dia, hora_inicio, hora_fin, aula, funcion_curso=None):
        oferta = OfertaAcademica.query.get(oferta_academica_id)
        if not oferta:
            return None, "Oferta académica no encontrada", 404

        if funcion_curso is not None and funcion_curso not in FUNCIONES_VALIDAS:
            return None, "El tipo de clase debe ser Teorico o Practico", 422

        if hora_fin <= hora_inicio:
            return None, "La hora de fin debe ser posterior a la hora de inicio", 400

        colision_aula = (
            OfertaAcademicaHorario.query
            .filter(
                OfertaAcademicaHorario.aula == aula,
                OfertaAcademicaHorario.dia == dia,
                OfertaAcademicaHorario.hora_inicio < hora_fin,
                OfertaAcademicaHorario.hora_fin > hora_inicio,
            )
            .join(OfertaAcademica, OfertaAcademicaHorario.oferta_academica_id == OfertaAcademica.id)
            .first()
        )
        if colision_aula:
            nombre_curso_existente = colision_aula.oferta_academica.curso.nombre
            return None, (
                f"El aula seleccionada ya se encuentra asignada al curso {nombre_curso_existente} en ese horario"
            ), 409

        colision_seccion = (
            OfertaAcademicaHorario.query
            .join(OfertaAcademica, OfertaAcademicaHorario.oferta_academica_id == OfertaAcademica.id)
            .filter(
                OfertaAcademica.semestre_id == oferta.semestre_id,
                OfertaAcademica.periodo_academico_id == oferta.periodo_academico_id,
                OfertaAcademicaHorario.dia == dia,
                OfertaAcademicaHorario.hora_inicio < hora_fin,
                OfertaAcademicaHorario.hora_fin > hora_inicio,
            )
            .first()
        )
        if colision_seccion:
            return None, "El grupo de estudiantes ya tiene una clase asignada en ese bloque horario", 409

        horario = OfertaAcademicaHorario(
            oferta_academica_id=oferta_academica_id,
            dia=dia,
            hora_inicio=hora_inicio,
            hora_fin=hora_fin,
            aula=aula,
            estado="Activo",
            funcion_curso=funcion_curso,
        )
        db.session.add(horario)
        db.session.commit()

        return {"id": horario.id, "estado": horario.estado}, None, 201

    @staticmethod
    def carga_docente(especialidad_id=None, periodo_academico_id=None):
        docentes = Docente.query.all()
        if not docentes:
            return []

        docente_ids = [d.id for d in docentes]

        consulta = OfertaAcademicaDocente.query.filter(
            OfertaAcademicaDocente.docente_id.in_(docente_ids)
        ).join(
            OfertaAcademica, OfertaAcademicaDocente.oferta_academica_id == OfertaAcademica.id
        ).options(
            joinedload(OfertaAcademicaDocente.oferta_academica).joinedload(OfertaAcademica.curso)
        )
        if periodo_academico_id:
            consulta = consulta.filter(OfertaAcademica.periodo_academico_id == periodo_academico_id)

        asignaciones_todas = consulta.all()

        asignaciones_por_docente = {}
        for a in asignaciones_todas:
            asignaciones_por_docente.setdefault(a.docente_id, []).append(a)

        curso_ids = {a.oferta_academica.curso_id for a in asignaciones_todas}

        especialidad_por_curso = {}
        if curso_ids:
            filas = (
                db.session.query(PlanCursosSemestre.curso_id, PlanDeEstudios.especialidad_id)
                .join(PlanDeEstudios, PlanCursosSemestre.plan_estudios_id == PlanDeEstudios.id)
                .filter(PlanCursosSemestre.curso_id.in_(curso_ids))
                .distinct()
                .all()
            )
            for curso_id, esp_id in filas:
                if esp_id is not None:
                    especialidad_por_curso.setdefault(curso_id, esp_id)

        especialidad_ids_usadas = set(especialidad_por_curso.values())
        especialidades = {}
        if especialidad_ids_usadas:
            especialidades = {
                e.id: e.nombre
                for e in Especialidad.query.filter(Especialidad.id.in_(especialidad_ids_usadas)).all()
            }

        docente_ids_para_filtro = None
        if especialidad_id:
            filas_filtro = (
                db.session.query(OfertaAcademicaDocente.docente_id)
                .join(OfertaAcademica, OfertaAcademica.id == OfertaAcademicaDocente.oferta_academica_id)
                .join(Curso, Curso.id == OfertaAcademica.curso_id)
                .join(PlanCursosSemestre, PlanCursosSemestre.curso_id == Curso.id)
                .join(PlanDeEstudios, PlanDeEstudios.id == PlanCursosSemestre.plan_estudios_id)
                .filter(PlanDeEstudios.especialidad_id == especialidad_id)
                .filter(OfertaAcademicaDocente.docente_id.in_(docente_ids))
                .distinct()
                .all()
            )
            docente_ids_para_filtro = {f[0] for f in filas_filtro}

        resultado = []
        for d in docentes:
            asignaciones = asignaciones_por_docente.get(d.id)
            if not asignaciones:
                continue

            if docente_ids_para_filtro is not None and d.id not in docente_ids_para_filtro:
                continue

            especialidad_nombre = None
            for a in asignaciones:
                esp_id = especialidad_por_curso.get(a.oferta_academica.curso_id)
                if esp_id:
                    especialidad_nombre = especialidades.get(esp_id)
                    break

            total_horas = sum(a.horas_asignadas or 0 for a in asignaciones)

            if total_horas < CARGA_MINIMA_SEMANAL:
                categoria = "Carga Incompleta"
            elif total_horas > CARGA_MAXIMA_SEMANAL:
                categoria = "Sobrecarga Laboral"
            else:
                categoria = "Carga Regular"

            resultado.append({
                "docente_id": d.id,
                "nombres": d.nombres,
                "apellido_paterno": d.apellido_paterno,
                "apellido_materno": d.apellido_materno,
                "especialidad": especialidad_nombre,
                "total_horas_semanales": total_horas,
                "categoria": categoria,
                "detalle_cursos": [
                    {
                        "curso_nombre": a.oferta_academica.curso.nombre,
                        "funcion_curso": a.funcion_curso,
                        "horas_asignadas": a.horas_asignadas,
                    }
                    for a in asignaciones
                ],
            })

        return resultado

    @staticmethod
    def cumplimiento_silabos(periodo_academico_id=None):
        if not periodo_academico_id:
            periodo = CursosDocentesService.periodo_activo()
            periodo_academico_id = periodo.id if periodo else None

        ofertas = OfertaAcademica.query.filter_by(
            periodo_academico_id=periodo_academico_id
        ).options(joinedload(OfertaAcademica.curso)).all()

        total_cursos = len(ofertas)
        total_cargados = 0
        pendientes = []
        por_especialidad = {}

        oferta_ids = [o.id for o in ofertas]
        curso_ids = {o.curso_id for o in ofertas}

        ofertas_con_silabo = set()
        if oferta_ids:
            silabos_todos = Silabo.query.filter(
                Silabo.oferta_academica_id.in_(oferta_ids)
            ).all()
            ofertas_con_silabo = {s.oferta_academica_id for s in silabos_todos}

        especialidad_por_curso = {}
        if curso_ids:
            filas = (
                db.session.query(PlanCursosSemestre.curso_id, PlanDeEstudios.especialidad_id)
                .join(PlanDeEstudios, PlanCursosSemestre.plan_estudios_id == PlanDeEstudios.id)
                .filter(PlanCursosSemestre.curso_id.in_(curso_ids))
                .distinct()
                .all()
            )
            for curso_id, esp_id in filas:
                especialidad_por_curso.setdefault(curso_id, esp_id)

        especialidad_ids_usadas = {e for e in especialidad_por_curso.values() if e}
        especialidades = {}
        if especialidad_ids_usadas:
            especialidades = {
                e.id: e.nombre
                for e in Especialidad.query.filter(Especialidad.id.in_(especialidad_ids_usadas)).all()
            }

        oferta_ids_sin_silabo = [o.id for o in ofertas if o.id not in ofertas_con_silabo]
        docente_por_oferta = {}
        if oferta_ids_sin_silabo:
            asignaciones_todas = (
                OfertaAcademicaDocente.query
                .options(joinedload(OfertaAcademicaDocente.docente))
                .filter(OfertaAcademicaDocente.oferta_academica_id.in_(oferta_ids_sin_silabo))
                .all()
            )
            for a in asignaciones_todas:
                docente_por_oferta.setdefault(a.oferta_academica_id, a.docente)

        for oferta in ofertas:
            especialidad_id_oferta = especialidad_por_curso.get(oferta.curso_id)
            nombre_especialidad = (
                especialidades.get(especialidad_id_oferta, "Sin especialidad")
                if especialidad_id_oferta
                else "Sin especialidad"
            )

            por_especialidad.setdefault(nombre_especialidad, {"total": 0, "cargados": 0})
            por_especialidad[nombre_especialidad]["total"] += 1

            if oferta.id in ofertas_con_silabo:
                total_cargados += 1
                por_especialidad[nombre_especialidad]["cargados"] += 1
            else:
                docente = docente_por_oferta.get(oferta.id)
                pendientes.append({
                    "oferta_academica_id": oferta.id,
                    "curso_nombre": oferta.curso.nombre,
                    "especialidad": nombre_especialidad,
                    "docente_nombre": (
                        f"{docente.nombres} {docente.apellido_paterno}" if docente else "Sin docente asignado"
                    ),
                    "docente_correo": docente.correo_institucional if docente else None,
                })

        porcentaje_general = round((total_cargados / total_cursos) * 100, 1) if total_cursos else 0

        resumen_por_especialidad = [
            {
                "especialidad": nombre,
                "total_cursos": datos["total"],
                "cursos_cargados": datos["cargados"],
                "porcentaje": round((datos["cargados"] / datos["total"]) * 100, 1) if datos["total"] else 0,
            }
            for nombre, datos in por_especialidad.items()
        ]

        return {
            "porcentaje_general": porcentaje_general,
            "total_cursos": total_cursos,
            "total_cargados": total_cargados,
            "resumen_por_especialidad": resumen_por_especialidad,
            "pendientes": pendientes,
        }