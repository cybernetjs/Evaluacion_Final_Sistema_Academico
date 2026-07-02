from flask import jsonify, request

def listar_matriculas():
    return jsonify({"mensaje": "lista de matrículas"})

def crear_matricula():
    data = request.get_json()
    return jsonify({"mensaje": "matrícula creada", "data": data}), 201