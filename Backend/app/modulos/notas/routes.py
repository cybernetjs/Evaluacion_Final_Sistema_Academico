from flask import Blueprint
from app.modulos.notas import controllers

notas_bp = Blueprint('notas', __name__)

@notas_bp.route('/', methods=['GET'])
def listar_notas():
    return controllers.listar_notas()

@notas_bp.route('/<int:id>', methods=['GET'])
def obtener_nota(id):
    return controllers.obtener_nota(id)

@notas_bp.route('/', methods=['POST'])
def crear_nota():
    return controllers.crear_nota()

@notas_bp.route('/<int:id>', methods=['PUT'])
def actualizar_nota(id):
    return controllers.actualizar_nota(id)

@notas_bp.route('/<int:id>', methods=['DELETE'])
def eliminar_nota(id):
    return controllers.eliminar_nota(id)