from app import db
from app.modelos.curso import Curso
from app.modelos.oferta_academica import OfertaAcademica
from app.modelos.periodo_academico import PeriodoAcademico
from app.modelos.semestre import Semestre


def ejecutar():
    if OfertaAcademica.query.first():
        print("Ofertas academicas ya existen")
        return

    periodo = PeriodoAcademico.query.first()
    curso = Curso.query.first()
    semestre = Semestre.query.first()

    if not periodo or not curso or not semestre:
        print("No hay periodo, curso o semestre suficiente para crear ofertas academicas")
        return

    oferta = OfertaAcademica(
        periodo_academico_id=periodo.id,
        curso_id=curso.id,
        semestre_id=semestre.id,
        cupos=40,
    )

    db.session.add(oferta)
    db.session.commit()

    print("Ofertas academicas creadas")