import io
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from app import db
from app.modelos.estudiante import Estudiante
from app.modelos.matricula import Matricula
from app.modelos.periodo_academico import PeriodoAcademico
from app.modelos.progreso_estudiante import ProgresoEstudiante

TEXTO_MARCA_AGUA = "REPORTE INFORMATIVO - NO OFICIAL"

ROMANOS_POR_SEMESTRE = {
    "01": "I", "02": "II", "03": "III", "04": "IV", "05": "V",
    "06": "VI", "07": "VII", "08": "VIII", "09": "IX", "10": "X",
}


class RecordAcademicoService:

    @staticmethod
    def _estudiante_por_usuario(usuario_id):
        return Estudiante.query.filter_by(usuario_id=usuario_id).first()

    @staticmethod
    def _filas_historial(estudiante_id):

        matriculas = (
            Matricula.query.filter_by(estudiante_id=estudiante_id)
            .join(PeriodoAcademico, Matricula.periodo_academico_id == PeriodoAcademico.id)
            .order_by(PeriodoAcademico.fecha_inicio.desc())
            .all()
        )

        filas = []
        for m in matriculas:

            for d in m.detalle:
                curso = d.oferta_academica.curso
                filas.append({
                    "periodo_academico": m.periodo_academico.nombre,
                    "semestre": ROMANOS_POR_SEMESTRE.get(m.semestre.codigo, m.semestre.codigo),
                    "codigo_curso": curso.codigo,
                    "nombre_curso": curso.nombre,
                    "creditos": curso.creditos,
                    "nota_final": float(d.nota_final) if d.nota_final is not None else None,
                    "estado": d.estado_curso.nombre if d.estado_curso else None,
                })
        return filas

    @staticmethod
    def _cabecera_metricas(estudiante_id, filas):

        progreso = ProgresoEstudiante.query.get(estudiante_id)
        total_matriculados = sum(f["creditos"] for f in filas)

        return {
            "total_creditos_matriculados": total_matriculados,
            "total_creditos_aprobados": progreso.creditos_aprobados_acumulados if progreso else 0,
            "promedio_ponderado_acumulado": float(progreso.promedio_ponderado_acumulado) if progreso else None,
        }

    @staticmethod
    def historial_completo(usuario_id):

        estudiante = RecordAcademicoService._estudiante_por_usuario(usuario_id)
        if not estudiante:
            return None, "No se encontró un estudiante asociado a este usuario"

        filas = RecordAcademicoService._filas_historial(estudiante.id)
        cabecera = RecordAcademicoService._cabecera_metricas(estudiante.id, filas)

        return {
            "estudiante": {
                "nombres": estudiante.nombres,
                "apellido_paterno": estudiante.apellido_paterno,
                "apellido_materno": estudiante.apellido_materno,
                "especialidad": estudiante.especialidad.nombre if estudiante.especialidad else None,
            },
            "cabecera": cabecera,
            "historial": filas,
        }, None

    @staticmethod
    def _dibujar_marca_de_agua(pdf, ancho, alto):
        pdf.saveState()
        pdf.setFont("Helvetica-Bold", 40)
        pdf.setFillColorRGB(0.5, 0.5, 0.5, alpha=0.25)
        pdf.translate(ancho / 2, alto / 2)
        pdf.rotate(45)
        pdf.drawCentredString(0, 0, TEXTO_MARCA_AGUA)
        pdf.restoreState()

    @staticmethod
    def generar_pdf_historial(usuario_id):
        estudiante = RecordAcademicoService._estudiante_por_usuario(usuario_id)
        if not estudiante:
            return None, "No se encontró un estudiante asociado a este usuario"

        filas = RecordAcademicoService._filas_historial(estudiante.id)
        cabecera = RecordAcademicoService._cabecera_metricas(estudiante.id, filas)

        ancho, alto = letter
        buffer = io.BytesIO()
        pdf = canvas.Canvas(buffer, pagesize=letter)

        def encabezado_pagina():
            RecordAcademicoService._dibujar_marca_de_agua(pdf, ancho, alto)
            pdf.setFont("Helvetica-Bold", 16)
            pdf.drawString(50, alto - 50, "REPORTE INFORMATIVO DE RECORD ACADEMICO")
            pdf.setFont("Helvetica", 10)
            pdf.drawString(
                50, alto - 70,
                f"Estudiante: {estudiante.nombres} {estudiante.apellido_paterno} {estudiante.apellido_materno}"
            )
            pdf.drawString(50, alto - 85, f"Codigo: {estudiante.id}")
            pdf.drawString(
                50, alto - 100,
                f"Especialidad: {estudiante.especialidad.nombre if estudiante.especialidad else '-'}"
            )
            pdf.setFont("Helvetica-Bold", 10)
            pdf.drawString(320, alto - 70, f"Creditos aprobados: {cabecera['total_creditos_aprobados']}")
            pdf.drawString(320, alto - 85, f"PPA: {cabecera['promedio_ponderado_acumulado']}")

            y = alto - 130
            pdf.setFont("Helvetica-Bold", 8)
            columnas = [
                ("Periodo", 50), ("Sem.", 110), ("Codigo", 140), ("Curso", 190),
                ("Cred.", 400), ("Nota", 440), ("Estado", 480)
            ]
            for texto, x in columnas:
                pdf.drawString(x, y, texto)
            pdf.line(50, y - 4, 545, y - 4)
            return y - 18, columnas

        y, columnas = encabezado_pagina()
        pdf.setFont("Helvetica", 8)

        for fila in filas:
            if y < 60:
                pdf.showPage()
                y, columnas = encabezado_pagina()
                pdf.setFont("Helvetica", 8)

            if fila["estado"] and fila["estado"].lower() == "desaprobado":
                pdf.setFillColorRGB(0.7, 0, 0)
            else:
                pdf.setFillColorRGB(0, 0, 0)

            valores = [
                fila["periodo_academico"], fila["semestre"], fila["codigo_curso"],
                (fila["nombre_curso"] or "")[:28],
                str(fila["creditos"]),
                str(fila["nota_final"] if fila["nota_final"] is not None else "-"),
                fila["estado"] or "-",
            ]
            for (_, x), valor in zip(columnas, valores):
                pdf.drawString(x, y, valor)

            y -= 14

        pdf.setFillColorRGB(0, 0, 0)
        pdf.save()
        buffer.seek(0)
        return buffer, None