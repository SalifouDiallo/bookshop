# Fichier de configuration générale du projet Bookshop.
# On regroupe ici les constantes utilisées un peu partout dans le backend.

# Taux de taxes appliqué sur les commandes (ex: 14.975 % au Québec)
TAXE_TOTALE = 0.14975

# Frais de livraison (en centimes). 500 = 5,00$
LIVRAISON_CENTS = 500

# Nom du fichier SQLite utilisé par Peewee
DB_FILE = "bookshop.db"

# Active le mode debug de Flask (utile en développement local)
DEBUG = True
