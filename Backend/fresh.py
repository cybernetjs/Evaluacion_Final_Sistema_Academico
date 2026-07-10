from app import crear_app, db
from app.seeders import ejecutar_todos

app = crear_app()

with app.app_context():
    respuesta = input("Esto va a borrar TODA la base de datos y recrearla. ¿Continuar? (si/no): ")

    if respuesta.lower() != "si":
        print("Operación cancelada")
        exit()

    db.drop_all()
    db.create_all()
    print("Base de datos recreada")

    ejecutar_todos()

    print("Listo: base de datos nueva con datos de prueba")