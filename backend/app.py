# app.py — Point d'entrée de l'application Flask.
#
# Ce fichier contient :
#   - la config de l'app (logging, CORS, en-têtes sécurité)
#   - les gestionnaires d'erreurs globaux (retournent toujours du JSON)
#   - les routes API pour les livres et les commandes
#   - le service des fichiers statiques du frontend

import logging
import pathlib
import re

from flask import Flask, request, jsonify, send_from_directory, redirect
from flask_cors import CORS
from peewee import DoesNotExist

from .config import TAXE_TOTALE, LIVRAISON_CENTS, DEBUG, MAX_ITEMS_PER_ORDER
from .database import db
from .models import Livre, Client, Commande, CommandeLivre


# --- Logging ---
# Je configure le logging ici pour avoir des traces lisibles pendant le dev.
logging.basicConfig(
    level=logging.DEBUG if DEBUG else logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("bookshop")


# --- App Flask ---
app = Flask(__name__)
CORS(app)

FRONTEND_DIR = pathlib.Path(__file__).resolve().parents[1] / "frontend"

# Regex pour la validation d'email (format de base suffisant pour ce projet)
_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


# --- En-têtes de sécurité HTTP ---
# Ajoutés automatiquement à chaque réponse.

@app.after_request
def add_security_headers(response):
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"]         = "DENY"
    response.headers["Referrer-Policy"]         = "strict-origin-when-cross-origin"
    return response


# --- Gestionnaires d'erreurs globaux ---
# Flask retourne du HTML par défaut pour les erreurs. Comme c'est une API REST,
# je surcharge ces handlers pour toujours retourner du JSON propre.

@app.errorhandler(400)
def bad_request(e):
    logger.warning("400 sur %s", request.path)
    return jsonify({"message": "Requête invalide", "code": 400}), 400

@app.errorhandler(404)
def not_found(e):
    logger.warning("404 sur %s", request.path)
    return jsonify({"message": "Ressource introuvable", "code": 404}), 404

@app.errorhandler(405)
def method_not_allowed(e):
    logger.warning("405 — %s %s", request.method, request.path)
    return jsonify({"message": "Méthode non autorisée", "code": 405}), 405

@app.errorhandler(500)
def internal_error(e):
    logger.error("500 — %s", e)
    return jsonify({"message": "Erreur interne du serveur", "code": 500}), 500


# --- Routes frontend ---

@app.get("/")
def root():
    return redirect("/app", code=302)

@app.get("/app")
def serve_app():
    return send_from_directory(FRONTEND_DIR, "app.html")

@app.get("/frontend/<path:path>")
def serve_frontend_files(path):
    return send_from_directory(FRONTEND_DIR, path)


# --- Initialisation de la base de données ---

def init_db():
    """Crée les tables si elles n'existent pas et applique les migrations légères."""
    with db:
        db.create_tables([Livre, Client, Commande, CommandeLivre])

        # Vérification des colonnes ajoutées après la première version du schéma
        cols = [row[1] for row in db.execute_sql('PRAGMA table_info("livre")').fetchall()]
        if "image_url" not in cols:
            db.execute_sql('ALTER TABLE "livre" ADD COLUMN "image_url" TEXT DEFAULT ""')
            logger.info("Migration : colonne image_url ajoutée.")
        if "description" not in cols:
            db.execute_sql('ALTER TABLE "livre" ADD COLUMN "description" TEXT DEFAULT ""')
            logger.info("Migration : colonne description ajoutée.")


@app.before_request
def _connect_db():
    if db.is_closed():
        db.connect(reuse_if_open=True)

@app.teardown_request
def _close_db(exc):
    if not db.is_closed():
        db.close()


# --- Fonctions utilitaires ---

def livre_to_dict(livre: Livre) -> dict:
    return {
        "id":          livre.id,
        "titre":       livre.titre,
        "auteur":      livre.auteur,
        "description": livre.description,
        "prix_cents":  livre.prix_cents,
        "disponible":  bool(livre.disponible),
        "image_url":   livre.image_url,
    }


def commande_to_dict(cmd: Commande, with_lines: bool = True) -> dict:
    data = {
        "id":               cmd.id,
        "statut":           cmd.statut,
        "client": {
            "id":      cmd.client.id,
            "nom":     cmd.client.nom,
            "email":   cmd.client.email,
            "adresse": cmd.client.adresse,
        },
        "sous_total_cents": cmd.sous_total_cents,
        "taxes_cents":      cmd.taxes_cents,
        "livraison_cents":  cmd.livraison_cents,
        "total_cents":      cmd.total_cents,
    }

    if with_lines:
        data["items"] = [
            {
                "book_id":             ligne.livre.id,
                "titre":               ligne.livre.titre,
                "quantite":            ligne.quantite,
                "prix_unitaire_cents": ligne.livre.prix_cents,
                "ligne_total_cents":   ligne.livre.prix_cents * ligne.quantite,
            }
            for ligne in cmd.lignes
        ]

    return data


def error(msg: str, code: int = 400):
    """Retourne une réponse d'erreur JSON standardisée."""
    logger.warning("Erreur %d : %s", code, msg)
    resp = jsonify({"message": msg, "code": code})
    resp.status_code = code
    return resp


def validate_email(email: str) -> bool:
    """Validation basique du format d'email avec une regex."""
    return bool(_EMAIL_RE.match(email.strip()))


# --- Routes API : Livres ---

@app.get("/books")
def list_books():
    """
    Liste les livres du catalogue.
    Paramètres optionnels : ?search= (titre ou auteur), ?disponible=true
    """
    q          = request.args.get("search", "").strip().lower()
    dispo_only = request.args.get("disponible", "").lower() == "true"

    qs = Livre.select()

    if q:
        qs = qs.where((Livre.titre.contains(q)) | (Livre.auteur.contains(q)))

    if dispo_only:
        qs = qs.where(Livre.disponible == True)

    return jsonify([livre_to_dict(l) for l in qs])


@app.get("/books/<int:book_id>")
def get_book(book_id: int):
    try:
        livre = Livre.get_by_id(book_id)
        return jsonify(livre_to_dict(livre))
    except DoesNotExist:
        return error("Livre introuvable", 404)


@app.post("/books")
def create_book():
    """
    Crée un livre. Champs obligatoires : titre, auteur, prix_cents.
    """
    data = request.get_json(force=True, silent=True) or {}

    for f in ["titre", "auteur", "prix_cents"]:
        if f not in data:
            return error("Champ manquant : " + f, 400)

    try:
        prix = int(data["prix_cents"])
        assert prix >= 0
    except Exception:
        return error("prix_cents doit être un entier >= 0", 400)

    livre = Livre.create(
        titre       = data["titre"],
        auteur      = data["auteur"],
        description = data.get("description", ""),
        prix_cents  = prix,
        disponible  = bool(data.get("disponible", True)),
        image_url   = data.get("image_url", ""),
    )

    logger.info("Livre créé : id=%d, titre=%r", livre.id, livre.titre)
    return jsonify(livre_to_dict(livre)), 201


@app.put("/books/<int:book_id>")
def update_book(book_id: int):
    """Met à jour un livre (modification partielle — seuls les champs fournis sont modifiés)."""
    data = request.get_json(force=True, silent=True) or {}

    try:
        livre = Livre.get_by_id(book_id)
    except DoesNotExist:
        return error("Livre introuvable", 404)

    if "titre"       in data: livre.titre       = data["titre"]
    if "auteur"      in data: livre.auteur      = data["auteur"]
    if "description" in data: livre.description = data["description"]
    if "disponible"  in data: livre.disponible  = bool(data["disponible"])
    if "image_url"   in data: livre.image_url   = data["image_url"]

    if "prix_cents" in data:
        try:
            p = int(data["prix_cents"])
            assert p >= 0
            livre.prix_cents = p
        except Exception:
            return error("prix_cents doit être un entier >= 0", 400)

    livre.save()
    return jsonify(livre_to_dict(livre))


@app.delete("/books/<int:book_id>")
def delete_book(book_id: int):
    try:
        livre = Livre.get_by_id(book_id)
    except DoesNotExist:
        return error("Livre introuvable", 404)

    livre.delete_instance(recursive=True)
    return jsonify({"message": "Livre supprimé"})


# --- Routes API : Commandes ---

VALID_STATUTS = {"en_attente", "payee", "livree"}


@app.get("/orders")
def list_orders():
    """
    Liste les commandes avec pagination.
    Paramètres optionnels : ?page=1, ?limit=10, ?statut=en_attente
    """
    try:
        page  = max(1, int(request.args.get("page",  1)))
        limit = min(100, max(1, int(request.args.get("limit", 10))))
    except ValueError:
        return error("page et limit doivent être des entiers", 400)

    statut_filter = request.args.get("statut", "").strip()
    if statut_filter and statut_filter not in VALID_STATUTS:
        return error("Statut invalide. Valeurs acceptées : " + ", ".join(sorted(VALID_STATUTS)), 400)

    qs = Commande.select().order_by(Commande.id.desc())

    if statut_filter:
        qs = qs.where(Commande.statut == statut_filter)

    total  = qs.count()
    offset = (page - 1) * limit
    items  = list(qs.offset(offset).limit(limit))

    return jsonify({
        "total":  total,
        "page":   page,
        "limit":  limit,
        "pages":  (total + limit - 1) // limit,
        "orders": [commande_to_dict(c, with_lines=False) for c in items],
    })


@app.post("/orders")
def create_order():
    """
    Crée une commande.
    Le corps JSON doit contenir un objet client (nom, email, adresse)
    et une liste d'items (book_id, quantite).
    """
    data   = request.get_json(force=True, silent=True) or {}
    client = data.get("client", {})
    items  = data.get("items", [])

    for f in ["nom", "email", "adresse"]:
        if not client.get(f):
            return error("Client." + f + " est requis", 400)

    if not validate_email(client["email"]):
        return error("Format d'email invalide", 400)

    if not items:
        return error("La commande doit contenir au moins un article", 400)

    if len(items) > MAX_ITEMS_PER_ORDER:
        return error(f"Maximum {MAX_ITEMS_PER_ORDER} articles différents par commande", 400)

    lignes     = []
    sous_total = 0

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

    taxes     = round(sous_total * TAXE_TOTALE)
    livraison = LIVRAISON_CENTS if sous_total > 0 else 0
    total     = sous_total + taxes + livraison

    c = Client.create(
        nom     = client["nom"],
        email   = client["email"],
        adresse = client["adresse"],
    )

    cmd = Commande.create(
        client           = c,
        sous_total_cents = sous_total,
        taxes_cents      = taxes,
        livraison_cents  = livraison,
        total_cents      = total,
        statut           = "en_attente",
    )

    for livre, qty in lignes:
        CommandeLivre.create(commande=cmd, livre=livre, quantite=qty)

    logger.info("Commande créée : id=%d, client=%r, total=%d¢", cmd.id, client["nom"], total)

    return jsonify({
        "id":               cmd.id,
        "statut":           cmd.statut,
        "sous_total_cents": sous_total,
        "taxes_cents":      taxes,
        "livraison_cents":  livraison,
        "total_cents":      total,
    }), 201


@app.get("/orders/<int:order_id>")
def get_order(order_id: int):
    try:
        cmd = Commande.get_by_id(order_id)
        _   = list(cmd.lignes)
        return jsonify(commande_to_dict(cmd))
    except DoesNotExist:
        return error("Commande introuvable", 404)


@app.put("/orders/<int:order_id>/status")
def update_order_status(order_id: int):
    """
    Met à jour le statut d'une commande.
    Transitions autorisées : en_attente -> payee -> livree
    """
    data = request.get_json(force=True, silent=True) or {}
    new  = data.get("statut", "")

    if new not in VALID_STATUTS:
        return error("Statut invalide. Valeurs acceptées : " + ", ".join(sorted(VALID_STATUTS)), 400)

    try:
        cmd = Commande.get_by_id(order_id)
    except DoesNotExist:
        return error("Commande introuvable", 404)

    current = cmd.statut

    if new == current:
        return jsonify({"id": cmd.id, "statut": cmd.statut})

    allowed = {
        "en_attente": {"payee"},
        "payee":      {"livree"},
        "livree":     set(),
    }

    if new not in allowed[current]:
        return error(f"Transition non autorisée : '{current}' -> '{new}'", 400)

    cmd.statut = new
    cmd.save()

    logger.info("Commande #%d : %r -> %r", order_id, current, new)
    return jsonify({"id": cmd.id, "statut": cmd.statut})


# --- Lancement ---

if __name__ == "__main__":
    init_db()
    logger.info("Serveur démarré sur http://127.0.0.1:5000")
    app.run(host="127.0.0.1", port=5000, debug=DEBUG)
