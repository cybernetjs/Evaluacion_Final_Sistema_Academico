from app import db
from app.dominio.modelos.academico.especialidad import Especialidad
from app.dominio.modelos.estudiantes.estudiante import Estudiante
from app.dominio.modelos.identidad.usuario import Usuario


def ejecutar():
    if Estudiante.query.first():
        print("Estudiantes ya existen")
        return

    usuario = Usuario.query.filter_by(username="estudiante_prueba").first()
    especialidad = Especialidad.query.first()

    if not usuario:
        print("No existe el usuario estudiante_prueba para crear estudiantes")
        return

    if not especialidad:
        print("No existe una especialidad para crear estudiantes")
        return

    estudiante = Estudiante(
        usuario_id=usuario.id,
        especialidad_id=especialidad.id,
        nombres="Maria Fernanda",
        apellido_paterno="Gomez",
        apellido_materno="Vargas",
        dni="87654321",
        correo_institucional="maria.gomez@uncp.edu.pe",
    )

    db.session.add(estudiante)
    db.session.commit()

    print("Estudiantes creados")