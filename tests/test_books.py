def test_list_books(client):
    """Test simple : la route /books doit répondre 200"""
    r = client.get("/books")
    assert r.status_code == 200
    assert isinstance(r.get_json(), list)


def test_create_and_get_book(client):
    """On crée un livre puis on le récupère via /books/<id>"""
    payload = {
        "titre": "Test Livre",
        "auteur": "Auteur X",
        "prix_cents": 1234
    }

    # Création
    r = client.post("/books", json=payload)
    assert r.status_code == 201
    data = r.get_json()
    book_id = data["id"]

    # Vérification avec GET
    r2 = client.get(f"/books/{book_id}")
    assert r2.status_code == 200
    data2 = r2.get_json()

    assert data2["titre"] == "Test Livre"
    assert data2["auteur"] == "Auteur X"
    assert data2["prix_cents"] == 1234
