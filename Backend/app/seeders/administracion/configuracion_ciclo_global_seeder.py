from app import db
from app.dominio.modelos.administracion.configuracion_ciclo_global import ConfiguracionCicloGlobal
from app.dominio.modelos.ofertas.periodo_academico import PeriodoAcademico


def ejecutar():
    if ConfiguracionCicloGlobal.query.first():
        print("Configuracion del ciclo global ya existe")
        return

    periodo_actual = PeriodoAcademico.query.order_by(PeriodoAcademico.fecha_inicio.desc()).first()

    configuracion = ConfiguracionCicloGlobal(
        id=1,
        periodo_academico_id=periodo_actual.id if periodo_actual else None,
        estado_ciclo="Inscripcion de Matricula Abierta",
    )
    db.session.add(configuracion)
    db.session.commit()

    print("Configuracion del ciclo global creada")
