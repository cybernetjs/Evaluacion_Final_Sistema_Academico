from flask import Blueprint
from app.modulos.certificados import controllers

certificados_bp = Blueprint('certificados', __name__)

@certificados_bp.route('/<int:estudiante_id>', methods=['GET'])
def generar_certificado(estudiante_id):
    return controllers.generar_certificado(estudiante_id)