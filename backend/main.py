from flask import Flask, jsonify, request, Blueprint
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

from apscheduler.schedulers.background import BackgroundScheduler
from threading import Thread 
 
import paho.mqtt.client as mqtt

import os, uuid, time, sys, logging, random, json, csv, datetime

from scipy.interpolate import interp1d 
import pandas as pd
import numpy as np


from models import db, User, SensorData, SensorHistory

from users import users_bp


logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logging.getLogger('apscheduler').setLevel(logging.DEBUG)


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

    return jsonify({"message": "Capteur ajouté", "sensor": new_sensor.to_dict()}), 201


@app.route('/api/sensors/<uuid:uid>', methods=['DELETE'])
def delete_sensor(uid):
    """
    Route pour supprimer un capteur

    uid : uid de l'utilisateur
    """
    sensor = SensorData.query.filter_by(uid=uid).first()
    if not sensor:
        return jsonify({"error": "Capteur inconnu"}), 404


    # Si le capteur est en pleine simulation, il faut l'arreter
    job = scheduler.get_job(uid)
    if job :
        manage_sensor_job(sensor, "delete")
        print(f"Job supprimé")

    # Delete sensor history
    delete_sensor_history_function(uid)

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

    # Pour la simulation en temps réel
    old_period = sensor.period

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



    return jsonify({"message": "Capteur mis à jour", "sensor": sensor.to_dict()}), 200


######################## STOCKAGE DONNEES SIMULEES ############################

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
            return jsonify({"message": "Aucun historique trouvé pour ce capteur"}), 404

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
    response, status_code = delete_sensor_history_function(sensor_uid)
    return jsonify(response), status_code


def delete_sensor_history_function(sensor_uid):
    """
    Fonction pour supprimer l'historique d'un capteur

    sensor_id : uid du capteur
    """
    try:
        history = SensorHistory.query.filter_by(sensor_uid=sensor_uid).all()
        if not history:
            return {"message": "Aucun historique trouvé pour ce capteur"}, 404

        for entry in history:
            db.session.delete(entry)
        db.session.commit()

        return {"message": "Historique supprimé pour ce capteur"}, 200

    except Exception as e:
        return {"error": f"Erreur lors de la suppression de l'historique: {e}"}, 500

########################## SIMULATION GENERATION TEMPS REEL ############################

# A modifier pour mettre un SensorData en parametre
def generate_sensor_data(sensor : SensorData):
    """
    Simule la génération en temps REEL de données pour un capteur spécifique

    sensor : le capteur à simuler 
    """
    sensor_str_uid = str(sensor.uid)
    with app.app_context():
        # on mettra surement un delta la dedans 
        value = random.uniform(sensor.min_value, sensor.max_value)  # Valeur aléatoire entre min et max
        payload = {
            "sensor_uid": sensor_str_uid, # l'uid ne se convertit pas automatiquement en string
            "value": value,
            "timestamp": datetime.datetime.now().isoformat(),
        }
        print(f"Envoi MQTT vers Topic: {sensor_str_uid}/datastore, Message: {json.dumps(payload)}")  # Debug
        mqtt_client.publish(f"{sensor_str_uid}/datastore", json.dumps(payload))  # Publie sur le topic du capteur

########################## SIMULATION GENERATION RAPIDE ############################

@app.route('/api/sensors/simulate/<uuid:sensor_id>', methods=['GET'])
def simulate_sensor(sensor_id):
    """
    Route pour simuler très rapidement un capteur spécifique

    sensor_id : uid du capteur
    """
    sensor_str_uid = str(sensor_id)
    sensor = SensorData.query.filter_by(uid=sensor_id).first()
    if not sensor:
        return jsonify({"error": "Capteur inconnu"}), 404


    duration = int(request.args.get('duration', 24))  # Durée en heures
    interval = int(request.args.get('interval', 10))  # Intervalle en minutes

    start_time = datetime.datetime.now() - datetime.timedelta(hours=duration)
    num_points = (duration * 60) // interval  # Nombre total de points générés

    for i in range(num_points):
        timestamp = start_time + datetime.timedelta(minutes=i * interval)
        value = round(random.uniform(sensor.min_value, sensor.max_value), 2)  # Génération a modifier

        payload = {
            "sensor_uid": sensor_str_uid,
            "timestamp": timestamp.isoformat(),
            "value": value
        }

        print(f"Envoi MQTT vers Topic: {sensor_str_uid}/datastore, Message: {json.dumps(payload)}")  # Debug
        mqtt_client.publish(f"{sensor_str_uid}/datastore", json.dumps(payload))
        time.sleep(0.1)  # Petit délai pour éviter de spammer MQTT trop vite

    return jsonify({"message": f"Simulation envoyée via MQTT pour capteur {sensor_id}"}), 200


