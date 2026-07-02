from flask import jsonify, request

def listar_cursos():
    return jsonify({"mensaje": "lista de cursos"})

def obtener_curso(id):
    return jsonify({"mensaje": f"curso {id}"})

def crear_curso():
    data = request.get_json()
    return jsonify({"mensaje": "curso creado", "data": data}), 201

def actualizar_curso(id):
    data = request.get_json()
    return jsonify({"mensaje": f"curso {id} actualizado", "data": data})

def eliminar_curso(id):
    return jsonify({"mensaje": f"curso {id} eliminado"})