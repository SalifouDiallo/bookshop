# bookshop
Application web de gestion de librairie (Flask, Peewee, SQLite).

# Librairie – Flask / Peewee / SQLite

Petite app pour gérer des livres : liste, ajout de commande et calcul des totaux.

## Lancer localement
```bash
# 1) venv (optionnel)
python -m venv venv && venv\Scripts\activate

# 2) dépendances
pip install -r backend/requirements.txt

# 3) init DB (création + seed)
python backend\app.py
python -m backend.scripts.seed

# 4) démarrer Flask
python backend\app.py
# Frontend : ouvrir frontend/app.html dans le navigateur

