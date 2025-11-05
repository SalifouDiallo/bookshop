from peewee import Model, CharField, IntegerField, BooleanField, ForeignKeyField, Check, TextField
from .database import db

class BaseModel(Model):
    class Meta:
        database = db

class Livre(BaseModel):
    titre = CharField()
    image_url = CharField(null=True, default='')
    auteur = CharField()
    prix_cents = IntegerField(constraints=[Check('prix_cents >= 0')])
    disponible = BooleanField(default=True)

class Client(BaseModel):
    nom = CharField()
    email = CharField()
    adresse = TextField()

class Commande(BaseModel):
    client = ForeignKeyField(Client, backref='commandes', on_delete='CASCADE')
    sous_total_cents = IntegerField(constraints=[Check('sous_total_cents >= 0')], default=0)
    taxes_cents = IntegerField(constraints=[Check('taxes_cents >= 0')], default=0)
    livraison_cents = IntegerField(constraints=[Check('livraison_cents >= 0')], default=0)
    total_cents = IntegerField(constraints=[Check('total_cents >= 0')], default=0)
    statut = CharField(default='en_attente')

class CommandeLivre(BaseModel):
    commande = ForeignKeyField(Commande, backref='lignes', on_delete='CASCADE')
    livre = ForeignKeyField(Livre, backref='lignes', on_delete='RESTRICT')
    quantite = IntegerField(constraints=[Check('quantite > 0')])
