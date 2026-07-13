from app import db
from app.dominio.modelos.academico.curso import Curso
from app.dominio.modelos.academico.pre_requisito import PreRequisito


def ejecutar():
    if PreRequisito.query.first():
        print("Prerequisitos ya existen")
        return

    cursos = {c.codigo: c for c in Curso.query.all()}

    pares_codigos = [
        ("PROG2", "PROG1"),
        ("BD1", "PROG1"),
        ("EDA1", "PROG2"),
        ("RED1", "ARQ1"),
        ("SO1", "ARQ1"),
        ("CIBER1", "RED1"),
        ("MAT2", "MAT1"),
    ]

    prerequisitos = []
    for codigo_dependiente, codigo_requisito in pares_codigos:
        dependiente = cursos.get(codigo_dependiente)
        requisito = cursos.get(codigo_requisito)
        if not dependiente or not requisito:
            continue
        prerequisitos.append(PreRequisito(
            curso_dependiente_id=dependiente.id,
            curso_requisito_id=requisito.id,
        ))

    if not prerequisitos:
        print("No hay cursos suficientes para crear prerequisitos")
        return

    db.session.add_all(prerequisitos)
    db.session.commit()

    print(f"Prerequisitos creados: {len(prerequisitos)}")
