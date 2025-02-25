import pytest
import json
from main import app, db
from models import SensorData, SensorTemplate
from flask_jwt_extended import create_access_token

# Pour lancer les tests
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


def test_get_templates(client, auth_token):
    """
    Test de récupération des templates
    """
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = client.get('/api/templates', headers=headers)

    assert response.status_code == 200

def test_create_template(client, auth_token):
    """
    Test de création d'une template
    """
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = client.post('/api/templates', json={
        "name": "TemperatureSensor",
        "description": "Capteur de température",
        "unit": "C",
        "min_value": -50.0,
        "max_value": 150.0,
        "delta_value": 1.0,
        "period": 10,
        "min_period": 5,
        "max_period": 20,
        "read_only": False
    }, headers=headers)

    assert response.status_code == 201
    assert response.json["message"] == "Template created successfully"


def test_delete_template(client, auth_token):
    """
    Test de suppression d'une template
    """
    with app.app_context():
        template = SensorTemplate(
            name="DeleteMe",
            description="Template à supprimer",
            unit="C",
            min_value=0.0,
            max_value=100.0,
            delta_value=1.0,
            period=10,
            min_period=5,
            max_period=20,
            read_only=False
        )
        db.session.add(template)
        db.session.commit()
        template_id = template.id

    headers = {"Authorization": f"Bearer {auth_token}"}
    response = client.delete(f'/api/templates/{template_id}', headers=headers)
    
    assert response.status_code == 200
    assert response.json["message"] == "Template deleted successfully"