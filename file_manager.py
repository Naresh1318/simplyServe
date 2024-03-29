import os
import shutil
from flask import current_app as app
from flask_login import login_required, current_user
from flask import jsonify, render_template, request, redirect, url_for, Blueprint, send_from_directory
from werkzeug.utils import secure_filename

from utils import list_files_n_dirs


bp = Blueprint("file_manager", __name__)

default_path = os.path.abspath("./linked_dir")
temp_zip_file = os.path.join("temp.tar")
admin_email = os.environ["ADMIN_EMAIL"]


@bp.route("/")
def home():
    """Render home page
    
    Returns:
        Rendered template
    """
    if current_user.is_authenticated:
        return render_template("./index.html", page="Home")
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
    response = {"files": [{"name": i, "size": j, "is_file": True} for i, j in zip(dir_files, dir_file_sizes)],
                "dirs": [{"name": i, "size": "---", "is_file": False} for i in dir_dirs]}
    return jsonify(response)


@bp.route("/linked_dir/<path:path>")
@login_required
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
@login_required
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


@bp.route("/public/<path:path>", methods=["GET"])
def download_public(path):
    path = path.split("/")
    filename = path[-1]
    relative_path = "/".join(path[:-1])
    directory = os.path.join(app.config['UPLOAD_FOLDER'], relative_path)
    return send_from_directory(directory, filename)


@bp.route("/public_uploads", methods=["POST"])
@login_required
def public_uploads():
    if current_user.email != admin_email:
        return jsonify({"ERROR": "User not admin"})
    if len(request.files) < 1:
        return jsonify({"ERROR": "Could not find files to upload"})

    for key in request.files:
        file = request.files[key]
        if file.filename == "":
            return jsonify({"ERROR": "No file uploaded"})

        filename = secure_filename(file.filename)
        folder = request.args.get("folder").split(".")[1]
        if folder != "":
            folder = folder[1:]  # Remove / prefix before join
        upload_dir = os.path.join(app.config["UPLOAD_FOLDER"], folder)
        file.save(os.path.join(upload_dir, filename))
    return jsonify({"INFO": "Uploaded"})


@bp.route("/uploads_ls", methods=["GET"])
@login_required
def uploads_ls():
    if current_user.email != admin_email:
        return jsonify({"ERROR": "User not admin"})
    dir_path = request.args.get("path")
    abs_path = os.path.abspath(os.path.join(app.config["UPLOAD_FOLDER"], dir_path))
    dir_files, dir_file_sizes, dir_dirs = list_files_n_dirs(abs_path)
    response = {"files": [{"name": i, "size": j, "is_file": True} for i, j in zip(dir_files, dir_file_sizes)],
                "dirs": [{"name": i, "size": "---", "is_file": False} for i in dir_dirs]}
    return jsonify(response)


@bp.route("/create_folder", methods=["POST"])
@login_required
def create_folder():
    if current_user.email != admin_email:
        return jsonify({"ERROR": "User not admin"})
    dir_path = request.json["path"].split(".")[1][1:]
    folder_name = request.json["name"]
    abs_dir_path = os.path.join(app.config["UPLOAD_FOLDER"], dir_path)
    try:
        os.mkdir(os.path.join(abs_dir_path, folder_name))
        return jsonify({"INFO": True})
    except FileExistsError as e:
        return jsonify({"ERROR": "Folder exists"})


@bp.route("/rename_item", methods=["POST"])
@login_required
def rename_item():
    if current_user.email != admin_email:
        return jsonify({"ERROR": "User not admin"})
    dir_path = request.json["path"].split(".")[1][1:]
    previous_name = request.json["previous"]
    item_name = request.json["name"]
    abs_dir_path = os.path.join(app.config["UPLOAD_FOLDER"], dir_path)
    previous_path = os.path.join(abs_dir_path, previous_name)
    new_path = os.path.join(abs_dir_path, item_name)
    try:
        os.rename(previous_path, new_path)
        return jsonify({"INFO": "Item renamed"})
    except FileNotFoundError as e:
        return jsonify({"ERROR": "Item not found or already exists"})


@bp.route("/delete_item", methods=["POST"])
@login_required
def delete_item():
    if current_user.email != admin_email:
        return jsonify({"ERROR": "User not admin"})
    dir_path = request.json["path"].split(".")[1][1:]
    item_name = request.json["name"]
    abs_dir_path = os.path.join(app.config["UPLOAD_FOLDER"], dir_path)
    path = os.path.join(abs_dir_path, item_name)
    try:
        if os.path.isdir(path):
            shutil.rmtree(path)
        else:
            os.remove(path)
        return jsonify({"INFO": True})
    except (FileNotFoundError, NotADirectoryError) as e:
        return jsonify({"ERROR": "Item not fount"})
