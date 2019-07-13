import os
from flask_login import login_required, current_user
from flask import jsonify, render_template, request, redirect, url_for, Blueprint, send_from_directory

from utils import list_files_n_dirs


bp = Blueprint("file_manager", __name__)

default_path = os.path.abspath("./linked_dir")
temp_zip_file = os.path.join("temp.tar")


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
    dir_files, dir_file_sizes, dir_dirs = list_files_n_dirs(dir_path)
    response = {"files": [{"name": i, "size": j} for i, j in zip(dir_files, dir_file_sizes)],
                "dirs": [{"name": i} for i in dir_dirs]}
    return jsonify(response)


@bp.route("/linked_dir/<path:path>")
def serve_file(path):
    path = os.path.join("./linked_dir", path)
    if ".." in path or "~" in path:
        return redirect(url_for("file_manager.home"))
    if current_user.is_authenticated:
        if os.path.exists(path):
            path = path.split("linked_dir")[1][1:]  # Remove full path and forward slash
            return send_from_directory(default_path, path, as_attachment=True)
    return redirect(url_for("auth.login"))  # TODO: This redirection causes the login page to be downloaded


@bp.route("/server_name", methods=["GET"])
def server_name():
    return jsonify({"server_name": os.getenv("SERVER_NAME")})


@bp.route("/download_selected", methods=["POST"])
@login_required
def download_selected():
    selected_dir = request.json["dir"]
    selected_files = request.json["files"]
    zipping_command = f"tar -c --use-compress-program=pigz -f {temp_zip_file} -C {selected_dir} "  # TODO: Limit #cores
    for file in selected_files:
        file_name = file["name"]
        selected_path = os.path.abspath(os.path.join(selected_dir, file_name))
        if os.path.exists(selected_path):
            zipping_command += "'" + file_name + "'" + " "  # Include file names with spaces
    os.system(zipping_command)
    return send_from_directory(".", temp_zip_file, as_attachment=True)
