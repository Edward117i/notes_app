from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user
from models import db, User

auth_bd = Blueprint("auth", __name__)

@auth_bd.route("/register", methods=["GET", "POST"])
def register():
    """Ruta para registrar un nuevo usuario"""
    if current_user.is_authenticated:
        return redirect(url_for("notes.home"))
    
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        # Validaciones
        if not username or not email or not password:
            flash("Por favor completa todos los campos", "error")
            return redirect(url_for("auth.register"))

        if len(password) < 6:
            flash("La contraseña debe tener al menos 6 caracteres", "error")
            return redirect(url_for("auth.register"))

        if password != confirm_password:
            flash("Las contraseñas no coinciden", "error")
            return redirect(url_for("auth.register"))

        # Verificar si el usuario ya existe
        if User.query.filter_by(username=username).first():
            flash("El usuario ya existe", "error")
            return redirect(url_for("auth.register"))

        if User.query.filter_by(email=email).first():
            flash("El email ya está registrado", "error")
            return redirect(url_for("auth.register"))

        # Crear nuevo usuario
        user = User(username=username, email=email)
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()

        flash("¡Registro exitoso! Por favor inicia sesión", "success")
        return redirect(url_for("auth.login"))

    return render_template("register.html")


@auth_bd.route("/login", methods=["GET", "POST"])
def login():
    """Ruta para iniciar sesión"""
    if current_user.is_authenticated:
        return redirect(url_for("notes.home"))
    
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if not username or not password:
            flash("Por favor completa todos los campos", "error")
            return redirect(url_for("auth.login"))

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user)
            flash(f"¡Bienvenido {user.username}!", "success")
            return redirect(url_for("notes.home"))
        else:
            flash("Usuario o contraseña incorrectos", "error")

    return render_template("login.html")


@auth_bd.route("/logout")
def logout():
    """Ruta para cerrar sesión"""
    logout_user()
    flash("Has cerrado sesión exitosamente", "success")
    return redirect(url_for("auth.login"))
