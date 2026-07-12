import io
import os
import uuid
from datetime import datetime
from marshmallow import ValidationError
from app import db
from app.dominio.modelos.ofertas.oferta_academica import OfertaAcademica
from app.dominio.modelos.ofertas.periodo_academico import PeriodoAcademico
from app.dominio.modelos.academico.curso import Curso
from app.dominio.modelos.academico.semestre import Semestre
from app.modulos.matriculas.aplicacion.servicios import MatriculaService


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