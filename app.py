import os
from flask import Flask, jsonify, render_template, request


# Change jinja template syntax
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
    """Render home page
    
    Returns:
        Rendered template
    """
    return render_template("./index.html")


@app.route("/default_dir")
def default_dir():
    """Returns the default home directory as a JSON object
    
    Returns:
        JSON: default home directory
    """
    return jsonify({"default_dir": default_path})


@app.route("/ls")
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


if __name__ == "__main__":
    app.run(debug=True)
