from app import db


class Acta(db.Model):
    __tablename__ = "actas"

    id = db.Column(db.Integer, primary_key=True)
    oferta_academica_id = db.Column(
        db.Integer, db.ForeignKey("ofertas_academicas.id"), nullable=False, unique=True
    )
    estado = db.Column(db.String(20), nullable=False, default="Abierta", index=True)
    notas_publicadas = db.Column(db.Boolean, nullable=False, default=False)
    hash_auditoria = db.Column(db.String(64))
    fecha_cierre = db.Column(db.DateTime)

    oferta_academica = db.relationship("OfertaAcademica", backref="acta", uselist=False)