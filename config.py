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
