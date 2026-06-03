from flask import Flask, redirect, request, jsonify, render_template, url_for

app = Flask(__name__)

import os
from flask_sqlalchemy import SQLAlchemy

DB_FILE_PATH = os.path.join(os.path.dirname(__file__), 'notes.sqlite')

app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_FILE_PATH}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'connect_args': {'timeout': 15, 'check_same_thread': False},
    'pool_recycle': 3600,
    'pool_pre_ping': True
}

db = SQLAlchemy(app)

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    content = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f'<Note {self.id}: {self.title}>'

@app.route('/')
def home():
    notes = Note.query.all()
    return render_template('home.html', notes=notes)

@app.route('/about')
def about():
    return "Esta es una aplicación Flask de ejemplo."

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        return "Formulario enviado correctamente", 201
    return "Pagina de contacto"

@app.route('/api/info')
def api_info(): 
    data = {
        "nombre": "Notes App",
        "version": "1.0.0"
    }
    return jsonify(data)

@app.route('/confirmation')
def confirmation():
    return "Prueba"

@app.route("/crear-nota", methods=['GET', 'POST'])
def create_note():
    if request.method == 'POST':
        title = request.form.get('title', '')
        content = request.form.get('content', '')
        
        note_db = Note(title=title, content=content)
        db.session.add(note_db)
        db.session.commit()
        
        return redirect(url_for('home'))
    
    return render_template('note_form.html')

@app.route("/editar-nota/<int:id>", methods=['GET', 'POST'])
def edit_note(id):
    note = Note.query.get_or_404(id)
    
    if request.method == 'POST':
        note.title = request.form.get('title', '')
        note.content = request.form.get('content', '')
        
        db.session.commit()
        
        return redirect(url_for('home'))
    
    return render_template('edit_form.html', note=note)
