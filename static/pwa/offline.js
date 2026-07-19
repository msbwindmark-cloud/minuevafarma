
const API = { login: "/api/login/", productos: "/api/productos/", venta: "/api/venta/offline/" };

function $(s){ return document.querySelector(s); }
function el(tag, attrs, html){ const e=document.createElement(tag); if(attrs) for(const k in attrs) e.setAttribute(k, attrs[k]); if(html!=null) e.innerHTML=html; return e; }

function estadoBar(){
  const b = $("#estado");
  if(!b) return;
  b.className = navigator.onLine ? "badge bg-success" : "badge bg-warning text-dark";
  b.textContent = navigator.onLine ? "ONLINE" : "OFFLINE";
}

function mostrarLogin(){
  $("#vista").innerHTML = `
    <div class="row justify-content-center mt-5">
      <div class="col-md-5">
        <div class="card shadow">
          <div class="card-header bg-primary text-white"><i class="bi bi-capsule"></i> MiNuevaFarma - App Offline</div>
          <div class="card-body text-center">
            <p class="mb-3">No has iniciado sesion en la web.</p>
            <a href="/" class="btn btn-primary w-100"><i class="bi bi-box-arrow-in-right"></i> Ir a la web y entrar</a>
            <small class="text-muted d-block mt-2">Entra en la web normal primero, luego usa la App Offline.</small>
          </div>
        </div>
      </div>
    </div>`;
}

function hashLocal(p){
  let h = 0;
  for(let i=0;i<p.length;i++){ h = (h*31 + p.charCodeAt(i)) >>> 0; }
  return "h"+h.toString(16);
}

function hacerLogin(){
  const u = $("#user").value, p = $("#pass").value;
  if(!u || !p){ $("#loginErr").textContent = "Introduce usuario y contrasena"; return; }
  if(navigator.onLine){
    fetch(API.login, { method:"POST", headers:{"Content-Type":"application/json"}, body: JSON.stringify({username:u, password:p}) })
      .then(r=>r.json())
      .then(d=>{
        if(!d.ok){ $("#loginErr").textContent = d.msg; return; }
        localStorage.setItem("mf_token", d.token);
        localStorage.setItem("mf_user", JSON.stringify(d.usuario));
        localStorage.setItem("mf_user_local", u);
        localStorage.setItem("mf_pass_local", hashLocal(p));
        entrarApp();
      })
      .catch(()=> loginOffline(u, p));
  } else {
    loginOffline(u, p);
  }
}

function loginOffline(u, p){
  const lu = localStorage.getItem("mf_user_local");
  const lp = localStorage.getItem("mf_pass_local");
  if(lu === u && lp === hashLocal(p)){
    let saved = localStorage.getItem("mf_user");
    if(!saved){
      const userObj = { id:"offline", username:u, nombre:u, rol:"", is_superuser:false };
      localStorage.setItem("mf_user", JSON.stringify(userObj));
      localStorage.setItem("mf_token", "offline-token");
    }
    Swal.fire("Modo offline", "Sesion restaurada localmente", "info");
    entrarApp();
    return;
  }
  $("#loginErr").textContent = "Sin conexion: credenciales no reconocidas localmente. Conectate e inicia sesion una vez.";
}

function sesionGuardada(){
  return localStorage.getItem("mf_token") && localStorage.getItem("mf_user");
}

function entrarApp(){
  const user = JSON.parse(localStorage.getItem("mf_user") || "{}");
  $("#vista").innerHTML = `
    <nav class="navbar navbar-dark bg-primary mb-3">
      <div class="container-fluid">
        <span class="navbar-brand"><i class="bi bi-capsule"></i> MiNuevaFarma</span>
        <span class="text-white">` + user.nombre + `</span>
        <a href="/" class="btn btn-light btn-sm me-2">Volver a la web</a>
        <span id="estado" class="badge bg-success">ONLINE</span>
        <button class="btn btn-warning btn-sm" id="btnSync" onclick="sincronizar()">
          <i class="bi bi-cloud-arrow-up"></i> <span id="syncCount">0</span> pendientes
        </button>
        <button class="btn btn-light btn-sm" onclick="salir()">Salir</button>
      </div>
    </nav>
    <div class="container">
      <div class="row">
        <div class="col-md-7">
          <input id="buscar" class="form-control mb-2" placeholder="Buscar producto..." onkeyup="renderProductos()">
          <div id="lista" class="d-flex flex-column gap-2"></div>
        </div>
        <div class="col-md-5">
          <div class="card shadow"><div class="card-header">Carrito</div><div class="card-body" id="carrito"></div></div>
        </div>
      </div>
    </div>`;
  estadoBar();
  setTimeout(cargarProductos, 200);
  carritoCargar();
  actualizarPendientes();
}

