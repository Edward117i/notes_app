from flask import flash, render_template, request, redirect, url_for, Blueprint
from flask_login import login_required, current_user
from models import Note, db

notes_bp = Blueprint("notes", __name__)

@notes_bp.route("/")
@login_required
def home():
    flash(f"¡Bienvenido de vuelta, {current_user.username}!", "info")
    notes = Note.query.filter_by(user_id=current_user.id).all()
    return render_template("home.html", notes=notes)


@notes_bp.route("/crear-nota", methods=["GET", "POST"])
@login_required
def create_note():
    if request.method == "POST":
        title = request.form.get("title", "")
        content = request.form.get("content", "")

        if not title or not content:
            flash("Por favor completa todos los campos", "error")
            return redirect(url_for("notes.create_note"))

        note_db = Note(title=title, content=content, user_id=current_user.id)
        db.session.add(note_db)
        db.session.commit()
        flash("Nota creada exitosamente", "success")

        return redirect(url_for("notes.home"))

    return render_template("note_form.html")


@notes_bp.route("/editar-nota/<int:id>", methods=["GET", "POST"])
@login_required
def edit_note(id):
    note = Note.query.get_or_404(id)
    
    # Verificar que el usuario sea el propietario de la nota
    if note.user_id != current_user.id:
        flash("No tienes permiso para editar esta nota", "error")
        return redirect(url_for("notes.home"))

    if request.method == "POST":
        note.title = request.form.get("title", "")
        note.content = request.form.get("content", "")

        if not note.title or not note.content:
            flash("Por favor completa todos los campos", "error")
            return redirect(url_for("notes.edit_note", id=id))

        db.session.commit()
        flash("Nota actualizada exitosamente", "success")

        return redirect(url_for("notes.home"))

    return render_template("edit_form.html", note=note)


@notes_bp.route("/eliminar-nota/<int:id>", methods=["GET", "POST"])
@login_required
def delete_note(id):
    note = Note.query.get_or_404(id)
    
    # Verificar que el usuario sea el propietario de la nota
    if note.user_id != current_user.id:
        flash("No tienes permiso para eliminar esta nota", "error")
        return redirect(url_for("notes.home"))

    if request.method == "POST":
        db.session.delete(note)
        db.session.commit()
        flash("Nota eliminada exitosamente", "success")

        return redirect(url_for("notes.home"))

    return render_template("delete_form.html", note=note)