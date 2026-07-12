from flask import Blueprint, jsonify
from app.modulos.docentes.presentacion import controladores
from app.compartido.middlewares.autorizacion import rol_requerido

docentes_bp = Blueprint('docentes', __name__)

# --- CRUD ---
@docentes_bp.route('/', methods=['GET'])
@rol_requerido("administrador", "direccion")
def listar_docentes():
    return controladores.listar_docentes()

@docentes_bp.route('/<int:id>', methods=['GET'])
@rol_requerido("administrador", "direccion", "docente")
def obtener_docente(id):
    return controladores.obtener_docente(id)

@docentes_bp.route('/', methods=['POST'])
@rol_requerido("administrador")
def registrar_docente():
    return controladores.registrar_docente()

@docentes_bp.route('/<int:id>', methods=['PUT'])
@rol_requerido("administrador", "direccion")
def actualizar_docente(id):
    return controladores.actualizar_docente(id)

@docentes_bp.route('/<int:id>', methods=['DELETE'])
@rol_requerido("administrador", "direccion")
def eliminar_docente(id):
    return controladores.eliminar_docente(id)
