from flask import Blueprint
from app.modulos.cursos_docentes import controllers

cursos_docentes_bp = Blueprint('cursos_docentes', __name__)

@cursos_docentes_bp.route('/', methods=['GET'])
def listar_cursos():
    return controllers.listar_cursos()

@cursos_docentes_bp.route('/<int:id>', methods=['GET'])
def obtener_curso(id):
    return controllers.obtener_curso(id)

@cursos_docentes_bp.route('/prerequisitos', methods=['GET'])
def listar_prerequisitos():
    return controllers.listar_prerequisitos()

@cursos_docentes_bp.route('/docentes', methods=['GET'])
def listar_docentes():
    return controllers.listar_docentes()

@cursos_docentes_bp.route('/tipos-docentes', methods=['GET'])
def listar_tipos_docentes():
    return controllers.listar_tipos_docentes()