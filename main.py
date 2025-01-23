from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required

from models import db, User, SensorData

app = Flask(__name__)
CORS(app)  # Applique CORS à toutes les routes pour eviter plein de bug, trust me

############## TEST BASE DE DONNES SQLLITE ###############

# Configuration de la base de données
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Création des tables
with app.app_context():
    db.create_all()

app.config["JWT_SECRET_KEY"] = "super-secret-key"  # À changer avec une vraie clé secrète en production
jwt = JWTManager(app)

###############################################""

# Simulons une base de données en mémoire
sensors = []


@app.route('/hello_world')
def hello_world():
    return "Hello world !"


#################### ACCOUNTS #####################

@app.route('/add_user', methods=['POST'])
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

@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([{
        "id": user.id,
        "username": user.username,
        "is_admin": user.is_admin
    } for user in users]), 200



# Clé secrète pour générer les tokens JWT
app.config['JWT_SECRET_KEY'] = 'votre_clé_secrète'
jwt = JWTManager(app)

# Simuler une base de données d'utilisateurs
users_db = {
    "admin": {"password": "admin123", "role": "admin"},
    "user1": {"password": "user123", "role": "user"}
}

@app.route('/api/login', methods=['POST'])
def login():
    username = request.json.get('username', None)
    password = request.json.get('password', None)

    # Vérifier si l'utilisateur existe
    if username in users_db and check_password_hash(users_db[username]["password"], password):
        # Créer un token d'accès
        access_token = create_access_token(identity=username)
        return jsonify(access_token=access_token), 200

    return jsonify({"msg": "Nom d'utilisateur ou mot de passe incorrect."}), 401


################# SENSORS ##################

@app.route('/api/sensors', methods=['POST'])
def add_sensor():
    data = request.json
    sensors.append(data)
    return jsonify({"message": "Capteur ajouté avec succès", "sensor": data}), 201

@app.route('/api/sensors', methods=['GET'])
def get_sensors():
    return jsonify(sensors)

# if __name__ == '__main__':
#     app.run(debug=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)










# Création de la base de données (au démarrage uniquement pour dev)
@app.before_first_request
def create_tables():
    db.create_all()

# Endpoint pour obtenir tous les capteurs
@app.route('/api/sensors', methods=['GET'])
def get_sensors():
    sensors = Sensor.query.all()
    return jsonify([sensor.to_dict() for sensor in sensors])

# Endpoint pour ajouter un capteur
@app.route('/api/sensors', methods=['POST'])
def add_sensor():
    data = request.json
    new_sensor = Sensor(
        name=data['name'],
        uid=data['uid'],
        unit=data['unit'],
        frequency=data['frequency']
    )
    db.session.add(new_sensor)
    db.session.commit()
    return jsonify(new_sensor.to_dict()), 201

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')

