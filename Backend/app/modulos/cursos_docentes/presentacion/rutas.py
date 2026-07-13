from flask import Blueprint
from app.modulos.cursos_docentes.presentacion import controladores
from app.compartido.middlewares.autorizacion import rol_requerido

cursos_docentes_bp = Blueprint('cursos_docentes', __name__)


@cursos_docentes_bp.route('/', methods=['GET'])
def listar_cursos():
    return controladores.listar_cursos()


@cursos_docentes_bp.route('/<int:id>', methods=['GET'])
def obtener_curso(id):
    return controladores.obtener_curso(id)


@cursos_docentes_bp.route('/cursos', methods=['POST'])
@rol_requerido("administrador")
def crear_curso():
    return controladores.crear_curso()


@cursos_docentes_bp.route('/ofertas', methods=['POST'])
@rol_requerido("administrador")
def crear_oferta_academica():
    return controladores.crear_oferta_academica()


@cursos_docentes_bp.route('/ofertas/<int:oferta_academica_id>/asignaciones', methods=['GET'])
@rol_requerido("administrador")
def asignaciones_oferta(oferta_academica_id):
    return controladores.asignaciones_oferta(oferta_academica_id)


@cursos_docentes_bp.route('/prerequisitos', methods=['GET'])
def listar_prerequisitos():
    return controladores.listar_prerequisitos()

@cursos_docentes_bp.route('/tipos-docentes', methods=['GET'])
def listar_tipos_docentes():
    return controladores.listar_tipos_docentes()


@cursos_docentes_bp.route('/carga-academica', methods=['GET'])
@rol_requerido("docente")
def mis_cursos_asignados():
    return controladores.mis_cursos_asignados()


@cursos_docentes_bp.route('/carga-academica/periodos-historicos', methods=['GET'])
@rol_requerido("docente")
def periodos_historicos_docente():
    return controladores.periodos_historicos_docente()


@cursos_docentes_bp.route('/ofertas/<int:oferta_academica_id>/asignar-docente', methods=['POST'])
@rol_requerido("administrador")
def asignar_docente(oferta_academica_id):
    return controladores.asignar_docente(oferta_academica_id)


@cursos_docentes_bp.route('/ofertas/<int:oferta_academica_id>/horario', methods=['POST'])
@rol_requerido("administrador")
def gestionar_horario(oferta_academica_id):
    return controladores.gestionar_horario(oferta_academica_id)


@cursos_docentes_bp.route('/carga-docente', methods=['GET'])
@rol_requerido("direccion")
def carga_docente():
    return controladores.carga_docente()


@cursos_docentes_bp.route('/ofertas/<int:oferta_academica_id>/silabo', methods=['POST'])
@rol_requerido("docente")
def cargar_silabo(oferta_academica_id):
    return controladores.cargar_silabo(oferta_academica_id)


@cursos_docentes_bp.route('/ofertas/<int:oferta_academica_id>/silabo', methods=['GET'])
def descargar_silabo(oferta_academica_id):
    return controladores.descargar_silabo(oferta_academica_id)


@cursos_docentes_bp.route('/auditoria/cumplimiento-silabos', methods=['GET'])
@rol_requerido("direccion")
def cumplimiento_silabos():
    return controladores.cumplimiento_silabos()