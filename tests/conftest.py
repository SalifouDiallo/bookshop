import pytest
from backend.app import app, init_db
from backend.database import db

@pytest.fixture
def client():
    """
    Client de test Flask.
    On initialise la BD avant chaque test.
    """
    init_db()
    app.config["TESTING"] = True

    with app.test_client() as client:
        yield client

    # On ferme proprement la BD après les tests
    if not db.is_closed():
        db.close()
