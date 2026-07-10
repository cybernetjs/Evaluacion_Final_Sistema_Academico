# pyrefly: ignore [missing-import]
from flask import Flask, request, jsonify
from marshmallow import Schema, fields, ValidationError, validates, validates_schema, validate
from datetime import date
from app.modelos.oferta_academica import OfertaAcademica
from app.modelos.usuario import Usuario
from app.modelos.docente import Docente
from app.modelos.semestre import Semestre
from app.modulos.matricula.services import MatriculaService

class CrearPeriodoAcademicoSchema(Schema):
    nombre = fields.String(
        required=True,
        error_messages={
            "required": "El periodo academico es un campo obligatorio.",
            "invalid": "El formato del periodo academico no es válido."
        }
    )

    fecha_inicio = fields.Date(
        required=True,
        error_messages={
            "required": "La fecha de inicio es un campo obligatorio.",
            "invalid": "El formato de la fecha de inicio no es válido."
        }
    )

    fecha_fin = fields.Date(
        required=True,
        error_messages={
            "required": "La fecha de fin es un campo obligatorio.",
            "invalid": "El formato de la fecha de fin no es válido."
        }
    )

    @validates("fecha_inicio")
    def validar_fecha_inicio(self, value, **kwargs):
        if value < date.today():
            raise ValidationError("La fecha de inicio debe ser mayor o igual a la fecha actual.")

    @validates_schema
    def validar_fechas(self, data, **kwargs):
        fecha_inicio = data.get("fecha_inicio")
        fecha_fin = data.get("fecha_fin")
        
        if fecha_inicio and fecha_fin and fecha_inicio > fecha_fin:
            raise ValidationError(
                {"fecha_fin": ["La fecha de fin del periodo académico debe ser mayor o igual a la fecha de inicio del periodo académico."]}
            )

    dias_limite_pago = fields.Integer(
        required = True,
        validate=validate.Range(min=1, max=31, error="Los días límite de pago deben estar entre 1 y 31."),
        error_messages={
            "required": "El campo días límite de pago es obligatorio.",
            "invalid": "Debe ingresar un número entero válido."
        }
    )

class ActualizarPeriodoAcademicoSchema(Schema):
    nombre = fields.String(
        required=False,
        error_messages={
            "invalid": "El formato del periodo academico no es válido."
        }
    )

    fecha_inicio = fields.Date(
        required=True,
        error_messages={
            "required": "La fecha de inicio es un campo obligatorio.",
            "invalid": "El formato de la fecha de inicio no es válido."
        }
    )

    fecha_fin = fields.Date(
        required=True,
        error_messages={
            "required": "La fecha de fin es un campo obligatorio.",
            "invalid": "El formato de la fecha de fin no es válido."
        }
    )

    dias_limite_pago = fields.Integer(
        required = False,
        validate=validate.Range(min=1, max=31, error="Los días límite de pago deben estar entre 1 y 31."),
        error_messages={
            "invalid": "Debe ingresar un número entero válido."
        }
    )

    @validates("fecha_inicio")
    def validar_fecha_inicio(self, value, **kwargs):
        periodo_id = self.context.get("id")
        if periodo_id:
            from app.modelos.periodo_academico import PeriodoAcademico
            periodo = PeriodoAcademico.query.get(periodo_id)
            if periodo and periodo.fecha_inicio:
                db_date = periodo.fecha_inicio.date() if hasattr(periodo.fecha_inicio, 'date') else periodo.fecha_inicio
                if db_date == value:
                    return
        if value < date.today():
            raise ValidationError("La fecha de inicio debe ser mayor o igual a la fecha actual.")

    @validates_schema
    def validar_fechas(self, data, **kwargs):
        fecha_inicio = data.get("fecha_inicio")
        fecha_fin = data.get("fecha_fin")
        if fecha_inicio and fecha_fin and fecha_inicio > fecha_fin:
            raise ValidationError(
                {"fecha_fin": ["La fecha de fin del periodo académico debe ser mayor o igual a la fecha de inicio del periodo académico."]}
            )