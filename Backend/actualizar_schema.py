from sqlalchemy import inspect, text

from app import crear_app, db
import app.modelos  # noqa: F401


def agregar_columna_si_falta(inspector, tabla, columna, ddl):
    columnas = {item["name"] for item in inspector.get_columns(tabla)}
    if columna in columnas:
        print(f"OK: {tabla}.{columna} ya existe")
        return

    db.session.execute(text(f"ALTER TABLE {tabla} ADD COLUMN {ddl}"))
    db.session.commit()
    print(f"Agregado: {tabla}.{columna}")


app = crear_app()

with app.app_context():
    db.create_all()

    inspector = inspect(db.engine)

    agregar_columna_si_falta(
        inspector,
        "periodos_academicos",
        "dias_limite_pago",
        "dias_limite_pago INT NOT NULL DEFAULT 15",
    )

    inspector = inspect(db.engine)
    agregar_columna_si_falta(
        inspector,
        "matricula_detalle",
        "nota_parcial2",
        "nota_parcial2 DECIMAL(4, 2) NULL",
    )

    inspector = inspect(db.engine)
    agregar_columna_si_falta(
        inspector,
        "matricula_detalle",
        "nota_practica",
        "nota_practica DECIMAL(4, 2) NULL",
    )

    print("Schema actualizado sin borrar datos")
