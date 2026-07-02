from flask import Blueprint
from app.modulos.matricula import controllers

matricula_bp = Blueprint('matricula', __name__)

@matricula_bp.route('/', methods=['GET'])
def listar_matriculas():
    return controllers.listar_matriculas()

@matricula_bp.route('/', methods=['POST'])
def crear_matricula():
    return controllers.crear_matricula()