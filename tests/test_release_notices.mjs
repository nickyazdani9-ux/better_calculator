import test from 'node:test';
import assert from 'node:assert/strict';
import {mkdtemp, mkdir, writeFile, readFile, cp, rm} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {spawnSync} from 'node:child_process';

async function fixture(run) {
  const root = await mkdtemp(join(tmpdir(), 'calculator-notices-'));
  try {
    await mkdir(join(root, 'scripts'));
    await cp(new URL('../scripts/build-web.mjs', import.meta.url), join(root, 'scripts/build-web.mjs'));
    for (const dir of ['assets','icons','src','python','vendor/pyodide','node_modules/katex/dist','licenses']) await mkdir(join(root, dir), {recursive:true});
    for (const file of ['index.html','manifest.webmanifest','sw.js','vendor/pyodide/pyodide-lock.json','node_modules/katex/dist/katex.js']) await writeFile(join(root,file), '{}');
    for (const [file,text] of [['LICENSE','synthetic project notice'],['node_modules/katex/LICENSE','synthetic KaTeX notice'],['licenses/PYODIDE-LICENSE','synthetic Pyodide notice'],['licenses/README.md','synthetic source attribution']]) await writeFile(join(root,file),text);
    await run(root);
  } finally { await rm(root,{recursive:true,force:true}); }
}
const build = root => spawnSync(process.execPath, ['scripts/build-web.mjs','--require-vendor'], {cwd:root,encoding:'utf8'});
test('release artifact preserves exact project and dependency notices', async () => fixture(async root => {
  const result=build(root); assert.equal(result.status,0,result.stderr);
  for(const [source,target] of [['LICENSE','LICENSE'],['node_modules/katex/LICENSE','licenses/KATEX-LICENSE'],['licenses/PYODIDE-LICENSE','licenses/PYODIDE-LICENSE'],['licenses/README.md','licenses/README.md']]) assert.equal(await readFile(join(root,'dist',target),'utf8'),await readFile(join(root,source),'utf8'));
}));
for(const missing of ['LICENSE','node_modules/katex/LICENSE','licenses/PYODIDE-LICENSE']) test(`release refuses missing ${missing}`, async () => fixture(async root => {
  await rm(join(root,missing)); const result=build(root); assert.notEqual(result.status,0,'missing notice must fail release build');
}));
for(const missing of ['vendor/pyodide/pyodide-lock.json','node_modules/katex/dist','index.html']) test(`failed preflight preserves existing output when ${missing} is absent`, async () => fixture(async root => {
  await mkdir(join(root,'dist'));
  await writeFile(join(root,'dist','previous.html'),'previous verified artifact');
  await rm(join(root,missing),{recursive:true});
  const result=build(root);
  assert.notEqual(result.status,0,'missing build input must fail');
  assert.equal(await readFile(join(root,'dist','previous.html'),'utf8'),'previous verified artifact');
}));
