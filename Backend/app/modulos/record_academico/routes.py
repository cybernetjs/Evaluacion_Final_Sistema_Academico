from flask import Blueprint
from flask import jsonify
from app.modulos.record_academico import controllers

record_academico_bp = Blueprint('record_academico', __name__)

@record_academico_bp.route('/', methods=['GET'])
def index_record_academico():
    return jsonify({
        "endpoints": [
            "/<estudiante_id>",
            "/progreso/<estudiante_id>",
            "/tipos-clasificacion",
            "/estados-permanencia"
        ]
    })

@record_academico_bp.route('/<int:estudiante_id>', methods=['GET'])
def obtener_record(estudiante_id):
    return controllers.obtener_record(estudiante_id)

@record_academico_bp.route('/progreso/<int:estudiante_id>', methods=['GET'])
def obtener_progreso(estudiante_id):
    return controllers.obtener_progreso(estudiante_id)

@record_academico_bp.route('/tipos-clasificacion', methods=['GET'])
def listar_tipos_clasificacion():
    return controllers.listar_tipos_clasificacion()

@record_academico_bp.route('/estados-permanencia', methods=['GET'])
def listar_estados_permanencia():
    return controllers.listar_estados_permanencia()