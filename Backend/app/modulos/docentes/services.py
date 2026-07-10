from app import bcrypt, db
from app.modelos.docente import Docente
from app.modelos.usuario import Usuario

class DocenteService:
    def __init__(self):
        pass

    def listar_docentes(self)->list:  #:
        '''
            Función especializada en listar todos los docentes del sistema
            
            @return Docente
        '''

        docentes = Docente.query.all()
        
        return docentes

    '''
        Función especializada en obtener un docente por id
        
        @param id: id del docente
        @returnretorna un JSON con el docente que se encuentra registrado en la base de datos.
    '''
    def obtener_docente(self, id: int | None)->Docente:
        '''
            Función especializada en obtener un docente por id
            
            @param id: id del docente
            @return jsonify -> list[dict[str | int]]
        '''

        docente = Docente.query.get_or_404(id)
        
        return docente

    def registrar_docente(self, data: dict) -> Docente:
        '''
            Función especializada en registrar un docente
            
            @param data: datos del docente
            @return Docente
        '''
        # Contraseña por defecto: dni
        usuario = Usuario(
            username=data.get("username"),
            password=bcrypt.generate_password_hash(data.get("dni")).decode("utf-8"),
            rol="docente",
        )

        db.session.add(usuario)
        db.session.flush()

        docente = Docente(
            usuario_id=usuario.id,
            nombres=data.get("nombres"),
            apellido_paterno=data.get("apellido_paterno"),
            apellido_materno=data.get("apellido_materno"),
            dni=data.get("dni"),
            correo_institucional=data.get("correo_institucional"),
        )

        db.session.add(docente)
        db.session.commit()

        # ---------------------
        # Respuesta
        # ---------------------
        return docente

    def actualizar_docente(self, id: int, data: dict) -> Docente:
        """
            Función especializada en actualizar un docente por id
            
            @param id: id del docente
            @param data: datos del docente
            @return Docente
        """

        # ---------------------
        # Verificar Campos
        # ---------------------
        campos_permitidos = [
            "username", 
            "password", 
            "nombres", 
            "apellido_paterno", 
            "apellido_materno", 
            "correo_institucional"
        ]

        # ---------------------
        # Validaciones de Negocio
        # --------------------- 

        docente = Docente.query.get_or_404(id)

        # Actualizar campos del Usuario asociado si están presentes
        username = data.pop("username", None)
        if username and docente.usuario:
            docente.usuario.username = username
            db.session.add(docente.usuario)

        # Actualizar campos de Docente
        if data:
            Docente.query.filter_by(id=id).update(data)
        
        db.session.commit()

        return docente

    def eliminar_docente(self, id: int) -> None:
        usuario = Usuario.query.get_or_404(id)
        docente = Docente.query.get_or_404(id)

        db.session.delete(docente)
        db.session.commit()

        # --- No hace falta gracias al DELETE CASCADE ---
        # db.session.delete(usuario)