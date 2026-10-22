import {validateCatalog, findOperation, defaultsFor} from './registry.js';
const $ = selector => document.querySelector(selector);
const STORE = 'calculator2.v1';
const safeLoad = () => { try {return JSON.parse(localStorage.getItem(STORE)) || {}} catch {return {}} };
const saved = safeLoad();
const state = {
  catalog:[], tab:saved.tab || 'basic', operation:saved.operation || 'evaluate',
  drafts:saved.drafts || {}, history:saved.history || [], theme:saved.theme || 'midnight',
  status:'loading', busy:false, requestId:0, lastResult:null, initialized:false,
  sidebar:false, working:Array.isArray(saved.working)?saved.working.slice(0,20):[], activeEntry:null, stepAdded:false,
};
const worker = new Worker('./src/worker.js');
const pending = new Map();
function persist(){
  try{localStorage.setItem(STORE,JSON.stringify({tab:state.tab,operation:state.operation,drafts:state.drafts,history:state.history.slice(0,40),working:state.working.slice(0,20),theme:state.theme}));}
  catch{ /* quota/private mode */ }
}
function el(tag,cls='',text=''){
  const node=document.createElement(tag);
  if(cls)node.className=cls;
  if(text)node.textContent=text;
  return node;
}
function setStatus(status,note){
  state.status=status;
  const indicator=$('#engine-indicator');
  indicator.dataset.state=status;
  $('#engine-label').textContent = status==='ready'?'SymPy online':status==='error'?'Engine unavailable':'Initializing CAS';
  $('#engine-details').textContent = note || '';
  $('#run').disabled=state.busy || status!=='ready';
  $('#run-caption').textContent=status==='ready'?'Done':'Loading engine…';
}
function renderTabs(){
  const tabs=$('#tabs');tabs.replaceChildren();
  for(const tab of state.catalog){
    const btn=el('button','tab'+(tab.id===state.tab?' active':''),tab.name);
    btn.type='button'; btn.role='tab';btn.setAttribute('aria-selected',String(tab.id===state.tab));
    btn.title=tab.name;
    btn.addEventListener('click',()=>switchTab(tab.id));
    tabs.append(btn);
  }
}
function switchTab(id){
  const tab=state.catalog.find(t=>t.id===id); if(!tab) return;
  state.tab=id;
  state.operation=tab.operations[0].id;
  state.lastResult=null;
  persist(); renderTabs();renderOperations();renderForm();clearResult();
}
function renderOperations(){
  const select=$('#operation');select.replaceChildren();
  const tab=state.catalog.find(t=>t.id===state.tab);
  if(!tab)return;
  for(const op of tab.operations){
    const option=el('option','',op.label);option.value=op.id; select.append(option);
  }
  if(!findOperation(state.catalog,state.tab,state.operation))state.operation=tab.operations[0].id;
  select.value=state.operation;
  $('#domain-title').textContent=tab.name;
  $('#domain-count').textContent=`${tab.operations.length} operations`;
}
function draftKey(){return `${state.tab}.${state.operation}`;}
function currentValues(){
  const inputs=$('#fields').querySelectorAll('[data-field-key]');
  return Object.fromEntries([...inputs].map(e=>[e.dataset.fieldKey,e.value]));
}
function saveDraft(){state.drafts[draftKey()]=currentValues();persist();}
function renderForm(){
  const op=findOperation(state.catalog,state.tab,state.operation);
  if(!op)return;
  $('#operation-description').textContent=op.description;
  const fields=$('#fields');fields.replaceChildren();
  const defaults=defaultsFor(state.catalog,state.tab,state.operation);
  const values={...defaults,...(state.drafts[draftKey()]||{})};
  for(const f of op.fields){
    const wrapper=el('div','form-field');const label=el('label','field-label',f.label);
    const id=`math-${f.key}`;label.htmlFor=id;
    const input=el(f.kind==='textarea'?'textarea':'input','field-input');
    if(f.kind==='textarea'){input.rows=2;input.spellcheck=false;}
    else{input.type='text';input.spellcheck=false;input.autocapitalize='off';}
    input.id=id;input.dataset.fieldKey=f.key;input.value=values[f.key] ?? '';
    input.autocomplete='off';input.addEventListener('input',saveDraft);
    input.addEventListener('focus',()=>state.focused=input);
    wrapper.append(label,input);
    if(f.hint)wrapper.append(el('p','field-hint',f.hint));
    fields.append(wrapper);
  }
  state.focused=fields.querySelector('[data-field-key]');
  $('#result-section').classList.add('empty');
}

