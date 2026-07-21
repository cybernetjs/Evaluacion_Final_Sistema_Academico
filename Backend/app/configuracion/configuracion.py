import os
import secrets
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///sistema_academico.db")
_ES_SQLITE = DATABASE_URL.startswith("sqlite")

class Config:
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = (
        {}
        if _ES_SQLITE
        else {
            "pool_pre_ping": True,
            "pool_recycle": 280,
            "pool_size": 5,
            "max_overflow": 10,
        }
    )
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "token")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)