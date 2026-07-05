from flask import jsonify, request
from flask_jwt_extended import get_jwt_identity
from datetime import time as hora_cls
from app import db
from app.modelos.curso import Curso
from app.modelos.pre_requisito import PreRequisito
from app.modelos.docente import Docente
from app.modelos.tipo_docente import TipoDocente
from app.modelos.oferta_academica import OfertaAcademica
from app.modelos.oferta_academica_docente import OfertaAcademicaDocente
from app.modelos.oferta_academica_horario import OfertaAcademicaHorario
from flask import send_file
from app.modulos.cursos_docentes.services import CursosDocentesService
from app.modulos.cursos_docentes.services import cumplimiento_plan_estudios


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
    docente = Docente.query.filter_by(usuario_id=usuario_id).first()

    if not docente:
        return jsonify({"error": "No se encontró un docente asociado a este usuario"}), 404

    asignaciones = OfertaAcademicaDocente.query.filter_by(docente_id=docente.id).all()

    resultado = []
    for a in asignaciones:
        oferta = a.oferta_academica
        resultado.append({
            "oferta_academica_id": oferta.id,
            "curso_id": oferta.curso_id,
            "curso_nombre": oferta.curso.nombre,
            "semestre_id": oferta.semestre_id,
            "periodo_academico_id": oferta.periodo_academico_id,
            "cupos": oferta.cupos,
            "tipo_docente_id": a.tipo_docente_id
        })

    return jsonify(resultado)


def asignar_docente(oferta_academica_id):
    data = request.get_json()
    docente_id = data.get("docente_id")
    tipo_docente_id = data.get("tipo_docente_id")

    oferta = OfertaAcademica.query.get(oferta_academica_id)
    if not oferta:
        return jsonify({"error": "Oferta académica no encontrada"}), 404

    asignacion = OfertaAcademicaDocente(
        oferta_academica_id=oferta_academica_id,
        docente_id=docente_id,
        tipo_docente_id=tipo_docente_id
    )
    db.session.add(asignacion)
    db.session.commit()

    return jsonify({"mensaje": "Docente asignado correctamente", "id": asignacion.id}), 201


def gestionar_horario(oferta_academica_id):
    data = request.get_json()

    dia_ingresado = data.get("dia")
    dias = {
        "lunes": 1,
        "martes": 2,
        "miercoles": 3,
        "miércoles": 3,
        "jueves": 4,
        "viernes": 5,
        "sabado": 6,
        "sábado": 6,
        "domingo": 7,
    }

    if isinstance(dia_ingresado, int):
        dia = dia_ingresado
    else:
        dia_normalizado = str(dia_ingresado).strip().lower()
        if dia_normalizado.isdigit():
            dia = int(dia_normalizado)
        else:
            dia = dias.get(dia_normalizado)

    if dia is None:
        return jsonify({"error": "Día inválido"}), 400

    try:
        hora_inicio = hora_cls.fromisoformat(str(data.get("hora_inicio")))
        hora_fin = hora_cls.fromisoformat(str(data.get("hora_fin")))
    except (TypeError, ValueError):
        return jsonify({"error": "Formato de hora inválido"}), 400

    oferta = OfertaAcademica.query.get(oferta_academica_id)
    if not oferta:
        return jsonify({"error": "Oferta académica no encontrada"}), 404

    horario = OfertaAcademicaHorario(
        oferta_academica_id=oferta_academica_id,
        dia=dia,
        hora_inicio=hora_inicio,
        hora_fin=hora_fin
    )
    db.session.add(horario)
    db.session.commit()

    return jsonify({"mensaje": "Horario registrado correctamente", "id": horario.id}), 201


def carga_docente():
    docentes = Docente.query.all()
    resultado = []

    for d in docentes:
        cantidad_cursos = OfertaAcademicaDocente.query.filter_by(docente_id=d.id).count()
        resultado.append({
            "docente_id": d.id,
            "nombres": d.nombres,
            "apellido_paterno": d.apellido_paterno,
            "cursos_asignados": cantidad_cursos
        })

    return jsonify(resultado)


def cargar_silabo(oferta_academica_id):
    usuario_id = int(get_jwt_identity())

    if "archivo" not in request.files:
        return jsonify({"error": "Debes adjuntar un archivo"}), 400

    archivo = request.files["archivo"]

    silabo, error = CursosDocentesService.cargar_silabo(
        usuario_id=usuario_id,
        oferta_academica_id=oferta_academica_id,
        nombre_archivo=archivo.filename,
        archivo_stream=archivo
    )

    if error:
        return jsonify({"error": error}), 400

    return jsonify({"mensaje": "Sílabo cargado correctamente", "nombre_archivo": silabo.nombre_archivo}), 201


def descargar_silabo(oferta_academica_id):
    silabo, error = CursosDocentesService.obtener_silabo(oferta_academica_id)

    if error:
        return jsonify({"error": error}), 404

    return send_file(silabo.ruta_archivo, as_attachment=True, download_name=silabo.nombre_archivo)



def evaluar_cumplimiento_plan():
    periodo_academico_id = request.args.get("periodo_academico_id", type=int)

    if not periodo_academico_id:
        return jsonify({"error": "Debes indicar periodo_academico_id como parámetro"}), 400

    resultado = cumplimiento_plan_estudios(periodo_academico_id)
    return jsonify(resultado)