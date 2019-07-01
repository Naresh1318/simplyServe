from flask_login import UserMixin
from . import db


class DBUser(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.Text, unique=True)
    password = db.Column(db.Text, nullable=False)
    username = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f"<DBUser: {self.username}>"
