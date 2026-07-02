from flask import jsonify

def listar_facultades():
    return jsonify({"mensaje": "lista de facultades"})

def listar_especialidades():
    return jsonify({"mensaje": "lista de especialidades"})

def listar_planes_estudio():
    return jsonify({"mensaje": "lista de planes de estudio"})