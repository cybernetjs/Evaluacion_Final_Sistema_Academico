from flask import jsonify, request
from flask_jwt_extended import get_jwt_identity
from app import db
from app.modelos.estudiante import Estudiante
from app.modelos.especialidad import Especialidad
from app.modelos.facultad import Facultad
from app.modelos.certificado import Certificado
from flask import send_file
from app.modulos.certificados.services import CertificadoService


def solicitar_certificado():
    usuario_id = get_jwt_identity()
    estudiante = Estudiante.query.filter_by(usuario_id=usuario_id).first()

    if not estudiante:
        return jsonify({"error": "No se encontró un estudiante asociado a este usuario"}), 404

    data = request.get_json()
    tipo = data.get("tipo")

    if not tipo:
        return jsonify({"error": "Debes indicar el tipo de certificado"}), 400

    certificado = Certificado(estudiante_id=estudiante.id, tipo=tipo)
    db.session.add(certificado)
    db.session.commit()

    return jsonify({
        "mensaje": "Solicitud de certificado registrada",
        "id": certificado.id,
        "tipo": certificado.tipo
    }), 201


def listar_solicitudes():
    certificados = Certificado.query.all()
    return jsonify([
        {
            "id": c.id,
            "estudiante_id": c.estudiante_id,
            "tipo": c.tipo,
            "autorizado": c.autorizado,
            "emitido": c.emitido,
            "codigo_verificacion": c.codigo_verificacion
        }
        for c in certificados
    ])


def autorizar_certificado(certificado_id):
    certificado = Certificado.query.get(certificado_id)

    if not certificado:
        return jsonify({"error": "Certificado no encontrado"}), 404

    certificado.autorizado = True
    db.session.commit()

    return jsonify({"mensaje": "Emisión de certificado autorizada", "id": certificado.id})


def emitir_certificado(certificado_id):
    certificado = Certificado.query.get(certificado_id)

    if not certificado:
        return jsonify({"error": "Certificado no encontrado"}), 404

    if not certificado.autorizado:
        return jsonify({"error": "El certificado debe ser autorizado por Dirección antes de emitirse"}), 400

    certificado.emitido = True
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
            "url_verificacion": f"/api/certificados/verificar/{certificado.codigo_verificacion}"
        },
        "estudiante": {
            "nombres": estudiante.nombres,
            "apellido_paterno": estudiante.apellido_paterno,
            "apellido_materno": estudiante.apellido_materno
        },
        "especialidad": especialidad.nombre if especialidad else None,
        "facultad": facultad.nombre if facultad else None
    })


def verificar_certificado(codigo):
    certificado = Certificado.query.filter_by(codigo_verificacion=codigo).first()

    if not certificado or not certificado.emitido:
        return jsonify({"valido": False, "mensaje": "Certificado no encontrado o no emitido"}), 404

    return jsonify({
        "valido": True,
        "tipo": certificado.tipo,
        "estudiante_id": certificado.estudiante_id,
        "emitido": certificado.emitido
    })


def descargar_qr(codigo):
    buffer, error = CertificadoService.generar_qr(codigo)

    if error:
        return jsonify({"error": error}), 404

    return send_file(
        buffer,
        mimetype="image/png",
        as_attachment=False
    )