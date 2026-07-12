from marshmallow import ValidationError
from app import db
from app.dominio.modelos.ofertas.periodo_academico import PeriodoAcademico

class PeriodoAcademicoService:
    def listar_periodos(self):
        periodos = PeriodoAcademico.query.order_by(PeriodoAcademico.fecha_inicio.desc()).all()
        return periodos
    
    def periodo_actual(self):
        from app.modulos.matriculas.aplicacion.servicios import MatriculaService
        return MatriculaService.periodo_actual()
    
    def obtener_periodo(self, id: int):
        periodo = PeriodoAcademico.query.get_or_404(id, description="Periodo académico no encontrado")
        return periodo

    def crear_periodo(self, data:dict):
        if PeriodoAcademico.query.filter_by(nombre=data.get("nombre")).first():
            raise ValidationError("Ya existe un periodo académico con este nombre.")
        
        periodo_academico = PeriodoAcademico(
            **data
        )
        
        db.session.add(periodo_academico)
        db.session.commit()
        
        return periodo_academico
    
    def actualizar_periodo(self, id:int, data:dict):
        periodo_academico = PeriodoAcademico.query.get_or_404(id, description="Periodo académico no encontrado")
        
        PeriodoAcademico.query.filter_by(id=id).update(data)
        db.session.commit()
        
        return True

    def eliminar_periodo(self, id:int):
        periodo_academico = PeriodoAcademico.query.get_or_404(id, description="Periodo académico no encontrado")
        
        db.session.delete(periodo_academico)
        db.session.commit()
        
        return True