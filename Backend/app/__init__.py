from flask import Flask
from flask_cors import CORS


def crear_app():
    app = Flask(__name__)
    CORS(app)

    @app.route("/")
    def inicio():
        return "El backend esta prendido"

    return app