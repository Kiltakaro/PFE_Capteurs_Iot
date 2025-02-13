from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import check_password_hash, generate_password_hash
from threading import Thread
import os, uuid, time


import paho.mqtt.client as mqtt
import json
import random
from apscheduler.schedulers.background import BackgroundScheduler
import logging
import pandas as pd
import sys


logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logging.getLogger('apscheduler').setLevel(logging.DEBUG)



from models import db, User, SensorData, SensorHistory

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


######################### BASE DE DONNES  ########################

# Configuration de la base de données
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user:password@database:5432/sensorDb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


# Ajoute un admin si aucun n'existe
def create_default_admin():
    with app.app_context():
        admin = User.query.filter_by(username="admin").first()
        if not admin:
            hashed_password = generate_password_hash("1133")
            new_admin = User(username="admin", password=hashed_password, is_admin=True)
            db.session.add(new_admin)
            db.session.commit()
            print("Admin créé avec succès")
        else:
            print("Un admin existe déjà")

# Ajoute un user normal si aucun n'existe
def create_default_user():
    with app.app_context():
        admin = User.query.filter_by(username="user").first()
        if not admin:
            hashed_password = generate_password_hash("123")
            new_user = User(username="user", password=hashed_password, is_admin=False)
            db.session.add(new_user)
            db.session.commit()
            print("User créé avec succès")
        else:
            print("Un user existe déjà")

db.init_app(app)

# Création des tables
with app.app_context():
    db.create_all()
    create_default_admin()
    create_default_user()

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
    """
    Route pour créer un User dans la database
    """
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
    """
    Route pour récupérer tous users
    """
    users = User.query.all()
    return jsonify([{
        "id": user.id,
        "username": user.username,
        "is_admin": user.is_admin
    } for user in users]), 200


# CELLE DU DESSUS CEST POUR TOUS LES USERS
# CELLE DU DESSOUS C'EST POUR SEULEMENT CELUI QUI EST CONNECTE
@app.route('/api/user', methods=['GET'])
@jwt_required()
def read_user():
    """
    Route pour récupérer l'utilisateur actuel 
    """
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
    """
    Route pour que l'utilisateur modifie ses données

    Arguments attendus
    username : nouveau nom de l'utilisateur
    password : nouveau mot de passe de l'utilisateur
    """
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
    """
    Route pour supprimer un utilisateur
    
    user_id : utilisateur à supprimer 
    """
    
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "User deleted successfully"}), 200


######################  LOGIN  #######################

@app.route('/api/login', methods=['POST'])
def login():
    """
    Route pour authentifier un utilisateur

    Arguments attendus
    username : nom de l'utilisateur
    password : mdp de l'utilisateur
    """
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


@app.route('/api/sensors', methods=['GET'])
def get_sensors():
    """
    Route pour récupérer les capteurs
    """
    sensors = SensorData.query.all()
    return jsonify([sensor.to_dict() for sensor in sensors])



# REFAIRE LES SSENSORS APRES
@app.route('/api/sensors', methods=['POST'])
def add_sensor():
    """
    Route pour ajouter un capteur

    Arguments attendus
    name : nom du capteur
    unit : unité RFC8789
    description : Description du capteur
    min_value : Valeur minimale pour la simulation
    max_value : Valeur maximale pour la simulation
    period : Fréquence d'envoi de données lors de la simulation
    ??min_period 
    ??max_period
    ??read_only
    ??value
    """
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


@app.route('/api/sensors/<uuid:uid>', methods=['DELETE'])
def delete_sensor(uid):
    """
    Route pour supprimer un capteur

    uid : uid de l'utilisateur
    """
    sensor = SensorData.query.filter_by(uid=uid).first()
    if not sensor:
        return jsonify({"error": "Capteur inconnu"}), 404


    # Si le capteur est en pleine simulation, il faut l'arretée
    job = scheduler.get_job(uid)
    if job :
        if old_period != sensor.period :
            manage_sensor_job(sensor, "delete")
            print(f"Job supprimé")


    db.session.delete(sensor)
    db.session.commit()

    return jsonify({"message": "Capteur supprimé"}), 200


