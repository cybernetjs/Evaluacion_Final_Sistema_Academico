from flask import jsonify, request
from flask_jwt_extended import get_jwt_identity
from app import bcrypt
from app import db
from app.modelos.docente import Docente
from app.modelos.usuario import Usuario
from app.modulos.docentes.services import DocenteService
from app.modulos.docentes.schemas import RegistroDocenteSchema, ActualizarDocenteSchema

docenteService = DocenteService()

def listar_docentes()->jsonify:  #:
    '''
        Función especializada en listar todos los docentes del sistema
        
        @return jsonify -> list[dict[str | int]]
    '''

    docentes = docenteService.listar_docentes()

    return jsonify([
        {
            "id": d.id, 
            "nombres": d.nombres,
            "apellido_paterno": d.apellido_paterno,
            "apellido_materno": d.apellido_materno,
            "correo_institucional": d.correo_institucional,
            "dni": d.dni
        }
        for d in docentes
    ])

def obtener_docente(id: int | None)->jsonify:
    '''
        Función especializada en obtener un docente por id
        
        @param id: id del docente
        @return jsonify -> list[dict[str | int]]
    '''

    docente = docenteService.obtener_docente(id)
    
    return jsonify({
        "id": docente.id,
        "nombres": docente.nombres,
        "apellido_paterno": docente.apellido_paterno,
        "apellido_materno": docente.apellido_materno,
        "correo_institucional": docente.correo_institucional,
        "dni": docente.dni
    })

def registrar_docente():
    data = request.get_json()

    schema = RegistroDocenteSchema()
    result = schema.load(data)

    docente = docenteService.registrar_docente(result)

    return jsonify({
        "mensaje": "Docente registrado correctamente",
        "usuario_id": docente.usuario_id,
        "docente_id": docente.id,
    }), 201

def actualizar_docente(id):
    data = request.get_json()

    schema = ActualizarDocenteSchema()
    schema.context = {"id": id}
    result = schema.load(data)

    docente = docenteService.actualizar_docente(id, result)

    return jsonify({
        "mensaje": "Docente actualizado correctamente",
        "docente_id": docente.id,
    }), 200

def eliminar_docente(id):
    docente = docenteService.eliminar_docente(id)

    return jsonify({
        "mensaje": "Docente eliminado correctamente",
    }), 200