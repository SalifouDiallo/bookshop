import pytest


# ─── Tests positifs ────────────────────────────────────────────────────────────

def test_list_books_empty(client):
    """La route /books doit répondre 200 et renvoyer une liste (vide au départ)."""
    r = client.get("/books")
    assert r.status_code == 200
    assert isinstance(r.get_json(), list)


def test_create_and_get_book(client):
    """On crée un livre puis on le récupère via /books/<id>."""
    payload = {
        "titre": "Test Livre",
        "auteur": "Auteur X",
        "prix_cents": 1234,
        "description": "Un livre de test.",
    }

    r = client.post("/books", json=payload)
    assert r.status_code == 201
    data = r.get_json()
    book_id = data["id"]

    r2 = client.get(f"/books/{book_id}")
    assert r2.status_code == 200
    data2 = r2.get_json()

    assert data2["titre"] == "Test Livre"
    assert data2["auteur"] == "Auteur X"
    assert data2["prix_cents"] == 1234
    assert data2["description"] == "Un livre de test."
    assert data2["disponible"] is True


def test_create_book_defaults(client):
    """Un livre créé sans disponible ni description doit avoir les bonnes valeurs par défaut."""
    r = client.post("/books", json={"titre": "Défaut", "auteur": "A", "prix_cents": 500})
    assert r.status_code == 201
    data = r.get_json()
    assert data["disponible"] is True
    assert data["description"] == ""


def test_update_book(client):
    """On crée un livre puis on le met à jour partiellement."""
    r = client.post("/books", json={"titre": "Ancien titre", "auteur": "X", "prix_cents": 100})
    book_id = r.get_json()["id"]

    r2 = client.put(f"/books/{book_id}", json={"titre": "Nouveau titre", "prix_cents": 200})
    assert r2.status_code == 200
    data = r2.get_json()
    assert data["titre"] == "Nouveau titre"
    assert data["prix_cents"] == 200
    assert data["auteur"] == "X"  # Inchangé


def test_delete_book(client):
    """On crée un livre, on le supprime, puis la récupération doit retourner 404."""
    r = client.post("/books", json={"titre": "À supprimer", "auteur": "X", "prix_cents": 100})
    book_id = r.get_json()["id"]

    r_del = client.delete(f"/books/{book_id}")
    assert r_del.status_code == 200

    r_get = client.get(f"/books/{book_id}")
    assert r_get.status_code == 404


def test_search_books(client):
    """La recherche par titre ou auteur doit filtrer correctement."""
    client.post("/books", json={"titre": "Python avancé", "auteur": "Dupont", "prix_cents": 999})
    client.post("/books", json={"titre": "Java débutant", "auteur": "Martin", "prix_cents": 999})

    r = client.get("/books?search=python")
    results = r.get_json()
    assert len(results) >= 1
    assert all("python" in b["titre"].lower() or "python" in b["auteur"].lower() for b in results)


# ─── Tests négatifs ────────────────────────────────────────────────────────────

def test_get_book_not_found(client):
    """GET /books/<id> avec un id inexistant doit retourner 404."""
    r = client.get("/books/99999")
    assert r.status_code == 404


def test_create_book_missing_titre(client):
    """Créer un livre sans titre doit retourner 400."""
    r = client.post("/books", json={"auteur": "X", "prix_cents": 100})
    assert r.status_code == 400


def test_create_book_missing_auteur(client):
    """Créer un livre sans auteur doit retourner 400."""
    r = client.post("/books", json={"titre": "X", "prix_cents": 100})
    assert r.status_code == 400


def test_create_book_missing_prix(client):
    """Créer un livre sans prix_cents doit retourner 400."""
    r = client.post("/books", json={"titre": "X", "auteur": "Y"})
    assert r.status_code == 400


def test_create_book_negative_price(client):
    """Créer un livre avec un prix négatif doit retourner 400."""
    r = client.post("/books", json={"titre": "X", "auteur": "Y", "prix_cents": -1})
    assert r.status_code == 400


def test_create_book_invalid_price_type(client):
    """Créer un livre avec un prix non-entier doit retourner 400."""
    r = client.post("/books", json={"titre": "X", "auteur": "Y", "prix_cents": "pas_un_nombre"})
    assert r.status_code == 400


def test_update_book_not_found(client):
    """Mettre à jour un livre inexistant doit retourner 404."""
    r = client.put("/books/99999", json={"titre": "X"})
    assert r.status_code == 404


def test_delete_book_not_found(client):
    """Supprimer un livre inexistant doit retourner 404."""
    r = client.delete("/books/99999")
    assert r.status_code == 404


# ─── Tests techniques ──────────────────────────────────────────────────────────

def test_404_returns_json(client):
    """Une route inexistante doit retourner du JSON, pas du HTML."""
    r = client.get("/route/qui/nexiste/pas")
    assert r.status_code == 404
    data = r.get_json()
    assert data is not None
    assert "message" in data


def test_security_headers_present(client):
    """Les en-têtes de sécurité HTTP doivent être présents sur toutes les réponses."""
    r = client.get("/books")
    assert r.headers.get("X-Content-Type-Options") == "nosniff"
    assert r.headers.get("X-Frame-Options")         == "DENY"


def test_books_filter_disponible(client):
    """Le filtre ?disponible=true ne retourne que les livres disponibles."""
    client.post("/books", json={"titre": "Dispo",   "auteur": "A", "prix_cents": 100, "disponible": True})
    client.post("/books", json={"titre": "Indispo",  "auteur": "B", "prix_cents": 100, "disponible": False})

    r       = client.get("/books?disponible=true")
    results = r.get_json()
    assert r.status_code == 200
    assert all(b["disponible"] for b in results)
