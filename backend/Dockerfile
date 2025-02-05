FROM python:3.10-slim

WORKDIR /backend

# Pour faire les pip install
COPY requirements.txt requirements.txt
COPY . .

# Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Exposer le port de Flask
EXPOSE 5000

# Pour avoir des comptes de test
# RUN python init_db.py

# Commande pour démarrer Flask
CMD ["python", "main.py"]
