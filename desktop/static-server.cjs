'use strict';
const http=require('node:http');
const fs=require('node:fs');
const path=require('node:path');
const types={'.html':'text/html; charset=utf-8','.js':'text/javascript; charset=utf-8',
  '.css':'text/css; charset=utf-8','.json':'application/json',
  '.wasm':'application/wasm','.webmanifest':'application/manifest+json',
  '.png':'image/png','.svg':'image/svg+xml','.zip':'application/zip',
  '.whl':'application/octet-stream','.py':'text/plain; charset=utf-8',
  '.map':'application/json'};
/** Host bundled assets over loopback: workers and WASM require a real origin. */
function createStaticServer(directory){
  const root=path.resolve(directory);
  return http.createServer((req,res)=>{
    if(req.method!=='GET'&&req.method!=='HEAD'){res.writeHead(405);res.end();return;}
    let name;
    try{
      name=decodeURIComponent(new URL(req.url,'http://localhost').pathname);
      if(name.includes('\0')||name.split('/').includes('..'))throw Error('bad path');
    }catch{res.writeHead(400);res.end();return;}
    const file=path.resolve(root,'.'+(name.endsWith('/')?name+'index.html':name));
    if(!file.startsWith(root+path.sep)){res.writeHead(403);res.end();return;}
    fs.stat(file,(err,stat)=>{
      if(err||!stat.isFile()){res.writeHead(404);res.end();return;}
      res.writeHead(200,{
        'Content-Type': types[path.extname(file).toLowerCase()]||'application/octet-stream',
        'X-Content-Type-Options':'nosniff',
        'Cache-Control':'no-cache',
        'Cross-Origin-Resource-Policy':'same-origin',
      });
      if(req.method==='HEAD'){res.end();return;}
      fs.createReadStream(file).pipe(res);
    });
  });
}
module.exports={createStaticServer};
