from app import db
from app.dominio.modelos.academico.curso import Curso
from app.dominio.modelos.estudiantes.historial_merito import HistorialMerito
from app.dominio.modelos.estudiantes.tipo_clasificacion_merito import TipoClasificacionMerito
from app.dominio.modelos.matriculas.matricula import Matricula
from app.dominio.modelos.matriculas.matricula_detalle import MatriculaDetalle
from app.dominio.modelos.notas.expediente_semestral import ExpedienteSemestral
from app.dominio.modelos.ofertas.oferta_academica import OfertaAcademica


def _semestre_predominante(estudiante_id, periodo_academico_id):
    fila = (
        db.session.query(OfertaAcademica.semestre_id, db.func.count(OfertaAcademica.id).label("total"))
        .join(MatriculaDetalle, MatriculaDetalle.oferta_academica_id == OfertaAcademica.id)
        .join(Matricula, MatriculaDetalle.matricula_id == Matricula.id)
        .filter(
            Matricula.estudiante_id == estudiante_id,
            Matricula.periodo_academico_id == periodo_academico_id,
        )
        .group_by(OfertaAcademica.semestre_id)
        .order_by(db.func.count(OfertaAcademica.id).desc())
        .first()
    )
    return fila.semestre_id if fila else None


def _creditos_matriculados(estudiante_id, periodo_academico_id):
    total = (
        db.session.query(db.func.coalesce(db.func.sum(Curso.creditos), 0))
        .select_from(MatriculaDetalle)
        .join(Matricula, MatriculaDetalle.matricula_id == Matricula.id)
        .join(OfertaAcademica, MatriculaDetalle.oferta_academica_id == OfertaAcademica.id)
        .join(Curso, OfertaAcademica.curso_id == Curso.id)
        .filter(
            Matricula.estudiante_id == estudiante_id,
            Matricula.periodo_academico_id == periodo_academico_id,
        )
        .scalar()
    )
    return int(total or 0)


def _clasificacion(percentil, tipos):
    if percentil <= 10 and "Bronce" in tipos:
        return tipos["Bronce"]
    if percentil <= 25 and "Plata" in tipos:
        return tipos["Plata"]
    if "Oro" in tipos:
        return tipos["Oro"]
    return next(iter(tipos.values()))


def ejecutar():
    if HistorialMerito.query.first():
        print("Historial de merito ya existe")
        return

    expedientes = ExpedienteSemestral.query.all()
    if not expedientes:
        print("No hay expedientes semestrales consolidados para crear historial de merito")
        return

    tipos = {t.nombre: t for t in TipoClasificacionMerito.query.all()}
    if not tipos:
        print("No hay tipos de clasificacion de merito para crear historial de merito")
        return

    historiales = []
    periodos_ids = {e.periodo_academico_id for e in expedientes}

    for periodo_id in periodos_ids:
        expedientes_periodo = sorted(
            (e for e in expedientes if e.periodo_academico_id == periodo_id),
            key=lambda e: float(e.promedio_ponderado_semestral),
            reverse=True,
        )
        total = len(expedientes_periodo)

        for posicion, expediente in enumerate(expedientes_periodo, start=1):
            estudiante = expediente.estudiante
            semestre_id = _semestre_predominante(estudiante.id, periodo_id)
            if not semestre_id:
                continue

            percentil = round((posicion / total) * 100, 2)
            tipo = _clasificacion(percentil, tipos)

            historiales.append(HistorialMerito(
                estudiante_id=estudiante.id,
                periodo_academico_id=periodo_id,
                semestre_id=semestre_id,
                especialidad_id=estudiante.especialidad_id,
                promedio_ponderado_periodo=expediente.promedio_ponderado_semestral,
                creditos_matriculados_periodo=_creditos_matriculados(estudiante.id, periodo_id),
                creditos_aprobados_periodo=expediente.creditos_aprobados_semestre,
                orden_merito=posicion,
                tipo_clasificacion_id=tipo.id,
            ))

    if not historiales:
        print("No se pudo construir el historial de merito a partir de los expedientes consolidados")
        return

    db.session.add_all(historiales)
    db.session.commit()

    print(f"Historial de merito creado: {len(historiales)}")
