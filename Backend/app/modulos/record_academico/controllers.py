from flask import jsonify
from flask_jwt_extended import get_jwt_identity
from app.modelos.historial_merito import HistorialMerito
from app.modelos.progreso_estudiante import ProgresoEstudiante
from app.modelos.tipo_clasificacion_merito import TipoClasificacionMerito
from app.modelos.estado_permanencia_estudiante import EstadoPermanenciaEstudiante
from app.modelos.estudiante import Estudiante
from app.modulos.record_academico.services import RecordAcademicoService


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
