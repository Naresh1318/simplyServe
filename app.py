import os
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_required, login_user, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, jsonify, render_template, request, redirect, url_for, send_file


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

# Configure flask
app = CustomFlask(__name__)  # This replaces your existing "app = Flask(__name__)"
app.secret_key = "sweetlittletest"  # TODO: Change this

db_path = os.path.join(os.path.dirname(__file__), "database/users.db")
db_uri = f"sqlite:///{db_path}"
app.config["SQLALCHEMY_DATABASE_URI"] = db_uri  # TODO: Turn off SQLAlchemy warning during production

login_manager = LoginManager()
login_manager.init_app(app)

db = SQLAlchemy(app)


class DBUser(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.Text, unique=True)
    password = db.Column(db.Text, nullable=False)
    username = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f"<DBUser: {self.username}>"


# Run db.create_all() at this line to generate the required tables
if not os.path.exists(db_path):
    db.create_all()


def add_user(email, password, name):
    user = DBUser(email=email, password=generate_password_hash(password), username=name)
    db.session.add(user)
    db.session.commit()


@login_manager.user_loader
def user_loader(user_id):
    return DBUser.query.get(int(user_id))


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
    if current_user.is_authenticated:
        return render_template("./index.html")
    else:
        return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("./login.html")

    email = request.form["email"]
    password = request.form["password"]

    user = DBUser.query.filter_by(email=email).first()

    if not user or not check_password_hash(user.password, password):
        return "Bad guy ;)"

    login_user(user, remember=True)
    return redirect(url_for("home"))


@app.route("/logout")
def logout():
    if current_user.is_authenticated:
        message = f"{current_user.username} logged out"
        logout_user()
        return message
    return redirect(url_for("login"))


@app.route("/admin", methods=["POST", "GET"])
@login_required
def admin():
    if current_user.username != "nn":  # TODO: change this to admin
        return redirect(url_for("login"))
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


@app.route("/default_dir")
@login_required
def default_dir():
    """Returns the default home directory as a JSON object
    
    Returns:
        JSON: default home directory
    """
    return jsonify({"default_dir": default_path})


@app.route("/ls")
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


@app.route("/static/linked_dir/<path:path>")
def serve_file(path):
    path = os.path.join("./static/linked_dir", path)
    if current_user.is_authenticated:
        if os.path.exists(path):
            return send_file(path, as_attachment=True)
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)
