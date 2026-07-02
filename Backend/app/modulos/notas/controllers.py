from flask import jsonify, request
from app import db
from app.modelos.matricula_detalle import MatriculaDetalle
from app.modelos.estado_curso import EstadoCurso


def listar_notas():
    detalles = MatriculaDetalle.query.all()
    return jsonify([
        {
            "matricula_id": d.matricula_id,
            "oferta_academica_id": d.oferta_academica_id,
            "nota_final": float(d.nota_final) if d.nota_final is not None else None,
            "estado_curso_id": d.estado_curso_id
        }
        for d in detalles
    ])


def obtener_notas_matricula(matricula_id):
    detalles = MatriculaDetalle.query.filter_by(matricula_id=matricula_id).all()
    return jsonify([
        {
            "oferta_academica_id": d.oferta_academica_id,
            "nota_final": float(d.nota_final) if d.nota_final is not None else None,
            "estado_curso_id": d.estado_curso_id
        }
        for d in detalles
    ])


def registrar_nota():
    data = request.get_json()
    detalle = MatriculaDetalle.query.filter_by(
        matricula_id=data.get("matricula_id"),
        oferta_academica_id=data.get("oferta_academica_id")
    ).first_or_404()

    detalle.nota_final = data.get("nota_final")
    detalle.estado_curso_id = data.get("estado_curso_id")
    db.session.commit()
    return jsonify({"mensaje": "nota registrada"})


def listar_estados_curso():
    estados = EstadoCurso.query.all()
    return jsonify([
        {"id": e.id, "nombre": e.nombre}
        for e in estados
    ])