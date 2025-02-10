from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import check_password_hash, generate_password_hash
from threading import Thread
import os, uuid, time
# from mqtt_client import start_mqtt
from models import db, User, SensorData

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

# Ajoute un utilisateur admin si aucun n'existe
def create_admin():
    with app.app_context():
        admin = User.query.filter_by(username="admin").first()
        if not admin:
            hashed_password = generate_password_hash("1122")
            new_admin = User(username="admin", password=hashed_password, is_admin=True)
            db.session.add(new_admin)
            db.session.commit()
            print("Admin créé avec succès")
        else:
            print("Un admin existe déjà")

db.init_app(app)

# Création des tables
with app.app_context():
    db.create_all()
    create_admin()

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
    unit = data.get('unit')
    description = data.get('description')
    min_value = data.get('min_value')
    max_value = data.get('max_value')
    delta_value = data.get('delta_value')
    period = data.get('period')
    min_period = data.get('min_period')
    max_period = data.get('max_period')
    read_only = data.get('read_only', False)
    value = data.get('value')

    new_sensor = SensorData(
        name=name,
        unit=unit,
        description=description,
        min_value=min_value,
        max_value=max_value,
        delta_value=delta_value,
        period=period,
        min_period=min_period,
        max_period=max_period,
        read_only=read_only,
        value=value
    )
    db.session.add(new_sensor)
    db.session.commit()

    return jsonify({"message": "Capteur ajouté avec succès", "sensor": new_sensor.to_dict()}), 201


# Route pour supprimer un capteur
@app.route('/api/sensors/<uuid:uid>', methods=['DELETE'])
def delete_sensor(uid):
    sensor = SensorData.query.filter_by(uid=uid).first()
    if not sensor:
        return jsonify({"error": "Capteur inconnu"}), 404

    db.session.delete(sensor)
    db.session.commit()
    return jsonify({"message": "Capteur supprimé"}), 200


# Route pour récupérer un capteur spécifique
@app.route('/api/sensors/<uuid:uid>', methods=['GET'])
def get_sensor(uid):
    sensor = SensorData.query.filter_by(uid=uid).first()
    if not sensor:
        return jsonify({"error": "Capteur inconnu"}), 404

    return jsonify(sensor.to_dict()), 200




# Route pour mettre à jour un capteur
# NON UTILISABLE
# Ne fonctionne pas caro n modifie pas comme ça dans le front
# on ne modifie peut etre pas la valeur etc, je sais pas comment on simule les capteurs
@app.route('/api/sensors/<uuid:uid>', methods=['PUT'])
def update_sensor(uid):
    sensor = SensorData.query.filter_by(uid=uid).first()
    if not sensor:
        return jsonify({"error": "Capteur inconnu"}), 404

    data = request.json
    sensor.name = data.get('name', sensor.name)
    sensor.unit = data.get('unit', sensor.unit)
    sensor.description = data.get('description', sensor.description)
    sensor.min_value = data.get('min_value', sensor.min_value)
    sensor.max_value = data.get('max_value', sensor.max_value)
    sensor.delta_value = data.get('delta_value', sensor.delta_value)
    sensor.period = data.get('period', sensor.period)
    sensor.min_period = data.get('min_period', sensor.min_period)
    sensor.max_period = data.get('max_period', sensor.max_period)
    sensor.read_only = data.get('read_only', sensor.read_only)
    sensor.value = data.get('value', sensor.value)

    db.session.commit()
    return jsonify({"message": "Capteur mis à jour avec succès", "sensor": sensor.to_dict()}), 200


########################## A FINIR ################
# Création de la base de données (au démarrage uniquement pour dev)


if __name__ == '__main__':
    # Lancer MQTT en parallèle de Flask
    # Thread(target=start_mqtt, daemon=True).start()
    app.run(host='0.0.0.0', port=5000, debug=True)