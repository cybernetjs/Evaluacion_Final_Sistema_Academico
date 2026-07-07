from datetime import datetime

from flask import jsonify, request, send_file
from flask_jwt_extended import get_jwt_identity
from app.modelos.estudiante import Estudiante
from app.modelos.periodo_academico import PeriodoAcademico
from app.modelos.oferta_academica import OfertaAcademica
from app.modelos.matricula import Matricula
from app.modelos.estado_matricula import EstadoMatricula
from app.modulos.matricula.services import MatriculaService


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


def periodo_actual():
    periodo = MatriculaService.periodo_actual()
    return jsonify({
        "id": periodo.id,
        "nombre": periodo.nombre,
        "fecha_inicio": periodo.fecha_inicio.isoformat() if isinstance(periodo.fecha_inicio, datetime) else periodo.fecha_inicio,
        "fecha_fin": periodo.fecha_fin.isoformat() if isinstance(periodo.fecha_fin, datetime) else periodo.fecha_fin
    })


def listar_ofertas():
    periodo = MatriculaService.periodo_actual()
    ofertas = OfertaAcademica.query.filter_by(periodo_academico_id=periodo.id).all()

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
        }
        for o in ofertas
    ])


def listar_matriculas():
    periodo_id = request.args.get("periodo_id", type=int)
    especialidad_id = request.args.get("especialidad_id", type=int)
    estado = request.args.get("estado")
    pagina = request.args.get("pagina", default=1, type=int)
    por_pagina = request.args.get("por_pagina", default=10, type=int)

    resultado, error = MatriculaService.listar_bandeja_validacion(
        periodo_id=periodo_id,
        especialidad_id=especialidad_id,
        estado_nombre=estado,
        pagina=pagina,
        por_pagina=por_pagina,
    )

    if error:
        return jsonify({"error": error}), 400

    return jsonify(resultado)


def validar_periodo(estudiante_id):
    resultado, error = MatriculaService.validar_periodo(estudiante_id)

    if error:
        return jsonify({"error": error}), 400

    return jsonify(resultado)


def cancelar_matricula():
    matricula_id = request.get_json().get("matricula_id")

    if not matricula_id:
        return jsonify({"error": "Debes indicar el ID de la matrícula"}), 400

    resultado, error = MatriculaService.cancelar_matricula(matricula_id)

    if error:
        return jsonify({"error": error}), 400

    return jsonify(resultado)


def crear_matricula():
    usuario_id = get_jwt_identity()
    ofertas_seleccionadas = request.get_json().get("ofertas_academicas_ids", [])

    resultado, error = MatriculaService.solicitar_matricula(usuario_id, ofertas_seleccionadas)

    if error:
        return jsonify({"error": error}), 400

    return jsonify({"mensaje": "Solicitud de matrícula registrada", **resultado}), 201


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
    from app import db
    db.session.commit()

    return jsonify({"mensaje": "Requisitos validados", "matricula_id": matricula.id})


def registrar_pago(matricula_id):
    numero_operacion = request.form.get("numero_operacion")
    fecha_pago = request.form.get("fecha_pago")
    monto = request.form.get("monto")
    archivo = request.files.get("comprobante")

    resultado, error, codigo = MatriculaService.registrar_pago(
        matricula_id, numero_operacion, fecha_pago, monto, archivo
    )

    if error:
        return jsonify({"error": error}), codigo

    return jsonify(resultado), codigo


def generar_ficha_oficial(matricula_id):
    resultado, error = MatriculaService.oficializar_matricula(matricula_id)

    if error:
        return jsonify({"error": error}), 400

    return jsonify(resultado)


def descargar_ficha_oficial_admin(matricula_id):
    buffer, error = MatriculaService.generar_pdf_ficha(matricula_id)

    if error:
        return jsonify({"error": error}), 400

    return send_file(
        buffer,
        as_attachment=False,
        download_name=f"ficha_matricula_oficial_{matricula_id}.pdf",
        mimetype="application/pdf"
    )


def descargar_ficha_oficial_estudiante():
    usuario_id = get_jwt_identity()
    buffer, error = MatriculaService.descargar_ficha_oficial_estudiante(usuario_id)

    if error:
        return jsonify({"error": error}), 400

    return send_file(
        buffer,
        as_attachment=False,
        download_name="ficha_matricula_oficial.pdf",
        mimetype="application/pdf"
    )


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


def cursos_disponibles():
    usuario_id = get_jwt_identity()
    periodo = MatriculaService.periodo_actual()

    resultado, error = MatriculaService.cursos_disponibles(usuario_id, periodo.id)

    if error:
        return jsonify({"error": error}), 400

    return jsonify(resultado)


def mi_solicitud_actual():
    usuario_id = get_jwt_identity()
    periodo = MatriculaService.periodo_actual()

    resultado, error = MatriculaService.mi_solicitud_actual(usuario_id, periodo.id)

    if error:
        return jsonify({"error": error}), 400

    return jsonify(resultado)


def descargar_ficha_preliminar():
    usuario_id = get_jwt_identity()
    ip_solicitante = request.headers.get("X-Forwarded-For", request.remote_addr)

    buffer, error = MatriculaService.generar_pdf_ficha_preliminar(usuario_id, ip_solicitante)

    if error:
        return jsonify({"error": error}), 400

    return send_file(
        buffer,
        as_attachment=False,
        download_name="ficha_matricula_preliminar.pdf",
        mimetype="application/pdf"
    )