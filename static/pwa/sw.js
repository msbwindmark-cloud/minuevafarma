
const CACHE = 'mf-cache-v6';
const PRECACHE = ['/offline/'];

self.addEventListener('install', function(e){
  self.skipWaiting();
  e.waitUntil(caches.open(CACHE).then(function(c){ return c.addAll(PRECACHE).catch(function(){ return Promise.resolve(); }); }));
});

self.addEventListener('activate', function(e){
  e.waitUntil(caches.keys().then(function(keys){
    return Promise.all(keys.map(function(k){ if(k !== CACHE) return caches.delete(k); }));
  }).then(function(){ return self.clients.claim(); }));
});

self.addEventListener('fetch', function(e){
  if (e.request.method !== 'GET') return;
  var url = new URL(e.request.url);
  if (url.origin !== location.origin) return;
  if (url.pathname.startsWith('/static/') || url.pathname.startsWith('/media/')) {
    e.respondWith(
      fetch(e.request).then(function(res){
        var copia = res.clone();
        caches.open(CACHE).then(function(c){ c.put(e.request, copia); });
        return res;
      }).catch(function(){
        return caches.match(e.request);
      })
    );
    return;
  }
  e.respondWith(
    fetch(e.request).then(function(res){
      if (res && res.status === 200 && res.type === 'basic') {
        var copia = res.clone();
        caches.open(CACHE).then(function(c){ c.put(e.request, copia); });
      }
      return res;
    }).catch(function(){
      if (url.pathname.indexOf('/offline') === 0) return caches.match('/offline/');
      return caches.match('/offline/').then(function(p){ return p || new Response('<h1>Offline</h1>', {status:200, headers:{'Content-Type':'text/html'}}); });
    })
  );
});