function renderMath(latex,holder){
  if(!latex || !window.katex)return false;
  const block=el('div','math-block');
  try{
    window.katex.render(latex,block,{throwOnError:true,displayMode:true,trust:false,strict:'ignore',maxExpand:100});
    holder.append(block);return true;
  }catch{return false;}
}
function clearResult(){
  $('#result-text').textContent='';
  $('#result-math').replaceChildren();$('#input-math').replaceChildren();$('#result-lines').replaceChildren();
  $('#result-state').textContent='Ready for a calculation';
  $('#result-section').classList.add('empty');
  $('#result-section').classList.remove('has-typeset');
  $('#input-typeset').hidden=true;$('#answer-caption').hidden=true;
  $('#copy').disabled=true;$('#reuse').disabled=true;$('#add-step').disabled=true;
  $('#print').disabled=!state.working.length;
  state.lastResult=null;state.activeEntry=null;state.stepAdded=false;
}
function fillTypesetInputs(result,target){
  let count=0;
  const inputs=Array.isArray(result.inputs)?result.inputs:[];
  for(const item of inputs){
    if(!item || typeof item.latex!=='string')continue;
    const region=el('div','typeset-field');
    if(inputs.length>1)region.append(el('span','math-field-label',item.key));
    if(renderMath(item.latex,region)){target.append(region);count++;}
  }
  return count;
}
function setResult(result){
  state.lastResult=result;
  const panel=$('#result-section');panel.classList.remove('empty','has-typeset');
  const pre=$('#result-text'),math=$('#result-math'),lines=$('#result-lines'),inputs=$('#input-math');
  math.replaceChildren();lines.replaceChildren();inputs.replaceChildren();
  $('#copy').disabled=!result.ok;
  $('#reuse').disabled=!(result.ok && result.reusable);
  $('#add-step').disabled=!(result.ok && state.activeEntry && !state.stepAdded);
  $('#print').disabled=!(result.ok || state.working.length);
  $('#result-state').textContent=result.ok?'Exact symbolic output':'Calculation error';
  panel.dataset.error=String(!result.ok);
  $('#input-typeset').hidden=true;$('#answer-caption').hidden=!result.ok;
  if(!result.ok){pre.textContent=result.error || 'Unknown error';return;}
  pre.textContent=result.text || '';
  const hasInput=fillTypesetInputs(result,inputs)>0;
  $('#input-typeset').hidden=!hasInput;
  const hasAnswer=renderMath(result.latex,math);
  if(hasAnswer)panel.classList.add('has-typeset');
  for(const line of result.lines || [])lines.append(el('div','result-line',line));
}
function renderWorking(){
  const sheet=$('#worksheet-card'),steps=$('#worksheet-steps');
  steps.replaceChildren();
  sheet.hidden=!state.working.length;
  $('#worksheet-count').textContent=state.working.length?('· '+state.working.length+' step'+(state.working.length===1?'':'s')):'';
  for(const [index,item] of state.working.entries()){
    const card=el('article','worksheet-step');
    card.append(el('h3','',`Step ${index+1} · ${item.tab} / ${item.operation}`));
    const inputs=el('div','math-blocks');
    if(!fillTypesetInputs(item.result,inputs)){
      const raw=Object.entries(item.values||{}).filter(([k])=>['expression','expressions','matrix','other','metric','vector'].includes(k))
        .map(([k,v])=>k+': '+v).join(' · ');
      if(raw)inputs.append(el('p','result-text',raw));
    }
    if(inputs.childNodes.length){card.append(el('p','math-caption','INPUT'),inputs);}
    card.append(el('p','math-caption','RESULT'));
    const output=el('div','math-blocks');
    if(!renderMath(item.result?.latex,output))output.append(el('p','result-text',item.result?.text||''));
    card.append(output);
    for(const line of item.result?.lines||[])card.append(el('div','result-line',line));
    steps.append(card);
  }
  $('#print').disabled=!(state.lastResult?.ok || state.working.length);
}
function useAnswer(){
  const result=state.lastResult;
  if(!result?.ok || !result.reusable)return;
  let input=$('#fields [data-field-key="expression"]');
  if(!input){
    state.tab='basic';state.operation='evaluate';
    renderTabs();renderOperations();renderForm();clearResult();
    input=$('#fields [data-field-key="expression"]');
  }
  if(!input)return;
  input.value='('+result.expr+')';
  input.dispatchEvent(new Event('input',{bubbles:true}));
  input.focus();input.select();
}
function addStep(){
  if(!state.lastResult?.ok || !state.activeEntry || state.stepAdded)return;
  state.working.push(state.activeEntry);
  state.working=state.working.slice(-20);
  state.stepAdded=true;$('#add-step').disabled=true;
  persist();renderWorking();
}
function printWorking(){
  if(!state.lastResult?.ok && !state.working.length)return;
  const mode=state.working.length?'printing-worksheet':'printing-single';
  document.body.classList.remove('printing-worksheet','printing-single');
  document.body.classList.add(mode);
  window.addEventListener('afterprint',()=>document.body.classList.remove(mode),{once:true});
  window.print();
}
async function calculate(){
  if(state.busy || state.status!=='ready')return;
  saveDraft();state.busy=true;setStatus(state.status,$('#engine-details').textContent);
  $('#run').disabled=true;$('#run-caption').textContent='Computing…';
  $('#result-state').textContent='Computing…';
  const payload={tab:state.tab,operation:state.operation,values:currentValues()};
  const id=++state.requestId;
  const result=await new Promise(resolve=>{
    pending.set(id,resolve);
    worker.postMessage({type:'calculate',id,payload});
  });
  state.busy=false;setStatus(state.status,$('#engine-details').textContent);
  state.activeEntry=result.ok?{tab:payload.tab,operation:payload.operation,values:payload.values,result,time:Date.now()}:null;
  state.stepAdded=false;
  setResult(result);
  if(result.ok){
    state.history.unshift(state.activeEntry);
    state.history=state.history.slice(0,40);persist();renderHistory();
  }
}
function renderHistory(){
  const list=$('#history-items');list.replaceChildren();
  if(!state.history.length){list.append(el('p','history-empty','Your results appear here.'));return;}
  for(const item of state.history){
    const btn=el('button','history-entry');btn.type='button';
    btn.append(el('span','history-domain',item.tab+' · '+item.operation));
    btn.append(el('strong','history-result',item.result?.text?.slice(0,88)||''));
    btn.addEventListener('click',()=>{
      if(!findOperation(state.catalog,item.tab,item.operation))return;
      state.tab=item.tab;state.operation=item.operation;
      state.drafts[draftKey()]=item.values;persist();
      renderTabs();renderOperations();renderForm();
      state.activeEntry=item;state.stepAdded=state.working.some(step=>step.time===item.time);
      setResult(item.result);
      $('#history-panel').classList.remove('open');
    });list.append(btn);
  }
}
function insertSymbol(symbol){
  const input=state.focused?.isConnected?state.focused:$('#fields [data-field-key]');
  if(!input)return;
  input.focus();
  const start=input.selectionStart || 0;const end=input.selectionEnd || start;
  input.setRangeText(symbol,start,end,'end');input.dispatchEvent(new Event('input',{bubbles:true}));
}
function buildPalette(){
  for(const sym of ['^','sqrt(', 'sin(', 'cos(', 'exp(', 'log(', 'pi','I','theta','(',')','[',']',',','*','/']){
    const btn=el('button','symbol-key',sym);btn.type='button';
    btn.addEventListener('click',()=>insertSymbol(sym));
    $('#symbols').append(btn);
  }
}
async function setup(){
  const katexStyle=document.createElement('link');katexStyle.rel='stylesheet';katexStyle.href='https://cdn.jsdelivr.net/npm/katex@0.16.25/dist/katex.min.css';katexStyle.media='print';katexStyle.onload=()=>{katexStyle.media='all';};document.head.append(katexStyle);
  document.documentElement.dataset.theme=state.theme;
  $('#theme').value=state.theme;
  try {
    const response=await fetch('./assets/catalog.json');
    if(!response.ok)throw Error('Missing operation catalog');
    const catalog=await response.json();
    if(!validateCatalog(catalog))throw Error('Operation catalog is invalid');
    state.catalog=catalog;
    if(!state.catalog.find(t=>t.id===state.tab))state.tab='basic';
    renderTabs();renderOperations();renderForm();renderHistory();renderWorking();buildPalette();
  }catch(error){setStatus('error',error.message);return;}
  $('#operation').addEventListener('change',ev=>{
    saveDraft();state.operation=ev.target.value;persist();renderForm();clearResult();
  });
  $('#calculator-form').addEventListener('submit',ev=>{ev.preventDefault();calculate();});
  $('#clear').addEventListener('click',()=>{
    state.drafts[draftKey()] = defaultsFor(state.catalog,state.tab,state.operation);
    persist();renderForm();clearResult();
  });
  $('#reuse').addEventListener('click',useAnswer);
  $('#add-step').addEventListener('click',addStep);
  $('#print').addEventListener('click',printWorking);
  $('#clear-worksheet').addEventListener('click',()=>{
    state.working=[];state.stepAdded=false;
    persist();renderWorking();
    $('#add-step').disabled=!(state.lastResult?.ok && state.activeEntry);
  });
  window.addEventListener('load',()=>{
    if(state.lastResult)setResult(state.lastResult);
    if(state.working.length)renderWorking();
  });
  $('#copy').addEventListener('click',async()=>{
    if(!state.lastResult?.ok)return;
    try{await navigator.clipboard.writeText(state.lastResult.text);$('#copy').textContent='Copied!';setTimeout(()=>$('#copy').textContent='Copy',1500)}catch{}
  });
  $('#theme').addEventListener('change',event=>{state.theme=event.target.value;document.documentElement.dataset.theme=state.theme;persist();});
  $('#history-toggle').addEventListener('click',()=>$('#history-panel').classList.toggle('open'));
  $('#history-close').addEventListener('click',()=>$('#history-panel').classList.remove('open'));
  $('#history-clear').addEventListener('click',()=>{state.history=[];persist();renderHistory();});
  $('#install').addEventListener('click',async()=>{
    if(!state.installPrompt){$('#install-note').textContent='Use browser menu → Install app / Add to Home screen (requires HTTPS).';return;}
    state.installPrompt.prompt();await state.installPrompt.userChoice;state.installPrompt=null;$('#install').hidden=true;
  });
  window.addEventListener('beforeinstallprompt',event=>{event.preventDefault();state.installPrompt=event;$('#install').hidden=false;});
  window.addEventListener('appinstalled',()=>{$('#install-note').textContent='Installed successfully.';$('#install').hidden=true;});
  worker.onmessage=event=>{
    const {type,status,note,id,result}=event.data||{};
    if(type==='status')setStatus(status,note);
    if(type==='response'){const resolve=pending.get(id);if(resolve){pending.delete(id);resolve(result);}}
  };
  worker.onerror=event=>setStatus('error','Worker failed: '+event.message);
  worker.postMessage({type:'init'});
  if('serviceWorker' in navigator){navigator.serviceWorker.register('./sw.js').catch(()=>{});}
}
setup();
