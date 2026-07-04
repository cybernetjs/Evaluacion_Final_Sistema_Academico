import io
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from app.modelos.matricula import Matricula
from app.modelos.estudiante import Estudiante


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