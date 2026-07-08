from datetime import datetime, timedelta

from app import db
from app.modelos.hito_academico import HitoAcademico
from app.modelos.periodo_academico import PeriodoAcademico


def ejecutar():
    if HitoAcademico.query.first():
        print("Hitos academicos ya existen")
        return

    periodos = PeriodoAcademico.query.all()
    if not periodos:
        print("No hay periodos academicos para crear hitos")
        return

    tipos_con_offset = [
        ("parcial1", 30),
        ("parcial2", 60),
        ("practica", 75),
        ("final", 90),
    ]

    hitos = [
        HitoAcademico(
            periodo_academico_id=periodo.id,
            tipo_nota=tipo,
            fecha_limite=(periodo.fecha_inicio or datetime.now()) + timedelta(days=offset),
        )
        for periodo in periodos
        for tipo, offset in tipos_con_offset
    ]

    db.session.add_all(hitos)
    db.session.commit()

    print(f"Hitos academicos creados: {len(hitos)}")