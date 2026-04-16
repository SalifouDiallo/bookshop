from peewee import SqliteDatabase
from .config import DB_FILE

# Configuration de la base SQLite avec optimisations
db = SqliteDatabase(
    DB_FILE,
    timeout=30,  # évite les erreurs de verrouillage
    pragmas={
        "journal_mode": "wal",      # meilleures performances en lecture/écriture
        "foreign_keys": 1,          # active les contraintes FK
        "cache_size": -1024 * 64    # ~64MB de cache mémoire
    }
)