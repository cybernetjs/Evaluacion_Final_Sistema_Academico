from flask import Blueprint
from app.modulos.autenticacion.presentacion import controladores
from app.compartido.middlewares.autorizacion import rol_requerido

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["POST"])
def login():
    return controladores.login()

@auth_bp.route("/logout", methods=["POST"])
def logout():
    return controladores.logout()


@auth_bp.route("/registrar", methods=["POST"])
@rol_requerido("administrador")
def registrar():
    return controladores.registrar()