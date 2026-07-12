from flask import jsonify, request, send_file
from flask_jwt_extended import get_jwt_identity
from app.dominio.modelos.estudiantes.historial_merito import HistorialMerito
from app.dominio.modelos.estudiantes.progreso_estudiante import ProgresoEstudiante
from app.dominio.modelos.estudiantes.tipo_clasificacion_merito import TipoClasificacionMerito
from app.dominio.modelos.estudiantes.estado_permanencia_estudiante import EstadoPermanenciaEstudiante
from app.dominio.modelos.estudiantes.estudiante import Estudiante
from app.modulos.record_academico.aplicacion.servicios import RecordAcademicoService


def obtener_record(estudiante_id):
    historial = HistorialMerito.query.filter_by(estudiante_id=estudiante_id).all()
    return jsonify([
        {
            "periodo_academico_id": h.periodo_academico_id,
            "semestre_id": h.semestre_id,
            "promedio_ponderado_periodo": float(h.promedio_ponderado_periodo),
            "creditos_aprobados_periodo": h.creditos_aprobados_periodo,
            "orden_merito": h.orden_merito,
            "tipo_clasificacion_id": h.tipo_clasificacion_id
        }
        for h in historial
    ])


def historial_completo():
    usuario_id = int(get_jwt_identity())
    resultado, error = RecordAcademicoService.historial_completo(usuario_id)

    if error:
        return jsonify({"error": error}), 404

    return jsonify(resultado)


def historial_completo_pdf():
    usuario_id = int(get_jwt_identity())
    buffer, error = RecordAcademicoService.generar_pdf_historial(usuario_id)

    if error:
        return jsonify({"error": error}), 404

    return send_file(
        buffer,
        as_attachment=True,
        download_name="reporte_informativo_historial.pdf",
        mimetype="application/pdf",
    )


def obtener_progreso(estudiante_id):
    progreso = ProgresoEstudiante.query.get(estudiante_id)
    if not progreso:
        return jsonify({"mensaje": "Progreso de estudiante no encontrado"}), 404
    return jsonify({
        "estudiante_id": progreso.estudiante_id,
        "estado_permanencia_id": progreso.estado_permanencia_id,
        "creditos_aprobados_acumulados": progreso.creditos_aprobados_acumulados,
        "promedio_ponderado_acumulado": float(progreso.promedio_ponderado_acumulado)
    })


def listar_tipos_clasificacion():
    tipos = TipoClasificacionMerito.query.all()
    return jsonify([
        {"id": t.id, "nombre": t.nombre, "porcentaje_limite": float(t.porcentaje_limite)}
        for t in tipos
    ])


def listar_estados_permanencia():
    estados = EstadoPermanenciaEstudiante.query.all()
    return jsonify([
        {"id": e.id, "nombre": e.nombre, "descripcion": e.descripcion}
        for e in estados
    ])


def anios_ingreso():
    anios = RecordAcademicoService.anios_ingreso_disponibles()
    return jsonify(anios)


def reportes_consolidados():
    anio_ingreso = request.args.get("anio_ingreso", type=int)
    especialidad_id = request.args.get("especialidad_id", type=int)
    estado = request.args.get("estado")

    filas, error = RecordAcademicoService.reportes_consolidados(anio_ingreso, especialidad_id, estado)

    if error:
        return jsonify({"error": error}), 400

    return jsonify(filas)


def exportar_reportes():
    anio_ingreso = request.args.get("anio_ingreso", type=int)
    especialidad_id = request.args.get("especialidad_id", type=int)
    estado = request.args.get("estado")

    buffer, error = RecordAcademicoService.exportar_reportes_xlsx(anio_ingreso, especialidad_id, estado)

    if error:
        return jsonify({"error": error}), 400

    return send_file(
        buffer,
        as_attachment=True,
        download_name="sabana_de_notas.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


def analisis_cohorte():
    especialidad_id = request.args.get("especialidad_id", type=int)
    anios_texto = request.args.get("anios", "")
    anios = [a for a in anios_texto.split(",") if a.strip()]

    resultado, error = RecordAcademicoService.analisis_cohorte(especialidad_id, anios)

    if error:
        return jsonify({"error": error}), 400

    return jsonify(resultado)