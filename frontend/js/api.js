const API_BASE='http://127.0.0.1:5000';
async function getBooks(search=''){const u=new URL(API_BASE+'/books');if(search.trim())u.searchParams.set('search',search.trim());const r=await fetch(u);if(!r.ok)throw new Error('Erreur chargement livres');return await r.json();}
async function createOrder(p){const r=await fetch(API_BASE+'/orders',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(p)});const d=await r.json();if(!r.ok)throw new Error(d.message||'Erreur création commande');return d;}
async function getOrderById(id){const r=await fetch(API_BASE+'/orders/'+id);const d=await r.json();if(!r.ok)throw new Error(d.message||'Commande introuvable');return d;}
async function updateOrderStatus(id,statut){const r=await fetch(API_BASE+'/orders/'+id+'/status',{method:'PUT',headers:{'Content-Type':'application/json'},body:JSON.stringify({statut})});const d=await r.json();if(!r.ok)throw new Error(d.message||'Erreur mise à jour statut');return d;}
export {getBooks,createOrder,getOrderById,updateOrderStatus};
