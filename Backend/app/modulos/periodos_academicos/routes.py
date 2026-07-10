from flask import Blueprint
from app.modulos.periodos_academicos import controllers
from app.utils.middlewares import rol_requerido

periodos_academicos_bp = Blueprint('periodos_academicos', __name__)

@periodos_academicos_bp.route('/', methods=['GET'])
@rol_requerido("administrador", "direccion")
def listar_periodos():
    return controllers.listar_periodos()

@periodos_academicos_bp.route('/<int:id>', methods=['GET'])
def obtener_periodo(id: int):
    return controllers.obtener_periodo(id)

@periodos_academicos_bp.route('/actual', methods=['GET'])
def periodo_actual():
    return controllers.periodo_actual()

@periodos_academicos_bp.route('/', methods=['POST'])
@rol_requerido("administrador", "direccion")
def crear_periodo():
    return controllers.crear_periodo()

@periodos_academicos_bp.route('/<int:id>', methods=['PUT'])
@rol_requerido("administrador", "direccion")
def actualizar_periodo(id: int):
    return controllers.actualizar_periodo(id)

@periodos_academicos_bp.route('/<int:id>', methods=['DELETE'])
@rol_requerido("administrador", "direccion")
def eliminar_periodo(id: int):
    return controllers.eliminar_periodo(id)