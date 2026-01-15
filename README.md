# Bookshop – Application web de gestion de livres

Ce projet a été réalisé dans le cadre du cours **8INF700**.  
L’objectif était de développer une petite application web locale permettant de gérer un catalogue de livres, de passer des commandes et de suivre leur statut.

L’application utilise un backend en **Flask** (Python) avec **Peewee** comme ORM, et une base de données **SQLite**.  
Le frontend est construit en **HTML/CSS/JavaScript**, avec **Bootstrap** pour la mise en forme.

---

## Fonctionnalités principales

### Catalogue
- Affichage de tous les livres disponibles.
- Recherche par **titre** ou **auteur**.
- Indication de disponibilité.
- Ajout d’un livre au panier.

### Panier & Commande
- Panier enregistré dans `localStorage` (côté client).
- Modification des quantités ou suppression d’articles.
- Formulaire client (nom, email, adresse).
- Création d’une commande via l’API Flask.
- Calcul automatique :
  - sous-total  
  - taxes (TAXE_TOTALE)  
  - frais de livraison  

### Suivi des commandes
- Recherche d’une commande par ID.
- Affichage des détails : client, livres, quantités, montants.
- Mise à jour du **statut** : `en_attente`, `payee`, `livree`.

---

## Technologies utilisées

### Backend
- Python 3
- Flask
- Peewee ORM
- SQLite

### Frontend
- HTML5 / CSS3
- Bootstrap 5
- JavaScript (ES modules)

---

## Organisation du projet

bookshop/
backend/
app.py <- routes Flask (books, orders)
models.py <- modèles Peewee
database.py <- configuration SQLite
config.py <- constantes (taxes, frais, debug)
requirements.txt
scripts/
seed.py <- insertion de livres de démo
frontend/
app.html <- page principale (SPA)
css/styles.css
js/api.js <- appels API (fetch)


---

## Installation et exécution

### 1. Cloner le projet
```bash
git clone <url>
cd bookshop
2. Créer l’environnement Python (optionnel mais recommandé)
python -m venv venv
source venv/bin/activate   # Linux/macOS
venv\Scripts\activate      # Windows
3. Installer les dépendances
pip install -r backend/requirements.txt
4. Lancer l’application
python -m backend.app
L’application démarre sur :
http://127.0.0.1:5000/app
Base de données et données de test
Pour remplir la base avec les livres de démonstration :
python -m backend.scripts.seed
Environ 30 livres sont insérés automatiquement.


Le projet fonctionne entièrement en local (aucun déploiement cloud).
Le code a été structuré pour être simple et facile à comprendre.
L’objectif principal était de mettre en pratique Flask, Peewee, SQLite et la création d’une API REST.

