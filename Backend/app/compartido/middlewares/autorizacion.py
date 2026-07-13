from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt


def rol_requerido(*roles_permitidos, recurso=None, accion=None):
    def decorador(funcion):
        @wraps(funcion)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            rol_usuario = claims.get("rol")

            if recurso and accion:
                from app.dominio.modelos.administracion.permiso_rol import PermisoRol

                campo = f"puede_{accion}"
                permiso = PermisoRol.query.filter_by(rol=rol_usuario, recurso=recurso).first()

                if not permiso or not getattr(permiso, campo, False):
                    return jsonify({"error": "No tienes permiso para esta acción"}), 403

                return funcion(*args, **kwargs)

            if rol_usuario not in roles_permitidos:
                return jsonify({"error": "No tienes permiso para esta acción"}), 403

            return funcion(*args, **kwargs)
        return wrapper
    return decorador