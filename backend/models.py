# Modèles de la base de données pour l'application Bookshop.
# On utilise Peewee comme ORM. Chaque classe correspond à une table SQL.

from peewee import (
    Model, CharField, IntegerField, BooleanField, ForeignKeyField,
    Check, TextField
)
from .database import db


# Toutes nos tables vont hériter de BaseModel,
# ce qui permet d'éviter de répéter database = db partout.
class BaseModel(Model):
    class Meta:
        database = db


# ---------------------- Table Livre ---------------------- #
class Livre(BaseModel):
    # Titre du livre (ex: "Python pour les nuls")
    titre = CharField()

    # URL d'une image (facultatif). On met un string vide par défaut.
    image_url = CharField(null=True, default='')

    # Nom de l'auteur
    auteur = CharField()

    # Prix en centimes pour éviter les flottants (ex: 2999 = 29.99$)
    prix_cents = IntegerField(constraints=[Check('prix_cents >= 0')])

    # Indique si le livre est en stock ou non
    disponible = BooleanField(default=True)


# ---------------------- Table Client ---------------------- #
class Client(BaseModel):
    # Informations de base du client
    nom = CharField()
    email = CharField()
    adresse = TextField()  # TextField utile si l'adresse est longue


# ---------------------- Table Commande ---------------------- #
class Commande(BaseModel):
    # Relation 1 client -> plusieurs commandes
    client = ForeignKeyField(
        Client,
        backref='commandes',
        on_delete='CASCADE'   # Si un client est supprimé -> ses commandes aussi
    )

    # Montants (toujours en centimes)
    sous_total_cents = IntegerField(
        constraints=[Check('sous_total_cents >= 0')],
        default=0
    )
    taxes_cents = IntegerField(
        constraints=[Check('taxes_cents >= 0')],
        default=0
    )
    livraison_cents = IntegerField(
        constraints=[Check('livraison_cents >= 0')],
        default=0
    )
    total_cents = IntegerField(
        constraints=[Check('total_cents >= 0')],
        default=0
    )

    # Statut de la commande : en_attente, payee, livree
    statut = CharField(default='en_attente')


# ---------------------- Table CommandeLivre ---------------------- #
class CommandeLivre(BaseModel):
    # Table d'association entre Commande et Livre
    # Une commande peut contenir plusieurs livres
    commande = ForeignKeyField(
        Commande,
        backref='lignes',
        on_delete='CASCADE'   # Si la commande est supprimée -> lignes supprimées
    )

    # Le livre associé à la commande
    livre = ForeignKeyField(
        Livre,
        backref='lignes',
        on_delete='RESTRICT'  # Interdit de supprimer un livre encore lié à une commande
    )

    # Quantité commandée pour ce livre
    quantite = IntegerField(constraints=[Check('quantite > 0')])
