import io
import os
import uuid
from datetime import datetime
from marshmallow import ValidationError
from app import db
from app.modelos.oferta_academica import OfertaAcademica
from app.modelos.periodo_academico import PeriodoAcademico
from app.modelos.curso import Curso
from app.modelos.semestre import Semestre
from app.modulos.matricula.services import MatriculaService


class OfertaAcademicaService:
    def listar_ofertas(self):
        periodo = MatriculaService.periodo_actual()
        ofertas = OfertaAcademica.query.filter_by(periodo_academico_id=periodo.id).all()

        return ofertas
    
    def obtener_oferta(self, id:int):
        oferta = OfertaAcademica.query.get_or_404(id, description="Oferta académica no encontrada")
        
        return oferta

    def crear_oferta(self, data:dict):
        oferta = OfertaAcademica.query.filter_by(periodo_academico_id=data["periodo_academico_id"]).filter_by(curso_id=data["curso_id"]).first()
        
        if oferta:
            raise ValidationError("La oferta académica que intenta agregar ya existe.")

        oferta_academica = OfertaAcademica(**data)
        db.session.add(oferta_academica)
        db.session.commit()

        return oferta_academica

    def actualizar_oferta(self, id:int, data:dict):
        oferta = OfertaAcademica.query.get_or_404(id, description="Oferta académica no encontrada")

        OfertaAcademica.query.filter_by(id=id).update(data)
        db.session.commit()

        return True

    def eliminar_oferta(self, id:int):
        oferta = OfertaAcademica.query.get_or_404(id, description="Oferta académica no encontrada")

        db.session.delete(oferta)
        db.session.commit()

        return True