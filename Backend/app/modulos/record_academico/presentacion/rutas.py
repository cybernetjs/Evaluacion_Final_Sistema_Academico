from flask import Blueprint, jsonify
from app.modulos.record_academico.presentacion import controladores
from app.compartido.middlewares.autorizacion import rol_requerido

record_academico_bp = Blueprint('record_academico', __name__)


@record_academico_bp.route('/', methods=['GET'])
def index_record_academico():
    return jsonify({
        "endpoints": [
            "/<estudiante_id>",
            "/historial-completo",
            "/historial-completo/pdf",
            "/progreso/<estudiante_id>",
            "/tipos-clasificacion",
            "/estados-permanencia",
            "/anios-ingreso",
            "/reportes",
            "/reportes/exportar",
            "/analisis-cohorte",
        ]
    })


@record_academico_bp.route('/<int:estudiante_id>', methods=['GET'])
@rol_requerido("administrador", "direccion")
def obtener_record(estudiante_id):
    return controladores.obtener_record(estudiante_id)


@record_academico_bp.route('/historial-completo', methods=['GET'])
@rol_requerido("estudiante")
def historial_completo():
    return controladores.historial_completo()


@record_academico_bp.route('/historial-completo/pdf', methods=['GET'])
@rol_requerido("estudiante")
def historial_completo_pdf():
    return controladores.historial_completo_pdf()


@record_academico_bp.route('/progreso/<int:estudiante_id>', methods=['GET'])
@rol_requerido("administrador", "direccion")
def obtener_progreso(estudiante_id):
    return controladores.obtener_progreso(estudiante_id)


@record_academico_bp.route('/tipos-clasificacion', methods=['GET'])
def listar_tipos_clasificacion():
    return controladores.listar_tipos_clasificacion()


@record_academico_bp.route('/estados-permanencia', methods=['GET'])
def listar_estados_permanencia():
    return controladores.listar_estados_permanencia()


@record_academico_bp.route('/anios-ingreso', methods=['GET'])
@rol_requerido("administrador", "direccion")
def anios_ingreso():
    return controladores.anios_ingreso()


@record_academico_bp.route('/reportes', methods=['GET'])
@rol_requerido("administrador", "direccion")
def reportes_consolidados():
    return controladores.reportes_consolidados()


@record_academico_bp.route('/reportes/exportar', methods=['GET'])
@rol_requerido("administrador", "direccion")
def exportar_reportes():
    return controladores.exportar_reportes()


@record_academico_bp.route('/analisis-cohorte', methods=['GET'])
@rol_requerido("direccion")
def analisis_cohorte():
    return controladores.analisis_cohorte()