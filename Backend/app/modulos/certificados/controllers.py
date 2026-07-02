from flask import jsonify
from app.modelos.estudiante import Estudiante
from app.modelos.especialidad import Especialidad
from app.modelos.facultad import Facultad


def generar_certificado(estudiante_id):
    estudiante = Estudiante.query.get(estudiante_id)
    if not estudiante:
        return jsonify({"mensaje": "Estudiante no encontrado"}), 404

    especialidad = Especialidad.query.get(estudiante.especialidad_id)
    facultad = Facultad.query.get(especialidad.facultad_id) if especialidad else None

    return jsonify({
        "estudiante": {
            "id": estudiante.id,
            "nombres": estudiante.nombres,
            "apellido_paterno": estudiante.apellido_paterno,
            "apellido_materno": estudiante.apellido_materno,
            "correo_institucional": estudiante.correo_institucional
        },
        "especialidad": especialidad.nombre if especialidad else None,
        "facultad": facultad.nombre if facultad else None
    })