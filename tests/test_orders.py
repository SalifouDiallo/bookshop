import pytest


def _create_book(client, disponible=True):
    """Utilitaire : crée un livre et retourne son id."""
    r = client.post("/books", json={
        "titre":      "Livre Commande",
        "auteur":     "Test",
        "prix_cents": 2000,
        "disponible": disponible,
    })
    assert r.status_code == 201
    return r.get_json()["id"]


def _create_order(client, book_id, quantite=2):
    """Utilitaire : crée une commande et retourne la réponse complète."""
    payload = {
        "client": {
            "nom":     "Test User",
            "email":   "test@exemple.com",
            "adresse": "123 Rue X",
        },
        "items": [{"book_id": book_id, "quantite": quantite}],
    }
    return client.post("/orders", json=payload)


# ─── Tests positifs — création ────────────────────────────────────────────────

def test_create_order(client):
    """Création d'une commande complète avec client + items."""
    book_id = _create_book(client)
    rc      = _create_order(client, book_id)
    assert rc.status_code == 201

    data = rc.get_json()
    assert "id"     in data
    assert data["statut"]      == "en_attente"
    assert data["total_cents"] > 0


def test_order_amounts_calculation(client):
    """Le calcul des montants (taxes + livraison) doit être exact."""
    book_id = _create_book(client)
    data    = _create_order(client, book_id, quantite=1).get_json()

    sous_total         = 2000
    taxes_attendues    = round(sous_total * 0.14975)
    livraison_attendue = 500

    assert data["sous_total_cents"] == sous_total
    assert data["taxes_cents"]      == taxes_attendues
    assert data["livraison_cents"]  == livraison_attendue
    assert data["total_cents"]      == sous_total + taxes_attendues + livraison_attendue


def test_get_order(client):
    """GET /orders/<id> retourne tous les détails de la commande."""
    book_id  = _create_book(client)
    order_id = _create_order(client, book_id).get_json()["id"]

    r    = client.get(f"/orders/{order_id}")
    data = r.get_json()

    assert r.status_code == 200
    assert data["id"]                   == order_id
    assert data["client"]["nom"]        == "Test User"
    assert data["client"]["email"]      == "test@exemple.com"
    assert len(data["items"])           == 1
    assert data["items"][0]["quantite"] == 2


def test_status_transition_en_attente_to_payee(client):
    """Transition en_attente → payee doit être autorisée."""
    book_id  = _create_book(client)
    order_id = _create_order(client, book_id).get_json()["id"]

    r = client.put(f"/orders/{order_id}/status", json={"statut": "payee"})
    assert r.status_code == 200
    assert r.get_json()["statut"] == "payee"


def test_status_transition_payee_to_livree(client):
    """Transition payee → livree doit être autorisée."""
    book_id  = _create_book(client)
    order_id = _create_order(client, book_id).get_json()["id"]

    client.put(f"/orders/{order_id}/status", json={"statut": "payee"})
    r = client.put(f"/orders/{order_id}/status", json={"statut": "livree"})
    assert r.status_code == 200
    assert r.get_json()["statut"] == "livree"


def test_status_same_value_is_idempotent(client):
    """Envoyer le statut actuel ne doit pas retourner d'erreur."""
    book_id  = _create_book(client)
    order_id = _create_order(client, book_id).get_json()["id"]

    r = client.put(f"/orders/{order_id}/status", json={"statut": "en_attente"})
    assert r.status_code == 200


# ─── Tests positifs — liste paginée ───────────────────────────────────────────

def test_list_orders_empty(client):
    """GET /orders renvoie 200 et une liste vide si aucune commande."""
    r    = client.get("/orders")
    data = r.get_json()

    assert r.status_code == 200
    assert data["total"]  == 0
    assert data["orders"] == []


def test_list_orders_returns_created(client):
    """GET /orders retourne bien la commande créée."""
    book_id = _create_book(client)
    _create_order(client, book_id)

    r    = client.get("/orders")
    data = r.get_json()

    assert r.status_code == 200
    assert data["total"]    == 1
    assert len(data["orders"]) == 1


def test_list_orders_pagination(client):
    """La pagination de GET /orders fonctionne correctement."""
    book_id = _create_book(client)
    for _ in range(5):
        _create_order(client, book_id)

    r1 = client.get("/orders?page=1&limit=3").get_json()
    r2 = client.get("/orders?page=2&limit=3").get_json()

    assert r1["total"]         == 5
    assert r1["pages"]         == 2
    assert len(r1["orders"])   == 3
    assert len(r2["orders"])   == 2


