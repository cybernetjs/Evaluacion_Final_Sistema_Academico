import os
import uuid
from app import db
from app.modelos.silabo import Silabo
from app.modelos.docente import Docente
from app.modelos.oferta_academica_docente import OfertaAcademicaDocente
from app.modelos.plan_cursos_semestre import PlanCursosSemestre
from app.modelos.oferta_academica import OfertaAcademica

CARPETA_SILABOS = os.path.join(os.getcwd(), "uploads", "silabos")


class CursosDocentesService:

    @staticmethod
    def cargar_silabo(usuario_id, oferta_academica_id, nombre_archivo, archivo_stream):
        docente = Docente.query.filter_by(usuario_id=usuario_id).first()

        if not docente:
            return None, "No se encontró un docente asociado a este usuario"

        asignado = OfertaAcademicaDocente.query.filter_by(
            oferta_academica_id=oferta_academica_id,
            docente_id=docente.id
        ).first()

        if not asignado:
            return None, "No tienes asignado este curso, no puedes cargar el sílabo"

        os.makedirs(CARPETA_SILABOS, exist_ok=True)

        extension = os.path.splitext(nombre_archivo)[1]
        nombre_unico = f"{uuid.uuid4()}{extension}"
        ruta_completa = os.path.join(CARPETA_SILABOS, nombre_unico)

        archivo_stream.save(ruta_completa)

        silabo = Silabo.query.filter_by(oferta_academica_id=oferta_academica_id).first()

        if silabo:
            silabo.nombre_archivo = nombre_archivo
            silabo.ruta_archivo = ruta_completa
        else:
            silabo = Silabo(
                oferta_academica_id=oferta_academica_id,
                nombre_archivo=nombre_archivo,
                ruta_archivo=ruta_completa
            )
            db.session.add(silabo)

        db.session.commit()
        return silabo, None

    @staticmethod
    def obtener_silabo(oferta_academica_id):
        silabo = Silabo.query.filter_by(oferta_academica_id=oferta_academica_id).first()

        if not silabo:
            return None, "No hay sílabo cargado para este curso"

        return silabo, None
    
def cumplimiento_plan_estudios(periodo_academico_id):
    cursos_del_plan = PlanCursosSemestre.query.all()

    resultado = []
    for item in cursos_del_plan:
        oferta = OfertaAcademica.query.filter_by(
            periodo_academico_id=periodo_academico_id,
            curso_id=item.curso_id,
            semestre_id=item.semestre_id
        ).first()

        docentes_asignados = 0
        cupos = None
        if oferta:
            docentes_asignados = OfertaAcademicaDocente.query.filter_by(
                oferta_academica_id=oferta.id
            ).count()
            cupos = oferta.cupos

        resultado.append({
            "plan_estudios_id": item.plan_estudios_id,
            "semestre_id": item.semestre_id,
            "curso_id": item.curso_id,
            "curso_nombre": item.curso.nombre,
            "tiene_oferta_este_periodo": oferta is not None,
            "docentes_asignados": docentes_asignados,
            "cupos": cupos
        })

    return resultado