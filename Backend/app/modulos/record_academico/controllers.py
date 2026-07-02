from flask import jsonify

def obtener_record(estudiante_id):
    return jsonify({"mensaje": f"record académico del estudiante {estudiante_id}"})