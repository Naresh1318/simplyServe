import os
from flask_login import login_required, login_user, logout_user, current_user
from werkzeug.security import check_password_hash
from flask import jsonify, render_template, request, redirect, url_for, send_file, Blueprint

from .models import DBUser, add_user


bp = Blueprint("file_manager", __name__)

# Create symbolic link to the required path, this is needed to download files in the appropriate format
default_path: str = os.environ.get("SERVE_DIR")
symbolic_path = "./static/linked_dir"
if os.path.exists(symbolic_path):
    os.remove(symbolic_path)
os.symlink(default_path, symbolic_path)
default_path = os.path.abspath(symbolic_path)


def list_files_n_dirs(path: str):
    """Returns a list of files and directories from the path
    
    Args:
        path (str): directory path
    
    Returns:
        [list, list]: list of files and directories
    """
    files = []
    dirs = []
    for (_, dir_names, file_names) in os.walk(path):
        files.extend(file_names)
        dirs.extend(dir_names)
        return files, dirs


@bp.route("/")
def home():
    """Render home page
    
    Returns:
        Rendered template
    """
    if current_user.is_authenticated:
        return render_template("./index.html")
    else:
        return redirect(url_for("file_manager.login"))


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
    return redirect(url_for("file_manager.login"))


@bp.route("/admin", methods=["POST", "GET"])
@login_required
def admin():
    if current_user.username != "nn":  # TODO: change this to admin
        return redirect(url_for("file_manager.login"))
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


@bp.route("/default_dir")
@login_required
def default_dir():
    """Returns the default home directory as a JSON object
    
    Returns:
        JSON: default home directory
    """
    return jsonify({"default_dir": default_path})


@bp.route("/ls")
@login_required
def ls():
    """Returns a JSON object containing files and folders from the desired path.
    Path must be passed as the request URL parameters with the key 'path'
    
    Returns:
        JSON: {"files": an object containing all the files with numeric indices as keys
               "dirs": an object containing all the directories with numeric indices as keys}
    """
    dir_path = request.args.get("path")
    dir_files, dir_dirs = list_files_n_dirs(dir_path)
    response = {"files": {i: j for i, j in enumerate(dir_files)},
                "dirs": {i: j for i, j in enumerate(dir_dirs)}}
    return jsonify(response) 


@bp.route("/static/linked_dir/<path:path>")
def serve_file(path):
    path = os.path.join("./static/linked_dir", path)
    if current_user.is_authenticated:
        if os.path.exists(path):
            return send_file(path, as_attachment=True)
    return redirect(url_for("file_manager.login"))
