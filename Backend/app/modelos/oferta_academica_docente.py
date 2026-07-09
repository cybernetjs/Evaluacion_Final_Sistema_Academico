from app import db


class OfertaAcademicaDocente(db.Model):
    __tablename__ = "oferta_academica_docentes"

    id = db.Column(db.Integer, primary_key=True)
    oferta_academica_id = db.Column(db.Integer, db.ForeignKey("ofertas_academicas.id"))
    docente_id = db.Column(db.Integer, db.ForeignKey("docentes.id"))
    tipo_docente_id = db.Column(db.Integer, db.ForeignKey("tipos_docentes.id"))
    funcion_curso = db.Column(db.String(20))
    horas_asignadas = db.Column(db.SmallInteger)

    oferta_academica = db.relationship("OfertaAcademica", backref="docentes_asignados")
    docente = db.relationship("Docente", backref="ofertas_asignadas")
    tipo_docente = db.relationship("TipoDocente", backref="asignaciones")