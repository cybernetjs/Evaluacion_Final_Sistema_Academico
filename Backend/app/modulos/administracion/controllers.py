from flask import jsonify, request
from flask_jwt_extended import get_jwt_identity
from app import db
from app.modelos.facultad import Facultad
from app.modelos.especialidad import Especialidad
from app.modelos.plan_de_estudios import PlanDeEstudios
from app.modelos.semestre import Semestre
from app.modelos.usuario import Usuario
from app.modelos.auditoria import Auditoria
from app.modelos.matricula import Matricula
from app.modelos.estudiante import Estudiante
from app.modelos.docente import Docente
from app.modelos.matricula_detalle import MatriculaDetalle
from app.modelos.certificado import Certificado


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


def listar_usuarios():
    usuarios = Usuario.query.all()
    return jsonify([
        {"id": u.id, "username": u.username, "rol": u.rol}
        for u in usuarios
    ])


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

    admin_id = get_jwt_identity()
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

    certificados_emitidos = Certificado.query.filter_by(emitido=True).count()
    certificados_pendientes = Certificado.query.filter_by(emitido=False).count()

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