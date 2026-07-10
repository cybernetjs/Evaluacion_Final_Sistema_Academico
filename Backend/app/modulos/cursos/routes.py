from flask import Blueprint
from app.modulos.cursos import controllers
from app.utils.middlewares import rol_requerido

cursos_bp = Blueprint('cursos', __name__)

# --- CRUD ---
@cursos_bp.route('/', methods=['GET'])
def listar_cursos():
    return controllers.listar_cursos()

@cursos_bp.route('/<int:id>', methods=['GET'])
def obtener_curso(id):
    return controllers.obtener_curso(id)

@cursos_bp.route('/', methods=['POST'])
@rol_requerido("administrador")
def registrar_curso():
    return controllers.registrar_curso()

@cursos_bp.route('/<int:id>', methods=['PUT'])
@rol_requerido("administrador", "direccion")
def actualizar_curso(id):
    return controllers.actualizar_curso(id)

@cursos_bp.route('/<int:id>', methods=['DELETE'])
@rol_requerido("administrador", "direccion")
def eliminar_curso(id):
    return controllers.eliminar_curso(id)

# -- PRECURSOS --
@cursos_bp.route('/<int:curso_id>/prerequisitos', methods=['GET'])
def listar_prerequisitos(curso_id):
    return controllers.listar_prerequisitos(curso_id)
