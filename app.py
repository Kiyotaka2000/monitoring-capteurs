import csv
import random
import threading
import time
from collections import defaultdict
from datetime import datetime
from flask import Flask

app = Flask(__name__)
CSV_FILE = "capteurs.csv"

# =====================
# LOGIQUE CAPTEURS
# =====================

def lire_capteur(nom, valeur):
    if nom.startswith("temp_"):
        if valeur > 30:
            statut = "ALERTE CHAUD"
        elif valeur < 0:
            statut = "ALERTE FROID"
        else:
            statut = "OK"
    elif nom.startswith("humidite_"):
        if valeur > 80:
            statut = "TROP HUMIDE"
        elif valeur < 20:
            statut = "TROP SEC"
        else:
            statut = "OK"
    else:
        statut = "INCONNU"
    return {"nom": nom, "valeur": valeur, "statut": statut}

def generer_valeur(derniere_valeur, min_val, max_val):
    variation = random.uniform(-2.0, 3.0)
    nouvelle_valeur = derniere_valeur + variation
    return round(max(min_val, min(max_val, nouvelle_valeur)), 1)

def monitoring_loop():
    valeurs = {
        "temp_cuisine": 23.0,
        "temp_serveur": 29.0,
        "humidite_cuisine": 50.0,
    }
    limites = {
        "temp_cuisine": (-10, 50),
        "temp_serveur": (-10, 50),
        "humidite_cuisine": (0, 100),
    }

    with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["timestamp", "nom", "valeur", "statut"])
        writer.writeheader()

    while True:
        with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["timestamp", "nom", "valeur", "statut"])
            for nom in valeurs:
                min_val, max_val = limites[nom]
                valeurs[nom] = generer_valeur(valeurs[nom], min_val, max_val)
                r = lire_capteur(nom, valeurs[nom])
                r["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                writer.writerow(r)
        time.sleep(1)

# =====================
# SERVEUR WEB
# =====================

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Monitoring Capteurs</title>
    <meta http-equiv="refresh" content="3">
    <style>
        body {{ font-family: Arial, sans-serif; padding: 20px; background: #f5f5f5; }}
        h1 {{ color: #1A56A0; }}
        nav {{ margin-bottom: 20px; }}
        nav a {{ margin-right: 20px; color: #1A56A0; font-weight: bold; text-decoration: none; }}
        nav a:hover {{ text-decoration: underline; }}
        table {{ border-collapse: collapse; width: 100%; background: white; }}
        th {{ background: #1A56A0; color: white; padding: 10px; text-align: center; }}
        td {{ padding: 10px; border-bottom: 1px solid #ddd; text-align: center; }}
        .alerte {{ color: red; font-weight: bold; }}
        .ok {{ color: green; }}
    </style>
</head>
<body>
    <h1>{titre}</h1>
    <nav>
        <a href="/">Toutes les données</a>
        <a href="/alertes">Alertes seulement</a>
    </nav>
    <p>{count} enregistrement(s)</p>
    <table>
        <tr>
            <th>Timestamp</th>
            <th>Capteur</th>
            <th>Valeur</th>
            <th>Statut</th>
        </tr>
        {lignes}
    </table>
</body>
</html>
"""

def construire_lignes(donnees):
    lignes = ""
    for r in donnees:
        classe = "ok" if r["statut"] == "OK" else "alerte"
        lignes += f"""
        <tr>
            <td>{r['timestamp']}</td>
            <td>{r['nom']}</td>
            <td>{r['valeur']}</td>
            <td class="{classe}">{r['statut']}</td>
        </tr>"""
    return lignes

def lire_csv(filtre_alerte=False):
    try:
        with open(CSV_FILE, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            donnees = list(reader)
        if filtre_alerte:
            donnees = [r for r in donnees if r["statut"] != "OK"]
        return donnees
    except FileNotFoundError:
        return []

@app.route("/")
def index():
    donnees = lire_csv()
    html = HTML.format(
        titre="Monitoring des capteurs",
        count=len(donnees),
        lignes=construire_lignes(donnees)
    )
    return html

@app.route("/alertes")
def alertes():
    donnees = lire_csv(filtre_alerte=True)
    html = HTML.format(
        titre="Alertes",
        count=len(donnees),
        lignes=construire_lignes(donnees)
    )
    return html

# =====================
# DÉMARRAGE
# =====================

if __name__ == "__main__":
    thread = threading.Thread(target=monitoring_loop, daemon=True)
    thread.start()
    print("Monitoring démarré — http://127.0.0.1:5000")
    app.run(debug=False)