/* Dedicated worker isolates expensive CAS work from the UI. */
const CDN = 'https://cdn.jsdelivr.net/pyodide/v0.29.5/full/';
const LOCAL = new URL('../vendor/pyodide/', self.location.href).href;
let pyodide;
let initializing;
let cachedVersion = '';
function state(status, note) { self.postMessage({type:'status',status,note}); }
async function loadRuntime() {
  // Vendor bundle is optional; downloaded by scripts/vendor-pyodide.sh.
  const localResponse = await fetch(new URL('../vendor/pyodide/pyodide.js', self.location.href), {method:'HEAD'}).catch(()=>null);
  const isLocal = Boolean(localResponse?.ok && /javascript/.test(localResponse.headers.get('content-type') || ''));
  const base = isLocal ? LOCAL : CDN;
  importScripts(base + 'pyodide.js');
  return loadPyodide({indexURL:base});
}
async function initialize() {
  if (initializing) return initializing;
  initializing = (async () => {
    state('loading','Loading Python / WebAssembly…');
    pyodide = await loadRuntime();
    state('loading','Loading SymPy symbolic engine…');
    await pyodide.loadPackage('sympy');
    state('loading','Registering mathematical extensions…');
    const [engine, modManifest, init] = await Promise.all([
      fetch(new URL('../python/engine.py', self.location.href)).then(r => {if(!r.ok) throw Error('Engine download failed'); return r.text();}),
      fetch(new URL('../python/plugins.json', self.location.href)).then(r=>r.json()),
      fetch(new URL('../python/plugins/__init__.py', self.location.href)).then(r=>r.text())
    ]);
    pyodide.FS.mkdirTree('/home/pyodide/plugins');
    pyodide.FS.writeFile('/home/pyodide/engine.py',engine);
    pyodide.FS.writeFile('/home/pyodide/plugins/__init__.py',init);
    const pluginSources = await Promise.all(modManifest.modules.map(async name=>{
      if(!/^[a-z][a-z0-9_]*$/.test(name)) throw Error('Invalid plugin filename');
      const response=await fetch(new URL(`../python/plugins/${name}.py`,self.location.href));
      if(!response.ok) throw Error(`Cannot load plugin: ${name}`);
      return [name, await response.text()];
    }));
    for(const [name,source] of pluginSources){pyodide.FS.writeFile(`/home/pyodide/plugins/${name}.py`,source);}
    pyodide.runPython('import sys; sys.path.insert(0,"/home/pyodide"); from engine import run_json');
    cachedVersion = pyodide.version;
    state('ready',`SymPy ready • Python ${cachedVersion}`);
    self.postMessage({type:'ready'});
  })().catch(error=>{initializing=null;state('error',String(error.message || error));throw error;});
  return initializing;
}
self.addEventListener('message',async event=>{
  const {type,id,payload} = event.data || {};
  if(type==='init') { try {await initialize();}catch{} return; }
  if(type!=='calculate')return;
  try {
    await initialize();
    pyodide.globals.set('request_payload_json',JSON.stringify(payload));
    const result=pyodide.runPython('run_json(request_payload_json)');
    self.postMessage({type:'response',id,result:JSON.parse(result)});
  } catch(error) {
    self.postMessage({type:'response',id,result:{ok:false,error:`Engine error: ${error.message || error}`}});
  }
});