@app.route('/api/sensors/<uuid:uid>', methods=['GET'])
def get_sensor(uid):
    """
    Route pour récupérer le capteur spécifique

    uid : uid du capteur
    """
    sensor = SensorData.query.filter_by(uid=uid).first()
    if not sensor:
        return jsonify({"error": "Capteur inconnu"}), 404

    return jsonify(sensor.to_dict()), 200


# on ne modifie peut etre pas la valeur etc, je sais pas comment on simule les capteurs
@app.route('/api/sensors/<uuid:uid>', methods=['PUT'])
def update_sensor(uid):
    """
    Route pour modifier un capteur

    uid : uid du capteur à modifier
    """

    sensor = SensorData.query.filter_by(uid=uid).first()
    if not sensor:
        return jsonify({"error": "Capteur inconnu"}), 404

    # Pour la simulation
    # old_sensor = sensor.period

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
    # JEN DOUTE FORT
    sensor.value = data.get('value', sensor.value)

    db.session.commit()

    # Si le capteur est en pleine simulation, il faut l'update si sa fréquence d'envoi change
    job = scheduler.get_job(uid)
    if job :
        if old_period != sensor.period :
            manage_sensor_job(sensor, "update")
            print(f"Job mis à jour")


    print(f"Capteur {sensor.name} mis à jour (période : {sensor.period}s)")



    return jsonify({"message": "Capteur mis à jour avec succès", "sensor": sensor.to_dict()}), 200


########################## A FINIR ################
######################### MQTT ####################
# Création de la base de données (au démarrage uniquement pour dev)

########## MQTT 
# Connexion + Publish + Subscribe

# Configuration du broker MQTT
MQTT_BROKER = "mosquitto"  # Nom du container docker
MQTT_PORT = 1883
MQTT_TOPIC = "#" # Tous les topics

def on_connect(client, userdata, flags, rc):
    print(f"PARFAIT Connecté au broker MQTT avec le code {rc}")
    client.subscribe(MQTT_TOPIC)


# pour verifier 
# curl http://localhost:5000/api/sensors/history
def on_message(client, userdata, msg):
    payload = msg.payload.decode()
    print(f"YOUPIIIIIII Message reçu sur {msg.topic}: {payload}")

    try:
        data = json.loads(payload)
        print(payload)
        print(data)

        sensor_uid = data["sensor_uid"]
        value = data["value"]

        with app.app_context():
            sensor = SensorData.query.filter_by(uid=sensor_uid).first()
            if sensor:
                history_entry = SensorHistory(sensor_uid=sensor_uid, value=value)
                db.session.add(history_entry)
                db.session.commit()
                print(f"Ajout en historique du capteur {sensor_uid}: {value} {sensor.unit}")
            else:
                print(f"Aucun capteur trouvé avec l'UID {sensor_uid}")

    except Exception as e:
        print(f"Erreur lors du traitement du message MQTT: {e}")


######################## DONNEES SIMULEES ####################

# curl http://localhost:5000/api/sensors/history
@app.route('/api/sensors/history', methods=['GET'])
def get_all_sensor_history():
    """
    Route pour récupérer les données simulées des capteurs
    """
    history = SensorHistory.query.all()
    return jsonify([entry.to_dict() for entry in history])

