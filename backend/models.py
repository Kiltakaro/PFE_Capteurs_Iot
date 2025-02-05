from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)  # Mot de passe hashé
    is_admin = db.Column(db.Boolean, default=False)  # False = user, True = admin

    def set_password(self, password):
        """Hash et stocke le mot de passe."""
        self.password = generate_password_hash(password)


class SensorData(db.Model):
    __tablename__ = 'sensor_data'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    unit = db.Column(db.String(10), nullable=False)
    # uid = db.Column(db.String(100), nullable=False)
    # description = db.Column(db.String(255), nullable=True)
    # min_value = db.Column(db.Float, nullable=True)
    # max_value = db.Column(db.Float, nullable=True)
    # delta_value = db.Column(db.Float, nullable=True)
    # period = db.Column(db.Integer, nullable=True)
    # min_period = db.Column(db.Integer, nullable=True)
    # max_period = db.Column(db.Integer, nullable=True)
    # read_only = db.Column(db.Boolean, default=False)
    # value = db.Column(db.Float, nullable=True)
    # timestamp = db.Column(db.DateTime, nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'unit': self.unit,
        }
