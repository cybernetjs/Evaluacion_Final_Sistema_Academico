from flask import jsonify, request
from flask_jwt_extended import get_jwt_identity
from datetime import datetime
from app import bcrypt
from app import db
from app.modelos.facultad import Facultad
from app.modelos.especialidad import Especialidad
from app.modelos.plan_de_estudios import PlanDeEstudios
from app.modelos.periodo_academico import PeriodoAcademico
from app.modelos.semestre import Semestre
from app.modelos.usuario import Usuario
from app.modelos.auditoria import Auditoria
from app.modelos.matricula import Matricula
from app.modelos.estudiante import Estudiante
from app.modelos.docente import Docente
from app.modelos.matricula_detalle import MatriculaDetalle
from app.modelos.certificado import Certificado
from app.modelos.configuracion_ciclo_global import ConfiguracionCicloGlobal
from app.utils.ciclo_academico import ESTADOS_CICLO, obtener_configuracion_activa


def listar_facultades():
    facultades = Facultad.query.all()
    return jsonify([
        {"id": f.id, "nombre": f.nombre}
        for f in facultades
    ])


def listar_especialidades():
    especialidades = Especialidad.query.all()
    return jsonify([
        {
            "id": e.id,
            "nombre": e.nombre,
            "facultad_id": e.facultad_id
        }
        for e in especialidades
    ])


def listar_planes_estudio():
    planes = PlanDeEstudios.query.all()
    return jsonify([
        {
            "id": p.id,
            "especialidad_id": p.especialidad_id,
            "anio_creacion": p.anio_creacion,
            "vigente": p.vigente
        }
        for p in planes
    ])


def listar_semestres():
    semestres = Semestre.query.all()
    return jsonify([
        {"id": s.id, "codigo": s.codigo}
        for s in semestres
    ])


def listar_periodos():
    periodos = PeriodoAcademico.query.order_by(PeriodoAcademico.fecha_inicio.desc()).all()
    return jsonify([
        {
            "id": p.id,
            "nombre": p.nombre,
            "fecha_inicio": p.fecha_inicio.isoformat() if p.fecha_inicio else None,
            "fecha_fin": p.fecha_fin.isoformat() if p.fecha_fin else None,
        }
        for p in periodos
    ])


def listar_usuarios():
    usuarios = Usuario.query.all()
    return jsonify([
        {"id": u.id, "username": u.username, "rol": u.rol}
        for u in usuarios
    ])


def registrar_docente():
    data = request.get_json()

    campos_requeridos = ["username", "password", "nombres", "apellido_paterno", "apellido_materno", "correo_institucional"]
    faltantes = [campo for campo in campos_requeridos if not data.get(campo)]

    if faltantes:
        return jsonify({"error": f"Faltan campos requeridos: {faltantes}"}), 400

    username = data.get("username")
    if Usuario.query.filter_by(username=username).first():
        return jsonify({"error": "El nombre de usuario ya está en uso"}), 400

    usuario = Usuario(
        username=username,
        password=bcrypt.generate_password_hash(data.get("password")).decode("utf-8"),
        rol="docente",
    )
    db.session.add(usuario)
    db.session.flush()

    docente = Docente(
        usuario_id=usuario.id,
        nombres=data.get("nombres"),
        apellido_paterno=data.get("apellido_paterno"),
        apellido_materno=data.get("apellido_materno"),
        correo_institucional=data.get("correo_institucional"),
    )
    db.session.add(docente)
    db.session.commit()

    return jsonify({
        "mensaje": "Docente registrado correctamente",
        "usuario_id": usuario.id,
        "docente_id": docente.id,
    }), 201


def cambiar_rol(usuario_id):
    data = request.get_json()
    nuevo_rol = data.get("rol")

    roles_validos = ["estudiante", "docente", "administrador", "direccion"]
    if nuevo_rol not in roles_validos:
        return jsonify({"error": f"Rol inválido. Debe ser uno de: {roles_validos}"}), 400

    usuario = Usuario.query.get(usuario_id)
    if not usuario:
        return jsonify({"error": "Usuario no encontrado"}), 404

    rol_anterior = usuario.rol
    usuario.rol = nuevo_rol

    admin_id = int(get_jwt_identity())
    registro = Auditoria(
        usuario_id=admin_id,
        accion="cambio_de_rol",
        detalle=f"Usuario {usuario.id} cambió de '{rol_anterior}' a '{nuevo_rol}'"
    )
    db.session.add(registro)
    db.session.commit()

    return jsonify({"mensaje": "Rol actualizado correctamente", "usuario_id": usuario.id, "rol": usuario.rol})


