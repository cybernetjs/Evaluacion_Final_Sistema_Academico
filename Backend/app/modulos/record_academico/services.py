import io
from app import db
from app.modelos.estudiante import Estudiante
from app.modelos.matricula import Matricula
from app.modelos.periodo_academico import PeriodoAcademico
from app.modelos.progreso_estudiante import ProgresoEstudiante

ROMANOS_POR_SEMESTRE = {
    "01": "I", "02": "II", "03": "III", "04": "IV", "05": "V",
    "06": "VI", "07": "VII", "08": "VIII", "09": "IX", "10": "X",
}


class RecordAcademicoService:

    @staticmethod
    def _estudiante_por_usuario(usuario_id):

        return Estudiante.query.filter_by(usuario_id=usuario_id).first()

    @staticmethod
    def _filas_historial(estudiante_id):

        matriculas = (
            Matricula.query.filter_by(estudiante_id=estudiante_id)
            .join(PeriodoAcademico, Matricula.periodo_academico_id == PeriodoAcademico.id)
            .order_by(PeriodoAcademico.fecha_inicio.desc())
            .all()
        )

        filas = []
        for m in matriculas:

            for d in m.detalle:
                curso = d.oferta_academica.curso
                filas.append({
                    "periodo_academico": m.periodo_academico.nombre,
                    "semestre": ROMANOS_POR_SEMESTRE.get(m.semestre.codigo, m.semestre.codigo),
                    "codigo_curso": curso.codigo,
                    "nombre_curso": curso.nombre,
                    "creditos": curso.creditos,
                    "nota_final": float(d.nota_final) if d.nota_final is not None else None,
                    "estado": d.estado_curso.nombre if d.estado_curso else None,
                })
        return filas

    @staticmethod
    def _cabecera_metricas(estudiante_id, filas):

        progreso = ProgresoEstudiante.query.get(estudiante_id)
        total_matriculados = sum(f["creditos"] for f in filas)

        return {
            "total_creditos_matriculados": total_matriculados,
            "total_creditos_aprobados": progreso.creditos_aprobados_acumulados if progreso else 0,
            "promedio_ponderado_acumulado": float(progreso.promedio_ponderado_acumulado) if progreso else None,
        }

    @staticmethod
    def historial_completo(usuario_id):

        estudiante = RecordAcademicoService._estudiante_por_usuario(usuario_id)
        if not estudiante:
            return None, "No se encontró un estudiante asociado a este usuario"

        filas = RecordAcademicoService._filas_historial(estudiante.id)
        cabecera = RecordAcademicoService._cabecera_metricas(estudiante.id, filas)

        return {
            "estudiante": {
                "nombres": estudiante.nombres,
                "apellido_paterno": estudiante.apellido_paterno,
                "apellido_materno": estudiante.apellido_materno,
                "especialidad": estudiante.especialidad.nombre if estudiante.especialidad else None,
            },
            "cabecera": cabecera,
            "historial": filas,
        }, None