# Fichier principal de l'application Flask.
# On y retrouve :
#  - la config de l'app,
#  - les routes API (livres, commandes),
#  - et le service des fichiers frontend.

from flask import Flask, request, jsonify, send_from_directory, redirect
from flask_cors import CORS
from peewee import DoesNotExist
from .database import db
from .models import Livre, Client, Commande, CommandeLivre
from .config import TAXE_TOTALE, LIVRAISON_CENTS, DEBUG
import pathlib

# Création de l'application Flask
app = Flask(__name__)
CORS(app)

# Chemin vers le dossier frontend (app.html, css, js, etc.)
FRONTEND_DIR = pathlib.Path(__file__).resolve().parents[1] / "frontend"


# ----------- Routes pour servir le frontend ----------- #

@app.get("/")
def root():
    """
    Redirige la racine vers /app pour afficher la page principale.
    """
    return redirect("/app", code=302)


@app.get("/app")
def serve_app():
    """
    Renvoie le fichier app.html (SPA du projet).
    """
    return send_from_directory(FRONTEND_DIR, "app.html")


@app.get("/frontend/<path:path>")
def serve_frontend_files(path):
    """
    Permet d'accéder aux fichiers statiques du frontend :
    /frontend/js/api.js, /frontend/css/styles.css, etc.
    """
    return send_from_directory(FRONTEND_DIR, path)


# ----------- Initialisation de la base de données ----------- #

def init_db():
    """
    Crée les tables si besoin et s'assure que la colonne image_url existe
    dans la table livre (cas où on relance sur une vieille BD).
    """
    with db:
        db.create_tables([Livre, Client, Commande, CommandeLivre])

        # On vérifie la présence de la colonne image_url dans la table livre
        cols = [row[1] for row in db.execute_sql('PRAGMA table_info("livre")').fetchall()]
        if "image_url" not in cols:
            db.execute_sql('ALTER TABLE "livre" ADD COLUMN "image_url" TEXT DEFAULT ""')


# Connexion / fermeture de la BD autour de chaque requête
@app.before_request
def _connect_db():
    """
    Ouvre une connexion à la BD avant chaque requête HTTP.
    """
    if db.is_closed():
        db.connect(reuse_if_open=True)


@app.teardown_request
def _close_db(exc):
    """
    Ferme la connexion à la BD après chaque requête.
    """
    if not db.is_closed():
        db.close()


# ----------- Fonctions utilitaires ----------- #

def livre_to_dict(livre: Livre) -> dict:
    """
    Transforme un objet Livre en dictionnaire prêt à être renvoyé en JSON.
    """
    return {
        "id": livre.id,
        "titre": livre.titre,
        "auteur": livre.auteur,
        "prix_cents": livre.prix_cents,
        "disponible": bool(livre.disponible),
        "image_url": livre.image_url,
    }


def commande_to_dict(cmd: Commande, with_lines: bool = True) -> dict:
    """
    Transforme une Commande en dictionnaire.
    Si with_lines=True, on ajoute la liste des livres de la commande.
    """
    data = {
        "id": cmd.id,
        "statut": cmd.statut,
        "client": {
            "id": cmd.client.id,
            "nom": cmd.client.nom,
            "email": cmd.client.email,
            "adresse": cmd.client.adresse,
        },
        "sous_total_cents": cmd.sous_total_cents,
        "taxes_cents": cmd.taxes_cents,
        "livraison_cents": cmd.livraison_cents,
        "total_cents": cmd.total_cents,
    }

    if with_lines:
        data["items"] = [
            {
                "book_id": ligne.livre.id,
                "titre": ligne.livre.titre,
                "quantite": ligne.quantite,
                "prix_unitaire_cents": ligne.livre.prix_cents,
                "ligne_total_cents": ligne.livre.prix_cents * ligne.quantite,
            }
            for ligne in cmd.lignes
        ]

    return data


def error(msg: str, code: int = 400):
    """
    Petite fonction utilitaire pour renvoyer un message d'erreur JSON
    avec un code HTTP adapté.
    """
    resp = jsonify({"message": msg, "code": code})
    resp.status_code = code
    return resp


# ----------- Routes API : Livres ----------- #

@app.get("/books")
def list_books():
    """
    Liste tous les livres.
    Si un paramètre search est fourni, on filtre par titre ou auteur.
    """
    q = (request.args.get("search", "").strip().lower())
    qs = Livre.select()

    if q:
        qs = qs.where(
            (Livre.titre.contains(q)) | (Livre.auteur.contains(q))
        )

    return jsonify([livre_to_dict(l) for l in qs])


@app.get("/books/<int:book_id>")
def get_book(book_id: int):
    """
    Renvoie un livre spécifique par son id.
    """
    try:
        livre = Livre.get_by_id(book_id)
        return jsonify(livre_to_dict(livre))
    except DoesNotExist:
        return error("Livre introuvable", 404)


@app.post("/books")
def create_book():
    """
    Crée un nouveau livre.
    Champs obligatoires : titre, auteur, prix_cents.
    """
    data = request.get_json(force=True, silent=True) or {}

    # Vérification des champs obligatoires
    for f in ["titre", "auteur", "prix_cents"]:
        if f not in data:
            return error("Champ manquant: " + f, 400)

    # Validation simple sur le prix
    try:
        prix = int(data["prix_cents"])
        assert prix >= 0
    except Exception:
        return error("prix_cents doit être un entier >= 0", 400)

    # Création du livre
    livre = Livre.create(
        titre=data["titre"],
        auteur=data["auteur"],
        prix_cents=prix,
        disponible=bool(data.get("disponible", True)),
        image_url=data.get("image_url", ""),
    )

    return jsonify(livre_to_dict(livre)), 201


