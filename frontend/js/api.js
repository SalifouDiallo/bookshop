// Adresse de base de notre API Flask
const API_BASE = 'http://127.0.0.1:5000';

/*
  Récupère la liste des livres.
  Si un terme de recherche est fourni, on l'ajoute dans l'URL.
*/
async function getBooks(search = '') {
  const u = new URL(API_BASE + '/books');

  if (search.trim()) {
    u.searchParams.set('search', search.trim());
  }

  const r = await fetch(u);

  let d = null;
  try {
    d = await r.json();
  } catch {
    d = null;
  }

  if (!r.ok) {
    throw new Error(d?.message || 'Erreur lors du chargement des livres');
  }

  return d;
}

/*
  Envoie une nouvelle commande au backend.
  Le payload contient les infos du client + les items du panier.
*/
async function createOrder(payload) {
  const r = await fetch(API_BASE + '/orders', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });

  let d = null;
  try {
    d = await r.json();
  } catch {
    d = null;
  }

  if (!r.ok) {
    throw new Error(d?.message || 'Erreur lors de la création de la commande');
  }

  return d;
}

/*
  Récupère une commande complète selon son ID.
*/
async function getOrderById(id) {
  const r = await fetch(API_BASE + '/orders/' + id);

  let d = null;
  try {
    d = await r.json();
  } catch {
    d = null;
  }

  if (!r.ok) {
    throw new Error(d?.message || 'Commande introuvable');
  }

  return d;
}

/*
  Met à jour uniquement le statut d'une commande.
  Statuts possibles : en_attente, payee, livree.
*/
async function updateOrderStatus(id, statut) {
  const r = await fetch(API_BASE + '/orders/' + id + '/status', {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ statut })
  });

  let d = null;
  try {
    d = await r.json();
  } catch {
    d = null;
  }

  if (!r.ok) {
    throw new Error(d?.message || 'Erreur lors de la mise à jour du statut');
  }

  return d;
}

// On exporte nos fonctions pour pouvoir les importer dans app.html
export { getBooks, createOrder, getOrderById, updateOrderStatus };