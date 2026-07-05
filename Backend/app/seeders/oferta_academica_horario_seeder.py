from datetime import time

from app import db
from app.modelos.oferta_academica import OfertaAcademica
from app.modelos.oferta_academica_horario import OfertaAcademicaHorario

BLOQUES = [
    [(1, time(8, 0), time(10, 0)), (3, time(8, 0), time(10, 0))],   
    [(2, time(10, 0), time(12, 0)), (4, time(10, 0), time(12, 0))],  
    [(1, time(14, 0), time(16, 0)), (3, time(14, 0), time(16, 0))],  
]


def ejecutar():
    if OfertaAcademicaHorario.query.first():
        print("Horarios de oferta academica ya existen")
        return

    ofertas = OfertaAcademica.query.all()
    if not ofertas:
        print("No hay ofertas academicas para crear horarios")
        return

    horarios = []
    for i, oferta in enumerate(ofertas):
        bloque = BLOQUES[i % len(BLOQUES)]  # va rotando los bloques para no cruzar horarios
        for dia, inicio, fin in bloque:
            horarios.append(
                OfertaAcademicaHorario(
                    oferta_academica_id=oferta.id, dia=dia, hora_inicio=inicio, hora_fin=fin
                )
            )

    db.session.add_all(horarios)
    db.session.commit()

    print(f"Horarios de oferta academica creados: {len(horarios)}")