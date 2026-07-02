from flask import Blueprint
from app.modulos.record_academico import controllers

record_academico_bp = Blueprint('record_academico', __name__)

@record_academico_bp.route('/<int:estudiante_id>', methods=['GET'])
def obtener_record(estudiante_id):
    return controllers.obtener_record(estudiante_id)