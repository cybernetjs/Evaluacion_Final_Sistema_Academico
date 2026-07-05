from datetime import datetime

from flask import jsonify, request
from app import db
from app.modelos.curso import Curso
from app.modelos.estudiante import Estudiante
from app.modelos.estado_curso import EstadoCurso
from app.modelos.matricula_detalle import MatriculaDetalle
from app.modelos.pre_requisito import PreRequisito
from app.modelos.periodo_academico import PeriodoAcademico
from app.modelos.oferta_academica import OfertaAcademica
from app.modelos.matricula import Matricula
from app.modelos.estado_matricula import EstadoMatricula
from flask import send_file
from app.modulos.matricula.services import MatriculaService


def _nombre_periodo_actual(fecha=None):
    fecha = fecha or datetime.now()
    semestre = "I" if fecha.month <= 6 else "II"
    return f"{fecha.year}-{semestre}"


def _obtener_o_crear_periodo_actual():
    fecha = datetime.now()
    nombre = _nombre_periodo_actual(fecha)
    periodo = PeriodoAcademico.query.filter_by(nombre=nombre).first()

    if periodo:
        return periodo

    if fecha.month <= 6:
        fecha_inicio = datetime(fecha.year, 1, 1)
        fecha_fin = datetime(fecha.year, 6, 30)
    else:
        fecha_inicio = datetime(fecha.year, 7, 1)
        fecha_fin = datetime(fecha.year, 12, 31)

    periodo = PeriodoAcademico(
        nombre=nombre,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
    )
    db.session.add(periodo)
    db.session.commit()
    return periodo


def _obtener_o_crear_estado_matricula(nombre_estado):
    estado = EstadoMatricula.query.filter_by(nombre=nombre_estado).first()
    if estado:
        return estado

    estado = EstadoMatricula(nombre=nombre_estado)
    db.session.add(estado)
    db.session.commit()
    return estado



def listar_periodos():
    periodos = PeriodoAcademico.query.order_by(PeriodoAcademico.fecha_inicio.desc()).all()
    return jsonify([
        {
            "id": p.id,
            "nombre": p.nombre,
            "fecha_inicio": p.fecha_inicio,
            "fecha_fin": p.fecha_fin
        }
        for p in periodos
    ])


def listar_periodo_actual():
    periodo = _obtener_o_crear_periodo_actual()
    return jsonify({
        "id": periodo.id,
        "nombre": periodo.nombre,
        "fecha_inicio": periodo.fecha_inicio,
        "fecha_fin": periodo.fecha_fin,
    })


def listar_ofertas():
    periodo_actual = _obtener_o_crear_periodo_actual()
    ofertas = OfertaAcademica.query.filter_by(periodo_academico_id=periodo_actual.id).all()

    usuario_id = None
    estudiante = None
    try:
        from flask_jwt_extended import get_jwt_identity

        usuario_id = int(get_jwt_identity())
        estudiante = Estudiante.query.filter_by(usuario_id=usuario_id).first()
    except Exception:
        estudiante = None

    cursos_aprobados = set()
    if estudiante:
        detalles = MatriculaDetalle.query.join(Matricula).join(EstadoCurso).filter(
            Matricula.estudiante_id == estudiante.id,
            EstadoCurso.nombre == "Aprobado",
        ).all()
        for detalle in detalles:
            cursos_aprobados.add(detalle.oferta_academica.curso_id)

    return jsonify([
        {
            "id": o.id,
            "periodo_academico_nombre": o.periodo_academico.nombre,
            "periodo_academico_id": o.periodo_academico_id,
            "curso_nombre": o.curso.nombre,
            "curso_id": o.curso_id,
            "semestre_codigo": o.semestre.codigo,
            "semestre_id": o.semestre_id,
            "cupos": o.cupos
            ,"disponible": None if not estudiante else True,
            "prerequisitos": [],
            "motivo": None,
        }
        for o in ofertas
    ])


def listar_matriculas():
    matriculas = Matricula.query.all()
    return jsonify([
        {
            "id": m.id,
            "estudiante_id": m.estudiante_id,
            "periodo_academico_id": m.periodo_academico_id,
            "semestre_id": m.semestre_id,
            "estado_id": m.estado_id,
            "pagado": m.pagado
        }
        for m in matriculas
    ])


