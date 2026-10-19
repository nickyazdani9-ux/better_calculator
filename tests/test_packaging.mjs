import {test} from 'node:test';
import assert from 'node:assert/strict';
import {mkdtemp,readFile,access,readdir,rm} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {spawnSync} from 'node:child_process';
const root=new URL('../', import.meta.url);
test('web build copies only required public files',async()=>{
  const dir=await mkdtemp(join(tmpdir(),'calculator2-build-'));
  try{
    const result=spawnSync(process.execPath,['scripts/build-web.mjs','--out',dir],{cwd:root,encoding:'utf8'});
    assert.equal(result.status,0,result.stderr);
    const files=await readdir(dir);
    for(const f of ['index.html','manifest.webmanifest','sw.js','src','python','assets','icons'])assert.ok(files.includes(f),f);
    for(const f of ['.git','tests','package.json','.github','README.md'])assert.ok(!files.includes(f),f);
    assert.match(await readFile(join(dir,'index.html'),'utf8'),/Calculator 2\.0/);
  }finally{await rm(dir,{recursive:true,force:true});}
});
test('native wrappers and workflows are present',async()=>{
  for(const f of ['capacitor.config.json','desktop/main.cjs','.github/workflows/pipeline.yml']){
    await access(new URL(f,root));
  }
});
test('native targets require offline Pyodide and do not ship tests',async()=>{
  const pkg=JSON.parse(await readFile(new URL('package.json',root),'utf8'));
  assert.ok(pkg.scripts['build:native']);
  assert.ok(pkg.scripts['test:js']);
  assert.equal(pkg.build.files.includes('dist/**'),true);
});
