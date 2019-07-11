from werkzeug.security import check_password_hash
from flask import request, render_template, Blueprint, redirect, url_for, jsonify
from flask_login import logout_user, login_user, current_user, login_required

from .models import DBUser, db_add_user, db_delete_user

admin_username = "nn"
bp = Blueprint("auth", __name__)


@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("./login.html")

    email = request.json["email"]
    password = request.json["password"]

    user = DBUser.query.filter_by(email=email).first()

    if not user or not check_password_hash(user.password, password):
        return jsonify({"logged_in": False})

    login_user(user, remember=True)
    return jsonify({"logged_in": True})


@bp.route("/logout")
def logout():
    if current_user.is_authenticated:
        logout_user()
        return redirect(url_for("file_manager.home"))
    return redirect(url_for("auth.login"))


@bp.route("/admin", methods=["GET"])
@login_required
def admin():
    if current_user.username != admin_username:
        return redirect(url_for("file_manager.home"))
    if request.method == "GET":
        return render_template("admin.html")


@bp.route("/add_user", methods=["POST"])
@login_required
def add_user():
    if current_user.username != admin_username:
        return redirect(url_for("file_manager.home"))
    email = request.json["email"]
    password = request.json["password"]
    username = request.json["username"]

    user = DBUser.query.filter_by(email=email).first()
    if not user:
        db_add_user(email, password, username)
        return jsonify({"user_added": True})
    return jsonify({"user_added": False})


@bp.route("/delete_user", methods=["POST"])
@login_required
def delete_user():
    if current_user.username != admin_username:
        return redirect(url_for("file_manager.home"))
    email = request.json["email"]

    user = DBUser.query.filter_by(email=email).first()
    if user:
        db_delete_user(user)
        return jsonify({"user_deleted": True})
    return jsonify({"user_deleted": False})


@bp.route("/is_admin", methods=["GET"])
@login_required
def is_admin():
    if current_user.username != admin_username:
        return jsonify({"admin": False})
    else:
        return jsonify({"admin": True})


@bp.route("/get_username", methods=["GET"])
@login_required
def get_username():
    return jsonify({"username": current_user.username})
