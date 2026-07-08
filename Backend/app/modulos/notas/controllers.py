from flask import jsonify, request
from flask_jwt_extended import get_jwt_identity
from app import db
from app.modelos.matricula_detalle import MatriculaDetalle
from app.modelos.estado_curso import EstadoCurso
from app.modulos.notas.services import NotasService


def listar_notas():
    detalles = MatriculaDetalle.query.all()
    return jsonify([
        {
            "matricula_id": d.matricula_id,
            "oferta_academica_id": d.oferta_academica_id,
            "nota_parcial": float(d.nota_parcial) if d.nota_parcial is not None else None,
            "nota_final": float(d.nota_final) if d.nota_final is not None else None,
            "estado_curso_id": d.estado_curso_id,
            "estado_curso": d.estado_curso.nombre if d.estado_curso else None
        }
        for d in detalles
    ])


def obtener_notas_matricula(matricula_id):
    detalles = MatriculaDetalle.query.filter_by(matricula_id=matricula_id).all()
    return jsonify([
        {
            "oferta_academica_id": d.oferta_academica_id,
            "nota_parcial": float(d.nota_parcial) if d.nota_parcial is not None else None,
            "nota_final": float(d.nota_final) if d.nota_final is not None else None,
            "estado_curso_id": d.estado_curso_id,
            "estado_curso": d.estado_curso.nombre if d.estado_curso else None
        }
        for d in detalles
    ])


def mi_hoja_de_notas():
    usuario_id = int(get_jwt_identity())
    semestre_id = request.args.get("semestre_id", type=int)
    periodo_academico_id = request.args.get("periodo_academico_id", type=int)

    resultado, error = NotasService.hoja_de_notas_por_ciclo(usuario_id, periodo_academico_id, semestre_id)

    if error:
        return jsonify({"error": error}), 404

    return jsonify(resultado)


def ciclos_cursados():
    usuario_id = int(get_jwt_identity())
    resultado, error = NotasService.ciclos_cursados(usuario_id)

    if error:
        return jsonify({"error": error}), 404

    return jsonify(resultado)


def publicar_notas():
    usuario_id = int(get_jwt_identity())
    data = request.get_json() or {}

    resultado, error = NotasService.publicar_notas(usuario_id, data.get("oferta_academica_id"))

    if error:
        return jsonify({"error": error}), 403

    return jsonify(resultado)


def panel_actas():
    resultado, error = NotasService.panel_actas()

    if error:
        return jsonify({"error": error}), 400

    return jsonify(resultado)


def alumnos_omisos(oferta_academica_id):
    resultado, error = NotasService.alumnos_omisos(oferta_academica_id)

    if error:
        return jsonify({"error": error}), 400

    return jsonify(resultado)


def cerrar_acta():
    data = request.get_json() or {}

    resultado, error, codigo = NotasService.cerrar_acta(data.get("oferta_academica_id"))

    if error:
        cuerpo = {"error": error}
        if isinstance(resultado, dict):
            cuerpo.update(resultado)
        return jsonify(cuerpo), codigo

    return jsonify(resultado), codigo


def estado_periodo_para_consolidar(periodo_academico_id):
    resultado, error = NotasService.estado_periodo_para_consolidar(periodo_academico_id)

    if error:
        return jsonify({"error": error}), 400

    return jsonify(resultado)


def consolidar_semestre():
    data = request.get_json() or {}
    periodo_academico_id = data.get("periodo_academico_id")

    resultado, error, codigo, secciones_pendientes = NotasService.consolidar_semestre(periodo_academico_id)

    if error:
        return jsonify({"error": error, "secciones_pendientes": secciones_pendientes}), codigo

    return jsonify(resultado), codigo


def indicadores_direccion():
    periodo_academico_id = request.args.get("periodo_academico_id", type=int)
    especialidad_id = request.args.get("especialidad_id", type=int)
    plan_estudios_id = request.args.get("plan_estudios_id", type=int)

    resultado, error = NotasService.indicadores_direccion(periodo_academico_id, especialidad_id, plan_estudios_id)

    if error:
        return jsonify({"error": error}), 400

    return jsonify(resultado)


def registrar_nota():
    data = request.get_json()

    detalle, error = NotasService.registrar_nota(
        matricula_id=data.get("matricula_id"),
        oferta_academica_id=data.get("oferta_academica_id"),
        nota_parcial=data.get("nota_parcial"),
        nota_final=data.get("nota_final"),
        estado_curso_id=data.get("estado_curso_id")
    )

    if error:
        return jsonify({"mensaje": error}), 404

    return jsonify({
        "mensaje": "Nota registrada",
        "nota_parcial": float(detalle.nota_parcial) if detalle.nota_parcial is not None else None,
        "nota_final": float(detalle.nota_final) if detalle.nota_final is not None else None
    })


def obtener_planilla(oferta_academica_id):
    usuario_id = int(get_jwt_identity())
    resultado, error = NotasService.obtener_planilla(oferta_academica_id, usuario_id)

    if error:
        return jsonify({"error": error}), 403

    return jsonify(resultado)


def estado_cronograma(oferta_academica_id):
    tipo_nota = request.args.get("tipo_nota", default="final")
    resultado, error = NotasService.estado_cronograma(oferta_academica_id, tipo_nota)

    if error:
        return jsonify({"error": error}), 400

    return jsonify(resultado)


def registrar_notas_planilla():
    usuario_id = int(get_jwt_identity())
    data = request.get_json() or {}

    resultado, error, codigo = NotasService.registrar_notas_planilla(
        usuario_id_docente=usuario_id,
        oferta_academica_id=data.get("oferta_academica_id"),
        tipo_nota=data.get("tipo_nota"),
        calificaciones=data.get("calificaciones", []),
    )

    if error:
        return jsonify({"error": error}), codigo

    return jsonify(resultado), codigo


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