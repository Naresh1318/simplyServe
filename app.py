import os
from flask import Flask, jsonify, render_template, request, send_from_directory, url_for


class CustomFlask(Flask):
    jinja_options = Flask.jinja_options.copy()
    jinja_options.update(dict(
        variable_start_string='%%',  # Default is '{{', I'm changing this because Vue.js uses '{{' / '}}'
        variable_end_string='%%',
    ))

# Create symbolic link to the required path, this is needed to download files in the appropriate format
default_path: str = "/home/naresh/Downloads"
symbolic_path = "./static/linked_dir"
if os.path.exists(symbolic_path):
    os.remove(symbolic_path)
os.symlink(default_path, symbolic_path)

default_path = os.path.abspath(symbolic_path)

app = CustomFlask(__name__)  # This replaces your existing "app = Flask(__name__)"

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


@app.route("/")
def home():
    return render_template("./index.html")


@app.route("/default_dir")
def default_dir():
    return jsonify({"default_dir": default_path})


@app.route("/ls")
def ls():
    dir_path = request.args.get("path")
    dir_files , dir_dirs = list_files_n_dirs(dir_path)
    response = {"files": {i: j for i, j in enumerate(dir_files)},
                "dirs": {i: j for i,j in enumerate(dir_dirs)}}
    return jsonify(response) 


@app.route("/download_file")
def download_file():
    directory_path = request.args.get("dir")
    file_name = request.args.get("file")
    try:
        return send_from_directory(directory_path, file_name, as_attachment=True)
    except Exception as e:
        return str(e)

if __name__ == "__main__":
    app.run(debug=True)
    