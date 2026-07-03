from flask import jsonify, request
from flask_jwt_extended import get_jwt_identity
from app import db
from app.modelos.matricula_detalle import MatriculaDetalle
from app.modelos.estado_curso import EstadoCurso
from app.modelos.matricula import Matricula
from app.modelos.estudiante import Estudiante


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


def mi_hoja_de_notas():
    usuario_id = get_jwt_identity()
    estudiante = Estudiante.query.filter_by(usuario_id=usuario_id).first()

    if not estudiante:
        return jsonify({"error": "No se encontró un estudiante asociado a este usuario"}), 404

    matriculas = Matricula.query.filter_by(estudiante_id=estudiante.id).all()

    resultado = []
    for m in matriculas:
        for d in m.detalle:
            resultado.append({
                "periodo_academico_id": m.periodo_academico_id,
                "semestre_id": m.semestre_id,
                "curso_id": d.oferta_academica.curso_id,
                "curso_nombre": d.oferta_academica.curso.nombre,
                "nota_final": float(d.nota_final) if d.nota_final is not None else None,
                "estado_curso_id": d.estado_curso_id
            })

    return jsonify(resultado)


def registrar_nota():
    data = request.get_json()
    detalle = MatriculaDetalle.query.filter_by(
        matricula_id=data.get("matricula_id"),
        oferta_academica_id=data.get("oferta_academica_id")
    ).first()
    if not detalle:
        return jsonify({"mensaje": "Detalle de matrícula no encontrado"}), 404
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


def validar_actas():
    total_detalles = MatriculaDetalle.query.count()
    con_nota = MatriculaDetalle.query.filter(MatriculaDetalle.nota_final.isnot(None)).count()
    sin_nota = total_detalles - con_nota

    return jsonify({
        "mensaje": "Estado de actas revisado",
        "total_cursos_matriculados": total_detalles,
        "con_nota_registrada": con_nota,
        "pendientes_de_nota": sin_nota
    })


def indicadores_academicos():
    detalles = MatriculaDetalle.query.filter(MatriculaDetalle.nota_final.isnot(None)).all()

    if not detalles:
        return jsonify({
            "promedio_general": None,
            "total_evaluados": 0
        })

    total = sum(float(d.nota_final) for d in detalles)
    promedio = round(total / len(detalles), 2)

    return jsonify({
        "promedio_general": promedio,
        "total_evaluados": len(detalles)
    })