from app import db
from app.dominio.modelos.academico.curso import Curso
from app.dominio.modelos.academico.plan_cursos_semestre import PlanCursosSemestre
from app.dominio.modelos.academico.plan_de_estudios import PlanDeEstudios
from app.dominio.modelos.academico.semestre import Semestre

CURSOS_POR_SEMESTRE = 4
CANTIDAD_SEMESTRES = 3


def ejecutar():
    if PlanCursosSemestre.query.first():
        print("Plan cursos semestre ya existe")
        return

    planes = PlanDeEstudios.query.all()
    cursos = Curso.query.order_by(Curso.id).all()
    semestres = Semestre.query.order_by(Semestre.id).limit(CANTIDAD_SEMESTRES).all()

    if not planes or not cursos or not semestres:
        print("No hay planes, cursos o semestres suficientes para crear plan_cursos_semestre")
        return

    if len(cursos) < CURSOS_POR_SEMESTRE * len(semestres):
        print("No hay cursos suficientes para repartir en los semestres configurados")
        return

    asignaciones = []
    for plan in planes:
        for indice_semestre, semestre in enumerate(semestres):
            inicio = indice_semestre * CURSOS_POR_SEMESTRE
            fin = inicio + CURSOS_POR_SEMESTRE
            for curso in cursos[inicio:fin]:
                asignaciones.append(PlanCursosSemestre(
                    plan_estudios_id=plan.id,
                    semestre_id=semestre.id,
                    curso_id=curso.id,
                ))

    db.session.add_all(asignaciones)
    db.session.commit()

    print(f"Plan cursos semestre creado: {len(asignaciones)} asignaciones para {len(planes)} plan(es)")
