from app import db
from app.modelos.estado_curso import EstadoCurso
from app.modelos.matricula import Matricula
from app.modelos.matricula_detalle import MatriculaDetalle
from app.modelos.oferta_academica import OfertaAcademica


def ejecutar():
    if MatriculaDetalle.query.first():
        print("Detalles de matricula ya existen")
        return

    matricula = Matricula.query.first()
    oferta = OfertaAcademica.query.first()
    estado_curso = EstadoCurso.query.filter_by(nombre="Aprobado").first()

    if not matricula or not oferta or not estado_curso:
        print("No hay datos suficientes para crear detalles de matricula")
        return

    detalle = MatriculaDetalle(
        matricula_id=matricula.id,
        oferta_academica_id=oferta.id,
        nota_final=15.50,
        estado_curso_id=estado_curso.id,
    )

    db.session.add(detalle)
    db.session.commit()

    print("Detalles de matricula creados")