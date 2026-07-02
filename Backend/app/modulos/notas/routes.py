from flask import Blueprint
from app.modulos.notas import controllers

notas_bp = Blueprint('notas', __name__)

@notas_bp.route('/', methods=['GET'])
def listar_notas():
    return controllers.listar_notas()

@notas_bp.route('/matricula/<int:matricula_id>', methods=['GET'])
def obtener_notas_matricula(matricula_id):
    return controllers.obtener_notas_matricula(matricula_id)

@notas_bp.route('/', methods=['PUT'])
def registrar_nota():
    return controllers.registrar_nota()

@notas_bp.route('/estados', methods=['GET'])
def listar_estados_curso():
    return controllers.listar_estados_curso()