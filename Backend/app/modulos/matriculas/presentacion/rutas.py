from flask import Blueprint
from app.modulos.matriculas.presentacion import controladores
from app.compartido.middlewares.autorizacion import rol_requerido

matricula_bp = Blueprint('matricula', __name__)


@matricula_bp.route('/', methods=['GET'])
@rol_requerido("administrador", "direccion")
def listar_matriculas():
    return controladores.listar_matriculas()


@matricula_bp.route('/', methods=['POST'])
@rol_requerido("estudiante")
def crear_matricula():
    return controladores.crear_matricula()


@matricula_bp.route('/periodos', methods=['GET'])
def listar_periodos():
    return controladores.listar_periodos()


@matricula_bp.route('/periodo-actual', methods=['GET'])
def periodo_actual():
    return controladores.periodo_actual()


@matricula_bp.route('/ofertas', methods=['GET'])
def listar_ofertas():
    return controladores.listar_ofertas()


@matricula_bp.route('/estados', methods=['GET'])
def listar_estados_matricula():
    return controladores.listar_estados_matricula()


@matricula_bp.route('/<int:matricula_id>/validar', methods=['PUT'])
@rol_requerido("administrador")
def validar_requisitos(matricula_id):
    return controladores.validar_requisitos(matricula_id)


@matricula_bp.route('/<int:matricula_id>/pago', methods=['POST'])
@rol_requerido("estudiante")
def registrar_pago(matricula_id):
    return controladores.registrar_pago(matricula_id)


@matricula_bp.route('/<int:matricula_id>/verificar-pago', methods=['PUT'])
@rol_requerido("administrador")
def verificar_pago(matricula_id):
    return controladores.verificar_pago(matricula_id)


@matricula_bp.route('/<int:matricula_id>/comprobante', methods=['GET'])
@rol_requerido("administrador")
def descargar_comprobante(matricula_id):
    return controladores.descargar_comprobante(matricula_id)


@matricula_bp.route('/<int:matricula_id>/ficha-oficial', methods=['POST'])
@rol_requerido("administrador")
def generar_ficha_oficial(matricula_id):
    return controladores.generar_ficha_oficial(matricula_id)


@matricula_bp.route('/estadisticas', methods=['GET'])
@rol_requerido("direccion")
def estadisticas():
    return controladores.estadisticas()


@matricula_bp.route('/dashboard/exportar', methods=['GET'])
@rol_requerido("direccion")
def exportar_reporte():
    return controladores.exportar_reporte()


@matricula_bp.route('/<int:matricula_id>/ficha', methods=['GET'])
@rol_requerido("administrador")
def descargar_ficha(matricula_id):
    return controladores.descargar_ficha_oficial_admin(matricula_id)


@matricula_bp.route('/ficha-oficial/descargar', methods=['GET'])
@rol_requerido("estudiante")
def descargar_ficha_oficial_estudiante():
    return controladores.descargar_ficha_oficial_estudiante()


@matricula_bp.route('/cursos-disponibles', methods=['GET'])
@rol_requerido("estudiante")
def cursos_disponibles():
    return controladores.cursos_disponibles()


@matricula_bp.route('/mi-solicitud-actual', methods=['GET'])
@rol_requerido("estudiante")
def mi_solicitud_actual():
    return controladores.mi_solicitud_actual()


@matricula_bp.route('/ficha-preliminar/descargar', methods=['GET'])
@rol_requerido("estudiante")
def descargar_ficha_preliminar():
    return controladores.descargar_ficha_preliminar()


@matricula_bp.route('/validar-periodo/<int:estudiante_id>', methods=['GET'])
@rol_requerido("administrador")
def validar_periodo(estudiante_id):
    return controladores.validar_periodo(estudiante_id)


@matricula_bp.route('/cancelar', methods=['POST'])
@rol_requerido("administrador")
def cancelar_matricula():
    return controladores.cancelar_matricula()