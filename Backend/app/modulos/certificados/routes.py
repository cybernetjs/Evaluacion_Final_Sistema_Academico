from flask import Blueprint, jsonify
from app.modulos.certificados import controllers
from app.utils.middlewares import rol_requerido

certificados_bp = Blueprint('certificados', __name__)


@certificados_bp.route('/', methods=['GET'])
@rol_requerido("administrador", "direccion")
def listar_solicitudes():
    return controllers.listar_solicitudes()


@certificados_bp.route('/solicitar', methods=['POST'])
@rol_requerido("estudiante")
def solicitar_certificado():
    return controllers.solicitar_certificado()


@certificados_bp.route('/<int:certificado_id>/autorizar', methods=['PUT'])
@rol_requerido("direccion")
def autorizar_certificado(certificado_id):
    return controllers.autorizar_certificado(certificado_id)


@certificados_bp.route('/<int:certificado_id>/emitir', methods=['POST'])
@rol_requerido("administrador")
def emitir_certificado(certificado_id):
    return controllers.emitir_certificado(certificado_id)


@certificados_bp.route('/verificar/<string:codigo>', methods=['GET'])
def verificar_certificado(codigo):
    return controllers.verificar_certificado(codigo)