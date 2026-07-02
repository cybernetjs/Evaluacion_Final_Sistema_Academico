from flask import Blueprint
from app.modulos.auth import controllers

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["POST"])
def login():
    return controllers.login()