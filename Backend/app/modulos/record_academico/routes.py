from flask import Blueprint
from app.modulos.cursos_docentes import controllers
from app.utils.middlewares import rol_requerido

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


@cursos_docentes_bp.route('/carga-academica', methods=['GET'])
@rol_requerido("docente")
def mis_cursos_asignados():
    return controllers.mis_cursos_asignados()


@cursos_docentes_bp.route('/carga-academica/periodos-historicos', methods=['GET'])
@rol_requerido("docente")
def periodos_historicos_docente():
    return controllers.periodos_historicos_docente()


@cursos_docentes_bp.route('/ofertas/<int:oferta_academica_id>/asignar-docente', methods=['POST'])
@rol_requerido("administrador")
def asignar_docente(oferta_academica_id):
    return controllers.asignar_docente(oferta_academica_id)


@cursos_docentes_bp.route('/ofertas/<int:oferta_academica_id>/horario', methods=['POST'])
@rol_requerido("administrador")
def gestionar_horario(oferta_academica_id):
    return controllers.gestionar_horario(oferta_academica_id)


@cursos_docentes_bp.route('/carga-docente', methods=['GET'])
@rol_requerido("direccion")
def carga_docente():
    return controllers.carga_docente()


@cursos_docentes_bp.route('/ofertas/<int:oferta_academica_id>/silabo', methods=['POST'])
@rol_requerido("docente")
def cargar_silabo(oferta_academica_id):
    return controllers.cargar_silabo(oferta_academica_id)


@cursos_docentes_bp.route('/ofertas/<int:oferta_academica_id>/silabo', methods=['GET'])
def descargar_silabo(oferta_academica_id):
    return controllers.descargar_silabo(oferta_academica_id)


@cursos_docentes_bp.route('/auditoria/cumplimiento-silabos', methods=['GET'])
@rol_requerido("direccion")
def cumplimiento_silabos():
    return controllers.cumplimiento_silabos()