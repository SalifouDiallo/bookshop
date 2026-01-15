# Configuration et création de la base SQLite utilisée par l'application.
# On utilise Peewee comme ORM. Ici on configure juste la connexion.

from peewee import SqliteDatabase
from .config import DB_FILE

# Création de la base SQLite.
# On active :
#   - WAL : meilleur pour les lectures/écritures en même temps
#   - foreign_keys : pour que les contraintes FK fonctionnent vraiment en SQLite
db = SqliteDatabase(
    DB_FILE,
    pragmas={
        "journal_mode": "wal",
        "foreign_keys": 1
    }
)
