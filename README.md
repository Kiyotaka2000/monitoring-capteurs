# Monitoring de capteurs — Python

Système de monitoring de capteurs embarqués simulés avec interface web en temps réel.

## Fonctionnalités

- Simulation de capteurs de température et d'humidité
- Logging automatique des données en CSV
- Interface web avec rafraîchissement automatique toutes les 3 secondes
- Page dédiée aux alertes
- Architecture multithread (monitoring + serveur web simultanés)

## Stack

- Python 3.12
- Flask
- CSV / threading / datetime

## Lancer le projet
```bash
pip install flask
python app.py
```

Ouvre http://127.0.0.1:5000 dans ton navigateur.

## Structure

- `app.py` — application principale
- `capteurs.csv` — données générées au runtime (non versionné)

## Contexte

Projet développé pour simuler un système embarqué de type Raspberry Pi — 
collecte de données de capteurs, détection d'alertes et visualisation web.
```