########################### GENERER COURBES AVEC POINTS DONNES ############################

@app.route('/api/sensors/generate-curve', methods=['POST'])
def generate_curve():
    """
    Génére une courbe en fonction des points données

    Arguments attendus :
    sensor_uid : uid du capteur
    points : liste de points (x, y) pour l'interpolation
    """
    data = request.json
    print("Received data:", data)  # Log les données reçues
    sensor_uid = data.get("sensor_uid")

    if not data:
        return jsonify({"error": "Requête vide ou format JSON invalide"}), 400

    user_points = data.get("points", [])
    duration = 24
    interval = 10

    if len(user_points) < 2:
        return jsonify({"error": "Au moins 2 points sont nécessaires"}), 400

    try:
        timestamps = [datetime.datetime.utcnow() + datetime.timedelta(hours=p["x"]) for p in user_points]
        values = [float(p["y"]) for p in user_points]
        print("Timestamps:", timestamps)
        print("Values:", values)
    except KeyError as e:
        return jsonify({"error": f"Clé manquante dans les points : {e}"}), 400
    except ValueError as e:
        return jsonify({"error": f"Format invalide des valeurs : {e}"}), 400
    except Exception as e:
        print("Erreur lors du traitement des points:", e)
        return jsonify({"error": f"Erreur inattendue : {e}"}), 500

    # Générer une interpolation
    try:
        x_numeric = np.linspace(0, len(timestamps) - 1, num=(duration * 60) // interval)
        interpolator = interp1d(range(len(timestamps)), values, kind='linear')
        y_generated = interpolator(x_numeric)
    except Exception as e:
        print("Erreur d'interpolation:", e)
        return jsonify({"error": f"Erreur d'interpolation : {e}"}), 500

    start_time = timestamps[0]

    for i in range(len(y_generated)):
        timestamp = start_time + datetime.timedelta(minutes=i * interval)
        value = float(y_generated[i])

        # Publier les données générées sur MQTT
        payload = {
            "sensor_uid": str(sensor_uid),
            "timestamp": timestamp.isoformat(),
            "value": value
        }
        print(f"Envoi MQTT vers Topic: {sensor_uid}/datastore, Message: {json.dumps(payload)}")  # Debug
        mqtt_client.publish(f"{sensor_uid}/datastore", json.dumps(payload))
        time.sleep(0.1)  # Petit délai pour éviter de spammer MQTT trop vite

    return jsonify({"message": f"Simulation envoyée via MQTT pour capteur {sensor_uid}"}), 200

######################################### IMPORT CSV ########################################

bp = Blueprint('csv_upload', __name__)

UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"csv"}

# Vérifier l'extension du fichier
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@bp.route("/api/sensors/upload-csv/<uuid:sensor_id>", methods=["POST"])
def upload_csv(sensor_id):
    """
    Route pour importer les données simulées / réelles d'un capteur à partir d'un fichier CSV
    Le but est de lire le CSV pour inserer ses données dans la base de données sans sauvegarder le fichier

    sensor_id : uid du capteur
    """
    if "file" not in request.files:
        return jsonify({"error": "Aucun fichier envoyé"}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"error": "Nom de fichier invalide"}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "Format de fichier non autorisé"}), 400

    try:
        file.stream.seek(0)  # Mettre le poiteur au début du fichier
        reader = csv.reader(file.stream.read().decode("utf-8").splitlines()) # Découpage
        next(reader)  # Sauter l'en-tête

        entries = []
        for row in reader:
            if len(row) != 2:
                continue  # Ignore qui n'ont pas le format attendu
            
            value, timestamp = row
            try:
                value = float(value)
                timestamp = datetime.datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
            except ValueError as ve:
                continue  # Ignore les lignes qui posent probleme

            entries.append(SensorHistory(sensor_uid=sensor_id, value=value, timestamp=timestamp))

        # Insértion dans la base de données
        db.session.bulk_save_objects(entries)
        db.session.commit()

        return jsonify({"message": "Données insérées avec succès"}), 201

    except Exception as e:
        db.session.rollback()
        print(f"Erreur lors de l'import: {e}")
        return jsonify({"error": f"Erreur lors de l'import : {str(e)}"}), 500

