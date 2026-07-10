from flask import Blueprint
from app.modulos.cursos_docentes import controllers
from app.utils.middlewares import rol_requerido

cursos_docentes_bp = Blueprint('cursos_docentes', __name__)

# --- CRUD ---
@cursos_docentes_bp.route('/', methods=['GET'])
def listar_cursos():
    return controllers.listar_cursos()

@cursos_docentes_bp.route('/<int:id>', methods=['GET'])
def obtener_curso(id):
    return controllers.obtener_curso(id)

@cursos_docentes_bp.route('/', methods=['POST'])
def registrar_curso():
    return controllers.registrar_curso()

@cursos_docentes_bp.route('/<int:id>', methods=['PUT'])
@rol_requerido("administrador", "direccion")
def actualizar_curso(id):
    return controllers.actualizar_curso(id)

@cursos_docentes_bp.route('/<int:id>', methods=['DELETE'])
@rol_requerido("administrador", "direccion")
def eliminar_curso(id):
    return controllers.eliminar_curso(id)

# -- PRECURSOS --
@cursos_docentes_bp.route('/<curso_id:int>/prerequisitos', methods=['GET'])
def listar_prerequisitos(curso_id):
    return controllers.listar_prerequisitos(curso_id)

