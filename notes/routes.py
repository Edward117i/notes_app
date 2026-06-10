from flask import flash, render_template, request, redirect, url_for, Blueprint, jsonify
from flask_login import login_required, current_user
from models import Note, db

notes_bp = Blueprint("notes", __name__)

@notes_bp.route("/")
@login_required
def home():
    flash(f"¡Bienvenido de vuelta, {current_user.username}!", "info")
    page = request.args.get('page', 1, type=int)
    per_page = 9
    notes = Note.query.filter_by(user_id=current_user.id)\
        .order_by(Note.created_at.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)
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
        # Responder JSON si es una petición AJAX
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'status': 'error', 'message': 'No tienes permiso para eliminar esta nota'}), 403
        flash("No tienes permiso para eliminar esta nota", "error")
        return redirect(url_for("notes.home"))

    if request.method == "POST":
        db.session.delete(note)
        db.session.commit()
        
        # Responder JSON si es una petición AJAX
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'status': 'success', 'message': 'Nota eliminada exitosamente'})
        
        flash("Nota eliminada exitosamente", "success")
        return redirect(url_for("notes.home"))

    return render_template("delete_form.html", note=note)


@notes_bp.route("/buscar-notas")
@login_required
def search_notes():
    """Endpoint para búsqueda en tiempo real de notas (AJAX)"""
    query = request.args.get('q', '').strip()
    page = request.args.get('page', 1, type=int)
    per_page = 9
    
    base_query = Note.query.filter_by(user_id=current_user.id)
    
    if query:
        base_query = base_query.filter(
            db.or_(
                Note.title.ilike(f'%{query}%'),
                Note.content.ilike(f'%{query}%')
            )
        )
    
    pagination = base_query.order_by(Note.created_at.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'status': 'success',
        'data': [note.to_dict() for note in pagination.items],
        'pagination': {
            'page': pagination.page,
            'pages': pagination.pages,
            'total': pagination.total,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev
        }
    })