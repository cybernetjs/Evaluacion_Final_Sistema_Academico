import os
import uuid
from datetime import datetime
from app import db
from app.modelos.silabo import Silabo
from app.modelos.docente import Docente
from app.modelos.curso import Curso
from app.modelos.oferta_academica import OfertaAcademica
from app.modelos.oferta_academica_docente import OfertaAcademicaDocente
from app.modelos.oferta_academica_horario import OfertaAcademicaHorario
from app.modelos.periodo_academico import PeriodoAcademico
from app.modelos.plan_cursos_semestre import PlanCursosSemestre
from app.modelos.plan_de_estudios import PlanDeEstudios
from app.modelos.especialidad import Especialidad

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
        from app.utils.ciclo_academico import periodo_activo as periodo_activo_global
        return periodo_activo_global()

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

        return [{"id": p.id, "nombre": p.nombre} for p in periodos], None

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
            .join(OfertaAcademica, OfertaAcademicaDocente.oferta_academica_id == OfertaAcademica.id)
            .filter(OfertaAcademica.periodo_academico_id == periodo_academico_id)
            .all()
        )

        resultado = []
        for a in asignaciones:
            oferta = a.oferta_academica
            curso = oferta.curso
            horarios = OfertaAcademicaHorario.query.filter_by(oferta_academica_id=oferta.id).all()
            silabo = Silabo.query.filter_by(oferta_academica_id=oferta.id).first()

            resultado.append({
                "oferta_academica_id": oferta.id,
                "codigo_curso": curso.codigo,
                "nombre_curso": curso.nombre,
                "creditos": curso.creditos,
                "seccion": f"S-{oferta.id}",
                "funcion_curso": a.funcion_curso,
                "horas_semanales": a.horas_asignadas,
                "estado_silabo": "Silabo Cargado" if silabo else "Silabo Pendiente",
                "horario": [
                    {
                        "dia": DIAS_SEMANA.get(h.dia, h.dia),
                        "dia_numero": h.dia,
                        "hora_inicio": h.hora_inicio.strftime("%H:%M") if h.hora_inicio else None,
                        "hora_fin": h.hora_fin.strftime("%H:%M") if h.hora_fin else None,
                        "aula": h.aula,
                    }
                    for h in horarios
                ],
            })

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
    def gestionar_horario(oferta_academica_id, dia, hora_inicio, hora_fin, aula):
        oferta = OfertaAcademica.query.get(oferta_academica_id)
        if not oferta:
            return None, "Oferta académica no encontrada", 404

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
        )
        db.session.add(horario)
        db.session.commit()

        return {"id": horario.id, "estado": horario.estado}, None, 201

    @staticmethod
    def _especialidad_por_docente(docente_id):
        curso_ids = (
            db.session.query(OfertaAcademica.curso_id)
            .join(OfertaAcademicaDocente, OfertaAcademicaDocente.oferta_academica_id == OfertaAcademica.id)
            .filter(OfertaAcademicaDocente.docente_id == docente_id)
            .distinct()
            .all()
        )
        curso_ids = [c[0] for c in curso_ids]

        especialidad_ids = (
            db.session.query(PlanDeEstudios.especialidad_id)
            .join(PlanCursosSemestre, PlanCursosSemestre.plan_estudios_id == PlanDeEstudios.id)
            .filter(PlanCursosSemestre.curso_id.in_(curso_ids))
            .distinct()
            .all()
        )
        ids = [e[0] for e in especialidad_ids if e[0]]
        if not ids:
            return None

        especialidad = Especialidad.query.get(ids[0])
        return especialidad.nombre if especialidad else None

    @staticmethod
    def carga_docente(especialidad_id=None, periodo_academico_id=None):
        docentes = Docente.query.all()
        resultado = []

        for d in docentes:
            consulta = OfertaAcademicaDocente.query.filter_by(docente_id=d.id).join(
                OfertaAcademica, OfertaAcademicaDocente.oferta_academica_id == OfertaAcademica.id
            )
            if periodo_academico_id:
                consulta = consulta.filter(OfertaAcademica.periodo_academico_id == periodo_academico_id)

            asignaciones = consulta.all()
            if not asignaciones:
                continue

            especialidad_nombre = CursosDocentesService._especialidad_por_docente(d.id)
            if especialidad_id:
                especialidades_docente = (
                    db.session.query(PlanDeEstudios.especialidad_id)
                    .join(PlanCursosSemestre, PlanCursosSemestre.plan_estudios_id == PlanDeEstudios.id)
                    .join(Curso, Curso.id == PlanCursosSemestre.curso_id)
                    .join(OfertaAcademica, OfertaAcademica.curso_id == Curso.id)
                    .join(OfertaAcademicaDocente, OfertaAcademicaDocente.oferta_academica_id == OfertaAcademica.id)
                    .filter(OfertaAcademicaDocente.docente_id == d.id)
                    .distinct()
                    .all()
                )
                ids_especialidad_docente = {e[0] for e in especialidades_docente}
                if int(especialidad_id) not in ids_especialidad_docente:
                    continue

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

        ofertas = OfertaAcademica.query.filter_by(periodo_academico_id=periodo_academico_id).all()

        total_cursos = len(ofertas)
        total_cargados = 0
        pendientes = []
        por_especialidad = {}

        for oferta in ofertas:
            silabo = Silabo.query.filter_by(oferta_academica_id=oferta.id).first()

            especialidad_ids = (
                db.session.query(PlanDeEstudios.especialidad_id)
                .join(PlanCursosSemestre, PlanCursosSemestre.plan_estudios_id == PlanDeEstudios.id)
                .filter(PlanCursosSemestre.curso_id == oferta.curso_id)
                .distinct()
                .all()
            )
            especialidad = Especialidad.query.get(especialidad_ids[0][0]) if especialidad_ids else None
            nombre_especialidad = especialidad.nombre if especialidad else "Sin especialidad"

            por_especialidad.setdefault(nombre_especialidad, {"total": 0, "cargados": 0})
            por_especialidad[nombre_especialidad]["total"] += 1

            if silabo:
                total_cargados += 1
                por_especialidad[nombre_especialidad]["cargados"] += 1
            else:
                docente_asignado = OfertaAcademicaDocente.query.filter_by(oferta_academica_id=oferta.id).first()
                docente = docente_asignado.docente if docente_asignado else None
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
