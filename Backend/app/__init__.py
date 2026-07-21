import os

from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt

from app.configuracion.configuracion import Config

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
bcrypt = Bcrypt()


def crear_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    origenes_permitidos = [
        "http://localhost:5173",
        os.getenv("FRONTEND_URL", "https://evaluacion-final-sistema-academico.vercel.app"),
    ]

    CORS(app, resources={
        r"/api/*": {
            "origins": origenes_permitidos,
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })

    db.init_app(app)
    migrate.init_app(app, db, directory='migraciones')
    jwt.init_app(app)
    bcrypt.init_app(app)

    from app.modulos.autenticacion.presentacion.rutas import auth_bp
    from app.modulos.matriculas.presentacion.rutas import matricula_bp
    from app.modulos.notas.presentacion.rutas import notas_bp
    from app.modulos.cursos_docentes.presentacion.rutas import cursos_docentes_bp
    from app.modulos.administracion.presentacion.rutas import administracion_bp, admin_bp
    from app.modulos.certificados.presentacion.rutas import certificados_bp
    from app.modulos.record_academico.presentacion.rutas import record_academico_bp
    from app.modulos.docentes.presentacion.rutas import docentes_bp
    from app.modulos.cursos.presentacion.rutas import cursos_bp
    from app.modulos.ofertas_academicas.presentacion.rutas import ofertas_academicas_bp
    from app.modulos.periodos_academicos.presentacion.rutas import periodos_academicos_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(matricula_bp, url_prefix='/api/matriculas')
    app.register_blueprint(notas_bp, url_prefix='/api/notas')
    app.register_blueprint(docentes_bp, url_prefix='/api/docentes')
    app.register_blueprint(cursos_bp, url_prefix='/api/cursos')
    app.register_blueprint(cursos_docentes_bp, url_prefix='/api/cursos-docentes')
    app.register_blueprint(administracion_bp, url_prefix='/api/administracion')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(certificados_bp, url_prefix='/api/documentos')
    app.register_blueprint(record_academico_bp, url_prefix='/api/record-academico')
    app.register_blueprint(ofertas_academicas_bp, url_prefix='/api/ofertas-academicas')
    app.register_blueprint(periodos_academicos_bp, url_prefix='/api/periodos-academicos')

    return app