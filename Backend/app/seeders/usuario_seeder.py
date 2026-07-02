from app import db
from app.modelos.usuario import Usuario


def ejecutar():
    usuarios = [
        Usuario(username="estudiante_prueba", password="123456"),
        Usuario(username="docente_prueba", password="123456"),
        Usuario(username="admin_prueba", password="123456"),
    ]

    db.session.add_all(usuarios)
    db.session.commit()

    print("Usuarios creados")