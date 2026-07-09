from flask import Blueprint
from app.modulos.notas import controllers
from app.utils.middlewares import rol_requerido

notas_bp = Blueprint('notas', __name__)


@notas_bp.route('/', methods=['GET'])
@rol_requerido("administrador", "direccion")
def listar_notas():
    return controllers.listar_notas()


@notas_bp.route('/matricula/<int:matricula_id>', methods=['GET'])
@rol_requerido("administrador", "direccion")
def obtener_notas_matricula(matricula_id):
    return controllers.obtener_notas_matricula(matricula_id)


@notas_bp.route('/mi-hoja', methods=['GET'])
@rol_requerido("estudiante")
def mi_hoja_de_notas():
    return controllers.mi_hoja_de_notas()


@notas_bp.route('/hoja-ciclo', methods=['GET'])
@rol_requerido("estudiante")
def hoja_ciclo():
    return controllers.mi_hoja_de_notas()


@notas_bp.route('/ciclos-cursados', methods=['GET'])
@rol_requerido("estudiante")
def ciclos_cursados():
    return controllers.ciclos_cursados()


@notas_bp.route('/publicar', methods=['POST'])
@rol_requerido("docente")
def publicar_notas():
    return controllers.publicar_notas()


@notas_bp.route('/actas', methods=['GET'])
@rol_requerido("administrador")
def panel_actas():
    return controllers.panel_actas()


@notas_bp.route('/actas/<int:oferta_academica_id>/omisos', methods=['GET'])
@rol_requerido("administrador")
def alumnos_omisos(oferta_academica_id):
    return controllers.alumnos_omisos(oferta_academica_id)


@notas_bp.route('/actas/cerrar', methods=['POST'])
@rol_requerido("administrador")
def cerrar_acta():
    return controllers.cerrar_acta()


@notas_bp.route('/periodo/<int:periodo_academico_id>/estado-consolidacion', methods=['GET'])
@rol_requerido("administrador")
def estado_periodo_para_consolidar(periodo_academico_id):
    return controllers.estado_periodo_para_consolidar(periodo_academico_id)


@notas_bp.route('/consolidar-semestre', methods=['POST'])
@rol_requerido("administrador")
def consolidar_semestre():
    return controllers.consolidar_semestre()


@notas_bp.route('/dashboard/indicadores', methods=['GET'])
@rol_requerido("direccion")
def indicadores_direccion():
    return controllers.indicadores_direccion()


@notas_bp.route('/', methods=['PUT'])
@rol_requerido("docente")
def registrar_nota():
    return controllers.registrar_nota()


@notas_bp.route('/planilla/<int:oferta_academica_id>', methods=['GET'])
@rol_requerido("docente")
def obtener_planilla(oferta_academica_id):
    return controllers.obtener_planilla(oferta_academica_id)


@notas_bp.route('/cronograma/<int:oferta_academica_id>', methods=['GET'])
@rol_requerido("docente")
def estado_cronograma(oferta_academica_id):
    return controllers.estado_cronograma(oferta_academica_id)


@notas_bp.route('/registro', methods=['PUT'])
@rol_requerido(recurso="notas", accion="actualizar")
def registrar_notas_planilla():
    return controllers.registrar_notas_planilla()


@notas_bp.route('/estados', methods=['GET'])
def listar_estados_curso():
    return controllers.listar_estados_curso()


@notas_bp.route('/validar-actas', methods=['GET'])
@rol_requerido("administrador")
def validar_actas():
    return controllers.validar_actas()


@notas_bp.route('/indicadores', methods=['GET'])
@rol_requerido("direccion")
def indicadores_academicos():
    return controllers.indicadores_academicos()