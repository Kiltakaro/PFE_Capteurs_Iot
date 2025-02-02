from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required
from werkzeug.security import check_password_hash, generate_password_hash


from models import db, User, SensorData

import uuid

app = Flask(__name__)
# Configuration CORS

origins = [
    "http://localhost",
    "http://localhost:8080",
    "http://127.0.0.1:5000",
    "http://frontend",
    "http://frontend:8080",
    "http://frontend:5000",
    "http://backend",
    "http://backend:8080",
    "http://backend:5000",
    "null"
]

CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)

# CORS(app, resources={r"/*": {"origins": origins}}, supports_credentials=True)



############## TEST BASE DE DONNES SQLLITE ###############

# Configuration de la base de données
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Création des tables
with app.app_context():
    db.create_all()

# Clé secrète pour générer les tokens JWT
app.config["JWT_SECRET_KEY"] = "super-secret-key"  # À changer avec une vraie clé secrète en production
jwt = JWTManager(app)


###############################################""


@app.route('/hello_world')
def hello_world():
    return "Hello world !"


#################### ACCOUNTS #####################

@app.route('/api/users/create', methods=['POST'])
def add_user():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    is_admin = data.get('is_admin', False)

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    # Vérification si l'utilisateur existe déjà
    if User.query.filter_by(username=username).first():
        return jsonify({"error": "User already exists"}), 400

    # Création de l'utilisateur
    new_user = User(username=username, is_admin=is_admin)
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User created successfully"}), 201


# ROute a proteger je pense
@app.route('/api/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([{
        "id": user.id,
        "username": user.username,
        "is_admin": user.is_admin
    } for user in users]), 200


# Ajouter sécurité
@app.route('/api/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "User deleted successfully"}), 200


@app.route('/api/login', methods=['POST'])
def login():

    username = request.json.get('username', None)
    password = request.json.get('password', None)

    # Vérifier si l'utilisateur existe dans la base de données
    user = User.query.filter_by(username=username).first()
    print("test")
    print(user)
    if user and check_password_hash(user.password, password):
        # Créer un token d'accès
        access_token = create_access_token(identity=username)
        return jsonify(access_token=access_token), 200

    return jsonify({"msg": "Nom d'utilisateur ou mot de passe incorrect."}), 401


################# SENSORS ##################


# Endpoint pour obtenir tous les capteurs
@app.route('/api/sensors', methods=['GET'])
def get_sensors():
    sensors = SensorData.query.all()
    return jsonify([sensor.to_dict() for sensor in sensors])



# Endpoint pour ajouter un capteur
# REFAIRE LES SSENSORS APRES
@app.route('/api/sensors', methods=['POST'])
def add_sensor():
    data = request.json
    name = data.get('name')
    # uid = uuid.uuid4()
    unit = data.get('unit')
    # frequency = 5
    # frequency = data.get('frequency')
    new_sensor = SensorData(
        name=name,
        unit=unit
    )
    db.session.add(new_sensor)
    db.session.commit()

    return jsonify({"message": "Capteur ajouté avec succès", "sensor": new_sensor.to_dict()}), 201


########################## A FINIR ################
# Création de la base de données (au démarrage uniquement pour dev)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