# curl http://localhost:5000/api/sensors/history/ METTRE UN UUID
@app.route('/api/sensors/history/<uuid:sensor_uid>', methods=['GET'])
def get_sensor_history(sensor_uid):
    """
    Route pour récupérer les données simulées d'un capteur spécifique

    sensor_uid : uid du capteur
    """
    try:
        history = SensorHistory.query.filter_by(sensor_uid=sensor_uid).order_by(SensorHistory.timestamp.desc()).all()
        if not history:
            return jsonify({"message": "Aucune donnée historique trouvée pour ce capteur"}), 404

        history_data = [
            {
                "value": entry.value,
                "timestamp": entry.timestamp.isoformat()
            } for entry in history
        ]

        return jsonify({"sensor_uid": str(sensor_uid), "history": history_data}), 200

    except Exception as e:
        return jsonify({"error": f"Erreur lors de la récupération de l'historique: {e}"}), 500


@app.route('/api/sensors/history/<uuid:sensor_uid>', methods=['DELETE'])
def delete_sensor_history(sensor_uid):
    """
    Route pour supprimer toutes les données d'un capteur spécifique

    sensor_uid : uid du capteur
    """
    try:
        history = SensorHistory.query.filter_by(sensor_uid=sensor_uid).all()
        if not history:
            return jsonify({"message": "Aucune donnée historique trouvée pour ce capteur"}), 404

        for entry in history:
            db.session.delete(entry)
        db.session.commit()

        return jsonify({"message": "Toutes les données historiques ont été supprimées pour ce capteur"}), 200

    except Exception as e:
        return jsonify({"error": f"Erreur lors de la suppression de l'historique: {e}"}), 500

################## MQTT ####################

# Création du client MQTT
mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

# Connexion au broker
mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
mqtt_client.loop_start()


@app.route('/api/mqtt/publish', methods=['POST'])
def publish_mqtt():
    data = request.json
    topic = data.get("topic", MQTT_TOPIC)  # Utilise le topic par défaut si absent
    message = data.get("message", "Valeur par défaut")

    mqtt_client.publish(topic, message)
    return jsonify({"message": f"Message '{message}' envoyé sur {topic}"}), 200


####### Config Broker MQTT

@app.route('/api/mqtt/config', methods=['POST'])
def update_mqtt_config():
    global MQTT_BROKER, MQTT_PORT, MQTT_TOPIC, mqtt_client

    data = request.json
    MQTT_BROKER = data.get("broker", MQTT_BROKER)
    MQTT_PORT = int(data.get("port", MQTT_PORT))
    MQTT_TOPIC = data.get("topic", MQTT_TOPIC)

    # Déconnexion et reconnexion avec les nouveaux paramètres
    mqtt_client.loop_stop()
    mqtt_client = mqtt.Client()
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message
    mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
    mqtt_client.loop_start()

    return jsonify({"message": "Configuration MQTT mise à jour"}), 200

################## SIMULATION CAPTEURS #######################


# A modifier pour mettre un SensorData en parametre
def generate_sensor_data(sensor : SensorData):
    """
    Simule la génération de données pour un capteur spécifique

    sensor : le capteur à simuler 
    """
    sensor_str_uid = str(sensor.uid)
    with app.app_context():
        # on mettra surement un delta la dedans 
        value = random.uniform(sensor.min_value, sensor.max_value)  # Valeur aléatoire entre min et max
        payload = {
            "sensor_uid": sensor_str_uid, # l'uid ne se convertit pas automatiquement en string
            "name": sensor.name,
            "value": value,
            "unit": sensor.unit
        }
        print(f"Envoi MQTT vers Topic: {sensor_str_uid}/datastore, Message: {json.dumps(payload)}")  # Debug
        mqtt_client.publish(f"{sensor_str_uid}/datastore", json.dumps(payload))  # Publie sur le topic du capteur
        print(f"Envoi MQTT Confirmed")  # Debug


########## Scheduler

scheduler = BackgroundScheduler()

# Programme les capteurs avec leurs fréquences respectives

def schedule_existing_sensors():
    """
    Met en place un job de simulation sur chaque capteur déjà dans la bdd
    """

    scheduler.remove_all_jobs()
    with app.app_context():
        sensors = SensorData.query.all()
        for sensor in sensors:
            print(f"Programmation du capteur {sensor.name} avec une période de {sensor.period} secondes")
            scheduler.add_job(generate_sensor_data, 'interval', seconds=sensor.period, id=str(sensor.uid), args=[sensor])
    print(f"Jobs actifs : {scheduler.get_jobs()}")


