import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync,existsSync} from 'node:fs';
import {join} from 'node:path';
import {validateCatalog} from '../src/registry.js';
const root=new URL('../',import.meta.url);
const read=p=>readFileSync(new URL(p,root),'utf8');

test('generated catalog includes every requested domain',()=>{
  const registry=JSON.parse(read('assets/catalog.json'));
  assert.ok(validateCatalog(registry));
  assert.deepEqual(registry.map(x=>x.id),['basic','calculus','complex','geometry','waves','linear']);
  assert.ok(registry.find(x=>x.id==='geometry').operations.length>=8);
});

test('each declared mathematical plugin ships with source',()=>{
  const modules=JSON.parse(read('python/plugins.json')).modules;
  for(const name of modules){
    assert.match(name,/^[a-z][a-z0-9_]*$/);
    assert.ok(existsSync(new URL(`python/plugins/${name}.py`,root)));
  }
  assert.equal(modules.length,6);
});

test('PWA manifest is installable and assets are cached',()=>{
  const manifest=JSON.parse(read('manifest.webmanifest'));
  assert.equal(manifest.display,'standalone');
  assert.equal(manifest.start_url,'./');
  assert.ok(manifest.icons.some(icon=>icon.sizes==='192x192'));
  assert.ok(manifest.icons.some(icon=>icon.sizes==='512x512'));
  const worker=read('sw.js');
  for(const core of ['src/app.js','assets/catalog.json','python/engine.py','python/workspace.py','python/plugins/geometry.py','manifest.webmanifest']) {
    assert.ok(worker.includes(core),`Offline shell missing ${core}`);
  }
});

test('frontend uses escaped DOM text for results, no innerHTML',()=>{
  const js=read('src/app.js');
  assert.ok(js.includes('textContent=result.text'));
  assert.ok(!js.includes('innerHTML'));
});
