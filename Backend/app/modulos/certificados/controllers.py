from flask import jsonify, request, send_file
from flask_jwt_extended import get_jwt_identity
from app import db
from app.modelos.estudiante import Estudiante
from app.modelos.especialidad import Especialidad
from app.modelos.facultad import Facultad
from app.modelos.certificado import Certificado
from app.modulos.certificados.services import CertificadoService


def solicitar_certificado() -> tuple[dict | None]:
    usuario_id = int(get_jwt_identity())
    tipo = request.form.get("tipo")
    archivo = request.files.get("comprobante")

    resultado, error, codigo = CertificadoService.solicitar_documento(usuario_id, tipo, archivo)

    if error:
        return jsonify({"error": error}), codigo

    return jsonify(resultado), codigo


def mis_solicitudes() -> list[dict]:
    usuario_id = int(get_jwt_identity())
    resultado, error = CertificadoService.mis_solicitudes(usuario_id)

    if error:
        return jsonify({
            "error": error
        }), 404

    return jsonify(resultado)


def listar_solicitudes() -> list[dict]:
    certificados = Certificado.query.all()
    return jsonify([
        {
            "id": c.id,
            "ticket_codigo": c.ticket_codigo,
            "estudiante_id": c.estudiante_id,
            "estudiante_nombre": f"{c.estudiante.nombres} {c.estudiante.apellido_paterno} {c.estudiante.apellido_materno}" if c.estudiante else None,
            "tipo": c.tipo,
            "estado": c.estado,
            "codigo_verificacion": c.codigo_verificacion
        }
        for c in certificados
    ])


def autorizar_certificado(certificado_id) -> list[dict]:
    certificado = Certificado.query.get(certificado_id)

    if not certificado:
        return jsonify({
            "error": "Certificado no encontrado"
        }), 404

    certificado.estado = "Apto para Firma"
    db.session.commit()

    return jsonify({
        "mensaje": "Emisión de certificado autorizada",
        "id": certificado.id
    })


def emitir_certificado(certificado_id) -> list[dict]:
    certificado = Certificado.query.get(certificado_id)

    if not certificado:
        return jsonify({"error": "Certificado no encontrado"}), 404

    if certificado.estado != "Apto para Firma":
        return jsonify({"error": "El certificado debe ser autorizado por Dirección antes de emitirse"}), 400

    certificado.estado = "Emitido"
    db.session.commit()

    estudiante = Estudiante.query.get(certificado.estudiante_id)
    especialidad = Especialidad.query.get(estudiante.especialidad_id)
    facultad = Facultad.query.get(especialidad.facultad_id) if especialidad else None

    return jsonify({
        "mensaje": "Certificado emitido con firma digital",
        "certificado": {
            "id": certificado.id,
            "tipo": certificado.tipo,
            "codigo_verificacion": certificado.codigo_verificacion,
            "url_verificacion": f"/api/documentos/publico/verificar/{certificado.codigo_verificacion}"
        },
        "estudiante": {
            "nombres": estudiante.nombres,
            "apellido_paterno": estudiante.apellido_paterno,
            "apellido_materno": estudiante.apellido_materno
        },
        "especialidad": especialidad.nombre if especialidad else None,
        "facultad": facultad.nombre if facultad else None
    })


def verificar_certificado(codigo) -> list[dict]:
    certificado = Certificado.query.filter_by(codigo_verificacion=codigo).first()

    if not certificado or certificado.estado != "Emitido":
        return jsonify({
            "valido": False,
            "mensaje": "Certificado no encontrado o no emitido"
        }), 404

    return jsonify({
        "valido": True,
        "tipo": certificado.tipo,
        "estudiante_id": certificado.estudiante_id,
        "estado": certificado.estado
    })


def descargar_qr(codigo) -> list[dict]:
    buffer, error = CertificadoService.generar_qr(codigo)

    if error:
        return jsonify({
            "error": error
        }), 404

    return send_file(
        buffer,
        mimetype="image/png",
        as_attachment=False
    )