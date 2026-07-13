from sqlalchemy import text
from app import crear_app, db

app = crear_app()

with app.app_context():
    respuesta = input(
        "Esto va a borrar TODA la base de datos y recrearla VACÍA (sin datos de prueba). "
        "¿Continuar? (si/no): "
    )

    if respuesta.lower() != "si":
        print("Operación cancelada")
        exit()

    es_mysql = db.engine.dialect.name == "mysql"

    if es_mysql:
        with db.engine.connect() as conexion:
            conexion.execute(text("SET FOREIGN_KEY_CHECKS=0"))
            conexion.commit()

    db.drop_all()
    db.create_all()

    if es_mysql:
        with db.engine.connect() as conexion:
            conexion.execute(text("SET FOREIGN_KEY_CHECKS=1"))
            conexion.commit()

    print("Listo: base de datos recreada vacía (sin seeders)")
