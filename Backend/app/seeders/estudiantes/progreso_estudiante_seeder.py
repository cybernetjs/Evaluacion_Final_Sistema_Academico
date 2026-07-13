from app import db
from app.dominio.modelos.estudiantes.estado_permanencia_estudiante import EstadoPermanenciaEstudiante
from app.dominio.modelos.estudiantes.estudiante import Estudiante
from app.dominio.modelos.estudiantes.progreso_estudiante import ProgresoEstudiante


def ejecutar():
    estado_regular = EstadoPermanenciaEstudiante.query.filter_by(nombre="Regular").first()
    if not estado_regular:
        print("No existe el estado de permanencia Regular para crear progreso")
        return

    estudiantes_sin_progreso = (
        Estudiante.query.filter(~Estudiante.id.in_(db.session.query(ProgresoEstudiante.estudiante_id)))
        .all()
    )

    if not estudiantes_sin_progreso:
        print("Progreso de estudiante ya existe para todos los estudiantes")
        return

    nuevos = [
        ProgresoEstudiante(
            estudiante_id=estudiante.id,
            estado_permanencia_id=estado_regular.id,
            creditos_aprobados_acumulados=0,
            promedio_ponderado_acumulado=0,
        )
        for estudiante in estudiantes_sin_progreso
    ]

    db.session.add_all(nuevos)
    db.session.commit()

    print(f"Progreso de estudiante creado (sin historial previo): {len(nuevos)}")
