# Image de l'API basée sur une image python
FROM python:3.9-alpine

# Création et positionnement du répertoire par défaut dans le container
WORKDIR /app

# Utilisation d'un user non-root pour des raisons de sécurité
# Note : lorsque l'instruction "WORKDIR /app" est exécutée au dessus,
# le répertoire est créé et appartient toujours à l'utilisateur root
# (et ce quelque soit le USER actif). Il est donc nécessaire de modifier
# les droits pour l'attribuer à notre nouvel utilisateur "quiz"
RUN addgroup -S quiz && \
    adduser -S quiz -G quiz && \
    chown -R quiz:quiz /app
USER quiz

# Ajout du chemin d'installation des utilitaires Python dans le $PATH
ENV PATH="$PATH:/home/quiz/.local/bin"

# Copie du fichier requirements local (machine hôte) vers le container
# (répertoire /app, car il s'agit du WORKDIR)
COPY --chown=quiz:quiz requirements.txt requirements.txt

# Installation des dépendances dans le container
RUN python -m pip install --no-cache-dir --upgrade pip && \
    python -m pip install --no-cache-dir -r requirements.txt

# Creation d'une base vide
RUN touch quiz.db

# Variables d'environement de production
ENV FLASK_DEBUG=0
ENV FLASK_ENV=production
ENV FLASK_APP=app.py

# Copie de l'ensemble du code + dépendances
COPY --chown=quiz:quiz . .

# Informations sur l'image
LABEL maintainer="Jenny CAO <jeny.cao@edu.esiee.fr>, Juan IVANOFF <juan.ivanoff@edu.esiee.fr>, Théo SZANTO <theo.szanto@edu.esiee.fr>" version="1.0"

# Port sur lequel se lance l'application
EXPOSE 5000

# Commande de démarrage du serveur gunicorn
CMD [ "gunicorn", "--bind", "0.0.0.0:5000", "app:app", "--log-level", "info", "--error-logfile", "-", "--access-logfile", "-" ]
