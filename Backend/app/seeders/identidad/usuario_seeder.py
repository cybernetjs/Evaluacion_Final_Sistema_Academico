from app import db, bcrypt
from app.dominio.modelos.identidad.usuario import Usuario


def ejecutar():
    if Usuario.query.first():
        print("Usuarios ya existen")
        return

    usuarios = [
        Usuario(
            username="estudiante_prueba",
            password=bcrypt.generate_password_hash("123456").decode("utf-8"),
            rol="estudiante",
        ),
        Usuario(
            username="estudiante_prueba2",
            password=bcrypt.generate_password_hash("123456").decode("utf-8"),
            rol="estudiante",
        ),
        Usuario(
            username="estudiante_prueba3",
            password=bcrypt.generate_password_hash("123456").decode("utf-8"),
            rol="estudiante",
        ),
        Usuario(

            username="estudiante_prueba4",
            password=bcrypt.generate_password_hash("123456").decode("utf-8"),
            rol="estudiante",
        ),
        Usuario(
            username="docente_prueba",
            password=bcrypt.generate_password_hash("123456").decode("utf-8"),
            rol="docente",
        ),
        Usuario(
            username="docente_prueba2",
            password=bcrypt.generate_password_hash("123456").decode("utf-8"),
            rol="docente",
        ),
        Usuario(
            username="docente_prueba3",
            password=bcrypt.generate_password_hash("123456").decode("utf-8"),
            rol="docente",
        ),
        Usuario(
            username="docente_prueba4",
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
