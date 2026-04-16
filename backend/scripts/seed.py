# Script de "seed" pour remplir la base avec une liste de livres.
# Ce fichier reste simple : il appelle init_db(), puis insère les lignes définies en bas.

from backend.database import db
from backend.models import Livre
from backend.app import init_db
import json

# Données de départ : une trentaine de livres avec descriptions.
ROWS = json.loads(r"""
[
  {"titre":"Python pour les nuls","auteur":"John Doe","prix_cents":2999,"disponible":true,"image_url":"https://picsum.photos/seed/py1/600/360","description":"Une introduction complète au langage Python, idéale pour les débutants souhaitant apprendre la programmation pas à pas."},
  {"titre":"Flask en pratique","auteur":"Jane Smith","prix_cents":3499,"disponible":true,"image_url":"https://picsum.photos/seed/flask/600/360","description":"Construisez des applications web modernes avec Flask, des routes aux APIs RESTful en passant par les templates Jinja2."},
  {"titre":"Bases de données SQLite","auteur":"A. Martin","prix_cents":2599,"disponible":true,"image_url":"https://picsum.photos/seed/sqlite/600/360","description":"Maîtrisez SQLite pour vos projets légers : création de schémas, requêtes optimisées et bonnes pratiques de persistance."},
  {"titre":"Peewee ORM Guide","auteur":"C. Brown","prix_cents":1999,"disponible":true,"image_url":"https://picsum.photos/seed/peewee/600/360","description":"Guide complet de l'ORM Peewee pour Python : modèles, relations, migrations et requêtes avancées avec SQLite et PostgreSQL."},
  {"titre":"Développement Web","auteur":"N. K.","prix_cents":2799,"disponible":false,"image_url":"https://picsum.photos/seed/web/600/360","description":"Vue d'ensemble du développement web moderne : HTML, CSS, JavaScript et les frameworks incontournables du marché."},
  {"titre":"Algorithmique débutant","auteur":"R. K.","prix_cents":2199,"disponible":true,"image_url":"https://picsum.photos/seed/algo/600/360","description":"Les bases de l'algorithmique expliquées simplement : tris, recherches, récursivité et complexité pour les étudiants."},
  {"titre":"Git & GitHub","auteur":"T. Nguyen","prix_cents":1899,"disponible":true,"image_url":"https://picsum.photos/seed/git/600/360","description":"Maîtrisez le versionnement avec Git et la collaboration via GitHub : branches, pull requests et workflows professionnels."},
  {"titre":"CSS moderne","auteur":"L. Dupont","prix_cents":1599,"disponible":true,"image_url":"https://picsum.photos/seed/css/600/360","description":"Flexbox, Grid, animations et variables CSS — tout ce qu'il faut pour créer des interfaces élégantes et responsives."},
  {"titre":"JavaScript pas à pas","auteur":"E. Roy","prix_cents":2899,"disponible":true,"image_url":"https://picsum.photos/seed/js/600/360","description":"De la syntaxe de base aux fonctionnalités ES2023 : closures, promesses, async/await et manipulation du DOM."},
  {"titre":"HTML5 essentiel","auteur":"C. Lee","prix_cents":1499,"disponible":true,"image_url":"https://picsum.photos/seed/html/600/360","description":"Structure sémantique, formulaires avancés, accessibilité et nouvelles API HTML5 pour construire des pages solides."},
  {"titre":"Data Science intro","auteur":"M. Chen","prix_cents":3299,"disponible":true,"image_url":"https://picsum.photos/seed/ds1/600/360","description":"Introduction à la science des données : exploration, visualisation et modélisation avec Python, Pandas et Matplotlib."},
  {"titre":"Apprendre Pandas","auteur":"S. Ali","prix_cents":2799,"disponible":true,"image_url":"https://picsum.photos/seed/pandas/600/360","description":"Manipulation et analyse de données avec Pandas : DataFrames, nettoyage, agrégations et export vers différents formats."},
  {"titre":"Apprendre NumPy","auteur":"S. Ali","prix_cents":2699,"disponible":true,"image_url":"https://picsum.photos/seed/numpy/600/360","description":"Calcul numérique haute performance avec NumPy : tableaux multidimensionnels, opérations vectorisées et algèbre linéaire."},
  {"titre":"APIs REST claires","auteur":"K. Omar","prix_cents":2399,"disponible":true,"image_url":"https://picsum.photos/seed/rest/600/360","description":"Conception et développement d'APIs RESTful robustes : principes HTTP, authentification, versionnement et documentation."},
  {"titre":"Test logiciel basique","auteur":"I. Novak","prix_cents":2199,"disponible":true,"image_url":"https://picsum.photos/seed/test/600/360","description":"Tests unitaires, d'intégration et fonctionnels : pytest, mocks, couverture de code et intégration continue."},
  {"titre":"Docker débutant","auteur":"P. Costa","prix_cents":3099,"disponible":true,"image_url":"https://picsum.photos/seed/docker/600/360","description":"Conteneurisez vos applications avec Docker : images, volumes, réseaux et composition de services avec Docker Compose."},
  {"titre":"Linux pratique","auteur":"G. Silva","prix_cents":2599,"disponible":true,"image_url":"https://picsum.photos/seed/linux/600/360","description":"Commandes essentielles, scripts Bash, gestion des processus et administration de base pour les développeurs sous Linux."},
  {"titre":"Réseaux informatiques","auteur":"B. Diallo","prix_cents":3399,"disponible":true,"image_url":"https://picsum.photos/seed/network/600/360","description":"Protocoles TCP/IP, DNS, HTTP/HTTPS et architecture réseau expliqués pour les développeurs et administrateurs systèmes."},
  {"titre":"Sécurité web","auteur":"Y. Kim","prix_cents":3199,"disponible":true,"image_url":"https://picsum.photos/seed/secweb/600/360","description":"OWASP Top 10, injections SQL, XSS, CSRF et bonnes pratiques pour sécuriser vos applications web contre les attaques courantes."},
  {"titre":"Cybersécurité 101","auteur":"A. Rossi","prix_cents":3399,"disponible":true,"image_url":"https://picsum.photos/seed/cyber/600/360","description":"Panorama de la cybersécurité : cryptographie, gestion des vulnérabilités, tests de pénétration et politique de sécurité."},
  {"titre":"SQL avancé","auteur":"D. Perez","prix_cents":2999,"disponible":true,"image_url":"https://picsum.photos/seed/sql2/600/360","description":"Requêtes complexes, fenêtres analytiques, optimisation des index et transactions pour maîtriser SQL en profondeur."},
  {"titre":"PostgreSQL pragmatique","auteur":"H. Klein","prix_cents":2899,"disponible":true,"image_url":"https://picsum.photos/seed/pg/600/360","description":"Déployez et optimisez PostgreSQL : types avancés, extensions, réplication et bonnes pratiques pour la production."},
  {"titre":"UML express","auteur":"J. Muller","prix_cents":2099,"disponible":true,"image_url":"https://picsum.photos/seed/uml/600/360","description":"Diagrammes de classes, de séquence et d'activité : apprenez UML rapidement pour documenter et concevoir vos systèmes."},
  {"titre":"Méthodes agiles","auteur":"F. Morel","prix_cents":2299,"disponible":true,"image_url":"https://picsum.photos/seed/agile/600/360","description":"Scrum, Kanban et Lean appliqués au développement logiciel : rituels, rôles et outils pour des équipes plus efficaces."},
  {"titre":"Scrum en pratique","auteur":"F. Morel","prix_cents":2299,"disponible":true,"image_url":"https://picsum.photos/seed/scrum/600/360","description":"Guide opérationnel de Scrum : sprint planning, daily stand-up, rétrospectives et gestion du backlog produit."},
  {"titre":"IA pour débutants","auteur":"L. Zhang","prix_cents":3499,"disponible":true,"image_url":"https://picsum.photos/seed/ai/600/360","description":"Introduction à l'intelligence artificielle : machine learning, réseaux de neurones et applications concrètes sans prérequis mathématiques avancés."},
  {"titre":"R pour l'analyse","auteur":"N. Patel","prix_cents":2899,"disponible":true,"image_url":"https://picsum.photos/seed/rstats/600/360","description":"Analyse statistique et visualisation avec R : ggplot2, dplyr, tests statistiques et rapports reproductibles avec R Markdown."},
  {"titre":"GraphQL aperçu","auteur":"T. Park","prix_cents":2599,"disponible":true,"image_url":"https://picsum.photos/seed/gql/600/360","description":"Découvrez GraphQL comme alternative à REST : schémas, requêtes, mutations, subscriptions et intégration avec Apollo."},
  {"titre":"CI/CD simple","auteur":"O. Arthur","prix_cents":2699,"disponible":true,"image_url":"https://picsum.photos/seed/cicd/600/360","description":"Automatisez vos déploiements avec GitHub Actions et GitLab CI : pipelines, tests automatiques et livraison continue."},
  {"titre":"Kubernetes facile","auteur":"V. Singh","prix_cents":3599,"disponible":true,"image_url":"https://picsum.photos/seed/k8s/600/360","description":"Orchestration de conteneurs avec Kubernetes : pods, services, déploiements et gestion de clusters en environnement cloud."}
]
""")


def run():
    """Lance l'initialisation + l'insertion des livres."""
    init_db()  # crée les tables si elles n'existent pas

    # Utiliser une transaction pour éviter les demi-insertions
    with db.atomic():
        for r in ROWS:
            Livre.create(**r)

    print(f"Seed OK : {len(ROWS)} livres insérés")


# En exécutant directement ce fichier -> on charge la BD automatiquement.
if __name__ == "__main__":
    run()
