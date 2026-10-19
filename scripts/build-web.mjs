/** Assemble a deliberately allow-listed static site for every target. */
import {cp, mkdir, rm, access, readdir} from 'node:fs/promises';
import {resolve, join, dirname} from 'node:path';
import {fileURLToPath} from 'node:url';
const root=resolve(dirname(fileURLToPath(import.meta.url)),'..');
const outputArg=process.argv.indexOf('--out');
const out=resolve(outputArg<0?join(root,'dist'):process.argv[outputArg+1]);
if(out===root || root.startsWith(out+'/'))throw Error('Unsafe output directory');
const required=['index.html','manifest.webmanifest','sw.js','assets','icons','src','python'];
await rm(out,{recursive:true,force:true});await mkdir(out,{recursive:true});
for(const file of required){await cp(join(root,file),join(out,file),{recursive:true});}
let vendor=false;
try{await access(join(root,'vendor/pyodide/pyodide-lock.json'));vendor=true;}
catch{if(process.argv.includes('--require-vendor'))throw Error('Offline Pyodide is missing. Run python3 scripts/vendor_pyodide.py');}
if(vendor)await cp(join(root,'vendor/pyodide'),join(out,'vendor/pyodide'),{recursive:true});
console.log(`Calculator 2.0 website -> ${out}; Pyodide vendored: ${vendor}`);
