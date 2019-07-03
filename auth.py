from werkzeug.security import check_password_hash
from flask import request, render_template, Blueprint, redirect, url_for
from flask_login import logout_user, login_user, current_user, login_required

from .models import DBUser, add_user

bp = Blueprint("auth", __name__)


@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("./login.html")

    email = request.form["email"]
    password = request.form["password"]

    user = DBUser.query.filter_by(email=email).first()

    if not user or not check_password_hash(user.password, password):
        return "Bad guy ;)"

    login_user(user, remember=True)
    return redirect(url_for("file_manager.home"))


@bp.route("/logout")
def logout():
    if current_user.is_authenticated:
        message = f"{current_user.username} logged out"
        logout_user()
        return message
    return redirect(url_for("auth.login"))


@bp.route("/admin", methods=["POST", "GET"])
@login_required
def admin():
    if current_user.username != "nn":  # TODO: change this to admin
        return redirect(url_for("file_manager.home"))
    if request.method == "GET":
        return render_template("admin.html")
    email = request.form["email"]
    password = request.form["password"]
    username = request.form["username"]

    user = DBUser.query.filter_by(email=email).first()
    if not user:
        add_user(email, password, username)
        return f"{username} added!"
    return "Email id taken"
