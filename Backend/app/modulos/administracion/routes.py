from flask import Blueprint
from app.modulos.administracion import controllers

administracion_bp = Blueprint('administracion', __name__)

@administracion_bp.route('/facultades', methods=['GET'])
def listar_facultades():
    return controllers.listar_facultades()

@administracion_bp.route('/especialidades', methods=['GET'])
def listar_especialidades():
    return controllers.listar_especialidades()

@administracion_bp.route('/planes-estudio', methods=['GET'])
def listar_planes_estudio():
    return controllers.listar_planes_estudio()

@administracion_bp.route('/semestres', methods=['GET'])
def listar_semestres():
    return controllers.listar_semestres()