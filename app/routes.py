from flask import Flask, jsonify, request

app = Flask(__name__)

# Simulation d'une base de données en mémoire en attendant la vrai
sensors = []

@app.route('/api/sensors', methods=['POST'])
def add_sensor():
    data = request.json  # Récupère les données JSON envoyées par le frontend
    sensors.append(data)  # Ajoute le capteur à la liste
    return jsonify({"message": "Capteur ajouté avec succès", "sensor": data}), 201

@app.route('/api/sensors', methods=['GET'])
def get_sensors():
    return jsonify(sensors)  # Renvoie tous les capteurs enregistrés

if __name__ == '__main__':
    app.run(debug=True)
