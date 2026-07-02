from flask import Blueprint
from flask import jsonify
from app.modulos.certificados import controllers

certificados_bp = Blueprint('certificados', __name__)

@certificados_bp.route('/', methods=['GET'])
def index_certificados():
    return jsonify({
        "mensaje": "Usa /api/certificados/<estudiante_id> para generar un certificado"
    })

@certificados_bp.route('/<int:estudiante_id>', methods=['GET'])
def generar_certificado(estudiante_id):
    return controllers.generar_certificado(estudiante_id)