FROM python:3.10-slim

WORKDIR /backend

# Pour faire les pip install
COPY requirements.txt requirements.txt
COPY . .

# Pour éviter un warning concernant la gestion de la timezone
ENV TZ=UTC
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Exposer le port de Flask
EXPOSE 5000

# Commande pour démarrer Flask
CMD ["python", "main.py"]
