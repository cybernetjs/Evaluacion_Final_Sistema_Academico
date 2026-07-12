from app.seeders.academico import facultad_seeder
from app.seeders.academico import especialidad_seeder
from app.seeders.academico import semestre_seeder
from app.seeders.ofertas import periodo_academico_seeder
from app.seeders.estudiantes import hito_academico_seeder
from app.seeders.administracion import permiso_rol_seeder
from app.seeders.academico import plan_de_estudios_seeder
from app.seeders.docentes import tipo_docente_seeder
from app.seeders.estudiantes import tipo_clasificacion_merito_seeder
from app.seeders.academico import estado_curso_seeder
from app.seeders.matriculas import estado_matricula_seeder
from app.seeders.estudiantes import estado_permanencia_estudiante_seeder
from app.seeders.academico import curso_seeder
from app.seeders.identidad import usuario_seeder
from app.seeders.docentes import docente_seeder
from app.seeders.estudiantes import estudiante_seeder
from app.seeders.estudiantes import plan_estudiante_seeder
from app.seeders.academico import pre_requisito_seeder
from app.seeders.academico import plan_cursos_semestre_seeder
from app.seeders.ofertas import oferta_academica_seeder
from app.seeders.ofertas import oferta_academica_horario_seeder
from app.seeders.matriculas import matricula_seeder
from app.seeders.matriculas import matricula_detalle_seeder
from app.seeders.ofertas import oferta_academica_docente_seeder
from app.seeders.estudiantes import historial_merito_seeder
from app.seeders.estudiantes import progreso_estudiante_seeder
from app.seeders.administracion import configuracion_ciclo_global_seeder


SEEDERS = [
    facultad_seeder.ejecutar,
    especialidad_seeder.ejecutar,
    semestre_seeder.ejecutar,
    periodo_academico_seeder.ejecutar,
    hito_academico_seeder.ejecutar,
    permiso_rol_seeder.ejecutar,
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
    pre_requisito_seeder.ejecutar,
    plan_cursos_semestre_seeder.ejecutar,
    oferta_academica_seeder.ejecutar,
    oferta_academica_horario_seeder.ejecutar,
    matricula_seeder.ejecutar,
    matricula_detalle_seeder.ejecutar,
    oferta_academica_docente_seeder.ejecutar,
    historial_merito_seeder.ejecutar,
    progreso_estudiante_seeder.ejecutar,
    configuracion_ciclo_global_seeder.ejecutar,
]


def ejecutar_todos():
    for ejecutar in SEEDERS:
        ejecutar()
