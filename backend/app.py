from flask import Flask, request, jsonify, send_from_directory, redirect
from flask_cors import CORS
from peewee import DoesNotExist
from .database import db
from .models import Livre, Client, Commande, CommandeLivre
from .config import TAXE_TOTALE, LIVRAISON_CENTS, DEBUG
import pathlib

app = Flask(__name__)
CORS(app)
FRONTEND_DIR = pathlib.Path(__file__).resolve().parents[1] / 'frontend'

@app.get('/')
def root():
    return redirect('/app', code=302)

@app.get('/app')
def serve_app():
    return send_from_directory(FRONTEND_DIR, 'app.html')

@app.get('/frontend/<path:path>')
def serve_frontend_files(path):
    return send_from_directory(FRONTEND_DIR, path)

def init_db():
    with db:
        db.create_tables([Livre, Client, Commande, CommandeLivre])
        cols = [row[1] for row in db.execute_sql('PRAGMA table_info("livre")').fetchall()]
        if 'image_url' not in cols:
            db.execute_sql('ALTER TABLE "livre" ADD COLUMN "image_url" TEXT DEFAULT ""')

@app.before_request
def _connect_db():
    if db.is_closed():
        db.connect(reuse_if_open=True)

@app.teardown_request
def _close_db(exc):
    if not db.is_closed():
        db.close()

def livre_to_dict(l):
    return {'id':l.id,'titre':l.titre,'auteur':l.auteur,'prix_cents':l.prix_cents,'disponible':bool(l.disponible),'image_url':l.image_url}

def commande_to_dict(c, with_lines=True):
    data={'id':c.id,'statut':c.statut,'client':{'id':c.client.id,'nom':c.client.nom,'email':c.client.email,'adresse':c.client.adresse},
          'sous_total_cents':c.sous_total_cents,'taxes_cents':c.taxes_cents,'livraison_cents':c.livraison_cents,'total_cents':c.total_cents}
    if with_lines:
        data['items']=[{'book_id':ln.livre.id,'titre':ln.livre.titre,'quantite':ln.quantite,'prix_unitaire_cents':ln.livre.prix_cents,'ligne_total_cents':ln.livre.prix_cents*ln.quantite} for ln in c.lignes]
    return data

def error(msg, code=400):
    resp= jsonify({'message':msg,'code':code}); resp.status_code=code; return resp

@app.get('/books')
def list_books():
    q=(request.args.get('search','').strip().lower())
    qs=Livre.select()
    if q:
        qs=qs.where((Livre.titre.contains(q)) | (Livre.auteur.contains(q)))
    return jsonify([livre_to_dict(l) for l in qs])

@app.get('/books/<int:book_id>')
def get_book(book_id):
    try:
        l=Livre.get_by_id(book_id); return jsonify(livre_to_dict(l))
    except DoesNotExist:
        return error('Livre introuvable',404)

@app.post('/books')
def create_book():
    data=request.get_json(force=True, silent=True) or {}
    for f in ['titre','auteur','prix_cents']:
        if f not in data: return error('Champ manquant: '+f,400)
    try:
        prix=int(data['prix_cents']); assert prix>=0
    except Exception:
        return error('prix_cents doit être un entier >= 0',400)
    l=Livre.create(titre=data['titre'], auteur=data['auteur'], prix_cents=prix, disponible=bool(data.get('disponible',True)), image_url=data.get('image_url',''))
    return jsonify(livre_to_dict(l)),201

@app.put('/books/<int:book_id>')
def update_book(book_id):
    data=request.get_json(force=True, silent=True) or {}
    try:
        l=Livre.get_by_id(book_id)
    except DoesNotExist:
        return error('Livre introuvable',404)
    if 'titre' in data: l.titre=data['titre']
    if 'auteur' in data: l.auteur=data['auteur']
    if 'prix_cents' in data:
        try:
            p=int(data['prix_cents']); assert p>=0; l.prix_cents=p
        except Exception:
            return error('prix_cents doit être un entier >= 0',400)
    if 'disponible' in data: l.disponible=bool(data['disponible'])
    if 'image_url' in data: l.image_url=data['image_url']
    l.save(); return jsonify(livre_to_dict(l))

@app.delete('/books/<int:book_id>')
def delete_book(book_id):
    try:
        l=Livre.get_by_id(book_id)
    except DoesNotExist:
        return error('Livre introuvable',404)
    l.delete_instance(recursive=True); return jsonify({'message':'Livre supprimé'})

VALID_STATUTS={'en_attente','payee','livree'}

@app.post('/orders')
def create_order():
    data=request.get_json(force=True, silent=True) or {}
    client=data.get('client',{}); items=data.get('items',[])
    for f in ['nom','email','adresse']:
        if not client.get(f): return error('Client.'+f+' est requis',400)
    if '@' not in client['email'] or '.' not in client['email']: return error('Email invalide',400)
    if not items: return error('La commande doit contenir au moins un article',400)
    lignes=[]; sous_total=0
    for it in items:
        try:
            bid=int(it['book_id']); qty=int(it.get('quantite',1))
        except Exception:
            return error('book_id et quantite doivent être des entiers',400)
        if qty<=0: return error('quantite doit être > 0',400)
        try:
            livre=Livre.get_by_id(bid)
        except DoesNotExist:
            return error(f'Livre {bid} introuvable',404)
        if not livre.disponible: return error(f"Le livre '{livre.titre}' n'est pas disponible",400)
        lignes.append((livre, qty)); sous_total += livre.prix_cents*qty
    taxes=round(sous_total*TAXE_TOTALE); livraison=LIVRAISON_CENTS if sous_total>0 else 0; total=sous_total+taxes+livraison
    c=Client.create(nom=client['nom'], email=client['email'], adresse=client['adresse'])
    cmd=Commande.create(client=c, sous_total_cents=sous_total, taxes_cents=taxes, livraison_cents=livraison, total_cents=total, statut='en_attente')
    for livre, qty in lignes: CommandeLivre.create(commande=cmd, livre=livre, quantite=qty)
    return jsonify({'id':cmd.id,'statut':cmd.statut,'sous_total_cents':sous_total,'taxes_cents':taxes,'livraison_cents':livraison,'total_cents':total}),201

@app.get('/orders/<int:order_id>')
def get_order(order_id):
    try:
        cmd=Commande.get_by_id(order_id); _=list(cmd.lignes); return jsonify(commande_to_dict(cmd))
    except DoesNotExist:
        return error('Commande introuvable',404)

@app.put('/orders/<int:order_id>/status')
def update_order_status(order_id):
    data=request.get_json(force=True, silent=True) or {}; new=data.get('statut','')
    if new not in VALID_STATUTS: return error('Statut invalide. Autorisés: '+str(sorted(list(VALID_STATUTS))),400)
    try: cmd=Commande.get_by_id(order_id)
    except DoesNotExist: return error('Commande introuvable',404)
    cmd.statut=new; cmd.save(); return jsonify({'id':cmd.id,'statut':cmd.statut})

if __name__=='__main__':
    init_db(); app.run(host='127.0.0.1', port=5000, debug=DEBUG)
