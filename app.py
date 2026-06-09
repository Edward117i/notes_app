from flask import Flask, request
from flask_login import LoginManager
from config import Config
from models import db, User
from notes.routes import notes_bp
from auth.routes import auth_bd

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

# Inicializar Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Por favor inicia sesión'
login_manager.login_message_category = 'warning'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Registrar el Blueprint
app.register_blueprint(notes_bp)
app.register_blueprint(auth_bd)



@app.route("/acerca-de")
def about():
    return "Esta es una aplicación Flask de ejemplo."


@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        return "Formulario enviado correctamente", 201
    return "Pagina de contacto"