import io
import qrcode
from app.modelos.certificado import Certificado


class CertificadoService:

    @staticmethod
    def generar_qr(codigo_verificacion):
        certificado = Certificado.query.filter_by(codigo_verificacion=codigo_verificacion).first()

        if not certificado or not certificado.emitido:
            return None, "Certificado no encontrado o no emitido"

        url_verificacion = f"http://localhost:5000/api/certificados/verificar/{codigo_verificacion}"

        qr = qrcode.QRCode(version=1, box_size=10, border=4)
        qr.add_data(url_verificacion)
        qr.make(fit=True)

        imagen = qr.make_image(fill_color="black", back_color="white")

        buffer = io.BytesIO()
        imagen.save(buffer, format="PNG")
        buffer.seek(0)

        return buffer, None