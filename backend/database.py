from peewee import SqliteDatabase
from .config import DB_FILE
db=SqliteDatabase(DB_FILE, pragmas={'journal_mode':'wal','foreign_keys':1})
