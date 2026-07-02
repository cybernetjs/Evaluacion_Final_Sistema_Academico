from app import db
from app.modelos.docente import Docente
from app.modelos.usuario import Usuario


def ejecutar():
    if Docente.query.first():
        print("Docentes ya existen")
        return

    usuario = Usuario.query.filter_by(username="docente_prueba").first()
    if not usuario:
        print("No existe el usuario docente_prueba para crear docentes")
        return

    docente = Docente(
        usuario_id=usuario.id,
        nombres="Juan Carlos",
        apellido_paterno="Perez",
        apellido_materno="Lopez",
        correo_institucional="juan.perez@universidad.edu.pe",
    )

    db.session.add(docente)
    db.session.commit()

    print("Docentes creados")