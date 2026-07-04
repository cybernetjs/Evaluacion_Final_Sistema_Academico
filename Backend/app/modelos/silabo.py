from datetime import datetime
from app import db


class Silabo(db.Model):
    __tablename__ = "silabos"

    id = db.Column(db.Integer, primary_key=True)
    oferta_academica_id = db.Column(db.Integer, db.ForeignKey("ofertas_academicas.id"), nullable=False, unique=True)
    nombre_archivo = db.Column(db.String(255), nullable=False)
    ruta_archivo = db.Column(db.String(500), nullable=False)
    subido_en = db.Column(db.DateTime, default=datetime.utcnow)

    oferta_academica = db.relationship("OfertaAcademica", backref="silabo", uselist=False)