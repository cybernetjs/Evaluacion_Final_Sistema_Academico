import io
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from app import db
from app.modelos.matricula import Matricula
from app.modelos.estudiante import Estudiante
from app.modelos.estado_matricula import EstadoMatricula


class MatriculaService:

    @staticmethod
    def generar_pdf_ficha(matricula_id):
        matricula = Matricula.query.get(matricula_id)

        if not matricula:
            return None, "Matrícula no encontrada"

        estudiante = Estudiante.query.get(matricula.estudiante_id)

        buffer = io.BytesIO()
        pdf = canvas.Canvas(buffer, pagesize=letter)

        pdf.setFont("Helvetica-Bold", 16)
        pdf.drawString(100, 750, "FICHA DE MATRÍCULA")

        pdf.setFont("Helvetica", 12)
        pdf.drawString(100, 700, f"N° de Matrícula: {matricula.id}")
        pdf.drawString(100, 680, f"Estudiante: {estudiante.nombres} {estudiante.apellido_paterno} {estudiante.apellido_materno}")
        pdf.drawString(100, 660, f"Correo institucional: {estudiante.correo_institucional}")
        pdf.drawString(100, 640, f"Periodo académico: {matricula.periodo_academico_id}")
        pdf.drawString(100, 620, f"Semestre: {matricula.semestre_id}")
        pdf.drawString(100, 600, f"Estado: {matricula.estado.nombre if matricula.estado else 'N/A'}")
        pdf.drawString(100, 580, f"Pagado: {'Sí' if matricula.pagado else 'No'}")

        pdf.showPage()
        pdf.save()

        buffer.seek(0)
        return buffer, None

    @staticmethod
    def _nombre_periodo_actual(fecha=None):
        fecha = fecha or datetime.now()
        semestre = "I" if fecha.month <= 6 else "II"
        return f"{fecha.year}-{semestre}"

    @staticmethod
    def periodo_actual():
        from app.modelos.periodo_academico import PeriodoAcademico

        fecha = datetime.now()
        nombre = MatriculaService._nombre_periodo_actual(fecha)
        periodo = PeriodoAcademico.query.filter_by(nombre=nombre).first()

        if periodo:
            return periodo

        if fecha.month <= 6:
            fecha_inicio = datetime(fecha.year, 1, 1)
            fecha_fin = datetime(fecha.year, 6, 30)
        else:
            fecha_inicio = datetime(fecha.year, 7, 1)
            fecha_fin = datetime(fecha.year, 12, 31)

        periodo = PeriodoAcademico(nombre=nombre, fecha_inicio=fecha_inicio, fecha_fin=fecha_fin)
        db.session.add(periodo)
        db.session.commit()
        return periodo

    @staticmethod
    def _cursos_aprobados_y_desaprobados(estudiante_id):
        from app.modelos.matricula_detalle import MatriculaDetalle
        from app.modelos.estado_curso import EstadoCurso

        matriculas_ids = [m.id for m in Matricula.query.filter_by(estudiante_id=estudiante_id).all()]
        detalles = MatriculaDetalle.query.filter(MatriculaDetalle.matricula_id.in_(matriculas_ids)).all()

        aprobados = set()
        desaprobados = set()

        for d in detalles:
            estado = EstadoCurso.query.get(d.estado_curso_id)
            curso_id = d.oferta_academica.curso_id
            if estado and estado.nombre.lower() == "aprobado":
                aprobados.add(curso_id)
                desaprobados.discard(curso_id)
            elif estado and estado.nombre.lower() == "desaprobado":
                if curso_id not in aprobados:
                    desaprobados.add(curso_id)

        return aprobados, desaprobados

    @staticmethod
    def _prerequisitos_faltantes(curso_id, aprobados):
        from app.modelos.pre_requisito import PreRequisito

        requisitos = PreRequisito.query.filter_by(curso_dependiente_id=curso_id).all()
        return [r.curso_requisito for r in requisitos if r.curso_requisito_id not in aprobados]

    @staticmethod
    def cursos_disponibles(usuario_id, periodo_academico_id):
        from app.modelos.plan_estudiante import PlanEstudiante
        from app.modelos.plan_cursos_semestre import PlanCursosSemestre
        from app.modelos.oferta_academica import OfertaAcademica

        estudiante = Estudiante.query.filter_by(usuario_id=usuario_id).first()
        if not estudiante:
            return None, "No se encontró un estudiante asociado a este usuario"

        plan_estudiante = PlanEstudiante.query.filter_by(estudiante_id=estudiante.id).first()
        if not plan_estudiante:
            return None, "El estudiante no tiene un plan de estudios asignado"

        plan_id = plan_estudiante.plan_estudios_id
        cursos_del_plan = PlanCursosSemestre.query.filter_by(plan_estudios_id=plan_id).order_by(
            PlanCursosSemestre.semestre_id
        ).all()

        aprobados, desaprobados = MatriculaService._cursos_aprobados_y_desaprobados(estudiante.id)

        semestres_ordenados = sorted(set(item.semestre_id for item in cursos_del_plan))
        semestre_actual = semestres_ordenados[-1] if semestres_ordenados else 1
        intentados = aprobados | desaprobados

        for sem in semestres_ordenados:
            cursos_sem = [i.curso_id for i in cursos_del_plan if i.semestre_id == sem]
            if not all(c in intentados for c in cursos_sem):
                semestre_actual = sem
                break
        else:
            semestre_actual = semestres_ordenados[-1] + 1 if semestres_ordenados else 1

        creditos_maximos = 22
        resultado = []

        def agregar_curso(item, tipo):
            curso = item.curso
            faltantes = MatriculaService._prerequisitos_faltantes(curso.id, aprobados)
            oferta = OfertaAcademica.query.filter_by(
                periodo_academico_id=periodo_academico_id,
                curso_id=curso.id,
                semestre_id=item.semestre_id
            ).first()

            habilitado = len(faltantes) == 0 and oferta is not None
            motivo = None
            if faltantes:
                motivo = "Falta aprobar: " + ", ".join(f.nombre for f in faltantes)
            elif not oferta:
                motivo = "No hay oferta académica para este curso en el periodo actual"

            horarios = []
            if oferta:
                for h in oferta.horarios:
                    horarios.append({"dia": h.dia, "hora_inicio": str(h.hora_inicio), "hora_fin": str(h.hora_fin)})

            resultado.append({
                "curso_id": curso.id,
                "curso_nombre": curso.nombre,
                "creditos": curso.creditos,
                "semestre_id": item.semestre_id,
                "tipo": tipo,
                "habilitado": habilitado,
                "motivo_bloqueo": motivo,
                "oferta_academica_id": oferta.id if oferta else None,
                "horarios": horarios
            })

        for item in cursos_del_plan:
            if item.semestre_id == semestre_actual:
                agregar_curso(item, "regular")

        for item in cursos_del_plan:
            if item.semestre_id < semestre_actual and item.curso_id in desaprobados:
                agregar_curso(item, "repetir")

        semestre_siguiente = semestre_actual + 1
        for item in cursos_del_plan:
            if item.semestre_id == semestre_siguiente:
                agregar_curso(item, "adelanto")

        return {
            "semestre_actual": semestre_actual,
            "creditos_maximos_por_ciclo": creditos_maximos,
            "cursos": resultado
        }, None

    @staticmethod
    def solicitar_matricula(usuario_id, ofertas_seleccionadas):
        from app.modelos.matricula_detalle import MatriculaDetalle
        from app.modelos.estado_curso import EstadoCurso

        if not ofertas_seleccionadas:
            return None, "Debes seleccionar al menos un curso"

        periodo = MatriculaService.periodo_actual()
        disponibles, error = MatriculaService.cursos_disponibles(usuario_id, periodo.id)
        if error:
            return None, error

        mapa_disponibles = {c["oferta_academica_id"]: c for c in disponibles["cursos"] if c["oferta_academica_id"]}

        total_creditos = 0
        horarios_ocupados = []

        for oferta_id in ofertas_seleccionadas:
            curso_info = mapa_disponibles.get(oferta_id)

            if not curso_info:
                return None, f"La oferta {oferta_id} no está disponible para este estudiante"

            if not curso_info["habilitado"]:
                return None, f"No puedes llevar '{curso_info['curso_nombre']}': {curso_info['motivo_bloqueo']}"

            for h in curso_info["horarios"]:
                for ocupado in horarios_ocupados:
                    if h["dia"] == ocupado["dia"] and h["hora_inicio"] < ocupado["hora_fin"] and h["hora_fin"] > ocupado["hora_inicio"]:
                        return None, f"Cruce de horario con el curso '{curso_info['curso_nombre']}'"
                horarios_ocupados.append(h)

            total_creditos += curso_info["creditos"]

        if total_creditos > disponibles["creditos_maximos_por_ciclo"]:
            return None, f"Excedes el máximo de {disponibles['creditos_maximos_por_ciclo']} créditos por ciclo"

        estudiante = Estudiante.query.filter_by(usuario_id=usuario_id).first()
        estado_pendiente = EstadoMatricula.query.filter_by(nombre="Pendiente").first()
        estado_cursando = EstadoCurso.query.filter_by(nombre="Cursando").first()

        matricula = Matricula(
            estudiante_id=estudiante.id,
            periodo_academico_id=periodo.id,
            semestre_id=disponibles["semestre_actual"],
            estado_id=estado_pendiente.id,
        )
        db.session.add(matricula)
        db.session.flush()

        for oferta_id in ofertas_seleccionadas:
            detalle = MatriculaDetalle(
                matricula_id=matricula.id,
                oferta_academica_id=oferta_id,
                estado_curso_id=estado_cursando.id if estado_cursando else None
            )
            db.session.add(detalle)

        db.session.commit()
        return {"id": matricula.id, "total_creditos": total_creditos}, None