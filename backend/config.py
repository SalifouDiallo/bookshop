# Fichier de configuration générale du projet Bookshop.
# Les valeurs sont chargées depuis un fichier .env si disponible,
# avec des valeurs par défaut raisonnables pour le développement local.

import os
from pathlib import Path

# Chargement du .env si python-dotenv est installé (optionnel mais recommandé)
try:
    from dotenv import load_dotenv
    # Cherche le .env à la racine du projet (deux niveaux au-dessus de config.py)
    _env_path = Path(__file__).resolve().parents[1] / ".env"
    load_dotenv(dotenv_path=_env_path)
except ImportError:
    pass  # python-dotenv absent : on continue avec les valeurs par défaut

# Environnement : "development" ou "production"
ENV = os.getenv("FLASK_ENV", "development")

# Mode debug Flask (actif en développement uniquement)
DEBUG = ENV == "development"

# Taux de taxes combinées (TPS 5 % + TVQ 9,975 % = 14,975 % au Québec)
TAXE_TOTALE = float(os.getenv("TAXE_TOTALE", "0.14975"))

# Frais de livraison fixes (en centimes). 500 = 5,00 $
LIVRAISON_CENTS = int(os.getenv("LIVRAISON_CENTS", "500"))

# Nom du fichier SQLite (relatif au répertoire de lancement)
DB_FILE = os.getenv("DB_FILE", "bookshop.db")

# Devise affichée dans l'interface
CURRENCY = os.getenv("CURRENCY", "CAD")

# Nombre maximum d'articles distincts par commande (protection contre les abus)
MAX_ITEMS_PER_ORDER = int(os.getenv("MAX_ITEMS_PER_ORDER", "50"))
