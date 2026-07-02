from app import db, bcrypt
from app.modelos.usuario import Usuario


def ejecutar():
    usuarios = [
        Usuario(
            username="estudiante_prueba",
            password=bcrypt.generate_password_hash("123456").decode("utf-8"),
            rol="estudiante",
        ),
        Usuario(
            username="docente_prueba",
            password=bcrypt.generate_password_hash("123456").decode("utf-8"),
            rol="docente",
        ),
        Usuario(
            username="admin_prueba",
            password=bcrypt.generate_password_hash("123456").decode("utf-8"),
            rol="administrador",
        ),
        Usuario(
            username="direccion_prueba",
            password=bcrypt.generate_password_hash("123456").decode("utf-8"),
            rol="direccion",
        ),
    ]

    db.session.add_all(usuarios)
    db.session.commit()

    print("Usuarios creados")