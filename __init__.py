import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager


# Change jinja template syntax
class CustomFlask(Flask):
    jinja_options = Flask.jinja_options.copy()
    jinja_options.update(dict(
        variable_start_string='%%',  # Default is '{{', I'm changing this because Vue.js uses '{{' / '}}'
        variable_end_string='%%',
    ))


# db must be initialized here for other files to access it
db_path = os.path.join(os.path.dirname(__file__), "database/users.db")
db = SQLAlchemy()


def create_app():
    """
    Creates and configures the flask app

    """
    # This must be imported here to avoid the chicken and the egg problem
    from . import file_manager

    db_uri = f"sqlite:///{db_path}"

    app = CustomFlask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="dev",
        SQLALCHEMY_DATABASE_URI=db_uri)
    app.register_blueprint(file_manager.bp)
    app.add_url_rule("/", endpoint="home")

    # Initialize login manager
    login_manager = LoginManager()
    login_manager.init_app(app)

    # Initialize database
    db.init_app(app)

    from .models import DBUser

    @login_manager.user_loader
    def user_loader(user_id):
        return DBUser.query.get(int(user_id))

    return app
