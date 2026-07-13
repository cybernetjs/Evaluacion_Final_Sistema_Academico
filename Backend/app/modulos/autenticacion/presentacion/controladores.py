import re
from flask import jsonify, request
from flask_jwt_extended import create_access_token
from app import bcrypt
from app.dominio.modelos.identidad.usuario import Usuario
from app.modulos.autenticacion.aplicacion.servicios import AuthService


def login():
    datos = request.get_json()

    username = datos.get("username")
    password = datos.get("password")

    usuario = Usuario.query.filter_by(username=username).first()

    if not usuario or not bcrypt.check_password_hash(usuario.password, password):
        return jsonify({"error": "Usuario o contraseña incorrectos"}), 401
    
    token = create_access_token(
        identity=str(usuario.id),
        additional_claims={
            "rol": usuario.rol, 
            "username": usuario.username
        },
    )
    return jsonify({
        "token": token,
        "usuario": {
            "id": usuario.id,
            "username": usuario.username,
            "rol": usuario.rol,
        },
    })

def logout():
    return jsonify({"mensaje": "Logout exitoso"})

def registrar():
    datos = request.get_json()

    campos_requeridos = ["username", "password", "nombres", "apellido_paterno", "apellido_materno", "dni", "correo_institucional", "especialidad_id"]
    faltantes = [campo for campo in campos_requeridos if not datos.get(campo)]

    if faltantes:
        return jsonify({"error": f"Faltan campos requeridos: {faltantes}"}), 400

    dni = datos.get("dni")
    if not re.fullmatch(r"\d{8}", dni):
        return jsonify({"error": "El DNI debe tener 8 dígitos numéricos"}), 400

    resultado, error = AuthService.registrar_estudiante(
        username=datos.get("username"),
        password=datos.get("password"),
        nombres=datos.get("nombres"),
        apellido_paterno=datos.get("apellido_paterno"),
        apellido_materno=datos.get("apellido_materno"),
        dni=dni,
        correo_institucional=datos.get("correo_institucional"),
        especialidad_id=datos.get("especialidad_id"),
        plan_estudios_id=datos.get("plan_estudios_id")
    )

    if error:
        return jsonify({"error": error}), 400

    return jsonify({"mensaje": "Estudiante registrado correctamente", **resultado}), 201