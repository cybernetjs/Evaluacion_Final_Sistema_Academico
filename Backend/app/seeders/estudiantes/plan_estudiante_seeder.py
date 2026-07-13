from app import db
from app.dominio.modelos.estudiantes.estudiante import Estudiante
from app.dominio.modelos.academico.plan_de_estudios import PlanDeEstudios
from app.dominio.modelos.estudiantes.plan_estudiante import PlanEstudiante


def ejecutar():
    if PlanEstudiante.query.first():
        print("Planes de estudiante ya existen")
        return

    estudiantes = Estudiante.query.all()
    if not estudiantes:
        print("No hay estudiantes para crear plan_estudiante")
        return

    planes_asignados = []
    for estudiante in estudiantes:
        plan = (
            PlanDeEstudios.query.filter_by(especialidad_id=estudiante.especialidad_id, vigente=True)
            .first()
        )
        if not plan:
            plan = PlanDeEstudios.query.first()
        if not plan:
            print(f"No hay plan de estudios para el estudiante {estudiante.id}")
            continue

        planes_asignados.append(PlanEstudiante(estudiante_id=estudiante.id, plan_estudios_id=plan.id))

    if not planes_asignados:
        print("No se pudo asignar ningun plan de estudiante")
        return

    db.session.add_all(planes_asignados)
    db.session.commit()

    print(f"Planes de estudiante creados: {len(planes_asignados)}")
