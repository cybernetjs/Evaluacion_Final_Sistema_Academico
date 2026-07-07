from datetime import datetime
from app import db
from app.modelos.matricula_detalle import MatriculaDetalle
from app.modelos.matricula import Matricula
from app.modelos.estudiante import Estudiante
from app.modelos.docente import Docente
from app.modelos.oferta_academica import OfertaAcademica
from app.modelos.oferta_academica_docente import OfertaAcademicaDocente
from app.modelos.hito_academico import HitoAcademico
from app.modelos.acta import Acta

CAMPOS_POR_TIPO = {
    "parcial1": "nota_parcial",
    "parcial2": "nota_parcial2",
    "practica": "nota_practica",
    "final": "nota_final",
}

PESOS_FORMULA_FINAL = {
    "nota_parcial": 0.3,
    "nota_parcial2": 0.3,
    "nota_practica": 0.4,
}


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
    def _notas_visibles_para_estudiante(oferta_academica_id):
        acta = Acta.query.filter_by(oferta_academica_id=oferta_academica_id).first()
        if not acta:
            return False
        return acta.notas_publicadas or acta.estado == "Cerrada"

    @staticmethod
    def hoja_de_notas_por_ciclo(usuario_id, periodo_academico_id=None, semestre_id=None):
        estudiante = Estudiante.query.filter_by(usuario_id=usuario_id).first()

        if not estudiante:
            return None, "No se encontró un estudiante asociado a este usuario"

        query = Matricula.query.filter_by(estudiante_id=estudiante.id)
        if periodo_academico_id:
            query = query.filter_by(periodo_academico_id=periodo_academico_id)
        if semestre_id:
            query = query.filter_by(semestre_id=semestre_id)

        matriculas = query.all()

        resultado = []
        for m in matriculas:
            for d in m.detalle:
                visible = NotasService._notas_visibles_para_estudiante(d.oferta_academica_id)

                resultado.append({
                    "periodo_academico_id": m.periodo_academico_id,
                    "semestre_id": m.semestre_id,
                    "curso_id": d.oferta_academica.curso_id,
                    "curso_nombre": d.oferta_academica.curso.nombre,
                    "nota_parcial1": float(d.nota_parcial) if visible and d.nota_parcial is not None else None,
                    "nota_parcial2": float(d.nota_parcial2) if visible and d.nota_parcial2 is not None else None,
                    "nota_practica": float(d.nota_practica) if visible and d.nota_practica is not None else None,
                    "nota_final": float(d.nota_final) if visible and d.nota_final is not None else None,
                    "estado_curso_id": d.estado_curso_id,
                    "publicado": visible,
                })

        return resultado, None

    @staticmethod
    def ciclos_cursados(usuario_id):
        estudiante = Estudiante.query.filter_by(usuario_id=usuario_id).first()
        if not estudiante:
            return None, "No se encontró un estudiante asociado a este usuario"

        matriculas = Matricula.query.filter_by(estudiante_id=estudiante.id).all()

        vistos = {}
        for m in matriculas:
            if m.periodo_academico_id not in vistos:
                vistos[m.periodo_academico_id] = m.periodo_academico.nombre if m.periodo_academico else None

        ciclos = [{"periodo_academico_id": pid, "nombre": nombre} for pid, nombre in vistos.items()]
        return ciclos, None

    @staticmethod
    def publicar_notas(usuario_id_docente, oferta_academica_id):
        docente = NotasService._docente_asignado(usuario_id_docente, oferta_academica_id)
        if not docente:
            return None, "No tienes asignada esta sección"

        acta = Acta.query.filter_by(oferta_academica_id=oferta_academica_id).first()
        if not acta:
            acta = Acta(oferta_academica_id=oferta_academica_id)
            db.session.add(acta)

        if acta.estado == "Cerrada":
            return None, "El acta ya está cerrada, las notas ya son oficiales"

        acta.notas_publicadas = True
        db.session.commit()

        return {"mensaje": "Notas publicadas a los estudiantes", "oferta_academica_id": oferta_academica_id}, None

    @staticmethod
    def _docente_asignado(usuario_id, oferta_academica_id):
        docente = Docente.query.filter_by(usuario_id=usuario_id).first()
        if not docente:
            return None

        asignacion = OfertaAcademicaDocente.query.filter_by(
            docente_id=docente.id, oferta_academica_id=oferta_academica_id
        ).first()

        return docente if asignacion else None

    @staticmethod
    def estado_cronograma(oferta_academica_id, tipo_nota):
        if tipo_nota not in CAMPOS_POR_TIPO:
            return None, "Tipo de nota inválido"

        oferta = OfertaAcademica.query.get(oferta_academica_id)
        if not oferta:
            return None, "Oferta académica no encontrada"

        hito = HitoAcademico.query.filter_by(
            periodo_academico_id=oferta.periodo_academico_id, tipo_nota=tipo_nota
        ).first()

        if not hito:
            return {"vigente": True, "fecha_limite": None}, None

        vigente = datetime.now() <= hito.fecha_limite
        return {"vigente": vigente, "fecha_limite": hito.fecha_limite.isoformat()}, None

    @staticmethod
    def obtener_planilla(oferta_academica_id, usuario_id_docente):
        docente = NotasService._docente_asignado(usuario_id_docente, oferta_academica_id)
        if not docente:
            return None, "No tienes asignada esta sección"

        oferta = OfertaAcademica.query.get(oferta_academica_id)
        if not oferta:
            return None, "Oferta académica no encontrada"

        detalles = MatriculaDetalle.query.filter_by(oferta_academica_id=oferta_academica_id).all()

        estudiantes = []
        for d in detalles:
            estudiante = d.matricula.estudiante
            estudiantes.append({
                "matricula_id": d.matricula_id,
                "estudiante_id": estudiante.id,
                "estudiante_nombre": f"{estudiante.nombres} {estudiante.apellido_paterno} {estudiante.apellido_materno}",
                "nota_parcial1": float(d.nota_parcial) if d.nota_parcial is not None else None,
                "nota_parcial2": float(d.nota_parcial2) if d.nota_parcial2 is not None else None,
                "nota_practica": float(d.nota_practica) if d.nota_practica is not None else None,
                "nota_final": float(d.nota_final) if d.nota_final is not None else None,
            })

        cronograma = {}
        for tipo in CAMPOS_POR_TIPO:
            estado, _ = NotasService.estado_cronograma(oferta_academica_id, tipo)
            cronograma[tipo] = estado

        return {
            "curso_nombre": oferta.curso.nombre,
            "estudiantes": estudiantes,
            "cronograma": cronograma,
        }, None

    @staticmethod
    def registrar_notas_planilla(usuario_id_docente, oferta_academica_id, tipo_nota, calificaciones):
        if tipo_nota not in CAMPOS_POR_TIPO:
            return None, "Tipo de nota inválido", 400

        docente = NotasService._docente_asignado(usuario_id_docente, oferta_academica_id)
        if not docente:
            return None, "No tienes asignada esta sección", 403

        cronograma, error = NotasService.estado_cronograma(oferta_academica_id, tipo_nota)
        if error:
            return None, error, 400
        if not cronograma["vigente"]:
            return None, "Periodo de ingreso cerrado por la administración", 423

        if not calificaciones:
            return None, "Debes enviar al menos una calificación", 400

        for item in calificaciones:
            valor = item.get("calificacion")
            try:
                valor_numerico = float(valor)
            except (TypeError, ValueError):
                return None, f"La calificación '{valor}' no es un valor numérico válido", 400
            if valor_numerico < 0 or valor_numerico > 20:
                return None, f"La calificación {valor_numerico} está fuera del rango permitido (0-20)", 400

        campo = CAMPOS_POR_TIPO[tipo_nota]
        actualizados = 0

        for item in calificaciones:
            estudiante_id = item.get("estudiante_id")
            valor_numerico = float(item.get("calificacion"))

            detalle = (
                MatriculaDetalle.query.join(Matricula, MatriculaDetalle.matricula_id == Matricula.id)
                .filter(
                    Matricula.estudiante_id == estudiante_id,
                    MatriculaDetalle.oferta_academica_id == oferta_academica_id,
                )
                .first()
            )
            if not detalle:
                continue

            setattr(detalle, campo, valor_numerico)

            if tipo_nota != "final":
                componentes = [detalle.nota_parcial, detalle.nota_parcial2, detalle.nota_practica]
                if all(c is not None for c in componentes):
                    ponderado = sum(
                        float(getattr(detalle, nombre_campo)) * peso
                        for nombre_campo, peso in PESOS_FORMULA_FINAL.items()
                    )
                    detalle.nota_final = round(ponderado, 2)

            actualizados += 1

        db.session.commit()
        return {"mensaje": "Calificaciones registradas", "total_actualizados": actualizados}, None, 200