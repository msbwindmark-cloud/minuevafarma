
const DB_NAME='mf_offline'; const DB_VER=1;
let _db=null;
function abrirDB(){
  return new Promise((res,rej)=>{
    if(_db){res(_db);return;}
    const req=indexedDB.open(DB_NAME,DB_VER);
    req.onupgradeneeded=e=>{
      const db=e.target.result;
      if(!db.objectStoreNames.contains('productos')) db.createObjectStore('productos',{keyPath:'id'});
      if(!db.objectStoreNames.contains('ventas_offline')){ db.createObjectStore('ventas_offline',{keyPath:'tmp_id'}); }
    };
    req.onsuccess=e=>{_db=e.target.result;res(_db);};
    req.onerror=e=>rej(e);
  });
}
function guardarVentaOffline(datos){
  if(!datos.tmp_id){
    datos.tmp_id = (window.crypto && crypto.randomUUID) ? ('t'+crypto.randomUUID()) : ('t'+Date.now()+'-'+Math.random().toString(36).slice(2,10));
  }
  datos.sync=0;
  return abrirDB().then(db=>new Promise((res,rej)=>{
    const tx=db.transaction('ventas_offline','readwrite'); tx.objectStore('ventas_offline').put(datos);
    tx.oncomplete=()=>res(datos.tmp_id); tx.onerror=()=>rej(tx.error);
  }));
}
function ventasPendientes(){
  return abrirDB().then(db=>new Promise((res,rej)=>{
    const tx=db.transaction('ventas_offline','readonly'); const st=tx.objectStore('ventas_offline');
    const req=st.getAll(); req.onsuccess=()=>res((req.result||[]).filter(v=>v.sync===0)); req.onerror=()=>rej(req.error);
  }));
}
function marcarSincronizada(tmp_id){
  return abrirDB().then(db=>new Promise((res,rej)=>{
    const tx=db.transaction('ventas_offline','readwrite'); const st=tx.objectStore('ventas_offline');
    const r=st.get(tmp_id); r.onsuccess=()=>{ const v=r.result; if(v){ v.sync=1; st.put(v); } tx.oncomplete=()=>res(true); };
    tx.onerror=()=>rej(tx.error);
  }));
}
function sincronizar(){
  return ventasPendientes().then(lista=>{
    if(!lista.length) return Promise.resolve(0);
    let hechas = 0;
    return Promise.all(lista.map(v=>{
      const payload = { carrito: v.carrito || [], total: v.total, entregado: v.entregado, cliente_nombre: v.cliente_nombre, cliente_telefono: v.cliente_telefono, cliente_email: v.cliente_email, metodo_pago: v.metodo_pago };
      return fetch('/api/venta/offline/', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(payload)})
        .then(r=>{ if(r.ok){ hechas++; return marcarSincronizada(v.tmp_id); } })
        .catch(()=>{});
    })).then(()=>hechas);
  });
}
function guardarProductos(lista){
  return abrirDB().then(db=>new Promise((res,rej)=>{
    const tx=db.transaction('productos','readwrite'); const st=tx.objectStore('productos');
    st.clear(); lista.forEach(p=>st.put(p));
    tx.oncomplete=()=>res(true); tx.onerror=()=>rej(tx.error);
  }));
}
function leerProductos(){
  return abrirDB().then(db=>new Promise((res,rej)=>{
    const tx=db.transaction('productos','readonly'); const st=tx.objectStore('productos');
    const req=st.getAll(); req.onsuccess=()=>res(req.result||[]); req.onerror=()=>rej(req.error);
  }));
}
window.MiFarmaOffline={abrirDB,guardarVentaOffline,ventasPendientes,sincronizar,marcarSincronizada,guardarProductos,leerProductos};
