from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from app.config import Config

db = SQLAlchemy()
migrate = Migrate()


def crear_app():
    app = Flask(__name__)
    
    from app.modulos.matricula.routes import matricula_bp
    from app.modulos.notas.routes import notas_bp
    from app.modulos.cursos_docentes.routes import cursos_docentes_bp
    from app.modulos.administracion.routes import administracion_bp
    from app.modulos.certificados.routes import certificados_bp
    from app.modulos.record_academico.routes import record_academico_bp

    app.register_blueprint(matricula_bp, url_prefix='/api/matriculas')
    app.register_blueprint(notas_bp, url_prefix='/api/notas')
    app.register_blueprint(cursos_docentes_bp, url_prefix='/api/cursos-docentes')
    app.register_blueprint(administracion_bp, url_prefix='/api/administracion')
    app.register_blueprint(certificados_bp, url_prefix='/api/certificados')
    app.register_blueprint(record_academico_bp, url_prefix='/api/record-academico')

    return app