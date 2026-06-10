import os

DB_FILE_PATH = os.path.join(os.path.dirname(__file__), "notes.sqlite")


class Config:
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{DB_FILE_PATH}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "connect_args": {"timeout": 15, "check_same_thread": False},
        "pool_recycle": 3600,
        "pool_pre_ping": True,
    }
    SECRET_KEY ="this-is-not-secret"
    
    # Configuración de caché
    CACHE_TYPE = "SimpleCache"
    CACHE_DEFAULT_TIMEOUT = 300

class TestConfig:
    """Configuración para pruebas unitarias"""
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"  # Base de datos en memoria para pruebas más rápidas
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "connect_args": {"timeout": 15, "check_same_thread": False},
        "pool_recycle": 3600,
        "pool_pre_ping": True,
    }
    SECRET_KEY = "test-secret-key-do-not-use-in-production"
    TESTING = True
    WTF_CSRF_ENABLED = False  # Deshabilitar CSRF para pruebas
    PRESERVE_CONTEXT_ON_EXCEPTION = False
    
    # Desactivar caché en tests
    CACHE_TYPE = "NullCache"

    
