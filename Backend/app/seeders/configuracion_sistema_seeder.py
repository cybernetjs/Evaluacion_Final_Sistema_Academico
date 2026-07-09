from app import db
from app.modelos.configuracion_sistema import ConfiguracionSistema


def ejecutar():
    if ConfiguracionSistema.query.first():
        print("Configuracion del sistema ya existe")
        return

    configuracion = ConfiguracionSistema(
        matricula_habilitada=True,
        estado_ciclo="Inscripcion Abierta",
    )
    db.session.add(configuracion)
    db.session.commit()

    print("Configuracion del sistema creada")
