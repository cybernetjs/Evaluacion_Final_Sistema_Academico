from app import db
from app.dominio.modelos.academico.estado_curso import EstadoCurso
from app.dominio.modelos.academico.semestre import Semestre
from app.dominio.modelos.matriculas.matricula import Matricula
from app.dominio.modelos.matriculas.matricula_detalle import MatriculaDetalle
from app.dominio.modelos.notas.acta import Acta
from app.dominio.modelos.ofertas.oferta_academica import OfertaAcademica
from app.dominio.modelos.ofertas.periodo_academico import PeriodoAcademico
from app.modulos.notas.aplicacion.servicios import NotasService, UMBRAL_APROBACION

NOTAS_BASE_POR_ESTUDIANTE = [
    [14.0, 13.0, 15.5, 12.0],
    [10.5, 9.0, 12.0, 11.0],
    [17.0, 16.0, 18.5, 15.5],
]


def _estado_curso(nombre):
    return EstadoCurso.query.filter_by(nombre=nombre).first()


def ejecutar():
    if MatriculaDetalle.query.first():
        print("Detalles de matricula ya existen")
        return

    periodos = PeriodoAcademico.query.order_by(PeriodoAcademico.fecha_inicio.desc()).limit(2).all()
    semestres = Semestre.query.order_by(Semestre.id).limit(2).all()

    if len(periodos) < 2 or len(semestres) < 2:
        print("No hay periodos o semestres suficientes para crear detalles de matricula")
        return

    periodo_actual, periodo_anterior = periodos[0], periodos[1]
    semestre_uno, semestre_dos = semestres[0], semestres[1]

    estado_aprobado = _estado_curso("Aprobado")
    estado_desaprobado = _estado_curso("Desaprobado")
    estado_cursando = _estado_curso("Cursando")

    if not estado_aprobado or not estado_desaprobado or not estado_cursando:
        print("No existen los estados de curso necesarios para crear detalles de matricula")
        return

    ofertas_semestre_uno = (
        OfertaAcademica.query.filter_by(periodo_academico_id=periodo_anterior.id, semestre_id=semestre_uno.id)
        .order_by(OfertaAcademica.id)
        .all()
    )
    ofertas_semestre_dos = (
        OfertaAcademica.query.filter_by(periodo_academico_id=periodo_actual.id, semestre_id=semestre_dos.id)
        .order_by(OfertaAcademica.id)
        .all()
    )

    matriculas_anteriores = (
        Matricula.query.filter_by(periodo_academico_id=periodo_anterior.id)
        .order_by(Matricula.estudiante_id)
        .all()
    )
    matriculas_actuales = (
        Matricula.query.filter_by(periodo_academico_id=periodo_actual.id)
        .order_by(Matricula.estudiante_id)
        .all()
    )

    if not ofertas_semestre_uno or not matriculas_anteriores:
        print("No hay ofertas o matriculas del periodo anterior para crear detalles")
        return

    detalles = []
    ofertas_a_cerrar = set()

    for indice_estudiante, matricula in enumerate(matriculas_anteriores):
        notas_curso = NOTAS_BASE_POR_ESTUDIANTE[indice_estudiante % len(NOTAS_BASE_POR_ESTUDIANTE)]

        for indice_oferta, oferta in enumerate(ofertas_semestre_uno):
            base = notas_curso[indice_oferta % len(notas_curso)]
            nota_parcial = round(base, 2)
            nota_parcial2 = round(min(20.0, base + 0.5), 2)
            nota_practica = round(max(0.0, base - 0.5), 2)
            nota_final = round(nota_parcial * 0.3 + nota_parcial2 * 0.3 + nota_practica * 0.4, 2)
            aprobado = nota_final >= UMBRAL_APROBACION

            detalles.append(MatriculaDetalle(
                matricula_id=matricula.id,
                oferta_academica_id=oferta.id,
                nota_parcial=nota_parcial,
                nota_parcial2=nota_parcial2,
                nota_practica=nota_practica,
                nota_final=nota_final,
                estado_curso_id=estado_aprobado.id if aprobado else estado_desaprobado.id,
            ))
            ofertas_a_cerrar.add(oferta.id)

    for matricula in matriculas_actuales:
        for oferta in ofertas_semestre_dos:
            detalles.append(MatriculaDetalle(
                matricula_id=matricula.id,
                oferta_academica_id=oferta.id,
                estado_curso_id=estado_cursando.id,
            ))

    db.session.add_all(detalles)
    db.session.flush()

    for oferta_id in ofertas_a_cerrar:
        acta = Acta.query.filter_by(oferta_academica_id=oferta_id).first()
        if not acta:
            acta = Acta(oferta_academica_id=oferta_id)
            db.session.add(acta)
        acta.estado = "Cerrada"
        acta.notas_publicadas = True

    db.session.commit()

    print(f"Detalles de matricula creados: {len(detalles)}")

    resultado, error, _, _ = NotasService.consolidar_semestre(periodo_anterior.id)
    if error:
        print(f"No se pudo consolidar el periodo anterior: {error}")
    else:
        print(f"Consolidacion del periodo anterior: {resultado['total_expedientes_actualizados']} expedientes")
