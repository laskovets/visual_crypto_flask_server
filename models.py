from server import db
from flask_login import UserMixin
from datetime import datetime


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000), unique=True)
    shadow = db.Column(db.Binary())
    # data for experiment
    shadows_generating_count = db.Column(db.Integer, default=0)
    experiments_count = db.Column(db.Integer, default=0)

    def __init__(self, name, email, password, shadow=None):
        self.name = name
        self.email = email
        self.password = password
        self.shadow = shadow
        self.shadows_generating_count = 0
        if shadow is not None:
            self.shadows_generating_count = 1

    def __repr__(self):
        return "<User('%s', '%s', '%s', '%s')>" % (self.name, self.email, self.password, self.shadow)


class Experiments(db.Model):
    __tablename__ = 'experiments'
    id = db.Column(db.Integer, primary_key=True)
    creation_date = db.Column(db.DateTime, default=datetime.utcnow)
    successful = db.Column(db.Boolean, default=False)
    finished = db.Column(db.Boolean, default=False)
    user_email = db.Column(db.String(100))
    fail_counter = db.Column(db.Integer, default=0)
    original_password = db.Column(db.String(100))
    duration = db.Column(db.Integer, default=None)
    failed_passwords = db.Column(db.String(100))

    def __init__(self, user_email, original_password):
        self.original_password = original_password
        self.user_email = user_email


if __name__ == '__main__':
    from server import db, create_app
    db.create_all(app=create_app()) # pass the create_app result so Flask-SQLAlchemy gets the configuration.