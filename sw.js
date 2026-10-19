/* Offline app shell + best-effort caching for the separately downloaded CAS runtime. */
const VERSION='calculator2-shell-v1';
const RUNTIME='calculator2-runtime-v1';
const CORE=['./','./index.html','./manifest.webmanifest','./assets/styles.css','./assets/catalog.json','./src/app.js','./src/registry.js','./src/worker.js','./icons/192.png','./icons/512.png','./python/engine.py','./python/plugins.json','./python/plugins/__init__.py','./python/plugins/basic.py','./python/plugins/calculus.py','./python/plugins/complex_ops.py','./python/plugins/geometry.py','./python/plugins/waves.py','./python/plugins/linear.py'];
self.addEventListener('install',event=>{
  event.waitUntil(caches.open(VERSION).then(cache=>cache.addAll(CORE)).then(()=>self.skipWaiting()));
});
self.addEventListener('activate',event=>{
  event.waitUntil(caches.keys().then(keys=>Promise.all(keys.filter(k=>!([VERSION,RUNTIME].includes(k))).map(k=>caches.delete(k)))).then(()=>self.clients.claim()));
});
self.addEventListener('fetch',event=>{
  const request=event.request;
  if(request.method!=='GET')return;
  const url=new URL(request.url);
  if(url.protocol!=='https:' && url.protocol!=='http:')return;
  if(url.origin===self.location.origin){
    if(request.mode==='navigate'){
      event.respondWith(fetch(request).catch(()=>caches.match('./index.html')));
    }else{
      event.respondWith(caches.match(request).then(hit=>hit || fetch(request).then(response=>{
        if(response.ok){const copy=response.clone();caches.open(VERSION).then(cache=>cache.put(request,copy));}
        return response;
      })));
    }
  }else if(url.hostname==='cdn.jsdelivr.net'){
    event.respondWith(caches.open(RUNTIME).then(async cache=>{
      const hit=await cache.match(request);if(hit)return hit;
      const response=await fetch(request);
      if(response.ok || response.type==='opaque')cache.put(request,response.clone()).catch(()=>{});
      return response;
    }));
  }
});