def test_list_orders_filter_by_statut(client):
    """Le filtre ?statut= retourne uniquement les commandes correspondantes."""
    book_id  = _create_book(client)
    order_id = _create_order(client, book_id).get_json()["id"]
    client.put(f"/orders/{order_id}/status", json={"statut": "payee"})

    r_attente = client.get("/orders?statut=en_attente").get_json()
    r_payee   = client.get("/orders?statut=payee").get_json()

    assert r_attente["total"] == 0
    assert r_payee["total"]   == 1


# ─── Tests négatifs — validation ─────────────────────────────────────────────

def test_create_order_missing_client_nom(client):
    """Commande sans nom client → 400."""
    book_id = _create_book(client)
    r = client.post("/orders", json={
        "client": {"email": "a@b.com", "adresse": "Rue X"},
        "items":  [{"book_id": book_id, "quantite": 1}],
    })
    assert r.status_code == 400


def test_create_order_missing_client_email(client):
    """Commande sans email client → 400."""
    book_id = _create_book(client)
    r = client.post("/orders", json={
        "client": {"nom": "A", "adresse": "Rue X"},
        "items":  [{"book_id": book_id, "quantite": 1}],
    })
    assert r.status_code == 400


def test_create_order_invalid_email_format(client):
    """Email sans domaine valide → 400."""
    book_id = _create_book(client)
    r = client.post("/orders", json={
        "client": {"nom": "A", "email": "pasunemail", "adresse": "Rue X"},
        "items":  [{"book_id": book_id, "quantite": 1}],
    })
    assert r.status_code == 400


def test_create_order_invalid_email_no_dot(client):
    """Email sans point dans le domaine → 400."""
    book_id = _create_book(client)
    r = client.post("/orders", json={
        "client": {"nom": "A", "email": "a@bcom", "adresse": "Rue X"},
        "items":  [{"book_id": book_id, "quantite": 1}],
    })
    assert r.status_code == 400


def test_create_order_empty_items(client):
    """Commande sans items → 400."""
    r = client.post("/orders", json={
        "client": {"nom": "A", "email": "a@b.com", "adresse": "Rue X"},
        "items":  [],
    })
    assert r.status_code == 400


def test_create_order_unavailable_book(client):
    """Commander un livre indisponible → 400."""
    book_id = _create_book(client, disponible=False)
    assert _create_order(client, book_id).status_code == 400


def test_create_order_book_not_found(client):
    """Commander un livre inexistant → 404."""
    r = client.post("/orders", json={
        "client": {"nom": "A", "email": "a@b.com", "adresse": "Rue X"},
        "items":  [{"book_id": 99999, "quantite": 1}],
    })
    assert r.status_code == 404


def test_create_order_zero_quantity(client):
    """quantite=0 → 400."""
    book_id = _create_book(client)
    r = client.post("/orders", json={
        "client": {"nom": "A", "email": "a@b.com", "adresse": "Rue X"},
        "items":  [{"book_id": book_id, "quantite": 0}],
    })
    assert r.status_code == 400


def test_get_order_not_found(client):
    """GET /orders/<id> inexistant → 404."""
    assert client.get("/orders/99999").status_code == 404


def test_invalid_status_value(client):
    """Statut inconnu → 400."""
    book_id  = _create_book(client)
    order_id = _create_order(client, book_id).get_json()["id"]
    assert client.put(f"/orders/{order_id}/status", json={"statut": "annulee"}).status_code == 400


def test_invalid_status_transition_backwards(client):
    """livree → en_attente → 400."""
    book_id  = _create_book(client)
    order_id = _create_order(client, book_id).get_json()["id"]
    client.put(f"/orders/{order_id}/status", json={"statut": "payee"})
    client.put(f"/orders/{order_id}/status", json={"statut": "livree"})
    assert client.put(f"/orders/{order_id}/status", json={"statut": "en_attente"}).status_code == 400


def test_invalid_status_transition_skip(client):
    """en_attente → livree (saut) → 400."""
    book_id  = _create_book(client)
    order_id = _create_order(client, book_id).get_json()["id"]
    assert client.put(f"/orders/{order_id}/status", json={"statut": "livree"}).status_code == 400


def test_update_order_status_not_found(client):
    """Statut d'une commande inexistante → 404."""
    assert client.put("/orders/99999/status", json={"statut": "payee"}).status_code == 404


def test_list_orders_invalid_statut_filter(client):
    """Filtre statut invalide dans GET /orders → 400."""
    assert client.get("/orders?statut=inconnu").status_code == 400
