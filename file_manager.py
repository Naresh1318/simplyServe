import os
from flask_login import login_required, current_user
from flask import jsonify, render_template, request, redirect, url_for, send_file, Blueprint


bp = Blueprint("file_manager", __name__)

default_path = os.path.abspath("./static/linked_dir")


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
        return redirect(url_for("auth.login"))


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
    if "linked_dir" not in dir_path or ".." in dir_path or "~" in dir_path:
        return redirect(url_for("file_manager.home"))
    dir_files, dir_dirs = list_files_n_dirs(dir_path)
    response = {"files": [{"name": j} for _, j in enumerate(dir_files)],
                "dirs": [{"name": j} for _, j in enumerate(dir_dirs)]}
    return jsonify(response)


@bp.route("/static/linked_dir/<path:path>")
def serve_file(path):
    path = os.path.join("./static/linked_dir", path)
    if ".." in path or "~" in path:
        return redirect(url_for("file_manager.home"))
    if current_user.is_authenticated:
        if os.path.exists(path):
            return send_file(path, as_attachment=True)
    return redirect(url_for("auth.login"))  # TODO: This redirection causes the login page to be downloaded


@bp.route("/server_name", methods=["GET"])
def server_name():
    return jsonify({"server_name": os.getenv("SERVER_NAME")})
