from flask import Blueprint
from app.modulos.cursos.presentacion import controladores
from app.compartido.middlewares.autorizacion import rol_requerido

cursos_bp = Blueprint('cursos', __name__)

# --- CRUD ---
@cursos_bp.route('/', methods=['GET'])
def listar_cursos():
    return controladores.listar_cursos()

@cursos_bp.route('/<int:id>', methods=['GET'])
def obtener_curso(id):
    return controladores.obtener_curso(id)

@cursos_bp.route('/', methods=['POST'])
@rol_requerido("administrador")
def registrar_curso():
    return controladores.registrar_curso()

@cursos_bp.route('/<int:id>', methods=['PUT'])
@rol_requerido("administrador", "direccion")
def actualizar_curso(id):
    return controladores.actualizar_curso(id)

@cursos_bp.route('/<int:id>', methods=['DELETE'])
@rol_requerido("administrador", "direccion")
def eliminar_curso(id):
    return controladores.eliminar_curso(id)

# -- PRECURSOS --
@cursos_bp.route('/<int:curso_id>/prerequisitos', methods=['GET'])
def listar_prerequisitos(curso_id):
    return controladores.listar_prerequisitos(curso_id)
