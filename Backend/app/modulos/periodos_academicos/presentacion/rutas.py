from flask import Blueprint
from app.modulos.periodos_academicos.presentacion import controladores
from app.compartido.middlewares.autorizacion import rol_requerido

periodos_academicos_bp = Blueprint('periodos_academicos', __name__)

@periodos_academicos_bp.route('/', methods=['GET'])
@rol_requerido("administrador", "direccion")
def listar_periodos():
    return controladores.listar_periodos()

@periodos_academicos_bp.route('/<int:id>', methods=['GET'])
def obtener_periodo(id: int):
    return controladores.obtener_periodo(id)

@periodos_academicos_bp.route('/actual', methods=['GET'])
def periodo_actual():
    return controladores.periodo_actual()

@periodos_academicos_bp.route('/', methods=['POST'])
@rol_requerido("administrador", "direccion")
def crear_periodo():
    return controladores.crear_periodo()

@periodos_academicos_bp.route('/<int:id>', methods=['PUT'])
@rol_requerido("administrador", "direccion")
def actualizar_periodo(id: int):
    return controladores.actualizar_periodo(id)

@periodos_academicos_bp.route('/<int:id>', methods=['DELETE'])
@rol_requerido("administrador", "direccion")
def eliminar_periodo(id: int):
    return controladores.eliminar_periodo(id)