from flask import Blueprint
from app.modulos.matricula import controllers
from app.utils.middlewares import rol_requerido

matricula_bp = Blueprint('matricula', __name__)


@matricula_bp.route('/', methods=['GET'])
@rol_requerido("administrador", "direccion")
def listar_matriculas():
    return controllers.listar_matriculas()


@matricula_bp.route('/', methods=['POST'])
@rol_requerido("estudiante")
def crear_matricula():
    return controllers.crear_matricula()


@matricula_bp.route('/periodos', methods=['GET'])
def listar_periodos():
    return controllers.listar_periodos()


@matricula_bp.route('/ofertas', methods=['GET'])
def listar_ofertas():
    return controllers.listar_ofertas()


@matricula_bp.route('/estados', methods=['GET'])
def listar_estados_matricula():
    return controllers.listar_estados_matricula()