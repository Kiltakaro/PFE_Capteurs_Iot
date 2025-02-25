from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash
import uuid
from sqlalchemy.types import TypeDecorator, String

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

class StringUUID(TypeDecorator):
    """
    Convertit un UUID en string pour PostgreSQL
    """
    impl = String(100)

    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if isinstance(value, uuid.UUID):
            return str(value)
        return value

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        return str(value)


class SensorData(db.Model):
    __tablename__ = 'sensor_data'
    uid = db.Column(StringUUID, primary_key=True, default=lambda: str(uuid.uuid4()))
    # uid = db.Column(db.String(100), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False)
    unit = db.Column(db.String(10), nullable=False)
    description = db.Column(db.String(255), nullable=True)
    min_value = db.Column(db.Float, nullable=True)
    max_value = db.Column(db.Float, nullable=True)
    delta_value = db.Column(db.Float, nullable=True)
    period = db.Column(db.Integer, nullable=True)
    min_period = db.Column(db.Integer, nullable=True)
    max_period = db.Column(db.Integer, nullable=True)
    read_only = db.Column(db.Boolean, default=False)
    value = db.Column(db.Float, nullable=True)
    timestamp = db.Column(db.DateTime, nullable=True, default=db.func.current_timestamp())

    def to_dict(self):
        return {
            'uid': self.uid,
            'name': self.name,
            'unit': self.unit,
            'description': self.description,
            'min_value': self.min_value,
            'max_value': self.max_value,
            'delta_value': self.delta_value,
            'period': self.period,
            'min_period': self.min_period,
            'max_period': self.max_period,
            'read_only': self.read_only,
            'value': self.value,
            'timestamp': self.timestamp
        }


class SensorHistory(db.Model):
    __tablename__ = 'sensor_history'
    id = db.Column(db.Integer, primary_key=True)
    sensor_uid = db.Column(StringUUID, db.ForeignKey('sensor_data.uid'), nullable=False)
    value = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())
    sensor = db.relationship('SensorData', backref=db.backref('history', lazy=True))

    def to_dict(self):
        return {
            'id': self.id,
            'sensor_uid': str(self.sensor_uid),
            'value': self.value,
            'timestamp': self.timestamp
        }
    

class SensorTemplate(db.Model):
    __tablename__ = 'sensor_templates'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.String(255), nullable=True)
    unit = db.Column(db.String(10), nullable=False)
    min_value = db.Column(db.Float, nullable=False)
    max_value = db.Column(db.Float, nullable=False)
    delta_value = db.Column(db.Float, default=1)
    period = db.Column(db.Integer, nullable=False)
    min_period = db.Column(db.Integer, default=60)
    max_period = db.Column(db.Integer, default=3600)
    read_only = db.Column(db.Boolean, default=False)
