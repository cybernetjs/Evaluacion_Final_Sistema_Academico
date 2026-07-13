from app import db
from app.dominio.modelos.academico.especialidad import Especialidad
from app.dominio.modelos.estudiantes.estudiante import Estudiante
from app.dominio.modelos.identidad.usuario import Usuario


def ejecutar():
    if Estudiante.query.first():
        print("Estudiantes ya existen")
        return

    especialidad = Especialidad.query.filter_by(nombre="Ingeniería de Software").first()
    if not especialidad:
        especialidad = Especialidad.query.first()

    if not especialidad:
        print("No existe una especialidad para crear estudiantes")
        return

    datos_estudiantes = [
        ("estudiante_prueba", "Maria Fernanda", "Gomez", "Vargas", "87654321", "maria.gomez@uncp.edu.pe"),
        ("estudiante_prueba2", "Diego Alonso", "Ramirez", "Castillo", "76543210", "diego.ramirez@uncp.edu.pe"),
        ("estudiante_prueba3", "Valeria Nicole", "Flores", "Cardenas", "65432109", "valeria.flores@uncp.edu.pe"),
        ("estudiante_prueba4", "Renato Sebastian", "Quispe", "Huaman", "54321098", "renato.quispe@uncp.edu.pe"),
    ]

    estudiantes = []
    for username, nombres, apellido_paterno, apellido_materno, dni, correo in datos_estudiantes:
        usuario = Usuario.query.filter_by(username=username).first()
        if not usuario:
            print(f"No existe el usuario {username} para crear el estudiante")
            continue

        estudiantes.append(Estudiante(
            usuario_id=usuario.id,
            especialidad_id=especialidad.id,
            nombres=nombres,
            apellido_paterno=apellido_paterno,
            apellido_materno=apellido_materno,
            dni=dni,
            correo_institucional=correo,
        ))

    if not estudiantes:
        print("No hay usuarios estudiantes para crear estudiantes")
        return

    db.session.add_all(estudiantes)
    db.session.commit()

    print(f"Estudiantes creados: {len(estudiantes)}")