app.register_blueprint(bp)
app.register_blueprint(users_bp)


######################### MQTT ####################

########## MQTT 
# Connexion + Publish + Subscribe

# Configuration du broker MQTT
MQTT_BROKER = "mosquitto"  # Nom du container docker
MQTT_PORT = 1883
MQTT_TOPIC = "#" # Tous les topics

def on_connect(client, userdata, flags, rc):
    print(f"PARFAIT Connecté au broker MQTT avec le code {rc}")
    client.subscribe(MQTT_TOPIC)



# Pour lire les messages du MQTT et les traiter
def on_message(client, userdata, msg):
    payload = msg.payload.decode()
    print(f"Message reçu sur {msg.topic}: {payload}")

    try:
        data = json.loads(payload)

        # Cas enregistrement de capteur
        if msg.topic == "system/register":
            sensor_uid = data.get("uid")
            with app.app_context():
                existing_sensor = SensorData.query.filter_by(uid=sensor_uid).first()
                
                if existing_sensor:
                    print(f"Le capteur {sensor_uid} existe déjà")
                    return
        
                else:            
                    print(f"Le capteur error ?")
                    description=data.get("description")
                    # AJOUTER VERIF SI UNITE RFC8789 ?
                    unit=data.get("unit") 
                    min_value=data.get("min_value")
                    max_value=data.get("max_value")
                    delta_value=data.get("delta_value")
                    period=data.get("period")
                    min_period=data.get("min_period")
                    max_period=data.get("max_period")

                    read_only=data.get("read_only")
                    if read_only.lower() == "true":
                        read_only = True
                    else:
                        read_only = False

                    value=data.get("value")


                    new_sensor = SensorData(
                        uid=uuid.UUID(sensor_uid),
                        name=str(sensor_uid),
                        description=description,
                        unit=unit,
                        min_value=min_value,
                        max_value=max_value,
                        delta_value=delta_value,
                        period=period,
                        min_period=min_period,
                        max_period=max_period,
                        read_only=read_only,
                        value=value
                    )
                    print(f"Le capteur error 2")
                    db.session.add(new_sensor)
                    print(f"Le capteur error 3")
                    db.session.commit()
                    print(f"Capteur {sensor_uid} ajouté")
                    db.session.close()
                    return

        # Cas reception de données
        else:
            sensor_uid = data.get("sensor_uid")
            timestamp = data.get("timestamp")
            value = data.get("value")  # Peut être None si ce n'est pas une valeur de capteur

            with app.app_context():
                sensor = SensorData.query.filter_by(uid=sensor_uid).first()
                print(f"Capteur {str(sensor.uid)} trouvé")
                # Cas capteur connu
                if sensor:
                    print(f"Capteur connu ({sensor_uid})")
                    history_entry = SensorHistory(sensor_uid=sensor_uid, value=value, timestamp=timestamp)
                    db.session.add(history_entry)
                    db.session.commit()
                    print(f"Ajout dans l'historique du capteur {sensor_uid}: {value} {sensor.unit}")

                # Cas capteur inconnu => demande d'enregistrement
                else:
                    print(f"Capteur inconnu ({sensor_uid}), demande d'enregistrement")
                    command_topic = f"{sensor_uid}/command"
                    mqtt_client.publish(command_topic, json.dumps({"command": "REGISTER"}))
                    print(f"Message REGISTER envoyé sur {command_topic}")

    except Exception as e:
        print(f"Erreur lors du traitement du message MQTT: {e}")



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
    """
    Route pour configurer la connexion au broker depuis le front
    """
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



scheduler.start()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)