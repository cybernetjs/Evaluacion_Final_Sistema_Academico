from datetime import datetime

from flask import jsonify, request, send_file
from flask_jwt_extended import get_jwt_identity
from app.dominio.modelos.estudiantes.estudiante import Estudiante
from app.dominio.modelos.ofertas.periodo_academico import PeriodoAcademico
from app.dominio.modelos.ofertas.oferta_academica import OfertaAcademica
from app.dominio.modelos.matriculas.matricula import Matricula
from app.dominio.modelos.matriculas.estado_matricula import EstadoMatricula
from app.modulos.matriculas.aplicacion.servicios import MatriculaService
from app.modulos.periodos_academicos.aplicacion.servicios import PeriodoAcademicoService
from app.modulos.periodos_academicos.presentacion.esquemas import CrearPeriodoAcademicoSchema, ActualizarPeriodoAcademicoSchema

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