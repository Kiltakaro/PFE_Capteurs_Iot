from flask import Flask, jsonify, request, Blueprint
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import check_password_hash, generate_password_hash

from models import db, User

users_bp = Blueprint('users_bp', __name__)

@users_bp.route('/api/users/create', methods=['POST'])
def create_user():
    """
    Route pour créer un User dans la database
    """
    data = request.json
    username = data.get('username')
    password = data.get('password')
    is_admin = data.get('is_admin', False)

    if not username or not password:
        return jsonify({"error": "Nom d'utilisateur et Mot de passe requis"}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({"error": "Utilisateur déjà existant"}), 400

    new_user = User(username=username, is_admin=is_admin)
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "Utilisateur créé"}), 201

@users_bp.route('/api/users', methods=['GET'])
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
@users_bp.route('/api/user', methods=['GET'])
@jwt_required()
def read_user():
    """
    Route pour récupérer l'utilisateur actuel 
    """
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user).first()
    if not user:
        return jsonify({"msg": "Utilisateur non existant"}), 404
    return jsonify({
        "id": user.id,
        "username": user.username,
        "is_admin": user.is_admin
    }), 200

@users_bp.route('/api/user', methods=['PUT'])
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
        return jsonify({"msg": "Utilisateur non existant"}), 404

    data = request.json
    username = data.get('username')
    password = data.get('password')

    if username:
        user.username = username
    if password:
        user.set_password(password)

    db.session.commit()
    return jsonify({"message": "User modifié"}), 200

@users_bp.route('/api/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """
    Route pour supprimer un utilisateur
    
    user_id : utilisateur à supprimer 
    """
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"error": "Utilisateur non existant"}), 404

    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "User supprimé"}), 200

############################  LOGIN  ##############################


@users_bp.route('/api/login', methods=['POST'])
def login():
    """
    Route pour authentifier un utilisateur

    Arguments attendus
    username : nom de l'utilisateur
    password : mdp de l'utilisateur
    """
    username = request.json.get('username', None)
    password = request.json.get('password', None)

    user = User.query.filter_by(username=username).first()

    if user and check_password_hash(user.password, password):
        # Créer un token d'accès
        token = create_access_token(identity=username)
        return jsonify(token=token), 200

    return jsonify({"msg": "Nom d'utilisateur ou mot de passe incorrect."}), 401