from marshmallow import Schema, fields, ValidationError, validates, validate
from app.modelos.curso import Curso

class RegistroCursoSchema(Schema):
    nombre = fields.Str(
        required=True,
        validate=validate.Length(max=100, error="El nombre del curso debe tener un máximo de 100 caracteres."),
        error_messages={
            "required": "El nombre del curso es un campo obligatorio.",
            "invalid": "El formato del nombre no es válido."
        }
    )
    codigo = fields.Str(
        required=True,
        validate=validate.Length(max=20, error="El código del curso debe tener un máximo de 20 caracteres."),
        error_messages={
            "required": "El código del curso es un campo obligatorio.",
            "invalid": "El formato del código no es válido."
        }
    )
    
    @validates("codigo")
    def validar_codigo_unico(self, value, **kwargs):
        if value and Curso.query.filter_by(codigo=value).first():
            raise ValidationError("El código del curso ya está registrado.")

    creditos = fields.Int(
        required=True,
        validate=validate.Range(min=0, error="Los créditos deben ser un valor positivo o cero."),
        error_messages={
            "required": "Los créditos son un campo obligatorio.",
            "invalid": "El valor de los créditos debe ser un número entero."
        }
    )
    horas_lectivas = fields.Int(
        required=True,
        validate=validate.Range(min=1, error="Las horas lectivas deben ser un valor positivo."),
        error_messages={
            "required": "Las horas lectivas son un campo obligatorio.",
            "invalid": "El valor de las horas lectivas debe ser un número entero."
        }
    )
    horas_practicas = fields.Int(
        required=True,
        validate=validate.Range(min=1, error="Las horas prácticas deben ser un valor positivo."),
        error_messages={
            "required": "Las horas prácticas son un campo obligatorio.",
            "invalid": "El valor de las horas prácticas debe ser un número entero."
        }
    )


class ActualizarCursoSchema(Schema):
    nombre = fields.Str(
        required=False,
        validate=validate.Length(max=100, error="El nombre del curso debe tener un máximo de 100 caracteres."),
        error_messages={
            "invalid": "El formato del nombre no es válido."
        }
    )
    codigo = fields.Str(
        required=False,
        validate=validate.Length(max=20, error="El código del curso debe tener un máximo de 20 caracteres."),
        error_messages={
            "invalid": "El formato del código no es válido."
        }
    )
    
    @validates("codigo")
    def validar_codigo_unico(self, value, **kwargs):
        curso_id = self.context.get("id", None)
        query = Curso.query.filter_by(codigo=value)
        if curso_id:
            query = query.filter(Curso.id != curso_id)
        if value and query.first():
            raise ValidationError("El código del curso ya está registrado.")

    creditos = fields.Int(
        required=False,
        validate=validate.Range(min=0, error="Los créditos deben ser un valor positivo o cero."),
        error_messages={
            "invalid": "El valor de los créditos debe ser un número entero."
        }
    )
    horas_lectivas = fields.Int(
        required=False,
        validate=validate.Range(min=0, error="Las horas lectivas deben ser un valor positivo o cero."),
        error_messages={
            "invalid": "El valor de las horas lectivas debe ser un número entero."
        }
    )
    horas_practicas = fields.Int(
        required=False,
        validate=validate.Range(min=0, error="Las horas prácticas deben ser un valor positivo o cero."),
        error_messages={
            "invalid": "El valor de las horas prácticas debe ser un número entero."
        }
    )
