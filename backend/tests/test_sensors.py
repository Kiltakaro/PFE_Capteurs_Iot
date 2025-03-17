import sys
import pytest
import json
import uuid

from main import app, db
from models import SensorData
from flask_jwt_extended import create_access_token


# Pour lancer les tests : 
# docker-compose run --rm backend sh -c "PYTHONPATH=/backend pytest -s"

@pytest.fixture
def client():
    """
    Crée un client de test Flask avec une base de données isolée
    """
    with app.app_context():
        db.create_all()
        yield app.test_client()  # Donne la main au test
        db.session.rollback()  # Annule les changements après chaque test
        db.drop_all()
        db.session.remove()


@pytest.fixture
def auth_token(client):
    """
    Crée un token JWT pour les tests
    """
    with app.app_context():
        token = create_access_token(identity="testuser")
        return token # sera utile pour la suite car les routes sont protégées


################### TESTS SENSORS ###################

def test_create_sensor(client, auth_token):
    """
    Test d'ajout d'un capteur
    """
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = client.post('/api/sensors', headers=headers, json={
        "name": "new_sensor",
        "unit": "C",
        "description": "New sensor",
        "min_value": 0.0,
        "max_value": 100.0,
        "delta_value": 1.0,
        "period": 10,
        "min_period": 5,
        "max_period": 20,
        "read_only": False,
        "value": 50.0
    })
    
    assert response.status_code == 201
    assert response.json["message"] == "Capteur ajouté"

##### Ajout d'un capteur dans la bdd pour effectuer des tests #####
@pytest.fixture
def new_sensor(client):
    """
    Ajoute un capteur de test et retourne son identifiant
    """
    with app.app_context():
        sensor = SensorData(
            name="test_sensor",
            unit="C",
            description="Test sensor",
            min_value=0.0,
            max_value=100.0,
            delta_value=1.0,
            period=10,
            min_period=5,
            max_period=20,
            read_only=False,
            value=50.0
        )
        db.session.add(sensor)
        db.session.commit()
        print(f"Capteur ajouté avec l'ID : {sensor.uid}")
        return sensor.uid


def test_get_sensors(client, new_sensor, auth_token):
    """
    Test de récupération de tous les capteurs et affichage du résultat
    """
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = client.get('/api/sensors', headers=headers)

    assert response.status_code == 200
    sensors = response.json
    assert len(sensors) > 0  # Vérifie qu'il y a au moins un capteur dans la réponse


def test_get_sensor(client, new_sensor, auth_token):
    """
    Test de récupération d'un capteur spécifique et affichage du résultat
    """
    sensor_id = str(new_sensor) 

    headers = {"Authorization": f"Bearer {auth_token}"}
    response = client.get(f'/api/sensors/{sensor_id}', headers=headers)

    assert response.status_code == 200
    assert response.json["name"] == "test_sensor"



def test_get_sensor_from_list_then_read_it(client, new_sensor, auth_token):
    """
    Récupère un capteur depuis /api/sensors et le lit via /api/sensors/<uid>
    """
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = client.get('/api/sensors', headers=headers)
    
    assert response.status_code == 200
    sensors = response.json
    assert len(sensors) > 0

    sensor_id = str(sensors[0]["uid"])

    # Vérifier si l'ID est bien en base
    with app.app_context():
        sensor_in_db = db.session.get(SensorData, sensor_id)
        assert sensor_in_db is not None, f"Le capteur {sensor_id} n'existe pas en base"

    response = client.get(f'/api/sensors/{sensor_id}', headers=headers)

    assert response.status_code == 200


def test_update_sensor(client, new_sensor, auth_token):
    """
    Test de mise à jour d'un capteur
    """
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = client.put(f'/api/sensors/{new_sensor}', headers=headers, json={
        "name": "updated_sensor",
        "unit": "F",
        "description": "Updated sensor",
        "min_value": -10.0,
        "max_value": 110.0,
        "delta_value": 2.0,
        "period": 15,
        "min_period": 10,
        "max_period": 30,
        "read_only": True,
        "value": 60.0
    })
    
    assert response.status_code == 200
    assert response.json["message"] == "Capteur mis à jour"



def test_delete_sensor(client, new_sensor, auth_token):
    """
    Test de suppression d'un capteur
    """
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = client.delete(f'/api/sensors/{new_sensor}', headers=headers)

    assert response.status_code == 200
    assert response.json["message"] == "Capteur supprimé"