@app.put("/books/<int:book_id>")
def update_book(book_id: int):
    """
    Met à jour un livre existant.
    Tous les champs sont optionnels, on ne modifie que ceux fournis.
    """
    data = request.get_json(force=True, silent=True) or {}

    try:
        livre = Livre.get_by_id(book_id)
    except DoesNotExist:
        return error("Livre introuvable", 404)

    if "titre" in data:
        livre.titre = data["titre"]
    if "auteur" in data:
        livre.auteur = data["auteur"]

    if "prix_cents" in data:
        try:
            p = int(data["prix_cents"])
            assert p >= 0
            livre.prix_cents = p
        except Exception:
            return error("prix_cents doit être un entier >= 0", 400)

    if "disponible" in data:
        livre.disponible = bool(data["disponible"])

    if "image_url" in data:
        livre.image_url = data["image_url"]

    livre.save()
    return jsonify(livre_to_dict(livre))


@app.delete("/books/<int:book_id>")
def delete_book(book_id: int):
    """
    Supprime un livre et ses liens éventuels.
    """
    try:
        livre = Livre.get_by_id(book_id)
    except DoesNotExist:
        return error("Livre introuvable", 404)

    livre.delete_instance(recursive=True)
    return jsonify({"message": "Livre supprimé"})


# ----------- Routes API : Commandes ----------- #

VALID_STATUTS = {"en_attente", "payee", "livree"}


@app.post("/orders")
def create_order():
    """
    Crée une nouvelle commande avec :
      - un client (nom, email, adresse)
      - une liste d'items (book_id, quantite)
    Calcule aussi les montants : sous-total, taxes, livraison, total.
    """
    data = request.get_json(force=True, silent=True) or {}
    client = data.get("client", {})
    items = data.get("items", [])

    # Vérification des champs client
    for f in ["nom", "email", "adresse"]:
        if not client.get(f):
            return error("Client." + f + " est requis", 400)

    # Validation très simple de l'email
    if "@" not in client["email"] or "." not in client["email"]:
        return error("Email invalide", 400)

    if not items:
        return error("La commande doit contenir au moins un article", 400)

    lignes = []
    sous_total = 0

    # On parcourt les items envoyés par le frontend
    for it in items:
        try:
            bid = int(it["book_id"])
            qty = int(it.get("quantite", 1))
        except Exception:
            return error("book_id et quantite doivent être des entiers", 400)

        if qty <= 0:
            return error("quantite doit être > 0", 400)

        try:
            livre = Livre.get_by_id(bid)
        except DoesNotExist:
            return error(f"Livre {bid} introuvable", 404)

        if not livre.disponible:
            return error(f"Le livre '{livre.titre}' n'est pas disponible", 400)

        lignes.append((livre, qty))
        sous_total += livre.prix_cents * qty

    # Calcul des montants
    taxes = round(sous_total * TAXE_TOTALE)
    livraison = LIVRAISON_CENTS if sous_total > 0 else 0
    total = sous_total + taxes + livraison

    # Création du client et de la commande
    c = Client.create(
        nom=client["nom"],
        email=client["email"],
        adresse=client["adresse"],
    )

    cmd = Commande.create(
        client=c,
        sous_total_cents=sous_total,
        taxes_cents=taxes,
        livraison_cents=livraison,
        total_cents=total,
        statut="en_attente",
    )

    # Insertion des lignes de commande
    for livre, qty in lignes:
        CommandeLivre.create(commande=cmd, livre=livre, quantite=qty)

    return (
        jsonify(
            {
                "id": cmd.id,
                "statut": cmd.statut,
                "sous_total_cents": sous_total,
                "taxes_cents": taxes,
                "livraison_cents": livraison,
                "total_cents": total,
            }
        ),
        201,
    )


@app.get("/orders/<int:order_id>")
def get_order(order_id: int):
    """
    Renvoie une commande complète (client + lignes).
    """
    try:
        cmd = Commande.get_by_id(order_id)

        # On force le chargement des lignes pour éviter les surprises
        _ = list(cmd.lignes)

        return jsonify(commande_to_dict(cmd))
    except DoesNotExist:
        return error("Commande introuvable", 404)


@app.put("/orders/<int:order_id>/status")
def update_order_status(order_id: int):
    """
    Met à jour uniquement le statut d'une commande.
    Statuts autorisés : en_attente, payee, livree.
    """
    data = request.get_json(force=True, silent=True) or {}
    new = data.get("statut", "")

    if new not in VALID_STATUTS:
        return error(
            "Statut invalide. Autorisés: " + str(sorted(list(VALID_STATUTS))),
            400,
        )

    try:
        cmd = Commande.get_by_id(order_id)
    except DoesNotExist:
        return error("Commande introuvable", 404)

    cmd.statut = new
    cmd.save()

    return jsonify({"id": cmd.id, "statut": cmd.statut})


# ----------- Lancement de l'application ----------- #

if __name__ == "__main__":
    # On initialise la BD et on lance le serveur en local.
    init_db()
    app.run(host="127.0.0.1", port=5000, debug=DEBUG)
