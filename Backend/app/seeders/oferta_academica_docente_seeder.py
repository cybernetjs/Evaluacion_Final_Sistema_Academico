from app import db
from app.modelos.docente import Docente
from app.modelos.oferta_academica import OfertaAcademica
from app.modelos.oferta_academica_docente import OfertaAcademicaDocente
from app.modelos.tipo_docente import TipoDocente


def ejecutar():
    if OfertaAcademicaDocente.query.first():
        print("Asignaciones de oferta academica a docentes ya existen")
        return

    oferta = OfertaAcademica.query.first()
    docente = Docente.query.first()
    tipo_docente = TipoDocente.query.filter_by(nombre="Nombrado").first()

    if not oferta or not docente or not tipo_docente:
        print("No hay datos suficientes para asignar docente a oferta academica")
        return

    asignacion = OfertaAcademicaDocente(
        oferta_academica_id=oferta.id,
        docente_id=docente.id,
        tipo_docente_id=tipo_docente.id,
    )

    db.session.add(asignacion)
    db.session.commit()

    print("Asignaciones de oferta academica a docentes creadas")