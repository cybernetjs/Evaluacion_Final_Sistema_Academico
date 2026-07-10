from flask import jsonify, request
from app.modulos.cursos.services import CursosService
from app.modulos.cursos.schemas import RegistroCursoSchema, ActualizarCursoSchema

def listar_cursos():
    cursos = CursosService.listar_cursos()
    return jsonify([
        {
            "id": c.id,
            "nombre": c.nombre,
            "codigo": c.codigo,
            "creditos": c.creditos,
            "horas_lectivas": c.horas_lectivas,
            "horas_practicas": c.horas_practicas
        }
        for c in cursos
    ])

def obtener_curso(id):
    c = CursosService.obtener_curso(id)
    return jsonify({
        "id": c.id,
        "nombre": c.nombre,
        "codigo": c.codigo,
        "creditos": c.creditos,
        "horas_lectivas": c.horas_lectivas,
        "horas_practicas": c.horas_practicas
    })

def registrar_curso():
    data = request.get_json()

    schema = RegistroCursoSchema()
    result = schema.load(data)

    curso = CursosService.registrar_curso(result)

    return jsonify({
        "mensaje": "Curso registrado correctamente",
        "curso_id": curso.id
    }), 201

def actualizar_curso(id):
    data = request.get_json()

    schema = ActualizarCursoSchema()
    schema.context = {"id": id}
    result = schema.load(data)

    curso = CursosService.actualizar_curso(id, result)

    return jsonify({
        "mensaje": "Curso actualizado correctamente",
        "curso_id": curso.id
    }), 200

def eliminar_curso(id):
    CursosService.eliminar_curso(id)

    return jsonify({
        "mensaje": "Curso eliminado correctamente"
    }), 200

def listar_prerequisitos(curso_id):
    prerequisitos = CursosService.listar_prerequisitos(curso_id)
    return jsonify([
        {
            "curso_dependiente_id": p.curso_dependiente_id,
            "curso_requisito_id": p.curso_requisito_id
        }
        for p in prerequisitos
    ])