import uuid
from datetime import datetime
from app import db


class Certificado(db.Model):
    __tablename__ = "certificados"

    id = db.Column(db.Integer, primary_key=True)
    estudiante_id = db.Column(db.Integer, db.ForeignKey("estudiantes.id"), nullable=False)
    tipo = db.Column(db.String(50), nullable=False)
    codigo_verificacion = db.Column(db.String(36), unique=True, default=lambda: str(uuid.uuid4()))
    autorizado = db.Column(db.Boolean, nullable=False, default=False)
    emitido = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    estudiante = db.relationship("Estudiante", backref="certificados")