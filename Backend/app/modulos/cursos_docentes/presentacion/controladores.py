from flask import jsonify, request, send_file
from flask_jwt_extended import get_jwt_identity
from datetime import time as hora_cls
from app.dominio.modelos.academico.curso import Curso
from app.dominio.modelos.academico.pre_requisito import PreRequisito
from app.dominio.modelos.docentes.docente import Docente
from app.dominio.modelos.docentes.tipo_docente import TipoDocente
from app.modulos.cursos_docentes.aplicacion.servicios import CursosDocentesService

DIAS_TEXTO = {
    "lunes": 1, "martes": 2, "miercoles": 3, "miércoles": 3,
    "jueves": 4, "viernes": 5, "sabado": 6, "sábado": 6, "domingo": 7,
}


def listar_cursos():
    cursos = Curso.query.all()
    return jsonify([
        {
            "id": c.id,
            "nombre": c.nombre,
            "codigo": c.codigo,
            "creditos": c.creditos,
            "horas_lectivas": c.horas_lectivas,
            "horas_practicas": c.horas_practicas
        }
        for c in cursos
    ])


def obtener_curso(id):
    c = Curso.query.get(id)
    if not c:
        return jsonify({"mensaje": "Curso no encontrado"}), 404
    return jsonify({
        "id": c.id,
        "nombre": c.nombre,
        "codigo": c.codigo,
        "creditos": c.creditos,
        "horas_lectivas": c.horas_lectivas,
        "horas_practicas": c.horas_practicas
    })


def crear_curso():
    data = request.get_json() or {}

    resultado, error, codigo = CursosDocentesService.crear_curso(
        nombre=data.get("nombre"),
        codigo=data.get("codigo"),
        creditos=data.get("creditos"),
        horas_lectivas=data.get("horas_lectivas"),
        horas_practicas=data.get("horas_practicas"),
    )

    if error:
        return jsonify({"error": error}), codigo

    return jsonify(resultado), codigo


def crear_oferta_academica():
    data = request.get_json() or {}

    resultado, error, codigo = CursosDocentesService.crear_oferta_academica(
        curso_id=data.get("curso_id"),
        periodo_academico_id=data.get("periodo_academico_id"),
        semestre_id=data.get("semestre_id"),
        cupos=data.get("cupos"),
    )

    if error:
        return jsonify({"error": error}), codigo

    return jsonify(resultado), codigo


def asignaciones_oferta(oferta_academica_id):
    resultado, error = CursosDocentesService.asignaciones_oferta(oferta_academica_id)

    if error:
        return jsonify({"error": error}), 404

    return jsonify(resultado)


def listar_prerequisitos():
    prerequisitos = PreRequisito.query.all()
    return jsonify([
        {
            "curso_dependiente_id": p.curso_dependiente_id,
            "curso_requisito_id": p.curso_requisito_id
        }
        for p in prerequisitos
    ])


def listar_docentes():
    docentes = Docente.query.all()
    return jsonify([
        {
            "id": d.id,
            "nombres": d.nombres,
            "apellido_paterno": d.apellido_paterno,
            "apellido_materno": d.apellido_materno,
            "correo_institucional": d.correo_institucional
        }
        for d in docentes
    ])


def listar_tipos_docentes():
    tipos = TipoDocente.query.all()
    return jsonify([
        {"id": t.id, "nombre": t.nombre}
        for t in tipos
    ])


def mis_cursos_asignados():
    usuario_id = int(get_jwt_identity())
    periodo_academico_id = request.args.get("periodo_academico_id", type=int)

    resultado, error = CursosDocentesService.mis_cursos(usuario_id, periodo_academico_id)

    if error:
        return jsonify({"error": error}), 404

    return jsonify(resultado)


def periodos_historicos_docente():
    usuario_id = int(get_jwt_identity())
    periodos, error = CursosDocentesService.periodos_historicos_docente(usuario_id)

    if error:
        return jsonify({"error": error}), 404

    return jsonify(periodos)


def asignar_docente(oferta_academica_id):
    data = request.get_json()
    docente_id = data.get("docente_id")
    tipo_docente_id = data.get("tipo_docente_id")
    funcion_curso = data.get("funcion_curso")
    horas_asignadas = data.get("horas_asignadas")

    resultado, error, codigo = CursosDocentesService.asignar_docente(
        oferta_academica_id=oferta_academica_id,
        docente_id=docente_id,
        funcion_curso=funcion_curso,
        horas_asignadas=horas_asignadas,
        tipo_docente_id=tipo_docente_id,
    )

    if error:
        return jsonify({"error": error}), codigo

    return jsonify(resultado), codigo


def gestionar_horario(oferta_academica_id):
    data = request.get_json()

    dia_ingresado = data.get("dia")
    if isinstance(dia_ingresado, int):
        dia = dia_ingresado
    else:
        dia_normalizado = str(dia_ingresado).strip().lower()
        dia = int(dia_normalizado) if dia_normalizado.isdigit() else DIAS_TEXTO.get(dia_normalizado)

    if dia is None:
        return jsonify({"error": "Día inválido"}), 400

    try:
        hora_inicio = hora_cls.fromisoformat(str(data.get("hora_inicio")))
        hora_fin = hora_cls.fromisoformat(str(data.get("hora_fin")))
    except (TypeError, ValueError):
        return jsonify({"error": "Formato de hora inválido"}), 400

    aula = data.get("aula")
    if not aula:
        return jsonify({"error": "Debes indicar el aula o el enlace virtual"}), 400

    funcion_curso = data.get("funcion_curso") or None

    resultado, error, codigo = CursosDocentesService.gestionar_horario(
        oferta_academica_id=oferta_academica_id,
        dia=dia,
        hora_inicio=hora_inicio,
        hora_fin=hora_fin,
        aula=aula,
        funcion_curso=funcion_curso,
    )

    if error:
        return jsonify({"error": error}), codigo

    return jsonify(resultado), codigo


def carga_docente():
    especialidad_id = request.args.get("especialidad_id", type=int)
    periodo_academico_id = request.args.get("periodo_academico_id", type=int)

    resultado = CursosDocentesService.carga_docente(especialidad_id, periodo_academico_id)
    return jsonify(resultado)


def cargar_silabo(oferta_academica_id):
    usuario_id = int(get_jwt_identity())

    if "archivo" not in request.files:
        return jsonify({"error": "Debes adjuntar un archivo"}), 400

    archivo = request.files["archivo"]

    silabo, error, codigo = CursosDocentesService.cargar_silabo(
        usuario_id=usuario_id,
        oferta_academica_id=oferta_academica_id,
        nombre_archivo=archivo.filename,
        archivo_stream=archivo
    )

    if error:
        return jsonify({"error": error}), codigo

    return jsonify({"mensaje": "Sílabo cargado correctamente", "nombre_archivo": silabo.nombre_archivo}), codigo


def descargar_silabo(oferta_academica_id):
    silabo, error = CursosDocentesService.obtener_silabo(oferta_academica_id)

    if error:
        return jsonify({"error": error}), 404

    return send_file(silabo.ruta_archivo, as_attachment=True, download_name=silabo.nombre_archivo)


def cumplimiento_silabos():
    periodo_academico_id = request.args.get("periodo_academico_id", type=int)
    resultado = CursosDocentesService.cumplimiento_silabos(periodo_academico_id)
    return jsonify(resultado)