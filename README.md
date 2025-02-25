# IoT Capteurs App

## Description
IoT Capteurs App est une application web permettant de gérer des capteurs IoT et de visualiser leurs données. Elle offre des fonctionnalités d'ajout, de modification, de suppression et de simulation de capteurs, ainsi que la gestion des utilisateurs.

## Technologies principales utilisées
- Backend : Flask, Flask-SQLAlchemy, Flask-JWT-Extended, APScheduler, paho-mqtt
- Frontend : Vue.js, Tailwind CSS
- Base de données : PostgreSQL
- Broker MQTT : Eclipse Mosquitto
- Conteneurisation : Docker, Docker Compose

## Installation

### Prérequis
- Docker
- Docker Compose

### Étapes d'installation
1. Clonez le dépôt :
    ```bash
    git clone https://github.com/Kiltakaro/PFE_Capteurs_Iot
    cd PFE_Capteurs_Iot
    ```

2. Démarrez les services Docker :
    ```bash
    docker-compose up --build
    ```

3. Accédez à l'application :
    - Frontend : [http://localhost:8080](http://localhost:8080)
    - Backend : [http://localhost:5000](http://localhost:5000)

## Utilisation

### Endpoints API

#### Utilisateurs
- `POST /api/users/create` : Créer un utilisateur
- `GET /api/users` : Récupérer tous les utilisateurs
- `GET /api/user` : Récupérer les informations de l'utilisateur connecté (nécessite un token JWT)
- `PUT /api/user` : Modifier les informations de l'utilisateur connecté (nécessite un token JWT)
- `DELETE /api/users/<int:user_id>` : Supprimer un utilisateur
- `POST /api/login` : Authentifier un utilisateur et obtenir un token JWT

#### Capteurs
- `GET /api/sensors` : Récupérer tous les capteurs
- `POST /api/sensors` : Ajouter un capteur
- `DELETE /api/sensors/<uuid:uid>` : Supprimer un capteur
- `GET /api/sensors/<uuid:uid>` : Récupérer les informations d'un capteur
- `PUT /api/sensors/<uuid:uid>` : Modifier les informations d'un capteur

#### Templates de capteurs
- `GET /api/templates` : Récupérer tous les templates de capteurs
- `POST /api/templates` : Ajouter un template de capteur
- `DELETE /api/templates/<int:template_id>` : Supprimer un template de capteur

#### Historique des capteurs
- `GET /api/sensors/history` : Récupérer l'historique de tous les capteurs
- `GET /api/sensors/history/<uuid:sensor_uid>` : Récupérer l'historique d'un capteur spécifique
- `DELETE /api/sensors/history/<uuid:sensor_uid>` : Supprimer l'historique d'un capteur spécifique

### Gestion des jobs de capteurs
- `POST /api/sensors/job/<uuid:sensor_uid>/start` : Démarrer le job d'un capteur
- `GET /api/sensors/job/<uuid:sensor_uid>/status` : Vérifier le statut du job d'un capteur
- `POST /api/sensors/job/<uuid:sensor_uid>/stop` : Arrêter le job d'un capteur

#### MQTT
- `POST /api/mqtt/publish` : Publier un message MQTT
- `POST /api/mqtt/config` : Mettre à jour la configuration du broker MQTT

## Configuration

### Backend
### Variables d'environnement
- `FLASK_ENV` :  deEnvironnement Flask (ex: development, production)
- `JWT_SECRET_KEY` : Clé secrète pour générer les tokens JWT
- `SQLALCHEMY_DATABASE_URI` : URI de connexion à la base de données PostgreSQL

### Dépendances
Les dépendances sont listées dans le fichier `backend/requirements.txt` pour le backend.

### MQTT
### Fichiers de configuration du broker MQTT
- `mosquitto/config/mosquitto.conf` : Configuration du broker MQTT Mosquitto (Expliqué plus en détail dans le fichier)


## Explications pour dev

### Docker et Docker Compose
Docker Compose est un outil permettant de définir et de gérer des applications multi-conteneurs Docker. Avec Docker Compose, vous pouvez utiliser un fichier YAML pour configurer les services de votre application, puis démarrer et arrêter tous les services avec une seule commande.  
  
Docker Compose peut reposer sur l'utilisation des Dockerfile afin de définir plus précisément une image. C'est justement ce que nous avons utilisé dans chacun des dossier afin de ségmenter notre architecture.

### Structure du fichier docker-compose.yml
Le fichier `docker-compose.yml` décrit les services, les réseaux et les volumes nécessaires pour votre application. Voici un aperçu des sections principales :

- **services** : Définit les conteneurs à exécuter.
- **volumes** : Définit les volumes partagés entre les conteneurs ou persistants sur le système hôte. C'est la où sont stockées les données.
- **networks** : Définit les réseaux Docker pour permettre la communication entre les conteneurs.

### Exemple de service
Voici 2 exemples de services :

```yaml
services:
  backend:
    container_name: backend  # Nom du conteneur Docker pour le backend
    build:
      context: ./backend  # Chemin vers le répertoire contenant le Dockerfile pour le backend
      dockerfile: Dockerfile  # Nom du Dockerfile à utiliser pour construire l'image
    ports:
      - "5000:5000"  # Mappe le port 5000 du conteneur au port 5000 de l'hôte
    volumes:
      - ./backend:/backend  # Monte le répertoire local ./backend dans le conteneur à /backend
    restart: unless-stopped  # Redémarre automatiquement en cas d'erreur le conteneur sauf s'il est explicitement arrêté
    environment:
      FLASK_ENV: development  # Définit la variable d'environnement FLASK_ENV à "development"
    networks:
      - app-network  # Connecte le conteneur au réseau Docker nommé "app-network"

  mosquitto:
    container_name: mosquitto  # Nom du conteneur Docker pour le broker MQTT Mosquitto
    image: eclipse-mosquitto:latest  # Utilise l'image Docker officielle de Mosquitto
    restart: always  # Redémarre toujours le conteneur en cas d'arrêt
    ports:
      - "1883:1883"  # Mappe le port 1883 du conteneur au port 1883 de l'hôte (port MQTT standard)
      - "9001:9001"  # Mappe le port 9001 du conteneur au port 9001 de l'hôte (WebSockets pour Vue.js, n'a pas été utilisé pour le moment)
    volumes:
      - ./mosquitto/config/mosquitto.conf:/mosquitto/config/mosquitto.conf  # Monte le fichier de configuration Mosquitto
      - ./mosquitto/config/pwfile:/mosquitto/config/pwfile  # Monte le fichier de mots de passe (si utilisé)
      - ./mosquitto/data:/mosquitto/data  # Monte le répertoire de données Mosquitto
      - ./mosquitto/log:/mosquitto/log  # Monte le répertoire de logs Mosquitto
    networks:
      - app-network  # Connecte le conteneur au réseau Docker nommé "app-network"
```

### Script de tests


1. Aller dans le main et décommenter comme ceci
```python
# Pour les tests :
app.config["TESTING"] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user:password@database_test:5432/testDb'
```
2. Toujours dans le main, mettre en commentaire comme ceci :
```python
# Pour la production :
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user:password@database:5432/sensorDb'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
```

3. A la fin du docker compose il y a beaucoup de commentaires. C'est la base de données de tests à utiliser pour lancer les tests pytest. Il suffit de décommenter le volume db_test_data et son conteneur associé. 

4. lancer : ```docker-compose run --rm backend sh -c "PYTHONPATH=/backend pytest"```


## Contributeurs
- Kiltakaro GRANDJEAN
- Hugo7764 MARTINEZ
- Katorrz MORAND
- Fripouney LABASTIE

