from flask import jsonify, request
from flask_jwt_extended import create_access_token
from app import bcrypt
from app.modelos.usuario import Usuario


def login():
    datos = request.get_json()
    username = datos.get("username")
    password = datos.get("password")

    usuario = Usuario.query.filter_by(username=username).first()

    if not usuario or not bcrypt.check_password_hash(usuario.password, password):
        return jsonify({"error": "Usuario o contraseña incorrectos"}), 401

    token = create_access_token(
        identity=str(usuario.id),
        additional_claims={"rol": usuario.rol, "username": usuario.username},
    )

    return jsonify({
        "token": token,
        "usuario": {
            "id": usuario.id,
            "username": usuario.username,
            "rol": usuario.rol,
        },
    })