import io
import os
import uuid
import hashlib
from datetime import datetime

import qrcode
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from app import db
from app.modelos.certificado import Certificado
from app.modelos.estudiante import Estudiante
from app.modelos.especialidad import Especialidad
from app.modelos.facultad import Facultad
from app.modulos.record_academico.services import RecordAcademicoService

CARPETA_COMPROBANTES = os.path.join(os.getcwd(), "uploads", "comprobantes_documentos")
CARPETA_CERTIFICADOS = os.path.join(os.getcwd(), "uploads", "certificados_emitidos")
EXTENSIONES_PERMITIDAS = {".pdf", ".jpg", ".jpeg", ".png"}
TAMANO_MAXIMO_BYTES = 5 * 1024 * 1024

TIPOS_DOCUMENTO_VALIDOS = {
    "Constancia de Estudios",
    "Certificado de Estudios",
    "Constancia de Tercio Superior",
}


class CertificadoService:

    @staticmethod
    def _generar_ticket_codigo():
        anio_actual = datetime.now().year
        prefijo = f"REQ-{anio_actual}-"
        total_del_anio = Certificado.query.filter(
            Certificado.ticket_codigo.like(f"{prefijo}%")
        ).count()
        correlativo = str(total_del_anio + 1).zfill(4)
        return f"{prefijo}{correlativo}"

    @staticmethod
    def solicitar_documento(usuario_id, tipo, archivo):
        estudiante = Estudiante.query.filter_by(usuario_id=usuario_id).first()
        if not estudiante:
            return None, "No se encontró un estudiante asociado a este usuario", 404

        if not tipo or tipo not in TIPOS_DOCUMENTO_VALIDOS:
            return None, "Debes seleccionar un tipo de documento válido", 400

        if not archivo or not archivo.filename:
            return None, "Debes adjuntar el sustento de pago", 400

        extension = os.path.splitext(archivo.filename)[1].lower()
        if extension not in EXTENSIONES_PERMITIDAS:
            return None, "El sustento de pago debe ser un archivo PDF, JPEG o PNG", 400

        archivo.stream.seek(0, os.SEEK_END)
        tamano = archivo.stream.tell()
        archivo.stream.seek(0)
        if tamano == 0:
            return None, "El archivo de sustento está vacío", 400
        if tamano > TAMANO_MAXIMO_BYTES:
            return None, "El sustento de pago no puede superar los 5 MB", 400

        if estudiante.tiene_deuda_activa:
            return None, "No es posible procesar la solicitud: el estudiante registra deudas financieras activas con la facultad", 422
        if estudiante.tiene_sancion_activa:
            return None, "No es posible procesar la solicitud: el estudiante registra sanciones disciplinarias vigentes", 422

        os.makedirs(CARPETA_COMPROBANTES, exist_ok=True)
        nombre_unico = f"{uuid.uuid4()}{extension}"
        ruta_completa = os.path.join(CARPETA_COMPROBANTES, nombre_unico)
        archivo.save(ruta_completa)

        certificado = Certificado(
            estudiante_id=estudiante.id,
            tipo=tipo,
            ticket_codigo=CertificadoService._generar_ticket_codigo(),
            estado="Pendiente de Validación",
            comprobante_pago_ruta=ruta_completa,
        )
        db.session.add(certificado)
        db.session.commit()

        return {
            "mensaje": "Solicitud registrada correctamente",
            "id": certificado.id,
            "ticket_codigo": certificado.ticket_codigo,
            "estado": certificado.estado,
        }, None, 201

    @staticmethod
    def mis_solicitudes(usuario_id):
        estudiante = Estudiante.query.filter_by(usuario_id=usuario_id).first()
        if not estudiante:
            return None, "No se encontró un estudiante asociado a este usuario"

        certificados = (
            Certificado.query.filter_by(estudiante_id=estudiante.id)
            .order_by(Certificado.id.desc())
            .all()
        )

        return [
            {
                "id": c.id,
                "ticket_codigo": c.ticket_codigo,
                "tipo": c.tipo,
                "estado": c.estado,
                "motivo_rechazo": c.motivo_rechazo,
                "fecha_creacion": c.created_at.isoformat() if c.created_at else None,
                "codigo_verificacion": c.codigo_verificacion if c.estado == "Emitido" else None,
            }
            for c in certificados
        ], None

    @staticmethod
    def bandeja_solicitudes(estado=None, pagina=1, por_pagina=10):
        consulta = Certificado.query
        if estado:
            consulta = consulta.filter(Certificado.estado == estado)

        consulta = consulta.order_by(Certificado.id.desc())
        total = consulta.count()
        certificados = consulta.offset((pagina - 1) * por_pagina).limit(por_pagina).all()

        return {
            "total": total,
            "pagina": pagina,
            "por_pagina": por_pagina,
            "solicitudes": [
                {
                    "id": c.id,
                    "ticket_codigo": c.ticket_codigo,
                    "estudiante_id": c.estudiante_id,
                    "estudiante_nombre": (
                        f"{c.estudiante.nombres} {c.estudiante.apellido_paterno} {c.estudiante.apellido_materno}"
                        if c.estudiante else None
                    ),
                    "tipo": c.tipo,
                    "estado": c.estado,
                    "fecha_creacion": c.created_at.isoformat() if c.created_at else None,
                }
                for c in certificados
            ],
        }, None

    @staticmethod
    def detalle_expediente(certificado_id):
        certificado = Certificado.query.get(certificado_id)
        if not certificado:
            return None, "Solicitud no encontrada"

        estudiante = certificado.estudiante
        if estudiante:
            filas_historial = RecordAcademicoService._filas_historial(estudiante.id)
            cabecera = RecordAcademicoService._cabecera_metricas(estudiante.id, filas_historial)
        else:
            cabecera = {"total_creditos_aprobados": 0, "promedio_ponderado_acumulado": None}

        return {
            "id": certificado.id,
            "ticket_codigo": certificado.ticket_codigo,
            "tipo": certificado.tipo,
            "estado": certificado.estado,
            "motivo_rechazo": certificado.motivo_rechazo,
            "comprobante_disponible": bool(certificado.comprobante_pago_ruta),
            "estudiante": {
                "nombres": estudiante.nombres,
                "apellido_paterno": estudiante.apellido_paterno,
                "apellido_materno": estudiante.apellido_materno,
                "especialidad": estudiante.especialidad.nombre if estudiante.especialidad else None,
                "tiene_deuda_activa": estudiante.tiene_deuda_activa,
                "tiene_sancion_activa": estudiante.tiene_sancion_activa,
            },
            "expediente_academico": {
                "creditos_aprobados_acumulados": cabecera["total_creditos_aprobados"],
                "promedio_ponderado_acumulado": cabecera["promedio_ponderado_acumulado"],
            },
        }, None

    @staticmethod
    def obtener_comprobante(certificado_id):
        certificado = Certificado.query.get(certificado_id)
        if not certificado or not certificado.comprobante_pago_ruta:
            return None, "No hay comprobante disponible para esta solicitud"
        return certificado.comprobante_pago_ruta, None

    @staticmethod
    def aprobar_tramite(certificado_id):
        certificado = Certificado.query.get(certificado_id)
        if not certificado:
            return None, "Solicitud no encontrada", 404

        if certificado.estado != "Pendiente de Validación":
            return None, "Solo se pueden aprobar solicitudes en estado Pendiente de Validación", 400

        certificado.estado = "Apto para Firma"
        db.session.commit()

        return {"mensaje": "Trámite aprobado y derivado a Dirección para firma", "id": certificado.id}, None, 200

    @staticmethod
    def rechazar_tramite(certificado_id, motivo):
        certificado = Certificado.query.get(certificado_id)
        if not certificado:
            return None, "Solicitud no encontrada", 404

        if certificado.estado != "Pendiente de Validación":
            return None, "Solo se pueden rechazar solicitudes en estado Pendiente de Validación", 400

        if not motivo or not motivo.strip():
            return None, "Debes indicar el motivo del rechazo", 400

        certificado.estado = "Rechazado"
        certificado.motivo_rechazo = motivo.strip()
        db.session.commit()

        return {"mensaje": "Trámite rechazado", "id": certificado.id}, None, 200

    @staticmethod
    def _dibujar_marca_de_agua(pdf, texto, ancho, alto):
        pdf.saveState()
        pdf.setFont("Helvetica-Bold", 36)
        pdf.setFillColorRGB(0.15, 0.15, 0.6, alpha=0.12)
        pdf.translate(ancho / 2, alto / 2)
        pdf.rotate(45)
        pdf.drawCentredString(0, 0, texto)
        pdf.restoreState()

    @staticmethod
    def _generar_pdf_certificado(certificado, hash_documento):
        estudiante = certificado.estudiante
        especialidad = estudiante.especialidad if estudiante else None
        facultad = especialidad.facultad if especialidad else None

        url_verificacion = f"http://localhost:5000/api/documentos/verificar/{certificado.codigo_verificacion}"

        qr = qrcode.QRCode(version=1, box_size=6, border=2)
        qr.add_data(url_verificacion)
        qr.make(fit=True)
        imagen_qr = qr.make_image(fill_color="black", back_color="white")
        buffer_qr = io.BytesIO()
        imagen_qr.save(buffer_qr, format="PNG")
        buffer_qr.seek(0)

        ancho, alto = letter
        buffer = io.BytesIO()
        pdf = canvas.Canvas(buffer, pagesize=letter)

        CertificadoService._dibujar_marca_de_agua(pdf, facultad.nombre if facultad else "FACULTAD", ancho, alto)

        pdf.setFont("Helvetica-Bold", 18)
        pdf.drawCentredString(ancho / 2, alto - 90, certificado.tipo.upper())

        pdf.setFont("Helvetica", 11)
        texto = (
            f"La {facultad.nombre if facultad else 'facultad'} deja constancia que "
            f"{estudiante.nombres} {estudiante.apellido_paterno} {estudiante.apellido_materno}, "
            f"identificado con código {estudiante.id}, se encuentra registrado en el programa de "
            f"{especialidad.nombre if especialidad else '-'}."
        )

        from reportlab.lib.utils import simpleSplit
        lineas = simpleSplit(texto, "Helvetica", 11, ancho - 160)
        y = alto - 160
        for linea in lineas:
            pdf.drawString(80, y, linea)
            y -= 16

        from reportlab.lib.utils import ImageReader
        pdf.drawImage(
            ImageReader(io.BytesIO(buffer_qr.getvalue())), 80, 80, width=90, height=90, mask="auto"
        )
        pdf.setFont("Helvetica", 8)
        pdf.drawString(180, 140, f"Código de verificación: {certificado.codigo_verificacion}")
        pdf.drawString(180, 128, f"Hash SHA-256: {hash_documento}")
        pdf.drawString(180, 116, "Verifique este documento escaneando el código QR o visitando el portal público de la facultad.")

        pdf.showPage()
        pdf.save()
        buffer.seek(0)
        return buffer

    @staticmethod
    def firmar_certificados(certificado_ids):
        if not certificado_ids:
            return None, "Debes seleccionar al menos un certificado para firmar", 400

        resultados = []
        for certificado_id in certificado_ids:
            certificado = Certificado.query.get(certificado_id)
            if not certificado:
                resultados.append({"id": certificado_id, "estado": "error", "detalle": "No encontrado"})
                continue

            if certificado.estado != "Apto para Firma":
                resultados.append({
                    "id": certificado_id, "estado": "error",
                    "detalle": "Solo se pueden firmar certificados en estado Apto para Firma"
                })
                continue

            base_hash = (
                f"{certificado.id}-{certificado.estudiante_id}-{certificado.tipo}-"
                f"{certificado.codigo_verificacion}-{datetime.utcnow().isoformat()}"
            )
            hash_documento = hashlib.sha256(base_hash.encode("utf-8")).hexdigest()

            buffer_pdf = CertificadoService._generar_pdf_certificado(certificado, hash_documento)

            os.makedirs(CARPETA_CERTIFICADOS, exist_ok=True)
            nombre_archivo = f"certificado_{certificado.id}_{certificado.codigo_verificacion}.pdf"
            ruta_completa = os.path.join(CARPETA_CERTIFICADOS, nombre_archivo)
            with open(ruta_completa, "wb") as archivo_salida:
                archivo_salida.write(buffer_pdf.getvalue())

            certificado.estado = "Emitido"
            certificado.hash_documento = hash_documento
            certificado.fecha_firma = datetime.utcnow()
            db.session.commit()

            resultados.append({"id": certificado.id, "estado": "firmado", "codigo_verificacion": certificado.codigo_verificacion})

        return {"resultados": resultados}, None

    @staticmethod
    def obtener_ruta_certificado_emitido(certificado_id):
        certificado = Certificado.query.get(certificado_id)
        if not certificado or certificado.estado != "Emitido":
            return None, "El certificado no ha sido emitido"

        nombre_archivo = f"certificado_{certificado.id}_{certificado.codigo_verificacion}.pdf"
        ruta_completa = os.path.join(CARPETA_CERTIFICADOS, nombre_archivo)

        if not os.path.exists(ruta_completa):
            return None, "El documento emitido no se encuentra disponible en el servidor"

        return ruta_completa, None

    @staticmethod
    def verificar_publico(codigo_verificacion):
        certificado = Certificado.query.filter_by(codigo_verificacion=codigo_verificacion).first()

        if not certificado or certificado.estado != "Emitido":
            return {
                "valido": False,
                "mensaje": "Código de Verificación Inválido. El documento no pertenece a los registros oficiales de la facultad",
            }, None

        estudiante = certificado.estudiante
        nombre_completo = None
        if estudiante:
            nombre_completo = (
                f"{estudiante.nombres} {estudiante.apellido_paterno} {estudiante.apellido_materno}"
            )

        return {
            "valido": True,
            "certificado_id": certificado.id,
            "tipo": certificado.tipo,
            "estado": certificado.estado,
            "fecha_emision": certificado.fecha_firma.isoformat() if certificado.fecha_firma else None,
            "estudiante_nombre": nombre_completo,
            "hash_documento": certificado.hash_documento,
        }, None