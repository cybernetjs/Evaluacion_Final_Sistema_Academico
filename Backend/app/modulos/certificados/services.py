import io
import os
import uuid
from datetime import datetime

import qrcode

from app import db
from app.modelos.certificado import Certificado
from app.modelos.estudiante import Estudiante

CARPETA_COMPROBANTES = os.path.join(os.getcwd(), "uploads", "comprobantes_documentos")
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
            }
            for c in certificados
        ], None

    @staticmethod
    def generar_qr(codigo_verificacion):
        certificado = Certificado.query.filter_by(codigo_verificacion=codigo_verificacion).first()

        if not certificado or certificado.estado != "Emitido":
            return None, "Certificado no encontrado o no emitido"

        url_verificacion = f"http://localhost:5000/api/documentos/publico/verificar/{codigo_verificacion}"

        qr = qrcode.QRCode(version=1, box_size=10, border=4)
        qr.add_data(url_verificacion)
        qr.make(fit=True)

        imagen = qr.make_image(fill_color="black", back_color="white")

        buffer = io.BytesIO()
        imagen.save(buffer, format="PNG")
        buffer.seek(0)

        return buffer, None