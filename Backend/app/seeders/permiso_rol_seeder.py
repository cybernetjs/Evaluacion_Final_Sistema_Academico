from app import db
from app.modelos.permiso_rol import PermisoRol


MATRIZ_POR_DEFECTO = [
    {"rol": "estudiante", "recurso": "matricula", "puede_crear": True, "puede_leer": True},
    {"rol": "administrador", "recurso": "matricula", "puede_leer": True, "puede_actualizar": True},
    {"rol": "direccion", "recurso": "matricula", "puede_leer": True},

    {"rol": "docente", "recurso": "notas", "puede_crear": True, "puede_leer": True, "puede_actualizar": True},
    {"rol": "administrador", "recurso": "notas", "puede_leer": True},
    {"rol": "direccion", "recurso": "notas", "puede_leer": True},

    {"rol": "estudiante", "recurso": "certificados", "puede_crear": True, "puede_leer": True},
    {"rol": "administrador", "recurso": "certificados", "puede_leer": True, "puede_actualizar": True},
    {"rol": "direccion", "recurso": "certificados", "puede_leer": True, "puede_actualizar": True, "puede_ejecutar_batch": True},

    {"rol": "administrador", "recurso": "cursos_docentes", "puede_crear": True, "puede_leer": True, "puede_actualizar": True},
    {"rol": "docente", "recurso": "cursos_docentes", "puede_crear": True, "puede_leer": True},
    {"rol": "direccion", "recurso": "cursos_docentes", "puede_leer": True},

    {"rol": "administrador", "recurso": "administracion", "puede_crear": True, "puede_leer": True, "puede_actualizar": True},

    {"rol": "administrador", "recurso": "auditoria", "puede_leer": True},
    {"rol": "direccion", "recurso": "auditoria", "puede_leer": True},

    {"rol": "estudiante", "recurso": "record_academico", "puede_leer": True},
    {"rol": "administrador", "recurso": "record_academico", "puede_leer": True},
    {"rol": "direccion", "recurso": "record_academico", "puede_leer": True},
]


def ejecutar():
    if PermisoRol.query.first():
        print("Matriz de permisos ya existe")
        return

    permisos = [PermisoRol(**fila) for fila in MATRIZ_POR_DEFECTO]
    db.session.add_all(permisos)
    db.session.commit()

    print(f"Matriz de permisos creada: {len(permisos)} combinaciones rol-recurso")
