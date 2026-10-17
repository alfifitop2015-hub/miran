// مِران: عامل خدمة بسيط — الشبكة أولاً، والنسخة المحفوظة عند انقطاع الإنترنت
const C='miran-v2';
self.addEventListener('install',e=>{self.skipWaiting();e.waitUntil(caches.open(C).then(c=>c.addAll(['./','index.html','manifest.json','icon-192.png','icon-512.png']).catch(()=>{})))});
self.addEventListener('activate',e=>e.waitUntil(self.clients.claim()));
self.addEventListener('fetch',e=>{const r=e.request;if(r.method!=='GET')return;const u=new URL(r.url);
 if(u.origin!==location.origin||u.pathname.includes('/chinese/')||/\.mp4$/.test(u.pathname))return;
 const fresh=r.mode==='navigate'||/\/(index\.html)?$/.test(u.pathname)||/\.json$/.test(u.pathname);
 e.respondWith((fresh?fetch(r.url,{cache:'no-cache',credentials:'same-origin'}):fetch(r)).then(res=>{if(res.ok&&res.type==='basic'){const cp=res.clone();caches.open(C).then(c=>c.put(r,cp))}return res}).catch(()=>caches.match(r).then(m=>m||caches.match('./'))))});
self.addEventListener('notificationclick',e=>{e.notification.close();e.waitUntil(self.clients.matchAll({type:'window',includeUncontrolled:true}).then(cs=>{const c=cs.find(x=>x.url.includes('/miran/')&&!x.url.includes('/chinese/'));return c?c.focus():self.clients.openWindow('./')}))});
