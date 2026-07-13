from flask import Blueprint, jsonify
from app.modulos.administracion.presentacion import controladores
from app.compartido.middlewares.autorizacion import rol_requerido

administracion_bp = Blueprint('administracion', __name__)

@administracion_bp.route('/', methods=['GET'])
def index_administracion():
    return jsonify({
        "endpoints": [
            "/facultades",
            "/especialidades",
            "/planes-estudio",
            "/semestres",
            "/usuarios",
            "/usuarios/<id>/rol",
            "/auditorias"
        ]
    })


@administracion_bp.route('/facultades', methods=['GET'])
def listar_facultades():
    return controladores.listar_facultades()


@administracion_bp.route('/especialidades', methods=['GET'])
def listar_especialidades():
    return controladores.listar_especialidades()


@administracion_bp.route('/planes-estudio', methods=['GET'])
def listar_planes_estudio():
    return controladores.listar_planes_estudio()


@administracion_bp.route('/semestres', methods=['GET'])
def listar_semestres():
    return controladores.listar_semestres()


@administracion_bp.route('/periodos', methods=['GET'])
def listar_periodos():
    return controladores.listar_periodos()


@administracion_bp.route('/usuarios', methods=['GET'])
@rol_requerido("administrador")
def listar_usuarios():
    return controladores.listar_usuarios()


@administracion_bp.route('/usuarios/<int:usuario_id>/rol', methods=['PUT'])
@rol_requerido(recurso="administracion", accion="actualizar")
def cambiar_rol(usuario_id):
    return controladores.cambiar_rol(usuario_id)


@administracion_bp.route('/docentes', methods=['POST'])
@rol_requerido("administrador")
def registrar_docente():
    return controladores.registrar_docente()


@administracion_bp.route('/personal', methods=['POST'])
@rol_requerido("administrador")
def registrar_personal():
    return controladores.registrar_personal()


@administracion_bp.route('/auditorias', methods=['GET'])
@rol_requerido("direccion")
def listar_auditorias():
    return controladores.listar_auditorias()

@administracion_bp.route('/reportes-estrategicos', methods=['GET'])
@rol_requerido("direccion")
def reportes_estrategicos():
    return controladores.reportes_estrategicos()


@administracion_bp.route('/permisos', methods=['GET'])
@rol_requerido("administrador")
def matriz_permisos():
    return controladores.obtener_matriz_permisos()


@administracion_bp.route('/permisos', methods=['PUT'])
@rol_requerido("administrador")
def actualizar_matriz_permisos():
    return controladores.actualizar_matriz_permisos()


admin_bp = Blueprint('admin_ciclo_global', __name__)


@admin_bp.route('/configuracion/ciclo-global', methods=['GET'])
@rol_requerido("administrador")
def configuracion_ciclo_global():
    return controladores.obtener_configuracion_ciclo()


@admin_bp.route('/configuracion/ciclo-global', methods=['PUT'])
@rol_requerido("administrador")
def actualizar_configuracion_ciclo_global():
    return controladores.actualizar_configuracion_ciclo()