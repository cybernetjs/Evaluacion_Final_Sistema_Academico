import io
from collections import defaultdict
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from openpyxl import Workbook
from app import db
from app.dominio.modelos.estudiantes.estudiante import Estudiante
from app.dominio.modelos.matriculas.matricula import Matricula
from app.dominio.modelos.matriculas.matricula_detalle import MatriculaDetalle
from app.dominio.modelos.ofertas.oferta_academica import OfertaAcademica
from app.dominio.modelos.academico.curso import Curso
from app.dominio.modelos.ofertas.periodo_academico import PeriodoAcademico
from app.dominio.modelos.estudiantes.progreso_estudiante import ProgresoEstudiante
from app.dominio.modelos.estudiantes.historial_merito import HistorialMerito
from app.dominio.modelos.academico.especialidad import Especialidad
from app.dominio.modelos.academico.semestre import Semestre

PROMEDIO_MINIMO_APROBATORIO = 10.5
UMBRAL_ALERTA_DESERCION = 25

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
        total_matriculados = sum(f["creditos"] for f in filas)

        total_aprobados = sum(
            f["creditos"] for f in filas
            if f["estado"] and f["estado"].lower() == "aprobado"
        )

        filas_con_nota = [
            f for f in filas
            if f["nota_final"] is not None
            and f["estado"] and f["estado"].lower() in ("aprobado", "desaprobado")
        ]
        creditos_evaluados = sum(f["creditos"] for f in filas_con_nota)
        if creditos_evaluados > 0:
            suma_ponderada = sum(f["nota_final"] * f["creditos"] for f in filas_con_nota)
            promedio_ponderado = round(suma_ponderada / creditos_evaluados, 2)
        else:
            promedio_ponderado = None

        return {
            "total_creditos_matriculados": total_matriculados,
            "total_creditos_aprobados": total_aprobados,
            "promedio_ponderado_acumulado": promedio_ponderado,
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

    @staticmethod
    def _anio_ingreso_por_estudiante():
        filas = (
            db.session.query(
                Matricula.estudiante_id,
                db.func.min(PeriodoAcademico.fecha_inicio).label("primera_fecha"),
            )
            .join(PeriodoAcademico, Matricula.periodo_academico_id == PeriodoAcademico.id)
            .group_by(Matricula.estudiante_id)
            .all()
        )
        return {f.estudiante_id: f.primera_fecha.year for f in filas if f.primera_fecha}

    @staticmethod
    def anios_ingreso_disponibles():
        anios = sorted(set(RecordAcademicoService._anio_ingreso_por_estudiante().values()), reverse=True)
        return anios

    @staticmethod
    def reportes_consolidados(anio_ingreso, especialidad_id, estado_nombre=None):
        if not anio_ingreso or not especialidad_id:
            return None, "Debes indicar Año de Ingreso y Especialidad"

        anios_por_estudiante = RecordAcademicoService._anio_ingreso_por_estudiante()
        estudiantes = Estudiante.query.filter_by(especialidad_id=especialidad_id).all()

        filas = []
        for est in estudiantes:
            if anios_por_estudiante.get(est.id) != int(anio_ingreso):
                continue

            progreso = ProgresoEstudiante.query.get(est.id)
            if estado_nombre and (
                not progreso or not progreso.estado_permanencia
                or progreso.estado_permanencia.nombre.lower() != estado_nombre.lower()
            ):
                continue

            ultimo_merito = (
                HistorialMerito.query.filter_by(estudiante_id=est.id)
                .join(PeriodoAcademico, HistorialMerito.periodo_academico_id == PeriodoAcademico.id)
                .order_by(PeriodoAcademico.fecha_inicio.desc())
                .first()
            )

            creditos_matriculados = (
                db.session.query(db.func.coalesce(db.func.sum(Curso.creditos), 0))
                .select_from(MatriculaDetalle)
                .join(Matricula, MatriculaDetalle.matricula_id == Matricula.id)
                .join(OfertaAcademica, MatriculaDetalle.oferta_academica_id == OfertaAcademica.id)
                .join(Curso, OfertaAcademica.curso_id == Curso.id)
                .filter(Matricula.estudiante_id == est.id)
                .scalar()
            )

            filas.append({
                "estudiante_id": est.id,
                "codigo": est.id,
                "nombres_completos": f"{est.nombres} {est.apellido_paterno} {est.apellido_materno}",
                "creditos_matriculados": int(creditos_matriculados or 0),
                "creditos_aprobados": progreso.creditos_aprobados_acumulados if progreso else 0,
                "pps_ultimo_ciclo": float(ultimo_merito.promedio_ponderado_periodo) if ultimo_merito else None,
                "ppa": float(progreso.promedio_ponderado_acumulado) if progreso else None,
                "estado_permanencia": progreso.estado_permanencia.nombre if progreso and progreso.estado_permanencia else None,
            })

        return filas, None

    @staticmethod
    def exportar_reportes_xlsx(anio_ingreso, especialidad_id, estado_nombre=None):
        filas, error = RecordAcademicoService.reportes_consolidados(anio_ingreso, especialidad_id, estado_nombre)
        if error:
            return None, error

        libro = Workbook()
        hoja = libro.active
        hoja.title = "Sabana de notas"

        encabezados = ["Codigo", "Nombres completos", "Creditos matriculados",
                       "Creditos aprobados", "PPS ultimo ciclo", "PPA"]
        hoja.append(encabezados)

        for fila in filas:
            hoja.append([
                fila["codigo"], fila["nombres_completos"], fila["creditos_matriculados"],
                fila["creditos_aprobados"], fila["pps_ultimo_ciclo"], fila["ppa"],
            ])

        for columna in hoja.columns:
            valores = [c.value for c in columna if c.value is not None]
            longitud = max((len(str(v)) for v in valores), default=10)
            hoja.column_dimensions[columna[0].column_letter].width = max(12, longitud + 2)

        buffer = io.BytesIO()
        libro.save(buffer)
        buffer.seek(0)
        return buffer, None

    @staticmethod
    def analisis_cohorte(especialidad_id, anios_ingreso):
        if not especialidad_id or not anios_ingreso:
            return None, "Debes indicar el programa de estudios y al menos un año de ingreso"

        anios_ingreso = anios_ingreso[:3]
        anios_por_estudiante = RecordAcademicoService._anio_ingreso_por_estudiante()
        estudiantes = Estudiante.query.filter_by(especialidad_id=especialidad_id).all()

        cohortes = {}
        for anio in anios_ingreso:
            ids_estudiantes = [e.id for e in estudiantes if anios_por_estudiante.get(e.id) == int(anio)]
            cohortes[anio] = {"ids": ids_estudiantes, "total": len(ids_estudiantes)}

        curvas = defaultdict(dict)
        for anio, datos in cohortes.items():
            if not datos["ids"]:
                continue

            registros = (
                HistorialMerito.query.filter(HistorialMerito.estudiante_id.in_(datos["ids"]))
                .join(Semestre, HistorialMerito.semestre_id == Semestre.id)
                .all()
            )

            acumulado_por_semestre = defaultdict(list)
            for r in registros:
                codigo = ROMANOS_POR_SEMESTRE.get(r.semestre.codigo, r.semestre.codigo)
                acumulado_por_semestre[codigo].append(float(r.promedio_ponderado_periodo))

            for codigo, valores in acumulado_por_semestre.items():
                curvas[codigo][f"cohorte_{anio}"] = round(sum(valores) / len(valores), 2)

        orden_semestres = list(ROMANOS_POR_SEMESTRE.values())
        serie_grafico = []
        for codigo in orden_semestres:
            if codigo in curvas:
                punto = {"semestre": codigo}
                punto.update(curvas[codigo])
                serie_grafico.append(punto)

        alertas = []
        for anio, datos in cohortes.items():
            if not datos["total"]:
                continue

            progresos = ProgresoEstudiante.query.filter(ProgresoEstudiante.estudiante_id.in_(datos["ids"])).all()

            en_riesgo = sum(
                1 for p in progresos
                if p.estado_permanencia and p.estado_permanencia.nombre.lower() not in ("regular", "egresado")
            )
            sin_progreso = datos["total"] - len(progresos)
            tasa_desercion = round(((en_riesgo + sin_progreso) / datos["total"]) * 100, 1)

            promedios = [float(p.promedio_ponderado_acumulado) for p in progresos]
            promedio_cohorte = round(sum(promedios) / len(promedios), 2) if promedios else None

            alerta = tasa_desercion > UMBRAL_ALERTA_DESERCION or (
                promedio_cohorte is not None and promedio_cohorte < PROMEDIO_MINIMO_APROBATORIO
            )

            alertas.append({
                "anio_ingreso": anio,
                "total_estudiantes": datos["total"],
                "tasa_desercion_porcentaje": tasa_desercion,
                "promedio_general": promedio_cohorte,
                "en_alerta": alerta,
            })

        return {"serie_grafico": serie_grafico, "cohortes": alertas}, None