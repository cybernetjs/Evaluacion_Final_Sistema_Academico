from flask import Blueprint
from app.modulos.certificados.presentacion import controladores
from app.compartido.middlewares.autorizacion import rol_requerido

certificados_bp = Blueprint('certificados', __name__)


@certificados_bp.route('/solicitar', methods=['POST'])
@rol_requerido("estudiante")
def solicitar_certificado():
    return controladores.solicitar_certificado()


@certificados_bp.route('/mis-solicitudes', methods=['GET'])
@rol_requerido("estudiante")
def mis_solicitudes():
    return controladores.mis_solicitudes()


@certificados_bp.route('/bandeja', methods=['GET'])
@rol_requerido("administrador", "direccion")
def bandeja_solicitudes():
    return controladores.bandeja_solicitudes()


@certificados_bp.route('/<int:certificado_id>/expediente', methods=['GET'])
@rol_requerido("administrador", "direccion")
def detalle_expediente(certificado_id):
    return controladores.detalle_expediente(certificado_id)


@certificados_bp.route('/<int:certificado_id>/comprobante', methods=['GET'])
@rol_requerido("administrador", "direccion")
def descargar_comprobante(certificado_id):
    return controladores.descargar_comprobante(certificado_id)


@certificados_bp.route('/<int:certificado_id>/notificar', methods=['POST'])
@rol_requerido("administrador", "direccion")
def notificar_solicitud(certificado_id):
    return controladores.notificar_solicitud(certificado_id)


@certificados_bp.route('/tramite/aprobar', methods=['PUT'])
@rol_requerido("administrador")
def aprobar_tramite():
    return controladores.aprobar_tramite()


@certificados_bp.route('/tramite/rechazar', methods=['PUT'])
@rol_requerido("administrador")
def rechazar_tramite():
    return controladores.rechazar_tramite()


@certificados_bp.route('/firmar', methods=['POST'])
@rol_requerido(recurso="certificados", accion="ejecutar_batch")
def firmar_certificados():
    return controladores.firmar_certificados()


@certificados_bp.route('/<int:certificado_id>/descargar', methods=['GET'])
def descargar_certificado_emitido(certificado_id):
    return controladores.descargar_certificado_emitido(certificado_id)


@certificados_bp.route('/verificar/<string:codigo>', methods=['GET'])
def verificar_certificado(codigo):
    return controladores.verificar_certificado(codigo)