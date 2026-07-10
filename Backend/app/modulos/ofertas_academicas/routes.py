# pyrefly: ignore [missing-import]
from flask import Blueprint
from app.modulos.ofertas_academicas import controllers
from app.utils.middlewares import rol_requerido

ofertas_academicas_bp = Blueprint('ofertas_academicas', __name__)

@ofertas_academicas_bp.route('/', methods=['GET'])
def listar_ofertas():
    return controllers.listar_ofertas()

@ofertas_academicas_bp.route('/<int:id>', methods=['GET'])
def obtener_oferta(id:int):
    return controllers.obtener_oferta(id)

@ofertas_academicas_bp.route('/', methods=['POST'])
def crear_oferta():
    return controllers.crear_oferta()

@ofertas_academicas_bp.route('/<int:id>', methods=['PUT'])
def actualizar_oferta(id: int):
    return controllers.actualizar_oferta(id)

@ofertas_academicas_bp.route('/<int:id>', methods=['DELETE'])
def eliminar_oferta(id: int):
    return controllers.eliminar_oferta(id)

