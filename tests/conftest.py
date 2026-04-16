import pytest
from peewee import SqliteDatabase
from backend.models import Livre, Client, Commande, CommandeLivre
from backend.app import app, init_db
import backend.database as db_module

# Base de données en mémoire réinitialisée à chaque test
TEST_DB = SqliteDatabase(
    ":memory:",
    pragmas={"foreign_keys": 1}
)

MODELS = [Livre, Client, Commande, CommandeLivre]


@pytest.fixture
def client():
    """
    Client de test Flask avec base de données en mémoire isolée.
    La BD est créée proprement avant chaque test et détruite après.
    """
    # Remplace la BD de production par la BD de test en mémoire
    db_module.db = TEST_DB
    for model in MODELS:
        model._meta.database = TEST_DB

    with TEST_DB:
        TEST_DB.create_tables(MODELS)
        app.config["TESTING"] = True

        with app.test_client() as test_client:
            yield test_client

        TEST_DB.drop_tables(MODELS)
