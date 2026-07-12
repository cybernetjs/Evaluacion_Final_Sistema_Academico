from app import db
from app.dominio.modelos.docentes.docente import Docente
from app.dominio.modelos.ofertas.oferta_academica import OfertaAcademica
from app.dominio.modelos.ofertas.oferta_academica_docente import OfertaAcademicaDocente
from app.dominio.modelos.docentes.tipo_docente import TipoDocente


def ejecutar():
    if OfertaAcademicaDocente.query.first():
        print("Asignaciones de oferta academica a docentes ya existen")
        return

    ofertas = OfertaAcademica.query.all()
    docente = Docente.query.first()
    tipo_docente = TipoDocente.query.filter_by(nombre="Nombrado").first()

    if not ofertas or not docente or not tipo_docente:
        print("No hay datos suficientes para asignar docente a oferta academica")
        return

    asignaciones = []
    for oferta in ofertas:
        curso = oferta.curso
        if curso.horas_lectivas:
            asignaciones.append(OfertaAcademicaDocente(
                oferta_academica_id=oferta.id,
                docente_id=docente.id,
                tipo_docente_id=tipo_docente.id,
                funcion_curso="Teorico",
                horas_asignadas=curso.horas_lectivas,
            ))
        if curso.horas_practicas:
            asignaciones.append(OfertaAcademicaDocente(
                oferta_academica_id=oferta.id,
                docente_id=docente.id,
                tipo_docente_id=tipo_docente.id,
                funcion_curso="Practico",
                horas_asignadas=curso.horas_practicas,
            ))

    db.session.add_all(asignaciones)
    db.session.commit()

    print(f"Asignaciones de oferta academica a docentes creadas: {len(asignaciones)}")