function salir(){
  localStorage.removeItem("mf_token"); localStorage.removeItem("mf_user");
  mostrarLogin();
}

let PRODUCTOS = [];
function cargarProductos(){
  try {
    if(window.PRODUCTOS_INICIAL && window.PRODUCTOS_INICIAL.length){
      PRODUCTOS = window.PRODUCTOS_INICIAL;
      if(window.MiFarmaOffline){ MiFarmaOffline.guardarProductos(PRODUCTOS); }
      renderProductos();
      return;
    }
  } catch(e){ console.log("err PRODUCTOS_INICIAL", e); }
  if(window.MiFarmaOffline){
    MiFarmaOffline.leerProductos().then(p=>{
      if(p && p.length){ PRODUCTOS = p; renderProductos(); }
    }).catch(()=>{});
  }
  if(navigator.onLine){
    fetch(API.productos).then(r=>r.json()).then(d=>{
      if(d.ok && d.productos){ PRODUCTOS = d.productos; if(window.MiFarmaOffline) MiFarmaOffline.guardarProductos(PRODUCTOS); renderProductos(); }
    }).catch(err=>{});
  }
}

function renderProductos(){
  const q = ($("#buscar").value||"").toLowerCase();
  const lista = $("#lista");
  lista.innerHTML = "";
  PRODUCTOS.filter(p=>p.nombre.toLowerCase().includes(q) || p.codigo.toLowerCase().includes(q)).forEach(p=>{
    const b = el("button", {class:"btn btn-outline-secondary text-start d-flex justify-content-between"}, "<span>"+p.nombre+"</span><span>"+p.precio_venta+" EUR · stock "+p.stock_actual+"</span>");
    b.onclick = ()=>carritoAdd(p);
    lista.appendChild(b);
  });
}

let CARRITO = [];
function carritoCargar(){ CARRITO = JSON.parse(sessionStorage.getItem("mf_carrito")||"[]"); renderCarrito(); }
function carritoGuardar(){ sessionStorage.setItem("mf_carrito", JSON.stringify(CARRITO)); }
function carritoAdd(p){
  const f = CARRITO.find(c=>c.id===p.id);
  if(f){ f.cantidad++; } else { CARRITO.push({id:p.id, codigo:p.codigo, nombre:p.nombre, precio:p.precio_venta, cantidad:1}); }
  carritoGuardar(); renderCarrito();
}
function carritoMenos(id){ const f=CARRITO.find(c=>c.id===id); if(f){ f.cantidad--; if(f.cantidad<=0) CARRITO=CARRITO.filter(c=>c.id!==id); } carritoGuardar(); renderCarrito(); }
function carritoMas(id){ const f=CARRITO.find(c=>c.id===id); if(f) f.cantidad++; carritoGuardar(); renderCarrito(); }
function carritoQuitar(id){ CARRITO=CARRITO.filter(c=>c.id!==id); carritoGuardar(); renderCarrito(); }
function carritoTotal(){ return CARRITO.reduce((s,c)=>s+(c.precio*c.cantidad),0); }

function renderCarrito(){
  const c = $("#carrito"); if(!c) return;
  if(!CARRITO.length){ c.innerHTML = "<p class='text-muted'>Carrito vacio.</p>"; return; }
  let html = "<ul class='list-group mb-2'>";
  CARRITO.forEach(i=>{ html += "<li class='list-group-item d-flex justify-content-between align-items-center'>"+i.nombre+" x"+i.cantidad+"<span>"+(i.precio*i.cantidad).toFixed(2)+" EUR <button class='btn btn-sm btn-outline-danger' onclick=\"carritoQuitar('"+i.id+"')\"><i class='bi bi-x'></i></button></span></li>"; });
  html += "</ul><h5>Total: "+carritoTotal().toFixed(2)+" EUR</h5>";
  html += "<button class='btn btn-success w-100' onclick='cobrar()'><i class='bi bi-check-lg'></i> Cobrar y generar ticket</button>";
  c.innerHTML = html;
}

