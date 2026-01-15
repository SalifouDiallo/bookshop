def test_create_order(client):
    """On crée une commande complète avec client + items"""
    # On crée d'abord un livre
    book_payload = {
        "titre": "Livre Commande",
        "auteur": "Test",
        "prix_cents": 2000
    }
    rb = client.post("/books", json=book_payload)
    assert rb.status_code == 201
    book_id = rb.get_json()["id"]

    # Maintenant on crée une commande
    order_payload = {
        "client": {
            "nom": "Test User",
            "email": "test@exemple.com",
            "adresse": "123 Rue X"
        },
        "items": [
            {"book_id": book_id, "quantite": 2}
        ]
    }

    rc = client.post("/orders", json=order_payload)
    assert rc.status_code == 201

    data = rc.get_json()

    # Vérification de base
    assert "id" in data
    assert data["statut"] == "en_attente"
    assert data["total_cents"] > 0
