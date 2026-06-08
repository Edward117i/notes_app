from flask import Blueprint, render_template, request, redirect, url_for, flash, session

auth_bd = Blueprint("auth", __name__)

@auth_bd.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # Aquí iría la lógica de autenticación
        username = request.form["username"]
        # Aquí iría la verificación de credenciales
        if username == "admin":  # Esto es solo un ejemplo, no uses esto en producción
            session["user"] = username
            return redirect(url_for("notes.home"))
        else:
            flash("Usuario no permitido", "error")
    return render_template("login.html")

@auth_bd.route("/logout")
def logout():
    session.pop("user", None)
    flash("Has cerrado sesión", "success")
    return redirect(url_for("auth.login"))
