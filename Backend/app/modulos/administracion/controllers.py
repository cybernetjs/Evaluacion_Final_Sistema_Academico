from flask import jsonify, request
from flask_jwt_extended import get_jwt_identity
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
from app.modelos.configuracion_sistema import ConfiguracionSistema
from app.modelos.estado_matricula import EstadoMatricula


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


def registrar_personal():
    data = request.get_json()

    campos_requeridos = ["username", "password", "rol"]
    faltantes = [campo for campo in campos_requeridos if not data.get(campo)]

    if faltantes:
        return jsonify({"error": f"Faltan campos requeridos: {faltantes}"}), 400

    roles_validos = ["administrador", "direccion"]
    rol = data.get("rol")
    if rol not in roles_validos:
        return jsonify({"error": f"Rol inválido. Debe ser uno de: {roles_validos}"}), 400

    username = data.get("username")
    if Usuario.query.filter_by(username=username).first():
        return jsonify({"error": "El nombre de usuario ya está en uso"}), 400

    usuario = Usuario(
        username=username,
        password=bcrypt.generate_password_hash(data.get("password")).decode("utf-8"),
        rol=rol,
    )
    db.session.add(usuario)
    db.session.commit()

    admin_id = int(get_jwt_identity())
    registro = Auditoria(
        usuario_id=admin_id,
        accion="registrar_personal",
        detalle=f"Se creó la cuenta '{username}' con rol '{rol}'",
    )
    db.session.add(registro)
    db.session.commit()

    return jsonify({
        "mensaje": "Cuenta de personal registrada correctamente",
        "usuario_id": usuario.id,
        "rol": usuario.rol,
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
    pagina = request.args.get("pagina", 1, type=int)
    por_pagina = request.args.get("por_pagina", 20, type=int)
    usuario_id = request.args.get("usuario_id", type=int)
    accion = request.args.get("accion", type=str)
    fecha_inicio = request.args.get("fecha_inicio", type=str)
    fecha_fin = request.args.get("fecha_fin", type=str)

    consulta = Auditoria.query

    if usuario_id:
        consulta = consulta.filter(Auditoria.usuario_id == usuario_id)
    if accion:
        consulta = consulta.filter(Auditoria.accion == accion)
    if fecha_inicio:
        consulta = consulta.filter(Auditoria.created_at >= fecha_inicio)
    if fecha_fin:
        consulta = consulta.filter(Auditoria.created_at <= fecha_fin)

    consulta = consulta.order_by(Auditoria.created_at.desc())
    paginado = consulta.paginate(page=pagina, per_page=por_pagina, error_out=False)

    return jsonify({
        "total": paginado.total,
        "pagina": pagina,
        "por_pagina": por_pagina,
        "registros": [
            {
                "id": a.id,
                "usuario_id": a.usuario_id,
                "accion": a.accion,
                "detalle": a.detalle,
                "created_at": a.created_at.isoformat() if a.created_at else None
            }
            for a in paginado.items
        ],
    })


def reportes_estrategicos():
    total_estudiantes = Estudiante.query.count()
    total_docentes = Docente.query.count()
    total_matriculas = Matricula.query.count()

    estado_matriculado = EstadoMatricula.query.filter_by(nombre="Matriculado").first()
    matriculas_confirmadas = (
        Matricula.query.filter_by(estado_id=estado_matriculado.id).count()
        if estado_matriculado else 0
    )

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


def obtener_configuracion():
    configuracion = ConfiguracionSistema.query.first()
    if not configuracion:
        return jsonify({"error": "No hay configuracion del sistema registrada"}), 404

    return jsonify({
        "matricula_habilitada": configuracion.matricula_habilitada,
        "estado_ciclo": configuracion.estado_ciclo,
        "actualizado": configuracion.updated_at.isoformat() if configuracion.updated_at else None,
    })


def actualizar_configuracion():
    data = request.get_json() or {}

    configuracion = ConfiguracionSistema.query.first()
    if not configuracion:
        configuracion = ConfiguracionSistema()
        db.session.add(configuracion)

    if "matricula_habilitada" in data:
        configuracion.matricula_habilitada = bool(data.get("matricula_habilitada"))
    if "estado_ciclo" in data:
        configuracion.estado_ciclo = data.get("estado_ciclo")

    admin_id = int(get_jwt_identity())
    configuracion.actualizado_por_id = admin_id

    registro = Auditoria(
        usuario_id=admin_id,
        accion="actualizar_configuracion_sistema",
        detalle=f"matricula_habilitada={configuracion.matricula_habilitada}, estado_ciclo={configuracion.estado_ciclo}",
    )
    db.session.add(registro)
    db.session.commit()

    return jsonify({
        "mensaje": "Configuracion actualizada correctamente",
        "matricula_habilitada": configuracion.matricula_habilitada,
        "estado_ciclo": configuracion.estado_ciclo,
    })