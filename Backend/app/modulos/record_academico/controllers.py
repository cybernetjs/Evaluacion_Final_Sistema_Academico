from flask import jsonify
from flask_jwt_extended import get_jwt_identity
from app.modelos.historial_merito import HistorialMerito
from app.modelos.progreso_estudiante import ProgresoEstudiante
from app.modelos.tipo_clasificacion_merito import TipoClasificacionMerito
from app.modelos.estado_permanencia_estudiante import EstadoPermanenciaEstudiante
from app.modelos.estudiante import Estudiante


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


def mi_historial():
    usuario_id = int(get_jwt_identity())
    estudiante = Estudiante.query.filter_by(usuario_id=usuario_id).first()

    if not estudiante:
        return jsonify({"error": "No se encontró un estudiante asociado a este usuario"}), 404

    historial = HistorialMerito.query.filter_by(estudiante_id=estudiante.id).all()
    progreso = ProgresoEstudiante.query.get(estudiante.id)

    return jsonify({
        "historial": [
            {
                "periodo_academico_id": h.periodo_academico_id,
                "semestre_id": h.semestre_id,
                "promedio_ponderado_periodo": float(h.promedio_ponderado_periodo),
                "creditos_aprobados_periodo": h.creditos_aprobados_periodo,
                "orden_merito": h.orden_merito,
                "tipo_clasificacion_id": h.tipo_clasificacion_id
            }
            for h in historial
        ],
        "progreso_actual": {
            "creditos_aprobados_acumulados": progreso.creditos_aprobados_acumulados,
            "promedio_ponderado_acumulado": float(progreso.promedio_ponderado_acumulado),
            "estado_permanencia_id": progreso.estado_permanencia_id
        } if progreso else None
    })


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


def reportes_consolidados():
    total_estudiantes = Estudiante.query.count()
    total_con_progreso = ProgresoEstudiante.query.count()

    progresos = ProgresoEstudiante.query.all()
    promedio_general = None
    if progresos:
        suma = sum(float(p.promedio_ponderado_acumulado) for p in progresos)
        promedio_general = round(suma / len(progresos), 2)

    return jsonify({
        "total_estudiantes": total_estudiantes,
        "estudiantes_con_registro_de_progreso": total_con_progreso,
        "promedio_general_institucional": promedio_general
    })


def desempeno_por_cohorte():
    historiales = HistorialMerito.query.all()
    agrupado = {}

    for h in historiales:
        clave = h.especialidad_id
        if clave not in agrupado:
            agrupado[clave] = {"especialidad_id": clave, "promedios": [], "total_estudiantes": 0}
        agrupado[clave]["promedios"].append(float(h.promedio_ponderado_periodo))
        agrupado[clave]["total_estudiantes"] += 1

    resultado = []
    for clave, datos in agrupado.items():
        promedio = round(sum(datos["promedios"]) / len(datos["promedios"]), 2)
        resultado.append({
            "especialidad_id": datos["especialidad_id"],
            "total_estudiantes": datos["total_estudiantes"],
            "promedio_ponderado": promedio
        })

    return jsonify(resultado)