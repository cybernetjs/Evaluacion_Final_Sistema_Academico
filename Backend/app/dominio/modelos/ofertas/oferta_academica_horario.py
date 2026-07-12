from app import db


class OfertaAcademicaHorario(db.Model):
    __tablename__ = "oferta_academica_horarios"

    id = db.Column(db.Integer, primary_key=True)
    oferta_academica_id = db.Column(db.Integer, db.ForeignKey("ofertas_academicas.id"))
    dia = db.Column(db.Integer)
    hora_inicio = db.Column(db.Time)
    hora_fin = db.Column(db.Time)
    aula = db.Column(db.String(100))
    estado = db.Column(db.String(20), default="Activo")

    oferta_academica = db.relationship("OfertaAcademica", backref="horarios")