@app.route('/api/sensors/job/<uuid:sensor_uid>/start', methods=['POST'])
def start_sensor_job(sensor_uid):
    """
    Route pour démarrer le job d'un capteur spécifique

    sensor_uid : uid du capteur
    """
    try:
        sensor = SensorData.query.filter_by(uid=sensor_uid).first()
        if not sensor:
            return jsonify({"message": "Capteur non trouvé"}), 404

        manage_sensor_job(sensor, "add")
        return jsonify({"message": f"Job démarré pour le capteur {sensor.name}"}), 200

    except Exception as e:
        return jsonify({"error": f"Erreur lors du démarrage du job: {e}"}), 500


@app.route('/api/sensors/job/<uuid:sensor_uid>/status', methods=['GET'])
def get_sensor_job_status(sensor_uid):
    """
    Route pour vérifier si le job d'un capteur spécifique est lancé ou pas

    sensor_uid : uid du capteur
    """
    try:
        sensor = SensorData.query.filter_by(uid=sensor_uid).first()
        if not sensor:
            return jsonify({"message": "Capteur non trouvé"}), 404

        job = scheduler.get_job(str(sensor.uid))
        if job:
            return jsonify({"running": True, "message": f"Job actif pour le capteur {sensor.name}"}), 200
        else:
            return jsonify({"running": False, "message": f"Aucun job actif pour le capteur {sensor.name}"}), 200

    except Exception as e:
        return jsonify({"error": f"Erreur lors de la vérification du statut du job: {e}"}), 500


@app.route('/api/sensors/job/<uuid:sensor_uid>/stop', methods=['POST'])
def stop_sensor_job(sensor_uid):
    """
    Route pour arrêter le job d'un capteur spécifique

    sensor_uid : uid du capteur
    """
    try:
        sensor = SensorData.query.filter_by(uid=sensor_uid).first()
        if not sensor:
            return jsonify({"message": "Capteur non trouvé"}), 404

        manage_sensor_job(sensor, "delete")
        return jsonify({"message": f"Job arrêté pour le capteur {sensor.name}"}), 200

    except Exception as e:
        return jsonify({"error": f"Erreur lors de l'arrêt du job: {e}"}), 500



# A MODIFIER PEUT ETRE PSK JE SUIS PAS SUR DE LA FACTORISATION DE SE COTE
def manage_sensor_job(sensor: SensorData, action: str):
    """
    Gère l'ajout, la mise à jour ou la suppression d'un job MQTT pour un capteur.
    
    action : "add" -> ajoute un job
             "update" -> met à jour un job (si la période change)
             "delete" -> supprime un job
    """

    sensor_str_uid = str(sensor.uid) # est aussi l'id du job

    if action == "add":
        scheduler.add_job(generate_sensor_data, 'interval', seconds=sensor.period, id=sensor_str_uid, args=[sensor])
        print(f"Job ajouté pour {sensor.name} (période : {sensor.period}s)")

    elif action == "update":
        if scheduler.get_job(sensor_str_uid):
            scheduler.remove_job(sensor_str_uid)  # Supprime l'ancien job
        scheduler.add_job(generate_sensor_data, 'interval', seconds=sensor.period, id=sensor_str_uid, args=[sensor])
        print(f"Job mis à jour pour {sensor.name} (nouvelle période : {sensor.period}s)")

    elif action == "delete":
        if scheduler.get_job(sensor_str_uid):
            scheduler.remove_job(sensor_str_uid)
            print(f"Job supprimé pour {sensor.name}")



# DECOMMENTER POUR TESTER LENVOI DANS LE MQTT
# schedule_existing_sensors()
scheduler.start()



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)