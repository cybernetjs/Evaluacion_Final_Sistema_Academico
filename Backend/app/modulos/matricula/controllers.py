from flask import jsonify, request
from app import db
from app.modelos.periodo_academico import PeriodoAcademico
from app.modelos.oferta_academica import OfertaAcademica
from app.modelos.matricula import Matricula
from app.modelos.estado_matricula import EstadoMatricula
from flask import send_file
from app.modulos.matricula.services import MatriculaService



def listar_periodos():
    periodos = PeriodoAcademico.query.all()
    return jsonify([
        {
            "id": p.id,
            "nombre": p.nombre,
            "fecha_inicio": p.fecha_inicio,
            "fecha_fin": p.fecha_fin
        }
        for p in periodos
    ])


def listar_ofertas():
    ofertas = OfertaAcademica.query.all()
    return jsonify([
        {
            "id": o.id,
            "periodo_academico_id": o.periodo_academico_id,
            "curso_id": o.curso_id,
            "semestre_id": o.semestre_id,
            "cupos": o.cupos
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
    data = request.get_json()
    nueva = Matricula(
        estudiante_id=data.get("estudiante_id"),
        periodo_academico_id=data.get("periodo_academico_id"),
        semestre_id=data.get("semestre_id"),
        estado_id=1  
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