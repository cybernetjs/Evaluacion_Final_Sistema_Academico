from flask import jsonify, request, send_file
from flask_jwt_extended import get_jwt_identity
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


def bandeja_solicitudes():
    estado = request.args.get("estado")
    pagina = request.args.get("pagina", default=1, type=int)
    por_pagina = request.args.get("por_pagina", default=10, type=int)

    resultado, error = CertificadoService.bandeja_solicitudes(estado, pagina, por_pagina)

    if error:
        return jsonify({"error": error}), 404

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


def detalle_expediente(certificado_id):
    resultado, error = CertificadoService.detalle_expediente(certificado_id)
def autorizar_certificado(certificado_id) -> list[dict]:
    certificado = Certificado.query.get(certificado_id)

    if not certificado:
        return jsonify({
            "error": "Certificado no encontrado"
        }), 404
    if error:
        return jsonify({"error": error}), 404

    return jsonify(resultado)


def descargar_comprobante(certificado_id):
    ruta, error = CertificadoService.obtener_comprobante(certificado_id)

    if error:
        return jsonify({"error": error}), 404

    return send_file(ruta)


def aprobar_tramite():
    certificado_id = request.get_json().get("id")

    resultado, error, codigo = CertificadoService.aprobar_tramite(certificado_id)

    if error:
        return jsonify({"error": error}), codigo

    return jsonify(resultado), codigo


def rechazar_tramite():
    datos = request.get_json()
    certificado_id = datos.get("id")
    motivo = datos.get("motivo")

    resultado, error, codigo = CertificadoService.rechazar_tramite(certificado_id, motivo)

    if error:
        return jsonify({"error": error}), codigo

    return jsonify(resultado), codigo


def firmar_certificados():
    certificado_ids = request.get_json().get("certificado_ids", [])

    resultado, error = CertificadoService.firmar_certificados(certificado_ids)

    if error:
        return jsonify({"error": error}), 400

    return jsonify(resultado)


def descargar_certificado_emitido(certificado_id):
    ruta, error = CertificadoService.obtener_ruta_certificado_emitido(certificado_id)

    if error:
        return jsonify({"error": error}), 404

    return send_file(ruta, as_attachment=True, download_name=f"certificado_{certificado_id}.pdf")


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

    return jsonify(resultado)