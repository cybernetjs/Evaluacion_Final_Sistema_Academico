from datetime import time

from app import db
from app.modelos.oferta_academica import OfertaAcademica
from app.modelos.oferta_academica_horario import OfertaAcademicaHorario


def ejecutar():
    if OfertaAcademicaHorario.query.first():
        print("Horarios de oferta academica ya existen")
        return

    oferta = OfertaAcademica.query.first()
    if not oferta:
        print("No hay oferta academica para crear horarios")
        return

    horarios = [
        OfertaAcademicaHorario(oferta_academica_id=oferta.id, dia=1, hora_inicio=time(8, 0), hora_fin=time(10, 0)),
        OfertaAcademicaHorario(oferta_academica_id=oferta.id, dia=3, hora_inicio=time(8, 0), hora_fin=time(10, 0)),
    ]

    db.session.add_all(horarios)
    db.session.commit()

    print("Horarios de oferta academica creados")