def listar_auditorias():
    registros = Auditoria.query.order_by(Auditoria.created_at.desc()).all()
    return jsonify([
        {
            "id": a.id,
            "usuario_id": a.usuario_id,
            "accion": a.accion,
            "detalle": a.detalle,
            "created_at": a.created_at.isoformat() if a.created_at else None
        }
        for a in registros
    ])


def reportes_estrategicos():
    total_estudiantes = Estudiante.query.count()
    total_docentes = Docente.query.count()
    total_matriculas = Matricula.query.count()
    matriculas_confirmadas = Matricula.query.filter_by(estado_id=3).count()

    detalles_con_nota = MatriculaDetalle.query.filter(MatriculaDetalle.nota_final.isnot(None)).all()
    promedio_institucional = None
    if detalles_con_nota:
        suma = sum(float(d.nota_final) for d in detalles_con_nota)
        promedio_institucional = round(suma / len(detalles_con_nota), 2)

    certificados_emitidos = Certificado.query.filter_by(estado="Emitido").count()
    certificados_pendientes = Certificado.query.filter(Certificado.estado != "Emitido").count()

    return jsonify({
        "poblacion": {
            "total_estudiantes": total_estudiantes,
            "total_docentes": total_docentes
        },
        "matricula": {
            "total_solicitudes": total_matriculas,
            "confirmadas": matriculas_confirmadas
        },
        "academico": {
            "promedio_institucional": promedio_institucional
        },
        "certificados": {
            "emitidos": certificados_emitidos,
            "pendientes": certificados_pendientes
        }
    })


def obtener_configuracion_ciclo():
    configuracion = obtener_configuracion_activa()

    return jsonify({
        "periodo_academico_id": configuracion.periodo_academico_id,
        "periodo_academico_nombre": configuracion.periodo_academico.nombre if configuracion.periodo_academico else None,
        "estado_ciclo": configuracion.estado_ciclo,
        "estados_disponibles": ESTADOS_CICLO,
        "fecha_cierre_matricula": configuracion.fecha_cierre_matricula.isoformat() if configuracion.fecha_cierre_matricula else None,
        "fecha_limite_notas": configuracion.fecha_limite_notas.isoformat() if configuracion.fecha_limite_notas else None,
        "fecha_cierre_actas": configuracion.fecha_cierre_actas.isoformat() if configuracion.fecha_cierre_actas else None,
        "actualizado_en": configuracion.actualizado_en.isoformat() if configuracion.actualizado_en else None,
    })


def actualizar_configuracion_ciclo():
    datos = request.get_json()
    configuracion = obtener_configuracion_activa()

    periodo_academico_id = datos.get("periodo_academico_id")
    estado_ciclo = datos.get("estado_ciclo")

    if periodo_academico_id is not None:
        periodo = PeriodoAcademico.query.get(periodo_academico_id)
        if not periodo:
            return jsonify({"error": "El periodo académico indicado no existe"}), 404
        configuracion.periodo_academico_id = periodo_academico_id

    if estado_ciclo is not None:
        if estado_ciclo not in ESTADOS_CICLO:
            return jsonify({"error": "El estado del ciclo indicado no es válido"}), 400
        configuracion.estado_ciclo = estado_ciclo

    for campo in ("fecha_cierre_matricula", "fecha_limite_notas", "fecha_cierre_actas"):
        if campo in datos and datos[campo]:
            try:
                setattr(configuracion, campo, datetime.fromisoformat(datos[campo]))
            except ValueError:
                return jsonify({"error": f"El formato de {campo} no es válido"}), 400

    if (
        configuracion.fecha_cierre_matricula
        and configuracion.fecha_limite_notas
        and configuracion.fecha_limite_notas < configuracion.fecha_cierre_matricula
    ):
        return jsonify({"error": "La fecha límite de notas no puede ser anterior al cierre de matrícula"}), 400

    if (
        configuracion.fecha_limite_notas
        and configuracion.fecha_cierre_actas
        and configuracion.fecha_cierre_actas < configuracion.fecha_limite_notas
    ):
        return jsonify({"error": "La fecha de cierre de actas no puede ser anterior a la fecha límite de notas"}), 400

    db.session.commit()

    return jsonify({"mensaje": "Configuración del ciclo actualizada correctamente"})