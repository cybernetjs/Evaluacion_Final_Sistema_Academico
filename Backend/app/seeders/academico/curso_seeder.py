from app import db
from app.dominio.modelos.academico.curso import Curso


def ejecutar():
    if Curso.query.first():
        print("Cursos ya existen")
        return

    cursos = [
        Curso(nombre="Programacion I", codigo="PROG1", creditos=4, horas_lectivas=4, horas_practicas=2),
        Curso(nombre="Matematica Basica", codigo="MAT1", creditos=4, horas_lectivas=4, horas_practicas=1),
        Curso(nombre="Comunicacion", codigo="COM1", creditos=3, horas_lectivas=3, horas_practicas=0),
        Curso(nombre="Introduccion a la Ingenieria", codigo="ING1", creditos=2, horas_lectivas=2, horas_practicas=0),

        Curso(nombre="Programacion II", codigo="PROG2", creditos=4, horas_lectivas=3, horas_practicas=2),
        Curso(nombre="Base de Datos I", codigo="BD1", creditos=4, horas_lectivas=3, horas_practicas=2),
        Curso(nombre="Matematica Discreta", codigo="MAT2", creditos=4, horas_lectivas=4, horas_practicas=0),
        Curso(nombre="Arquitectura de Computadoras", codigo="ARQ1", creditos=3, horas_lectivas=3, horas_practicas=1),

        Curso(nombre="Estructura de Datos", codigo="EDA1", creditos=4, horas_lectivas=3, horas_practicas=2),
        Curso(nombre="Redes de Computadoras", codigo="RED1", creditos=3, horas_lectivas=3, horas_practicas=1),
        Curso(nombre="Sistemas Operativos", codigo="SO1", creditos=4, horas_lectivas=3, horas_practicas=1),
        Curso(nombre="Ciberseguridad", codigo="CIBER1", creditos=5, horas_lectivas=3, horas_practicas=2),
    ]

    db.session.add_all(cursos)
    db.session.commit()

    print(f"Cursos creados: {len(cursos)}")
