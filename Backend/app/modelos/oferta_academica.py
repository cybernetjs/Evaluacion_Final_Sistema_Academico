from app import db


class OfertaAcademica(db.Model):
    __tablename__ = "ofertas_academicas"

    id = db.Column(db.Integer, primary_key=True)
    periodo_academico_id = db.Column(
        db.Integer, db.ForeignKey("periodos_academicos.id"), nullable=False
    )
    curso_id = db.Column(db.Integer, db.ForeignKey("cursos.id"), nullable=False)
    semestre_id = db.Column(db.Integer, db.ForeignKey("semestres.id"), nullable=False)
    cupos = db.Column(db.SmallInteger, default=40)

    __table_args__ = (
        db.UniqueConstraint("periodo_academico_id", "curso_id", "semestre_id"),
    )

    periodo_academico = db.relationship("PeriodoAcademico", backref="ofertas")
    curso = db.relationship("Curso", backref="ofertas")
    semestre = db.relationship("Semestre", backref="ofertas")