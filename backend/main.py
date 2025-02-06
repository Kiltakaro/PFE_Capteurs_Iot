from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import check_password_hash, generate_password_hash


from threading import Thread

import os
import uuid

# from mqtt_client import start_mqtt

from models import db, User, SensorData

import time

time.sleep(5)

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
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user:password@database:5432/sensorDb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


################### POUR MQTT #####################

# Désactiver la connexion MQTT si nécessaire
# if os.environ.get('DISABLE_MQTT') != '1':
#     from mqtt_client import start_mqtt
#     start_mqtt()


db.init_app(app)

# Création des tables
with app.app_context():
    db.create_all()

# Clé secrète pour générer les tokens JWT
app.config["JWT_SECRET_KEY"] = "super-secret-key"  # À changer avec une vraie clé secrète en production
jwt = JWTManager(app)


######################################################


@app.route('/hello_world')
def hello_world():
    return "Hello world !"


######################  ACCOUNTS #######################
#####################  CRUD  USER  #####################
@app.route('/api/users/create', methods=['POST'])
def create_user():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    is_admin = data.get('is_admin', False)

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    # Vérification si le nom d'utilisateur existe déjà
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
def read_users():
    users = User.query.all()
    return jsonify([{
        "id": user.id,
        "username": user.username,
        "is_admin": user.is_admin
    } for user in users]), 200


# CELLE DU DESSUS CEST POUR TOUS LES USERS
# CELLE DU DESSOUS C'EST POUR SEULEMENT CELUI QUI EST CONNECTE
# Route pour récupérer les informations de l'utilisateur connecté
@app.route('/api/user', methods=['GET'])
@jwt_required()
def read_user():
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user).first()
    if not user:
        return jsonify({"msg": "User not found"}), 404
    return jsonify({
        "id": user.id,
        "username": user.username,
        "is_admin": user.is_admin
    }), 200

# Il faudra peut etre rajouter un cas ou c'est l'admin qui veut modifier
# Route pour mettre à jour un utilisateur
@app.route('/api/user', methods=['PUT'])
@jwt_required()
def update_user():
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user).first()
    if not user:
        return jsonify({"msg": "User not found"}), 404

    data = request.json
    username = data.get('username')
    password = data.get('password')

    if username:
        user.username = username
    if password:
        user.set_password(password)

    db.session.commit()
    return jsonify({"message": "User updated successfully"}), 200




# Ajouter sécurité
@app.route('/api/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "User deleted successfully"}), 200


######################  LOGIN  #######################

@app.route('/api/login', methods=['POST'])
def login():

    username = request.json.get('username', None)
    password = request.json.get('password', None)

    # Vérifier si l'utilisateur existe dans la base de données
    user = User.query.filter_by(username=username).first()

    if user and check_password_hash(user.password, password):
        # Créer un token d'accès
        token = create_access_token(identity=username)
        token = str(token)
        print(token)
        return jsonify(token=token), 200

    return jsonify({"msg": "Nom d'utilisateur ou mot de passe incorrect."}), 401


############################## SENSORS ###############################


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

    new_sensor = SensorData(
        name=name,
        unit=unit
    )
    db.session.add(new_sensor)
    db.session.commit()

    return jsonify({"message": "Capteur ajouté avec succès", "sensor": new_sensor.to_dict()}), 201

@app.route('/api/sensors/<int:sensor_id>', methods=['DELETE'])
def delete_sensor(sensor_id):
    sensor = SensorData.query.get(sensor_id)
    if not sensor:
        return jsonify({"error": "Capteur inconnu"}), 404

    db.session.delete(sensor)
    db.session.commit()
    return jsonify({"message": "Capteur supprimé"}), 200

########################## A FINIR ################
# Création de la base de données (au démarrage uniquement pour dev)


if __name__ == '__main__':
    # Lancer MQTT en parallèle de Flask
    # Thread(target=start_mqtt, daemon=True).start()
    app.run(host='0.0.0.0', port=5000, debug=True)

