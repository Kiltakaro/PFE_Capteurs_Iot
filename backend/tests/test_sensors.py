import sys
import pytest
import json
import uuid

from main import app, db
from models import SensorData

# Pour lancer les tests : 
# docker-compose run --rm backend sh -c "PYTHONPATH=/backend pytest"

@pytest.fixture
def client():
    """
    Crée un client de test Flask avec une base de données isolée
    """
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://user:password@database_test:5432/testDb"

    with app.app_context():
        db.create_all()
        yield app.test_client()  # Donne la main au test
        db.session.rollback()  # Annule les changements après chaque test
        db.drop_all()
        db.session.remove()

################### TESTS SENSORS ###################

def test_create_sensor(client):
    """
    Test d'ajout d'un capteur
    """
    response = client.post('/api/sensors', json={
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
        return sensor.uid

def test_read_sensor(client, new_sensor):
    """
    Test de récupération d'un capteur
    """
    sensor_id = new_sensor

    response = client.get(f'/api/sensors/{sensor_id}')
    assert response.status_code == 200
    assert response.json["name"] == "test_sensor"