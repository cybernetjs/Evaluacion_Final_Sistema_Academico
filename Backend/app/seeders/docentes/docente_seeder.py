from app import db
from app.dominio.modelos.docentes.docente import Docente
from app.dominio.modelos.identidad.usuario import Usuario


def ejecutar():
    if Docente.query.first():
        print("Docentes ya existen")
        return

    datos_docentes = [
        ("docente_prueba", "Juan Carlos", "Perez", "Lopez", "12345678", "juan.perez@uncp.edu.pe"),
        ("docente_prueba2", "Rosa Elvira", "Quispe", "Mamani", "23456789", "rosa.quispe@uncp.edu.pe"),
        ("docente_prueba3", "Luis Alberto", "Huaman", "Rojas", "34567890", "luis.huaman@uncp.edu.pe"),
        ("docente_prueba4", "Carmen Isabel", "Torres", "Vega", "45678901", "carmen.torres@uncp.edu.pe"),
    ]

    docentes = []
    for username, nombres, apellido_paterno, apellido_materno, dni, correo in datos_docentes:
        usuario = Usuario.query.filter_by(username=username).first()
        if not usuario:
            print(f"No existe el usuario {username} para crear el docente")
            continue

        docentes.append(Docente(
            usuario_id=usuario.id,
            nombres=nombres,
            apellido_paterno=apellido_paterno,
            apellido_materno=apellido_materno,
            dni=dni,
            correo_institucional=correo,
        ))

    if not docentes:
        print("No hay usuarios docentes para crear docentes")
        return

    db.session.add_all(docentes)
    db.session.commit()

    print(f"Docentes creados: {len(docentes)}")
