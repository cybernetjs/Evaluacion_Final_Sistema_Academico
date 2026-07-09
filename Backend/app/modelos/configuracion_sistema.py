from datetime import datetime
from app import db


class ConfiguracionSistema(db.Model):
    __tablename__ = "configuracion_sistema"

    id = db.Column(db.Integer, primary_key=True)
    matricula_habilitada = db.Column(db.Boolean, nullable=False, default=True)
    estado_ciclo = db.Column(db.String(50), nullable=False, default="Inscripcion Abierta")
    actualizado_por_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"))
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    actualizado_por = db.relationship("Usuario")
