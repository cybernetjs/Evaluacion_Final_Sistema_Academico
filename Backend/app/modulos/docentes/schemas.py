# pyrefly: ignore [missing-import]
from flask import Flask, request, jsonify
from marshmallow import Schema, fields, ValidationError, validates, validate
from app.modelos.usuario import Usuario
from app.modelos.docente import Docente

class RegistroDocenteSchema(Schema):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    username = fields.Str(
        required=True,
        validate=validate.Length(max=100, error="El nombre de usuario debe tener un máximo de 100 caracteres."),
        error_messages={
            "required": "El nombre de usuario es un campo obligatorio.",
            "invalid": "El formato del nombre de usuario no es válido."
        }
    )

    @validates("username")
    def validar_username_unico(self, value, **kwargs):
        if Usuario.query.filter_by(username=value).first():
            raise ValidationError("El nombre de usuario ya está registrado.")

    correo_institucional = fields.Email(
        required=True,
        error_messages={
            "required": "El correo institucional es un campo obligatorio.",
            "invalid": "El formato del correo institucional no es válido."
        }
    )
    
    @validates("correo_institucional")
    def validar_correo_unico(self, value, **kwargs):
        if Docente.query.filter_by(correo_institucional=value).first():
            raise ValidationError("El correo institucional ya está registrado.")
    
    @validates("correo_institucional")
    def validar_dominio_institucional(self, value, **kwargs):
        if not value.endswith("@uncp.edu.pe"):
            raise ValidationError("El correo debe pertenecer al dominio @uncp.edu.pe.")
    
    nombres = fields.Str(
        required=True,
        validate=validate.Length(max=100, error="El nombre debe tener un máximo de 100 caracteres."),
        error_messages={
            "required": "El nombre es un campo obligatorio.",
            "invalid": "El formato del nombre no es válido."
        }
    )
    apellido_paterno = fields.Str(
        required=True,
        validate=validate.Length(max=100, error="El apellido paterno debe tener un máximo de 100 caracteres."),
        error_messages={
            "required": "El apellido paterno es un campo obligatorio.",
            "invalid": "El formato del apellido paterno no es válido."
        }
    )
    apellido_materno = fields.Str(
        required=True,
        validate=validate.Length(max=100, error="El apellido materno debe tener un máximo de 100 caracteres."),
        error_messages={
            "required": "El apellido materno es un campo obligatorio.",
            "invalid": "El formato del apellido materno no es válido."
        }
    )

    dni = fields.Str(
        required=True,
        validate=validate.Length(min=8, max=8, error="El DNI debe tener 8 caracteres."),
        error_messages={
            "required": "El DNI es un campo obligatorio.",
            "invalid": "El formato del DNI no es válido."
        }
    )

    @validates("dni")
    def validar_dni_unico(self, value, **kwargs):
        if Docente.query.filter_by(dni=value).first():
            raise ValidationError("El DNI ya está registrado.")

class ActualizarDocenteSchema(Schema):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    username = fields.Str(
        required=False,
        validate=validate.Length(max=100, error="El nombre de usuario debe tener un máximo de 100 caracteres."),
        error_messages={
            "required": "El nombre de usuario es un campo obligatorio.",
            "invalid": "El formato del nombre de usuario no es válido."
        }
    )

    @validates("username")
    def validar_username_unico(self, value, **kwargs):
        docente_id = self.context.get("id", None)
        query = Usuario.query.filter_by(username=value)
        if docente_id:
            docente = Docente.query.get(docente_id)
            if docente and docente.usuario_id:
                query = query.filter(Usuario.id != docente.usuario_id)
        if value and query.first():
            raise ValidationError("El nombre de usuario ya está registrado.")

    nombres = fields.Str(
        required=False,
        validate=validate.Length(max=100, error="El nombre debe tener un máximo de 100 caracteres."),
        error_messages={
            "invalid": "El formato del nombre no es válido."
        }
    )

    apellido_paterno = fields.Str(
        required=False,
        validate=validate.Length(max=100, error="El apellido paterno debe tener un máximo de 100 caracteres."),
        error_messages={
            "invalid": "El formato del apellido paterno no es válido."
        }
    )

    apellido_materno = fields.Str(
        required=False,
        validate=validate.Length(max=100, error="El apellido materno debe tener un máximo de 100 caracteres."),
        error_messages={
            "invalid": "El formato del apellido materno no es válido."
        }
    )

    correo_institucional = fields.Email(
        required=False,
        error_messages={
            "invalid": "El formato del correo institucional no es válido."
        }
    )
    
    @validates("correo_institucional")
    def validar_correo_unico(self, value, **kwargs):
        docente_id = self.context.get("id", None)
        
        query = Docente.query.filter_by(correo_institucional=value).filter(Docente.id != docente_id)

        if value and query.first():
            raise ValidationError("El correo institucional ya está registrado.")
    
    @validates("correo_institucional")
    def validar_dominio_institucional(self, value, **kwargs):
        if value and not value.endswith("@uncp.edu.pe"):
            raise ValidationError("El correo debe pertenecer al dominio @uncp.edu.pe.")
    
    dni = fields.Str(
        required=False,
        validate=validate.Length(min=8, max=8, error="El DNI debe tener 8 caracteres."),
        error_messages={
            "invalid": "El formato del DNI no es válido."
        }
    )

    @validates("dni")
    def validar_dni_unico(self, value, **kwargs):
        docente_id = self.context.get("id", None)

        query = Docente.query.filter_by(dni=value)
        
        if docente_id:
            query = query.filter(Docente.id != docente_id)
        
        if value and query.first():
            raise ValidationError("El DNI ya está registrado.")