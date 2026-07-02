from flask import Blueprint
from app.modulos.cursos_docentes import controllers

cursos_docentes_bp = Blueprint('cursos_docentes', __name__)

@cursos_docentes_bp.route('/', methods=['GET'])
def listar_cursos():
    return controllers.listar_cursos()

@cursos_docentes_bp.route('/<int:id>', methods=['GET'])
def obtener_curso(id):
    return controllers.obtener_curso(id)

@cursos_docentes_bp.route('/', methods=['POST'])
def crear_curso():
    return controllers.crear_curso()

@cursos_docentes_bp.route('/<int:id>', methods=['PUT'])
def actualizar_curso(id):
    return controllers.actualizar_curso(id)

@cursos_docentes_bp.route('/<int:id>', methods=['DELETE'])
def eliminar_curso(id):
    return controllers.eliminar_curso(id)