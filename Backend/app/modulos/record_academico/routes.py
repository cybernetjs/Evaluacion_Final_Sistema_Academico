from flask import Blueprint, jsonify
from app.modulos.record_academico import controllers
from app.utils.middlewares import rol_requerido

record_academico_bp = Blueprint('record_academico', __name__)


@record_academico_bp.route('/', methods=['GET'])
def index_record_academico():
    return jsonify({
        "endpoints": [
            "/<estudiante_id>",
            "/historial-completo",
            "/progreso/<estudiante_id>",
            "/tipos-clasificacion",
            "/estados-permanencia",
        ]
    })


@record_academico_bp.route('/<int:estudiante_id>', methods=['GET'])
@rol_requerido("administrador", "direccion")
def obtener_record(estudiante_id):
    return controllers.obtener_record(estudiante_id)


@record_academico_bp.route('/historial-completo', methods=['GET'])
@rol_requerido("estudiante")
def historial_completo():
    return controllers.historial_completo()


@record_academico_bp.route('/progreso/<int:estudiante_id>', methods=['GET'])
@rol_requerido("administrador", "direccion")
def obtener_progreso(estudiante_id):
    return controllers.obtener_progreso(estudiante_id)


@record_academico_bp.route('/tipos-clasificacion', methods=['GET'])
def listar_tipos_clasificacion():
    return controllers.listar_tipos_clasificacion()


@record_academico_bp.route('/estados-permanencia', methods=['GET'])
def listar_estados_permanencia():
    return controllers.listar_estados_permanencia()
