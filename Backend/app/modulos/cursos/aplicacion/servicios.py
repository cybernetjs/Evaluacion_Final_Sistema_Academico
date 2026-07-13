import os
import uuid
from datetime import datetime
from app import db
from app.dominio.modelos.academico.silabo import Silabo
from app.dominio.modelos.docentes.docente import Docente
from app.dominio.modelos.academico.curso import Curso
from app.dominio.modelos.ofertas.oferta_academica import OfertaAcademica
from app.dominio.modelos.ofertas.oferta_academica_docente import OfertaAcademicaDocente
from app.dominio.modelos.ofertas.oferta_academica_horario import OfertaAcademicaHorario
from app.dominio.modelos.ofertas.periodo_academico import PeriodoAcademico
from app.dominio.modelos.academico.plan_cursos_semestre import PlanCursosSemestre
from app.dominio.modelos.academico.plan_de_estudios import PlanDeEstudios
from app.dominio.modelos.academico.especialidad import Especialidad

CARPETA_SILABOS = os.path.join(os.getcwd(), "uploads", "silabos")
TAMANO_MAXIMO_SILABO_BYTES = 10 * 1024 * 1024
CARGA_MINIMA_SEMANAL = 8
CARGA_MAXIMA_SEMANAL = 20
FUNCIONES_VALIDAS = ("Teorico", "Practico")

DIAS_SEMANA = {
    1: "Lunes", 2: "Martes", 3: "Miercoles", 4: "Jueves",
    5: "Viernes", 6: "Sabado", 7: "Domingo",
}

class CursosService:
    def periodo_activo():
        hoy = datetime.utcnow()
        periodo = (
            PeriodoAcademico.query
            .filter(PeriodoAcademico.fecha_inicio <= hoy, PeriodoAcademico.fecha_fin >= hoy)
            .first()
        )
        if periodo:
            return periodo
        return PeriodoAcademico.query.order_by(PeriodoAcademico.fecha_inicio.desc()).first()
    
    def listar_cursos():
        cursos = Curso.query.all()
        return cursos
    
    def obtener_curso(id):
        curso = Curso.query.get_or_404(id)
        return curso

    def registrar_curso(data):
        curso = Curso(
            nombre=data.get("nombre"),
            codigo=data.get("codigo"),
            creditos=data.get("creditos"),
            horas_lectivas=data.get("horas_lectivas"),
            horas_practicas=data.get("horas_practicas")
        )
        db.session.add(curso)
        db.session.commit()
        return curso

    def actualizar_curso(id, data):
        curso = Curso.query.get_or_404(id)
        Curso.query.filter_by(id=id).update(data)
        db.session.commit()
        return curso

    def eliminar_curso(id):
        curso = Curso.query.get_or_404(id)
        db.session.delete(curso)
        db.session.commit()

    def listar_prerequisitos(curso_id):
        from app.dominio.modelos.academico.pre_requisito import PreRequisito
        return PreRequisito.query.filter_by(curso_dependiente_id=curso_id).all()