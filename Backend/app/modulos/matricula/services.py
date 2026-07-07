import io
import os
import uuid
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from app import db
from app.modelos.matricula import Matricula
from app.modelos.estudiante import Estudiante
from app.modelos.estado_matricula import EstadoMatricula

CARPETA_COMPROBANTES = os.path.join(os.getcwd(), "uploads", "comprobantes")
EXTENSIONES_PERMITIDAS = {".pdf", ".jpg", ".jpeg", ".png"}
TAMANO_MAXIMO_BYTES = 5 * 1024 * 1024


class MatriculaService:

    @staticmethod
    def _dibujar_marca_de_agua(pdf, texto, ancho_pagina, alto_pagina):
        pdf.saveState()
        pdf.setFont("Helvetica-Bold", 40)
        pdf.setFillColorRGB(0.85, 0.15, 0.15, alpha=0.25)
        pdf.translate(ancho_pagina / 2, alto_pagina / 2)
        pdf.rotate(45)
        pdf.drawCentredString(0, 0, texto)
        pdf.restoreState()

    @staticmethod
    def mi_solicitud_actual(usuario_id, periodo_id):
        estudiante = Estudiante.query.filter_by(usuario_id=usuario_id).first()
        if not estudiante:
            return None, "Estudiante no encontrado"

        matricula = (
            Matricula.query.filter_by(estudiante_id=estudiante.id, periodo_academico_id=periodo_id)
            .order_by(Matricula.id.desc())
            .first()
        )

        if not matricula:
            return {"matricula": None}, None

        return {
            "matricula": {
                "id": matricula.id,
                "estado": matricula.estado.nombre if matricula.estado else None,
                "pagado": matricula.pagado,
            }
        }, None

    @staticmethod
    def generar_pdf_ficha_preliminar(usuario_id, ip_solicitante):
        from reportlab.lib.pagesizes import letter as tamano_letter
        from app.modelos.matricula_detalle import MatriculaDetalle
        from app.modelos.usuario import Usuario
        from app.modelos.auditoria import Auditoria

        estudiante = Estudiante.query.filter_by(usuario_id=usuario_id).first()
        if not estudiante:
            return None, "Estudiante no encontrado"

        periodo = MatriculaService.periodo_actual()

        matricula = (
            Matricula.query.filter_by(estudiante_id=estudiante.id, periodo_academico_id=periodo.id)
            .join(EstadoMatricula, Matricula.estado_id == EstadoMatricula.id)
            .filter(db.func.lower(EstadoMatricula.nombre) == "pendiente")
            .order_by(Matricula.id.desc())
            .first()
        )

        if not matricula:
            return None, "No tienes una solicitud de matrícula pendiente de validación en este periodo"

        detalles = MatriculaDetalle.query.filter_by(matricula_id=matricula.id).all()
        usuario = Usuario.query.get(usuario_id)

        ancho, alto = tamano_letter
        buffer = io.BytesIO()
        pdf = canvas.Canvas(buffer, pagesize=tamano_letter)

        def encabezado():
            MatriculaService._dibujar_marca_de_agua(
                pdf, "DOCUMENTO PRELIMINAR - SIN VALOR OFICIAL", ancho, alto
            )
            pdf.setFont("Helvetica-Bold", 16)
            pdf.drawString(80, alto - 60, "FICHA DE MATRÍCULA PRELIMINAR")
            pdf.setFont("Helvetica", 11)
            pdf.drawString(80, alto - 90, f"Código: {usuario.username}")
            pdf.drawString(
                80, alto - 108,
                f"Estudiante: {estudiante.nombres} {estudiante.apellido_paterno} {estudiante.apellido_materno}"
            )
            pdf.drawString(80, alto - 126, f"Periodo académico: {periodo.nombre}")
            pdf.drawString(80, alto - 144, f"N° de solicitud: {matricula.id}  —  Estado: Pendiente de Validación")

        encabezado()

        y = alto - 180
        pdf.setFont("Helvetica-Bold", 10)
        pdf.drawString(80, y, "Código")
        pdf.drawString(150, y, "Curso")
        pdf.drawString(360, y, "Créditos")
        pdf.drawString(430, y, "Horario")
        y -= 16
        pdf.setFont("Helvetica", 9)

        for d in detalles:
            oferta = d.oferta_academica
            curso = oferta.curso
            horarios = ", ".join(
                f"{h.dia}° día {h.hora_inicio.strftime('%H:%M')}-{h.hora_fin.strftime('%H:%M')}"
                for h in oferta.horarios
            ) or "Sin horario"

            if y < 100:
                pdf.showPage()
                encabezado()
                y = alto - 180

            pdf.drawString(80, y, curso.codigo)
            pdf.drawString(150, y, curso.nombre[:35])
            pdf.drawString(370, y, str(curso.creditos))
            pdf.drawString(430, y, horarios[:45])
            y -= 16

        pdf.showPage()
        pdf.save()
        buffer.seek(0)

        auditoria = Auditoria(
            usuario_id=usuario_id,
            accion="Descarga de ficha preliminar",
            detalle=f"matricula_id={matricula.id}, ip={ip_solicitante}",
        )
        db.session.add(auditoria)
        db.session.commit()

        return buffer, None

    @staticmethod
    def _generar_hash_matricula(matricula):
        import hashlib
        from app.modelos.matricula_detalle import MatriculaDetalle

        detalles = MatriculaDetalle.query.filter_by(matricula_id=matricula.id).order_by(
            MatriculaDetalle.oferta_academica_id
        ).all()
        ofertas_texto = "-".join(str(d.oferta_academica_id) for d in detalles)
        base = f"{matricula.id}|{matricula.estudiante_id}|{matricula.periodo_academico_id}|{ofertas_texto}"
        return hashlib.sha256(base.encode("utf-8")).hexdigest()

    @staticmethod
    def _generar_imagen_qr(texto):
        import qrcode
        from reportlab.lib.utils import ImageReader

        qr = qrcode.QRCode(box_size=4, border=2)
        qr.add_data(texto)
        qr.make(fit=True)
        imagen = qr.make_image(fill_color="black", back_color="white")
        buffer_qr = io.BytesIO()
        imagen.save(buffer_qr, format="PNG")
        buffer_qr.seek(0)
        return ImageReader(buffer_qr)

    @staticmethod
    def generar_pdf_ficha(matricula_id):
        from app.modelos.matricula_detalle import MatriculaDetalle
        from app.modelos.usuario import Usuario

        matricula = Matricula.query.get(matricula_id)
        if not matricula:
            return None, "Matrícula no encontrada"

        estudiante = Estudiante.query.get(matricula.estudiante_id)
        usuario = Usuario.query.get(estudiante.usuario_id)
        detalles = MatriculaDetalle.query.filter_by(matricula_id=matricula.id).all()
        hash_verificacion = MatriculaService._generar_hash_matricula(matricula)

        ancho, alto = letter
        buffer = io.BytesIO()
        pdf = canvas.Canvas(buffer, pagesize=letter)

        pdf.setFont("Helvetica-Bold", 16)
        pdf.drawString(80, alto - 60, "FICHA DE MATRÍCULA OFICIAL")

        pdf.setFont("Helvetica", 11)
        pdf.drawString(80, alto - 90, f"Código: {usuario.username}")
        pdf.drawString(
            80, alto - 108,
            f"Estudiante: {estudiante.nombres} {estudiante.apellido_paterno} {estudiante.apellido_materno}"
        )
        pdf.drawString(80, alto - 126, f"Periodo académico: {matricula.periodo_academico.nombre}")
        pdf.drawString(80, alto - 144, f"N° de matrícula: {matricula.id}  —  Estado: Matriculado")

        y = alto - 180
        pdf.setFont("Helvetica-Bold", 10)
        pdf.drawString(80, y, "Código")
        pdf.drawString(150, y, "Curso")
        pdf.drawString(340, y, "Créditos")
        pdf.drawString(400, y, "Sección")
        pdf.drawString(460, y, "Horario")
        y -= 16
        pdf.setFont("Helvetica", 9)

        for d in detalles:
            oferta = d.oferta_academica
            curso = oferta.curso
            horarios = ", ".join(
                f"{h.dia}° día {h.hora_inicio.strftime('%H:%M')}-{h.hora_fin.strftime('%H:%M')}"
                for h in oferta.horarios
            ) or "Sin horario"

            pdf.drawString(80, y, curso.codigo)
            pdf.drawString(150, y, curso.nombre[:30])
            pdf.drawString(350, y, str(curso.creditos))
            pdf.drawString(400, y, str(oferta.id))
            pdf.drawString(460, y, horarios[:40])
            y -= 16

        imagen_qr = MatriculaService._generar_imagen_qr(hash_verificacion)
        pdf.drawImage(imagen_qr, 80, 60, width=80, height=80)
        pdf.setFont("Helvetica", 7)
        pdf.drawString(170, 100, "Código de verificación:")
        pdf.drawString(170, 88, hash_verificacion)

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
    def _cursos_matriculados_activos(estudiante_id):
        from app.modelos.matricula_detalle import MatriculaDetalle
        from app.modelos.estado_curso import EstadoCurso

        matriculas_ids = [m.id for m in Matricula.query.filter_by(estudiante_id=estudiante_id).all()]
        detalles = MatriculaDetalle.query.filter(MatriculaDetalle.matricula_id.in_(matriculas_ids)).all()

        activos = set()
        for d in detalles:
            estado = EstadoCurso.query.get(d.estado_curso_id)
            if estado and estado.nombre.lower() == "cursando":
                activos.add(d.oferta_academica.curso_id)

        return activos

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
        matriculados_activos = MatriculaService._cursos_matriculados_activos(estudiante.id)

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
            ya_matriculado = curso.id in matriculados_activos
            faltantes = [] if ya_matriculado else MatriculaService._prerequisitos_faltantes(curso.id, aprobados)
            oferta = OfertaAcademica.query.filter_by(
                periodo_academico_id=periodo_academico_id,
                curso_id=curso.id,
                semestre_id=item.semestre_id
            ).first()

            habilitado = len(faltantes) == 0 and oferta is not None and not ya_matriculado
            motivo = None
            if ya_matriculado:
                motivo = "Ya te encuentras matriculado en este curso"
            elif faltantes:
                nombres_faltantes = ", ".join(f.nombre for f in faltantes)
                motivo = f"Asignatura no elegible debido a la falta de los siguientes sub-requisitos: [{nombres_faltantes}]"
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

        estudiante_actual = Estudiante.query.filter_by(usuario_id=usuario_id).first()
        estados_activos = ["pendiente", "validado", "matriculado"]
        matricula_activa = (
            Matricula.query.filter_by(estudiante_id=estudiante_actual.id, periodo_academico_id=periodo.id)
            .join(EstadoMatricula, Matricula.estado_id == EstadoMatricula.id)
            .filter(db.func.lower(EstadoMatricula.nombre).in_(estados_activos))
            .first()
        )
        if matricula_activa:
            return None, "Ya tienes una solicitud de matrícula activa para este periodo, no puedes enviar otra"

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

        estado_pendiente = EstadoMatricula.query.filter_by(nombre="Pendiente").first()
        estado_cursando = EstadoCurso.query.filter_by(nombre="Cursando").first()

        matricula = Matricula(
            estudiante_id=estudiante_actual.id,
            periodo_academico_id=periodo.id,
            semestre_id=disponibles["semestre_actual"],
            estado_id=estado_pendiente.id,
            created_at=datetime.now(),
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

    @staticmethod
    def registrar_pago(matricula_id, numero_operacion, fecha_pago, monto, archivo):
        from app.modelos.pago import Pago

        matricula = Matricula.query.get(matricula_id)
        if not matricula:
            return None, "Matrícula no encontrada", 404

        if not matricula.estado or matricula.estado.nombre != "Validado":
            return None, "La matrícula debe estar validada antes de registrar el pago", 400

        if not numero_operacion or not numero_operacion.strip():
            return None, "El número de operación es obligatorio", 400

        try:
            monto_decimal = float(monto)
        except (TypeError, ValueError):
            return None, "El monto pagado debe ser un valor numérico", 400

        if monto_decimal <= 0:
            return None, "El monto pagado debe ser mayor a cero", 400

        try:
            fecha_pago_convertida = datetime.strptime(fecha_pago, "%Y-%m-%d").date()
        except (TypeError, ValueError):
            return None, "La fecha de pago debe tener el formato AAAA-MM-DD", 400

        if not archivo or not archivo.filename:
            return None, "Debes adjuntar el comprobante de pago", 400

        extension = os.path.splitext(archivo.filename)[1].lower()
        if extension not in EXTENSIONES_PERMITIDAS:
            return None, "El comprobante debe ser un archivo PDF, JPEG o PNG", 400

        archivo.stream.seek(0, os.SEEK_END)
        tamano = archivo.stream.tell()
        archivo.stream.seek(0)
        if tamano > TAMANO_MAXIMO_BYTES:
            return None, "El comprobante no puede superar los 5 MB", 400

        duplicado = (
            Pago.query.join(Matricula, Pago.matricula_id == Matricula.id)
            .filter(
                Matricula.periodo_academico_id == matricula.periodo_academico_id,
                Pago.numero_operacion == numero_operacion.strip(),
            )
            .first()
        )
        if duplicado:
            return None, "El número de operación ya fue registrado en este periodo", 409

        os.makedirs(CARPETA_COMPROBANTES, exist_ok=True)
        nombre_unico = f"{uuid.uuid4()}{extension}"
        ruta_completa = os.path.join(CARPETA_COMPROBANTES, nombre_unico)
        archivo.save(ruta_completa)

        pago = Pago(
            matricula_id=matricula.id,
            numero_operacion=numero_operacion.strip(),
            fecha_pago=fecha_pago_convertida,
            monto=monto_decimal,
            comprobante_ruta=ruta_completa,
            comprobante_nombre_original=archivo.filename,
        )
        db.session.add(pago)

        matricula.pagado = True
        db.session.commit()

        return {
            "mensaje": "Pago registrado y verificado correctamente",
            "matricula_id": matricula.id,
            "pago_id": pago.id,
        }, None, 201

    @staticmethod
    def _plazo_vencido(matricula):
        if not matricula.created_at:
            return False
        dias_transcurridos = (datetime.now() - matricula.created_at).days
        limite = matricula.periodo_academico.dias_limite_pago or 15
        return dias_transcurridos > limite

    @staticmethod
    def listar_bandeja_validacion(periodo_id=None, especialidad_id=None, estado_nombre=None, pagina=1, por_pagina=10):
        consulta = Matricula.query.join(Estudiante, Matricula.estudiante_id == Estudiante.id).join(
            EstadoMatricula, Matricula.estado_id == EstadoMatricula.id
        )

        if periodo_id:
            consulta = consulta.filter(Matricula.periodo_academico_id == periodo_id)
        if especialidad_id:
            consulta = consulta.filter(Estudiante.especialidad_id == especialidad_id)
        if estado_nombre:
            consulta = consulta.filter(db.func.lower(EstadoMatricula.nombre) == estado_nombre.lower())

        total = consulta.count()
        matriculas = (
            consulta.order_by(Matricula.id.desc())
            .offset((pagina - 1) * por_pagina)
            .limit(por_pagina)
            .all()
        )

        filas = []
        for m in matriculas:
            estudiante = m.estudiante
            filas.append({
                "id": m.id,
                "estudiante_nombre": f"{estudiante.nombres} {estudiante.apellido_paterno} {estudiante.apellido_materno}",
                "especialidad_nombre": estudiante.especialidad.nombre if estudiante.especialidad else None,
                "periodo_nombre": m.periodo_academico.nombre if m.periodo_academico else None,
                "semestre_codigo": m.semestre.codigo if m.semestre else None,
                "estado": m.estado.nombre if m.estado else None,
                "pagado": m.pagado,
                "plazo_vencido": MatriculaService._plazo_vencido(m),
                "puede_cancelar": MatriculaService._plazo_vencido(m)
                and not m.pagado
                and m.estado.nombre.lower() not in ("matriculado", "observado", "anulado", "retirado"),
            })

        return {"matriculas": filas, "total": total, "pagina": pagina, "por_pagina": por_pagina}, None

    @staticmethod
    def validar_periodo(estudiante_id):
        matricula = (
            Matricula.query.filter_by(estudiante_id=estudiante_id)
            .join(EstadoMatricula, Matricula.estado_id == EstadoMatricula.id)
            .filter(db.func.lower(EstadoMatricula.nombre) == "pendiente")
            .order_by(Matricula.id.desc())
            .first()
        )

        if not matricula:
            return None, "El estudiante no tiene una solicitud pendiente de validación"

        return {"plazo_vencido": MatriculaService._plazo_vencido(matricula)}, None

    @staticmethod
    def cancelar_matricula(matricula_id):
        matricula = Matricula.query.get(matricula_id)
        if not matricula:
            return None, "Matrícula no encontrada"

        if matricula.pagado or matricula.estado.nombre.lower() == "matriculado":
            return None, "No se puede cancelar una matrícula con pago verificado o ya matriculada"

        if not MatriculaService._plazo_vencido(matricula):
            return None, "El plazo de pago aún no ha vencido, no se puede cancelar la matrícula"

        estado_observado = EstadoMatricula.query.filter_by(nombre="Observado").first()
        matricula.estado_id = estado_observado.id
        db.session.commit()

        return {
            "id": matricula.id,
            "estado": estado_observado.nombre,
            "motivo": "Cancelación por incumplimiento del periodo de pago establecido",
        }, None

    @staticmethod
    def oficializar_matricula(matricula_id):
        matricula = Matricula.query.get(matricula_id)
        if not matricula:
            return None, "Matrícula no encontrada"

        if not matricula.estado or matricula.estado.nombre != "Validado":
            return None, "La matrícula debe estar validada antes de generar la ficha oficial"

        if not matricula.pagado:
            return None, "No se puede generar la ficha oficial sin el pago verificado"

        estado_matriculado = EstadoMatricula.query.filter_by(nombre="Matriculado").first()
        matricula.estado_id = estado_matriculado.id
        db.session.commit()

        return {
            "mensaje": "Ficha oficial generada, matrícula confirmada",
            "matricula_id": matricula.id,
            "estado": estado_matriculado.nombre,
            "hash_verificacion": MatriculaService._generar_hash_matricula(matricula),
        }, None

    @staticmethod
    def descargar_ficha_oficial_estudiante(usuario_id):
        estudiante = Estudiante.query.filter_by(usuario_id=usuario_id).first()
        if not estudiante:
            return None, "Estudiante no encontrado"

        matricula = (
            Matricula.query.filter_by(estudiante_id=estudiante.id)
            .join(EstadoMatricula, Matricula.estado_id == EstadoMatricula.id)
            .filter(db.func.lower(EstadoMatricula.nombre) == "matriculado")
            .order_by(Matricula.id.desc())
            .first()
        )

        if not matricula:
            return None, "No tienes una matrícula oficializada"

        return MatriculaService.generar_pdf_ficha(matricula.id)

    @staticmethod
    def estadisticas_dashboard(periodo_id=None, especialidad_id=None):
        from app.modelos.especialidad import Especialidad
        from app.modelos.semestre import Semestre
        from app.modelos.oferta_academica import OfertaAcademica
        from app.modelos.curso import Curso
        from app.modelos.matricula_detalle import MatriculaDetalle
        from app.modelos.periodo_academico import PeriodoAcademico

        base = Matricula.query.join(Estudiante, Matricula.estudiante_id == Estudiante.id).join(
            EstadoMatricula, Matricula.estado_id == EstadoMatricula.id
        )
        if periodo_id:
            base = base.filter(Matricula.periodo_academico_id == periodo_id)
        if especialidad_id:
            base = base.filter(Estudiante.especialidad_id == especialidad_id)

        total_matriculados = base.filter(db.func.lower(EstadoMatricula.nombre) == "matriculado").count()
        total_pendientes = base.filter(db.func.lower(EstadoMatricula.nombre) == "pendiente").count()

        filas_ciclo = (
            base.filter(db.func.lower(EstadoMatricula.nombre) == "matriculado")
            .join(Semestre, Matricula.semestre_id == Semestre.id)
            .join(Especialidad, Estudiante.especialidad_id == Especialidad.id)
            .with_entities(
                Semestre.codigo.label("ciclo"),
                Especialidad.nombre.label("especialidad"),
                db.func.count(Matricula.id).label("total"),
            )
            .group_by(Semestre.codigo, Especialidad.nombre)
            .all()
        )
        matriculados_por_ciclo = [
            {"ciclo": f.ciclo, "especialidad": f.especialidad, "total": f.total} for f in filas_ciclo
        ]

        consulta_cursos = (
            MatriculaDetalle.query.join(OfertaAcademica, MatriculaDetalle.oferta_academica_id == OfertaAcademica.id)
            .join(Curso, OfertaAcademica.curso_id == Curso.id)
            .join(Matricula, MatriculaDetalle.matricula_id == Matricula.id)
        )
        if periodo_id:
            consulta_cursos = consulta_cursos.filter(Matricula.periodo_academico_id == periodo_id)

        filas_cursos = (
            consulta_cursos.with_entities(
                Curso.id.label("curso_id"),
                Curso.nombre.label("curso_nombre"),
                db.func.count(MatriculaDetalle.matricula_id).label("total_matriculados"),
            )
            .group_by(Curso.id, Curso.nombre)
            .order_by(db.func.count(MatriculaDetalle.matricula_id).desc())
            .limit(5)
            .all()
        )

        top_cursos = []
        for f in filas_cursos:
            ofertas_curso = OfertaAcademica.query.filter_by(curso_id=f.curso_id).all()
            cupos_totales = sum(o.cupos for o in ofertas_curso) or 1
            ocupacion = round((f.total_matriculados / cupos_totales) * 100, 1)
            top_cursos.append({
                "curso": f.curso_nombre,
                "matriculados": f.total_matriculados,
                "ocupacion_porcentaje": ocupacion,
                "seccion_critica": ocupacion >= 80,
            })

        periodo_actual_obj = None
        if periodo_id:
            periodo_actual_obj = PeriodoAcademico.query.get(periodo_id)

        ratio_avance = None
        if periodo_actual_obj:
            periodo_anterior = (
                PeriodoAcademico.query.filter(PeriodoAcademico.id != periodo_actual_obj.id)
                .filter(PeriodoAcademico.fecha_inicio < periodo_actual_obj.fecha_inicio)
                .order_by(PeriodoAcademico.fecha_inicio.desc())
                .first()
            )
            if periodo_anterior:
                total_anterior = (
                    Matricula.query.join(EstadoMatricula, Matricula.estado_id == EstadoMatricula.id)
                    .filter(Matricula.periodo_academico_id == periodo_anterior.id)
                    .filter(db.func.lower(EstadoMatricula.nombre) == "matriculado")
                    .count()
                )
                if total_anterior > 0:
                    ratio_avance = round(((total_matriculados - total_anterior) / total_anterior) * 100, 1)

        return {
            "total_matriculados": total_matriculados,
            "total_pendientes": total_pendientes,
            "matriculados_por_ciclo": matriculados_por_ciclo,
            "top_cursos": top_cursos,
            "ratio_avance_porcentaje": ratio_avance,
        }, None

    @staticmethod
    def exportar_reporte(periodo_id=None, especialidad_id=None, formato="csv"):
        consulta = Matricula.query.join(Estudiante, Matricula.estudiante_id == Estudiante.id).join(
            EstadoMatricula, Matricula.estado_id == EstadoMatricula.id
        )
        if periodo_id:
            consulta = consulta.filter(Matricula.periodo_academico_id == periodo_id)
        if especialidad_id:
            consulta = consulta.filter(Estudiante.especialidad_id == especialidad_id)

        registros = consulta.all()
        encabezados = ["id", "estudiante", "especialidad", "periodo", "estado", "pagado"]
        filas = []
        for m in registros:
            filas.append([
                m.id,
                f"{m.estudiante.nombres} {m.estudiante.apellido_paterno} {m.estudiante.apellido_materno}",
                m.estudiante.especialidad.nombre if m.estudiante.especialidad else "",
                m.periodo_academico.nombre if m.periodo_academico else "",
                m.estado.nombre if m.estado else "",
                "Sí" if m.pagado else "No",
            ])

        if formato == "xlsx":
            from openpyxl import Workbook

            libro = Workbook()
            hoja = libro.active
            hoja.append(encabezados)
            for fila in filas:
                hoja.append(fila)
            buffer = io.BytesIO()
            libro.save(buffer)
            buffer.seek(0)
            return buffer, "reporte_matriculas.xlsx", None

        import csv

        buffer_texto = io.StringIO()
        escritor = csv.writer(buffer_texto)
        escritor.writerow(encabezados)
        escritor.writerows(filas)
        buffer = io.BytesIO(buffer_texto.getvalue().encode("utf-8-sig"))
        return buffer, "reporte_matriculas.csv", None