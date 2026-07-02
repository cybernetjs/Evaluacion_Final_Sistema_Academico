from flask import jsonify, request

def listar_notas():
    return jsonify({"mensaje": "lista de notas"})

def obtener_nota(id):
    return jsonify({"mensaje": f"nota {id}"})

def crear_nota():
    data = request.get_json()
    return jsonify({"mensaje": "nota creada", "data": data}), 201

def actualizar_nota(id):
    data = request.get_json()
    return jsonify({"mensaje": f"nota {id} actualizada", "data": data})

def eliminar_nota(id):
    return jsonify({"mensaje": f"nota {id} eliminada"})