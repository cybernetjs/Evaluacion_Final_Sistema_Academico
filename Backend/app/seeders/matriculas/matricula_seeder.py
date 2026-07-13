from app import db
from app.dominio.modelos.matriculas.estado_matricula import EstadoMatricula
from app.dominio.modelos.estudiantes.estudiante import Estudiante
from app.dominio.modelos.matriculas.matricula import Matricula
from app.dominio.modelos.ofertas.periodo_academico import PeriodoAcademico
from app.dominio.modelos.academico.semestre import Semestre


def ejecutar():
    if Matricula.query.first():
        print("Matriculas ya existen")
        return

    estudiantes = Estudiante.query.order_by(Estudiante.id).all()
    periodos = PeriodoAcademico.query.order_by(PeriodoAcademico.fecha_inicio.desc()).limit(2).all()
    semestres = Semestre.query.order_by(Semestre.id).limit(2).all()
    estado = EstadoMatricula.query.filter_by(nombre="Matriculado").first()

    if not estudiantes or len(periodos) < 2 or len(semestres) < 2 or not estado:
        print("No hay datos suficientes para crear matriculas")
        return

    periodo_actual, periodo_anterior = periodos[0], periodos[1]
    semestre_uno, semestre_dos = semestres[0], semestres[1]

    matriculas = []
    for estudiante in estudiantes:
        matriculas.append(Matricula(
            estudiante_id=estudiante.id,
            periodo_academico_id=periodo_anterior.id,
            semestre_id=semestre_uno.id,
            estado_id=estado.id,
            pagado=True,
        ))
        matriculas.append(Matricula(
            estudiante_id=estudiante.id,
            periodo_academico_id=periodo_actual.id,
            semestre_id=semestre_dos.id,
            estado_id=estado.id,
            pagado=True,
        ))

    db.session.add_all(matriculas)
    db.session.commit()

    print(f"Matriculas creadas: {len(matriculas)}")
