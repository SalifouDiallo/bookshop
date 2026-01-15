# Script de "seed" pour remplir la base avec une liste de livres.
# On l'utilise surtout au début du projet pour avoir des données de test.
# Ce fichier reste simple : il appelle init_db(), puis insère les lignes définies en bas.

from ..database import db
from ..models import Livre
from ..app import init_db
import json

# Données de départ : une trentaine de livres.
# On les met dans un JSON multi-ligne pour que ce soit plus propre
# et plus facile à modifier si jamais on ajoute/enlève un livre.
ROWS = json.loads(r"""
[
  {"titre":"Python pour les nuls","auteur":"John Doe","prix_cents":2999,"disponible":true,"image_url":"https://picsum.photos/seed/py1/600/360"},
  {"titre":"Flask en pratique","auteur":"Jane Smith","prix_cents":3499,"disponible":true,"image_url":"https://picsum.photos/seed/flask/600/360"},
  {"titre":"Bases de données SQLite","auteur":"A. Martin","prix_cents":2599,"disponible":true,"image_url":"https://picsum.photos/seed/sqlite/600/360"},
  {"titre":"Peewee ORM Guide","auteur":"C. Brown","prix_cents":1999,"disponible":true,"image_url":"https://picsum.photos/seed/peewee/600/360"},
  {"titre":"Développement Web","auteur":"N. K.","prix_cents":2799,"disponible":false,"image_url":"https://picsum.photos/seed/web/600/360"},
  {"titre":"Algorithmique débutant","auteur":"R. K.","prix_cents":2199,"disponible":true,"image_url":"https://picsum.photos/seed/algo/600/360"},
  {"titre":"Git & GitHub","auteur":"T. Nguyen","prix_cents":1899,"disponible":true,"image_url":"https://picsum.photos/seed/git/600/360"},
  {"titre":"CSS moderne","auteur":"L. Dupont","prix_cents":1599,"disponible":true,"image_url":"https://picsum.photos/seed/css/600/360"},
  {"titre":"JavaScript pas à pas","auteur":"E. Roy","prix_cents":2899,"disponible":true,"image_url":"https://picsum.photos/seed/js/600/360"},
  {"titre":"HTML5 essentiel","auteur":"C. Lee","prix_cents":1499,"disponible":true,"image_url":"https://picsum.photos/seed/html/600/360"},
  {"titre":"Data Science intro","auteur":"M. Chen","prix_cents":3299,"disponible":true,"image_url":"https://picsum.photos/seed/ds1/600/360"},
  {"titre":"Apprendre Pandas","auteur":"S. Ali","prix_cents":2799,"disponible":true,"image_url":"https://picsum.photos/seed/pandas/600/360"},
  {"titre":"Apprendre NumPy","auteur":"S. Ali","prix_cents":2699,"disponible":true,"image_url":"https://picsum.photos/seed/numpy/600/360"},
  {"titre":"APIs REST claires","auteur":"K. Omar","prix_cents":2399,"disponible":true,"image_url":"https://picsum.photos/seed/rest/600/360"},
  {"titre":"Test logiciel basique","auteur":"I. Novak","prix_cents":2199,"disponible":true,"image_url":"https://picsum.photos/seed/test/600/360"},
  {"titre":"Docker débutant","auteur":"P. Costa","prix_cents":3099,"disponible":true,"image_url":"https://picsum.photos/seed/docker/600/360"},
  {"titre":"Linux pratique","auteur":"G. Silva","prix_cents":2599,"disponible":true,"image_url":"https://picsum.photos/seed/linux/600/360"},
  {"titre":"Réseaux informatiques","auteur":"B. Diallo","prix_cents":3399,"disponible":true,"image_url":"https://picsum.photos/seed/network/600/360"},
  {"titre":"Sécurité web","auteur":"Y. Kim","prix_cents":3199,"disponible":true,"image_url":"https://picsum.photos/seed/secweb/600/360"},
  {"titre":"Cybersécurité 101","auteur":"A. Rossi","prix_cents":3399,"disponible":true,"image_url":"https://picsum.photos/seed/cyber/600/360"},
  {"titre":"SQL avancé","auteur":"D. Perez","prix_cents":2999,"disponible":true,"image_url":"https://picsum.photos/seed/sql2/600/360"},
  {"titre":"PostgreSQL pragmatique","auteur":"H. Klein","prix_cents":2899,"disponible":true,"image_url":"https://picsum.photos/seed/pg/600/360"},
  {"titre":"UML express","auteur":"J. Muller","prix_cents":2099,"disponible":true,"image_url":"https://picsum.photos/seed/uml/600/360"},
  {"titre":"Méthodes agiles","auteur":"F. Morel","prix_cents":2299,"disponible":true,"image_url":"https://picsum.photos/seed/agile/600/360"},
  {"titre":"Scrum en pratique","auteur":"F. Morel","prix_cents":2299,"disponible":true,"image_url":"https://picsum.photos/seed/scrum/600/360"},
  {"titre":"IA pour débutants","auteur":"L. Zhang","prix_cents":3499,"disponible":true,"image_url":"https://picsum.photos/seed/ai/600/360"},
  {"titre":"R pour l'analyse","auteur":"N. Patel","prix_cents":2899,"disponible":true,"image_url":"https://picsum.photos/seed/rstats/600/360"},
  {"titre":"GraphQL aperçu","auteur":"T. Park","prix_cents":2599,"disponible":true,"image_url":"https://picsum.photos/seed/gql/600/360"},
  {"titre":"CI/CD simple","auteur":"O. Arthur","prix_cents":2699,"disponible":true,"image_url":"https://picsum.photos/seed/cicd/600/360"},
  {"titre":"Kubernetes facile","auteur":"V. Singh","prix_cents":3599,"disponible":true,"image_url":"https://picsum.photos/seed/k8s/600/360"}
]
""")

def run():
    """Lance l’initialisation + l’insertion des livres."""
    init_db()  # crée les tables si elles n’existent pas

    # On utilise une transaction pour éviter les demi-insertions
    with db.atomic():
        for r in ROWS:
            Livre.create(**r)

    print(f"Seed OK : {len(ROWS)} livres insérés")


# Si on exécute directement ce fichier -> on charge la BD automatiquement.
if __name__ == "__main__":
    run()
