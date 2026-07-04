from app import db
from app.modelos.matricula_detalle import MatriculaDetalle
from app.modelos.matricula import Matricula
from app.modelos.estudiante import Estudiante


class NotasService:

    @staticmethod
    def registrar_nota(matricula_id, oferta_academica_id, nota_parcial=None, nota_final=None, estado_curso_id=None):
        detalle = MatriculaDetalle.query.filter_by(
            matricula_id=matricula_id,
            oferta_academica_id=oferta_academica_id
        ).first()

        if not detalle:
            return None, "Detalle de matrícula no encontrado"

        if nota_parcial is not None:
            detalle.nota_parcial = nota_parcial
        if nota_final is not None:
            detalle.nota_final = nota_final
        if estado_curso_id is not None:
            detalle.estado_curso_id = estado_curso_id

        db.session.commit()
        return detalle, None

    @staticmethod
    def hoja_de_notas_por_ciclo(usuario_id, semestre_id=None):
        estudiante = Estudiante.query.filter_by(usuario_id=usuario_id).first()

        if not estudiante:
            return None, "No se encontró un estudiante asociado a este usuario"

        query = Matricula.query.filter_by(estudiante_id=estudiante.id)
        if semestre_id:
            query = query.filter_by(semestre_id=semestre_id)

        matriculas = query.all()

        resultado = []
        for m in matriculas:
            for d in m.detalle:
                resultado.append({
                    "periodo_academico_id": m.periodo_academico_id,
                    "semestre_id": m.semestre_id,
                    "curso_id": d.oferta_academica.curso_id,
                    "curso_nombre": d.oferta_academica.curso.nombre,
                    "nota_parcial": float(d.nota_parcial) if d.nota_parcial is not None else None,
                    "nota_final": float(d.nota_final) if d.nota_final is not None else None,
                    "estado_curso_id": d.estado_curso_id
                })

        return resultado, None