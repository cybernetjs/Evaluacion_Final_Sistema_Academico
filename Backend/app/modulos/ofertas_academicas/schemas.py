# pyrefly: ignore [missing-import]
from flask import Flask, request, jsonify
from marshmallow import Schema, fields, ValidationError, validates, validates_schema, validate
from app.modelos.oferta_academica import OfertaAcademica
from app.modelos.usuario import Usuario
from app.modelos.docente import Docente
from app.modelos.semestre import Semestre
from app.modulos.matricula.services import MatriculaService

class CrearOfertaAcademicaSchema(Schema):
    periodo_academico_id = fields.Integer(
        required=True,
        error_messages={
            "required": "El periodo academico es un campo obligatorio.",
            "invalid": "El formato del periodo academico no es válido."
        }
    )

    @validates("periodo_academico_id")
    def validar_periodo_academico_actual(self, value, **kwargs):
        periodo_actual_id = MatriculaService.periodo_actual().id

        if value != periodo_actual_id:
            raise ValidationError("El periodo academico debe ser igual al periodo actual.")

    curso_id = fields.Integer(
        required=True,
        error_messages={
            "required": "El curso es un campo obligatorio.",
            "invalid": "El formato del curso no es válido."
        }
    )
    
    @validates_schema
    def validar_curso_periodo_unico(self, data, **kwargs):
        curso_id = data.get("curso_id")
        periodo_academico_id = data.get("periodo_academico_id")
        
        if OfertaAcademica.query.filter_by(curso_id=curso_id, periodo_academico_id=periodo_academico_id).first():
            raise ValidationError(
                {"curso_id": ["El curso ya está registrado en el periodo academico actual."]}
            )
    
    semestre_id = fields.Integer(
        required = True,
        error_messages = {
            "required" : "El semestre es un campo obligatorio.",
            "invalid" : "El formato del semestre no es válido."
        }
    )

    @validates("semestre_id")
    def validar_semestre_existente(self, value, **kwargs):
        if not Semestre.query.filter_by(id=value).first():
            raise ValidationError("El semestre no existe.")

    cupos = fields.Integer(
        required = True,
        validate = validate.Range(min=1, max=40, error="Los cupos deben ser como mínimo 1 y como máximo de 40."),
        error_messages = {
            "required" : "Los cupos son un campo obligatorio.",
            "invalid" : "El formato de los cupos no es válido."
        }
    )

class ActualizarOfertaAcademicaSchema(Schema):
    cupos = fields.Integer(
        required = True,
        validate = validate.Range(min=1, max=40, error="Los cupos deben ser como mínimo 1 y como máximo de 40."),
        error_messages = {
            "required" : "Los cupos son un campo obligatorio.",
            "invalid" : "El formato de los cupos no es válido."
        }
    )