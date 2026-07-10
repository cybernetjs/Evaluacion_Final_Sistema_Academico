from datetime import datetime

from flask import jsonify, request, send_file
from flask_jwt_extended import get_jwt_identity
from app.modelos.estudiante import Estudiante
from app.modelos.periodo_academico import PeriodoAcademico
from app.modelos.oferta_academica import OfertaAcademica
from app.modelos.matricula import Matricula
from app.modelos.estado_matricula import EstadoMatricula
from app.modulos.matricula.services import MatriculaService
from app.modulos.periodos_academicos.services import PeriodoAcademicoService
from app.modulos.periodos_academicos.schemas import CrearPeriodoAcademicoSchema, ActualizarPeriodoAcademicoSchema

periodoAcademicoService = PeriodoAcademicoService()

def listar_periodos():
    periodos = periodoAcademicoService.listar_periodos()

    return jsonify([
        {
            "id": p.id,
            "nombre": p.nombre,
            "fecha_inicio": p.fecha_inicio,
            "fecha_fin": p.fecha_fin
        }
        for p in periodos
    ])

def obtener_periodo(id:int):
    periodo = periodoAcademicoService.obtener_periodo(id)

    return jsonify({
        "id": periodo.id,
        "nombre": periodo.nombre,
        "fecha_inicio": periodo.fecha_inicio,
        "fecha_fin": periodo.fecha_fin
    })

def periodo_actual():
    periodo = MatriculaService.periodo_actual()
    return jsonify({
        "id": periodo.id,
        "nombre": periodo.nombre,
        "fecha_inicio": periodo.fecha_inicio,
        "fecha_fin": periodo.fecha_fin
    })

def crear_periodo():
    data = request.get_json()
    
    schema = CrearPeriodoAcademicoSchema()
    result = schema.load(data)

    periodo = periodoAcademicoService.crear_periodo(result)

    return jsonify({
        "message": "Periodo académico creado exitosamente."
    })

def actualizar_periodo(id: int):
    data = request.get_json()
    
    schema = ActualizarPeriodoAcademicoSchema()
    schema.context = {"id": id}
    result = schema.load(data)

    periodoAcademicoService.actualizar_periodo(id, result)

    return jsonify({
        "message": "Periodo académico actualizado exitosamente."
    })

def eliminar_periodo(id: int):
    periodoAcademicoService.eliminar_periodo(id)

    return jsonify({
        "message": "Periodo académico eliminado exitosamente."
    })