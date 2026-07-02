from flask import jsonify
from app.modelos.curso import Curso
from app.modelos.pre_requisito import PreRequisito
from app.modelos.docente import Docente
from app.modelos.tipo_docente import TipoDocente


def listar_cursos():
    cursos = Curso.query.all()
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
    c = Curso.query.get_or_404(id)
    return jsonify({
        "id": c.id,
        "nombre": c.nombre,
        "codigo": c.codigo,
        "creditos": c.creditos,
        "horas_lectivas": c.horas_lectivas,
        "horas_practicas": c.horas_practicas
    })


def listar_prerequisitos():
    prerequisitos = PreRequisito.query.all()
    return jsonify([
        {
            "curso_dependiente_id": p.curso_dependiente_id,
            "curso_requisito_id": p.curso_requisito_id
        }
        for p in prerequisitos
    ])


def listar_docentes():
    docentes = Docente.query.all()
    return jsonify([
        {
            "id": d.id,
            "nombres": d.nombres,
            "apellido_paterno": d.apellido_paterno,
            "apellido_materno": d.apellido_materno,
            "correo_institucional": d.correo_institucional
        }
        for d in docentes
    ])


def listar_tipos_docentes():
    tipos = TipoDocente.query.all()
    return jsonify([
        {"id": t.id, "nombre": t.nombre}
        for t in tipos
    ])