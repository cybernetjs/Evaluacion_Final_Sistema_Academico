from flask import jsonify, request
from app import db
from app.modelos.periodo_academico import PeriodoAcademico
from app.modelos.oferta_academica import OfertaAcademica
from app.modelos.matricula import Matricula
from app.modelos.estado_matricula import EstadoMatricula


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
            "estado_id": m.estado_id
        }
        for m in matriculas
    ])


def crear_matricula():
    data = request.get_json()
    nueva = Matricula(
        estudiante_id=data.get("estudiante_id"),
        periodo_academico_id=data.get("periodo_academico_id"),
        semestre_id=data.get("semestre_id"),
        estado_id=data.get("estado_id")
    )
    db.session.add(nueva)
    db.session.commit()
    return jsonify({"mensaje": "matrícula creada", "id": nueva.id}), 201


def listar_estados_matricula():
    estados = EstadoMatricula.query.all()
    return jsonify([
        {"id": e.id, "nombre": e.nombre}
        for e in estados
    ])