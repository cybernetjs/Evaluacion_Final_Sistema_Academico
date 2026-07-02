from flask import jsonify
from app.modelos.facultad import Facultad
from app.modelos.especialidad import Especialidad
from app.modelos.plan_de_estudios import PlanDeEstudios
from app.modelos.semestre import Semestre


def listar_facultades():
    facultades = Facultad.query.all()
    return jsonify([
        {"id": f.id, "nombre": f.nombre}
        for f in facultades
    ])


def listar_especialidades():
    especialidades = Especialidad.query.all()
    return jsonify([
        {
            "id": e.id,
            "nombre": e.nombre,
            "facultad_id": e.facultad_id
        }
        for e in especialidades
    ])


def listar_planes_estudio():
    planes = PlanDeEstudios.query.all()
    return jsonify([
        {
            "id": p.id,
            "especialidad_id": p.especialidad_id,
            "anio_creacion": p.anio_creacion,
            "vigente": p.vigente
        }
        for p in planes
    ])


def listar_semestres():
    semestres = Semestre.query.all()
    return jsonify([
        {"id": s.id, "codigo": s.codigo}
        for s in semestres
    ])