function cobrar(){
  if(!CARRITO.length){ Swal.fire("Carrito vacio", "Anade productos primero", "warning"); return; }
  const total = carritoTotal();
  Swal.fire({
    title: "Cobrar venta",
    html:
      "<input id='sw_cli' class='swal2-input' placeholder='Nombre del cliente (opcional)'>" +
      "<input id='sw_tel' class='swal2-input' placeholder='Telefono (para SMS)'>" +
      "<input id='sw_ema' class='swal2-input' placeholder='Email (para ticket)'>" +
      "<select id='sw_met' class='swal2-input'><option value='EFECTIVO'>Efectivo</option><option value='TARJETA'>Tarjeta</option><option value='TRANSFERENCIA'>Transferencia</option></select>" +
      "<input id='sw_ent' type='number' min='0' step='0.01' class='swal2-input' placeholder='Entregado (EUR)' value='" + total.toFixed(2) + "'>" +
      "<p class='text-muted'>Total: " + total.toFixed(2) + " EUR</p>" +
      "<p id='sw_cam' class='text-success'>Cambio: 0.00 EUR</p>",
    focusConfirm: false,
    showCancelButton: true,
    confirmButtonText: "<i class='bi bi-check-lg'></i> Cobrar y generar ticket",
    didOpen: function(){
      document.getElementById('sw_ent').addEventListener('input', function(){
        const e = parseFloat(this.value)||0;
        document.getElementById('sw_cam').textContent = "Cambio: " + (e - total).toFixed(2) + " EUR";
      });
    },
    preConfirm: function(){
      const cliente = document.getElementById('sw_cli').value || "";
      const telefono = document.getElementById('sw_tel').value || "";
      const email = document.getElementById('sw_ema').value || "";
      const metodo = document.getElementById('sw_met').value;
      const entregado = parseFloat(document.getElementById('sw_ent').value) || total;
      return { cliente: cliente, telefono: telefono, email: email, metodo: metodo, entregado: entregado };
    }
  }).then(function(res){
    if(!res.isConfirmed) return;
    const d = res.value;
    const venta = {
      carrito: CARRITO.map(c=>({id:c.id, cantidad:c.cantidad, precio:c.precio, subtotal:c.precio*c.cantidad})),
      total: total, entregado: d.entregado, cliente_nombre: d.cliente,
      cliente_telefono: d.telefono, cliente_email: d.email, metodo_pago: d.metodo
    };
    if(navigator.onLine){
      fetch(API.venta, { method:"POST", headers:{"Content-Type":"application/json"}, body: JSON.stringify(venta) })
        .then(r=>r.json()).then(dd=>{ if(dd.ok){ CARRITO=[]; carritoGuardar(); renderCarrito(); Swal.fire("Venta registrada", "Codigo "+dd.codigo, "success"); } else { Swal.fire("Error", dd.msg, "error"); } })
        .catch(()=>guardarOffline(venta));
    } else {
      guardarOffline(venta);
    }
  });
}

function guardarOffline(venta){
  MiFarmaOffline.guardarVentaOffline(venta).then(()=>{ CARRITO=[]; carritoGuardar(); renderCarrito(); actualizarPendientes(); Swal.fire("Sin conexion", "Venta guardada en modo offline. Se sincronizara al reconectar.", "info"); });
}

function actualizarPendientes(){
  const s = $("#syncCount"); if(!s) return;
  MiFarmaOffline.ventasPendientes().then(l=>{ s.textContent = l.length; });
}

function sincronizar(){
  if(!navigator.onLine){ Swal.fire("Sin conexion", "Conectate para sincronizar", "warning"); return; }
  Swal.fire({ title:"Sincronizando...", allowOutsideClick:false, didOpen:()=>Swal.showLoading() });
  MiFarmaOffline.sincronizar().then(n=>{ Swal.fire("Sincronizado", n+" venta(s) enviada(s)", "success").then(()=>actualizarPendientes()); })
    .catch(()=>Swal.fire("Error", "No se pudo sincronizar", "error"));
}

window.addEventListener("online", ()=>{ estadoBar(); actualizarPendientes(); });
window.addEventListener("offline", estadoBar);

function arrancar(){
  if(sesionGuardada() || (window.PRODUCTOS_INICIAL && window.PRODUCTOS_INICIAL.length)){ entrarApp(); }
  else { mostrarLogin(); }
}

if(document.readyState === "loading"){ document.addEventListener("DOMContentLoaded", arrancar); }
else { arrancar(); }
