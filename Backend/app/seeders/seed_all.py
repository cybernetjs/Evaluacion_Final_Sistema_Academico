from app.seeders import (
    curso_seeder,
    docente_seeder,
    especialidad_seeder,
    estado_curso_seeder,
    estado_matricula_seeder,
    estado_permanencia_estudiante_seeder,
    estudiante_seeder,
    facultad_seeder,
    historial_merito_seeder,
    matricula_detalle_seeder,
    matricula_seeder,
    oferta_academica_horario_seeder,
    oferta_academica_docente_seeder,
    oferta_academica_seeder,
    periodo_academico_seeder,
    plan_de_estudios_seeder,
    plan_cursos_semestre_seeder,
    plan_estudiante_seeder,
    pre_requisito_seeder,
    progreso_estudiante_seeder,
    semestre_seeder,
    tipo_clasificacion_merito_seeder,
    tipo_docente_seeder,
    usuario_seeder,
)


SEEDERS = [
    facultad_seeder.ejecutar,
    especialidad_seeder.ejecutar,
    semestre_seeder.ejecutar,
    periodo_academico_seeder.ejecutar,
    plan_de_estudios_seeder.ejecutar,
    tipo_docente_seeder.ejecutar,
    tipo_clasificacion_merito_seeder.ejecutar,
    estado_curso_seeder.ejecutar,
    estado_matricula_seeder.ejecutar,
    estado_permanencia_estudiante_seeder.ejecutar,
    curso_seeder.ejecutar,
    usuario_seeder.ejecutar,
    docente_seeder.ejecutar,
    estudiante_seeder.ejecutar,
    plan_estudiante_seeder.ejecutar,
    oferta_academica_seeder.ejecutar,
    oferta_academica_horario_seeder.ejecutar,
    pre_requisito_seeder.ejecutar,
    plan_cursos_semestre_seeder.ejecutar,
    matricula_seeder.ejecutar,
    matricula_detalle_seeder.ejecutar,
    oferta_academica_docente_seeder.ejecutar,
    historial_merito_seeder.ejecutar,
    progreso_estudiante_seeder.ejecutar,
]


def ejecutar_todos():
    for ejecutar in SEEDERS:
        ejecutar()