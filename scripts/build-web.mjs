/** Assemble a deliberately allow-listed static site for every target. */
import {cp, mkdir, rm, access, readFile} from 'node:fs/promises';
import {resolve, join, dirname} from 'node:path';
import {fileURLToPath} from 'node:url';
const root=resolve(dirname(fileURLToPath(import.meta.url)),'..');
const outputArg=process.argv.indexOf('--out');
const out=resolve(outputArg<0?join(root,'dist'):process.argv[outputArg+1]);
if(out===root || root.startsWith(out+'/'))throw Error('Unsafe output directory');
const required=['index.html','manifest.webmanifest','sw.js','assets','icons','src','python','LICENSE','licenses'];
// Fail before replacing an existing output if a required release notice is absent.
for (const file of ['LICENSE','licenses/PYODIDE-LICENSE',
  ...(process.argv.includes('--require-vendor') ? ['node_modules/katex/LICENSE'] : [])]) {
  if (!(await readFile(join(root,file),'utf8')).trim()) throw Error(`Empty release notice: ${file}`);
}
await rm(out,{recursive:true,force:true});await mkdir(out,{recursive:true});
for(const file of required){await cp(join(root,file),join(out,file),{recursive:true});}
let vendor=false;
try{await access(join(root,'vendor/pyodide/pyodide-lock.json'));vendor=true;}
catch{if(process.argv.includes('--require-vendor'))throw Error('Offline Pyodide is missing. Run python3 scripts/vendor_pyodide.py');}
if(vendor)await cp(join(root,'vendor/pyodide'),join(out,'vendor/pyodide'),{recursive:true});
try{
  await cp(join(root,'node_modules/katex/dist'),join(out,'assets/katex'),{recursive:true});
  await cp(join(root,'node_modules/katex/LICENSE'),join(out,'licenses/KATEX-LICENSE'));
}catch{
  if(process.argv.includes('--require-vendor'))throw Error('Offline typesetting is missing. Run npm ci.');
}
console.log(`Calculator 2.0 website -> ${out}; Pyodide vendored: ${vendor}`);
