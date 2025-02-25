import pytest
import json
from main import app, db
from models import User
from werkzeug.security import generate_password_hash

# Pour lancer les tests : 
# docker-compose run --rm backend sh -c "PYTHONPATH=/backend pytest -s"

@pytest.fixture
def client():
    """
    Crée un client de test Flask avec une base de données isolée.
    """
    with app.app_context():
        db.create_all()
        yield app.test_client()  # Donne la main au test
        db.session.rollback()  # Annule les changements après chaque test
        db.drop_all()
        db.session.remove()

################### TESTS USERS ###################

def test_create_user(client):
    """
    Test de création d'un utilisateur
    """
    response = client.post('/api/users/create', json={
        "username": "newuser",
        "password": "newpassword"
    })
    assert response.status_code == 201
    assert response.json["message"] == "Utilisateur créé"

##### Ajout d'un utilisateur dans la bdd pour effectuer des tests #####
@pytest.fixture
def new_user(client):
    """
    Ajoute un utilisateur de test.
    """
    with app.app_context():
        user = User(
            username="testuser", 
            password=generate_password_hash("testpassword")
        )
        db.session.add(user)
        db.session.commit()
        return user

def test_read_users(client, new_user):
    """
    Test de récupération de tous les utilisateurs
    """
    response = client.get('/api/users')
    assert response.status_code == 200
    assert len(response.json) > 0

def test_login_success(client, new_user):
    """
    Test de connexion réussie
    """
    response = client.post('/api/login', json={
        "username": "testuser",
        "password": "testpassword"
    })
    assert response.status_code == 200
    assert "token" in response.json

def test_login_failure(client):
    """
    Test de connexion avec mauvais mot de passe
    """
    response = client.post('/api/login', json={
        "username": "testuser",
        "password": "wrongpassword"
    })
    assert response.status_code == 401
    assert response.json["msg"] == "Nom d'utilisateur ou mot de passe incorrect."