def crear_matricula():
    usuario_id = int(get_jwt_identity())
    estudiante = Estudiante.query.filter_by(usuario_id=usuario_id).first()

    if not estudiante:
        return jsonify({"error": "No se encontró un estudiante asociado a este usuario"}), 404

    data = request.get_json()
    periodo_actual = _obtener_o_crear_periodo_actual()
    estado_pendiente = _obtener_o_crear_estado_matricula("Pendiente")
    periodo_academico_id = data.get("periodo_academico_id") or periodo_actual.id
    semestre_id = data.get("semestre_id")

    if periodo_academico_id != periodo_actual.id:
        return jsonify({"error": "Solo puedes solicitar matrícula en el periodo académico actual"}), 400

    if not 1 <= int(semestre_id) <= 10:
        return jsonify({"error": "El semestre debe estar entre 1 y 10"}), 400

    matricula_existente = Matricula.query.filter_by(
        estudiante_id=estudiante.id,
        periodo_academico_id=periodo_actual.id,
        semestre_id=semestre_id,
    ).first()

    if matricula_existente:
        return jsonify({"error": "Ya existe una solicitud de matrícula para este periodo y semestre"}), 400

    nueva = Matricula(
        estudiante_id=estudiante.id,
        periodo_academico_id=periodo_actual.id,
        semestre_id=int(semestre_id),
        estado_id=estado_pendiente.id,
    )
    db.session.add(nueva)
    db.session.commit()
    return jsonify({"mensaje": "Solicitud de matrícula registrada", "id": nueva.id}), 201


def listar_estados_matricula():
    estados = EstadoMatricula.query.all()
    return jsonify([
        {"id": e.id, "nombre": e.nombre}
        for e in estados
    ])


def validar_requisitos(matricula_id):
    matricula = Matricula.query.get(matricula_id)

    if not matricula:
        return jsonify({"error": "Matrícula no encontrada"}), 404

    if matricula.estado_id != 1:
        return jsonify({"error": "Solo se pueden validar matrículas pendientes"}), 400

    matricula.estado_id = 2  
    db.session.commit()

    return jsonify({"mensaje": "Requisitos validados", "matricula_id": matricula.id})


def registrar_pago(matricula_id):
    matricula = Matricula.query.get(matricula_id)

    if not matricula:
        return jsonify({"error": "Matrícula no encontrada"}), 404

    if matricula.estado_id != 2:
        return jsonify({"error": "La matrícula debe estar validada antes de registrar el pago"}), 400

    matricula.pagado = True
    db.session.commit()

    return jsonify({"mensaje": "Pago registrado", "matricula_id": matricula.id})


def generar_ficha_oficial(matricula_id):
    matricula = Matricula.query.get(matricula_id)

    if not matricula:
        return jsonify({"error": "Matrícula no encontrada"}), 404

    if not matricula.pagado:
        return jsonify({"error": "No se puede generar la ficha sin el pago registrado"}), 400

    matricula.estado_id = 3  
    db.session.commit()

    return jsonify({
        "mensaje": "Ficha oficial generada, matrícula confirmada",
        "matricula": {
            "id": matricula.id,
            "estudiante_id": matricula.estudiante_id,
            "estado_id": matricula.estado_id,
            "pagado": matricula.pagado
        }
    })


def estadisticas():
    total = Matricula.query.count()
    matriculados = Matricula.query.filter_by(estado_id=3).count()
    pendientes = Matricula.query.filter_by(estado_id=1).count()
    validados = Matricula.query.filter_by(estado_id=2).count()

    return jsonify({
        "total_solicitudes": total,
        "matriculados": matriculados,
        "pendientes": pendientes,
        "validados": validados
    })

def descargar_ficha(matricula_id):
    buffer, error = MatriculaService.generar_pdf_ficha(matricula_id)

    if error:
        return jsonify({"error": error}), 404

    return send_file(
        buffer,
        as_attachment=True,
        download_name=f"ficha_matricula_{matricula_id}.pdf",
        mimetype="application/pdf"
    )