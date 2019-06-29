import os
from flask import Flask, jsonify, render_template, request


class CustomFlask(Flask):
    jinja_options = Flask.jinja_options.copy()
    jinja_options.update(dict(
        variable_start_string='%%',  # Default is '{{', I'm changing this because Vue.js uses '{{' / '}}'
        variable_end_string='%%',
    ))


app = CustomFlask(__name__)  # This replaces your existing "app = Flask(__name__)"

default_path: str = "/home/naresh/Projects/imagenet_training"

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

if __name__ == "__main__":
    app.run(debug=True)
    