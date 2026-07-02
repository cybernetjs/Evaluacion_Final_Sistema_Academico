from flask import jsonify

def generar_certificado(estudiante_id):
    return jsonify({"mensaje": f"certificado del estudiante {estudiante_id}"})