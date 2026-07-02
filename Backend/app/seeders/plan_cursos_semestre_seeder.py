from app import db
from app.modelos.curso import Curso
from app.modelos.plan_cursos_semestre import PlanCursosSemestre
from app.modelos.plan_de_estudios import PlanDeEstudios
from app.modelos.semestre import Semestre


def ejecutar():
    if PlanCursosSemestre.query.first():
        print("Plan cursos semestre ya existe")
        return

    plan = PlanDeEstudios.query.first()
    cursos = Curso.query.limit(3).all()
    semestres = Semestre.query.limit(3).all()

    if not plan or len(cursos) < 3 or len(semestres) < 3:
        print("No hay datos suficientes para crear plan_cursos_semestre")
        return

    asignaciones = [
        PlanCursosSemestre(plan_estudios_id=plan.id, semestre_id=semestres[0].id, curso_id=cursos[0].id),
        PlanCursosSemestre(plan_estudios_id=plan.id, semestre_id=semestres[1].id, curso_id=cursos[1].id),
        PlanCursosSemestre(plan_estudios_id=plan.id, semestre_id=semestres[2].id, curso_id=cursos[2].id),
    ]

    db.session.add_all(asignaciones)
    db.session.commit()

    print("Plan cursos semestre creado")
