from app import db, bcrypt
from app.dominio.modelos.identidad.usuario import Usuario
from app.dominio.modelos.estudiantes.estudiante import Estudiante

class AuthService:

    @staticmethod
    def registrar_estudiante(username: str, password: str, nombres: str, apellido_paterno: str, apellido_materno: str, dni: str, correo_institucional: str, especialidad_id: int, plan_estudios_id: int = None) -> tuple[dict | None]:
        from app.dominio.modelos.academico.plan_de_estudios import PlanDeEstudios
        from app.dominio.modelos.estudiantes.plan_estudiante import PlanEstudiante

        if Usuario.query.filter_by(username=username).first():
            return None, "El nombre de usuario ya está en uso"

        if Estudiante.query.filter_by(dni=dni).first():
            return None, "Ya existe un estudiante registrado con ese DNI"

        plan = None
        if plan_estudios_id:
            plan = PlanDeEstudios.query.get(plan_estudios_id)
            if not plan:
                return None, "El plan de estudios seleccionado no existe"
            if plan.especialidad_id != especialidad_id:
                return None, "El plan de estudios seleccionado no pertenece a la especialidad indicada"
        else:

            plan = (
                PlanDeEstudios.query.filter_by(especialidad_id=especialidad_id, vigente=True)
                .order_by(PlanDeEstudios.anio_creacion.desc())
                .first()
            )

        password_encriptado = bcrypt.generate_password_hash(password).decode("utf-8")

        usuario = Usuario(username=username, password=password_encriptado, rol="estudiante")
        db.session.add(usuario)
        db.session.flush()

        estudiante = Estudiante(
            usuario_id=usuario.id,
            especialidad_id=especialidad_id,
            nombres=nombres,
            apellido_paterno=apellido_paterno,
            apellido_materno=apellido_materno,
            dni=dni,
            correo_institucional=correo_institucional
        )
        db.session.add(estudiante)
        db.session.flush()

        if plan:
            db.session.add(PlanEstudiante(estudiante_id=estudiante.id, plan_estudios_id=plan.id))

        db.session.commit()

        return {
            "usuario_id": usuario.id,
            "estudiante_id": estudiante.id,
            "plan_estudios_id": plan.id if plan else None,
            "aviso": None if plan else "No se encontró un plan de estudios vigente para esta especialidad; el estudiante no podrá matricularse hasta que se le asigne uno."
        }, None