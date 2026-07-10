from datetime import datetime

from flask import jsonify, request, send_file
from flask_jwt_extended import get_jwt_identity
from app.modelos.periodo_academico import PeriodoAcademico
from app.modulos.matricula.services import MatriculaService
from app.modulos.ofertas_academicas.services import OfertaAcademicaService
from app.modulos.ofertas_academicas.schemas import CrearOfertaAcademicaSchema, ActualizarOfertaAcademicaSchema

ofertaAcademicaService = OfertaAcademicaService()

def listar_ofertas():
    ofertas =  ofertaAcademicaService.listar_ofertas()

    return jsonify([
        {
            "id": o.id,
            "periodo_academico_nombre": o.periodo_academico.nombre,
            "periodo_academico_id": o.periodo_academico_id,
            "curso_nombre": o.curso.nombre,
            "curso_id": o.curso_id,
            "semestre_codigo": o.semestre.codigo,
            "semestre_id": o.semestre_id,
            "cupos": o.cupos
        }
        for o in ofertas
    ])

def obtener_oferta(id: int):
    oferta = ofertaAcademicaService.obtener_oferta(id)
    
    return jsonify({
        "id": oferta.id,
        "periodo_academico_nombre": oferta.periodo_academico.nombre,
        "periodo_academico_id": oferta.periodo_academico_id,
        "curso_nombre": oferta.curso.nombre,
        "curso_id": oferta.curso_id,
        "semestre_codigo": oferta.semestre.codigo,
        "semestre_id": oferta.semestre_id,
        "cupos": oferta.cupos
    })

def crear_oferta():
    data = request.get_json()
    
    schema = CrearOfertaAcademicaSchema()
    result = schema.load(data)

    oferta = ofertaAcademicaService.crear_oferta(result)

    return jsonify({
        "message": "Oferta académica creada exitosamente."
    })

def actualizar_oferta(id: int):
    data = request.get_json()
    
    schema = ActualizarOfertaAcademicaSchema()
    result = schema.load(data)

    oferta = ofertaAcademicaService.actualizar_oferta(id, result)

    return jsonify({
        "message": "Oferta académica actualizada exitosamente."
    })

def eliminar_oferta(id: int):
    ofertaAcademicaService.eliminar_oferta(id)

    return jsonify({
        "message": "Oferta académica eliminada exitosamente."
    })
