from datetime import time

from app import db
from app.dominio.modelos.ofertas.oferta_academica import OfertaAcademica
from app.dominio.modelos.ofertas.oferta_academica_docente import OfertaAcademicaDocente
from app.dominio.modelos.ofertas.oferta_academica_horario import OfertaAcademicaHorario

BLOQUES_TEORICO = [
    (1, time(8, 0), time(10, 0)),
    (2, time(10, 0), time(12, 0)),
    (3, time(8, 0), time(10, 0)),
    (4, time(10, 0), time(12, 0)),
]

BLOQUES_PRACTICO = [
    (1, time(14, 0), time(16, 0)),
    (2, time(14, 0), time(16, 0)),
    (3, time(14, 0), time(16, 0)),
    (4, time(14, 0), time(16, 0)),
]


def ejecutar():
    if OfertaAcademicaHorario.query.first():
        print("Horarios de oferta academica ya existen")
        return

    ofertas = OfertaAcademica.query.order_by(OfertaAcademica.id).all()
    if not ofertas:
        print("No hay ofertas academicas para crear horarios")
        return

    horarios = []
    for indice, oferta in enumerate(ofertas):
        funciones = {
            a.funcion_curso
            for a in OfertaAcademicaDocente.query.filter_by(oferta_academica_id=oferta.id).all()
        }

        if "Teorico" in funciones or not funciones:
            dia, inicio, fin = BLOQUES_TEORICO[indice % len(BLOQUES_TEORICO)]
            horarios.append(OfertaAcademicaHorario(
                oferta_academica_id=oferta.id,
                dia=dia,
                hora_inicio=inicio,
                hora_fin=fin,
                aula=f"Aula {201 + (indice % 6)}",
                funcion_curso="Teorico" if funciones else None,
            ))

        if "Practico" in funciones:
            dia, inicio, fin = BLOQUES_PRACTICO[indice % len(BLOQUES_PRACTICO)]
            horarios.append(OfertaAcademicaHorario(
                oferta_academica_id=oferta.id,
                dia=dia,
                hora_inicio=inicio,
                hora_fin=fin,
                aula=f"Laboratorio {1 + (indice % 3)}",
                funcion_curso="Practico",
            ))

    db.session.add_all(horarios)
    db.session.commit()

    print(f"Horarios de oferta academica creados: {len(horarios)}")
