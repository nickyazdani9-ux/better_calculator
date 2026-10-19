import {test} from 'node:test';
import assert from 'node:assert/strict';
import {createRequire} from 'node:module';
import {mkdtemp,writeFile,rm} from 'node:fs/promises';
import {join} from 'node:path';
import {tmpdir} from 'node:os';
const require=createRequire(import.meta.url);
const {createStaticServer}=require('../desktop/static-server.cjs');
test('static desktop host serves assets with correct WASM MIME and prevents traversal',async()=>{
  const root=await mkdtemp(join(tmpdir(),'calculator2-http-'));
  await writeFile(join(root,'index.html'),'app');
  await writeFile(join(root,'runtime.wasm'),Buffer.from([0,97,115,109]));
  const server=createStaticServer(root);
  await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
  const url=`http://127.0.0.1:${server.address().port}`;
  try{
    const index=await fetch(url+'/');assert.equal(index.status,200);assert.equal(await index.text(),'app');
    const wasm=await fetch(url+'/runtime.wasm');assert.equal(wasm.headers.get('content-type'),'application/wasm');
    assert.equal((await fetch(url+'/missing')).status,404);
    assert.equal((await fetch(url+'/index.html',{method:'POST'})).status,405);
    assert.notEqual((await fetch(url+'/%2e%2e/%2e%2e/etc/passwd')).status,200);
  }finally{await new Promise(resolve=>server.close(resolve));await rm(root,{recursive:true,force:true});}
});
