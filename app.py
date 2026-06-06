from flask import Flask, request
from config import Config
from models import db
from notes.routes import notes_bp

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

# Registrar el Blueprint
app.register_blueprint(notes_bp)


@app.route("/acerca-de")
def about():
    return "Esta es una aplicación Flask de ejemplo."


@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        return "Formulario enviado correctamente", 201
    return "Pagina de contacto"