from datetime import datetime

from app import db
from app.dominio.modelos.ofertas.periodo_academico import PeriodoAcademico


def ejecutar():
    if PeriodoAcademico.query.first():
        print("Periodos academicos ya existen")
        return

    periodos = [
        PeriodoAcademico(
            nombre="2025-I",
            fecha_inicio=datetime(2025, 3, 1),
            fecha_fin=datetime(2025, 7, 31),
        ),
        PeriodoAcademico(
            nombre="2025-II",
            fecha_inicio=datetime(2025, 8, 1),
            fecha_fin=datetime(2025, 12, 20),
        ),
        PeriodoAcademico(
            nombre="2026-I",
            fecha_inicio=datetime(2026, 3, 1),
            fecha_fin=datetime(2026, 6, 30),
        ),
    ]

    fecha_actual = datetime.now()
    mitad = "I" if fecha_actual.month <= 6 else "II"
    nombre_actual = f"{fecha_actual.year}-{mitad}"

    if nombre_actual not in [p.nombre for p in periodos]:
        if mitad == "I":
            inicio, fin = datetime(fecha_actual.year, 1, 1), datetime(fecha_actual.year, 6, 30)
        else:
            inicio, fin = datetime(fecha_actual.year, 7, 1), datetime(fecha_actual.year, 12, 31)
        periodos.append(PeriodoAcademico(nombre=nombre_actual, fecha_inicio=inicio, fecha_fin=fin))

    db.session.add_all(periodos)
    db.session.commit()

    print("Periodos academicos creados")