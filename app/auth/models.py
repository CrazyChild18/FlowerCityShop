from app import db


class User(db.Model):
    username = db.Column(db.String, index=True, unique=True)
    email = db.Column(db.String, index=True, primary_key=True)
    password = db.Column(db.String, index=True)