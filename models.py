import os
from flask_login import UserMixin
from werkzeug.security import generate_password_hash
from . import db


class DBUser(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.Text, unique=True)
    password = db.Column(db.Text, nullable=False)
    username = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f"<DBUser: {self.username}>"


def db_add_user(email, password, name):
    user = DBUser(email=email, password=generate_password_hash(password), username=name)
    db.session.add(user)
    db.session.commit()


def db_delete_user(user):
    db.session.delete(user)
    db.session.commit()


# Run db.create_all() at this line to generate the required tables
db_path = os.path.join(os.path.dirname(__file__), "database/users.db")
if not os.path.exists(db_path):
    db.create_all()
