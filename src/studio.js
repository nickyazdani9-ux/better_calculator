// A visible client of the typed Python workspace. Display strings never become
// operands: continuation always uses node IDs validated by the math engine.
const $=selector=>document.querySelector(selector);
const label=name=>name.replaceAll('_',' ').replace(/^./,letter=>letter.toUpperCase());
const element=(tag,className='',text='')=>{
  const node=document.createElement(tag);node.className=className;node.textContent=text;return node;
};
const EXAMPLES={
  complex:[
    {command:'define',id:'f',expression:'(x+I*y)^2',coordinates:['x','y'],metric:'[[1,0],[0,1]]'},
    {command:'apply',id:'df',source:'f',operation:'exterior_derivative'},
    {command:'apply',id:'norm',source:'df',operation:'norm_squared'},
    {command:'apply',id:'expected',source:'norm',operation:'expectation',independent:true,
      normals:{x:{mean:'0',std:'1'},y:{mean:'0',std:'1'}}}
  ],
  fourier:[
    {command:'define',id:'gaussian',expression:'exp(-pi*x^2)'},
    {command:'apply',id:'spectrum',source:'gaussian',operation:'fourier',variable:'x',frequency:'k'},
    {command:'define',id:'m',kind:'matrix',matrix:'[[2,0],[0,1]]'},
    {command:'apply',id:'det',source:'m',operation:'determinant'},
    {command:'apply',id:'scaled',source:'spectrum',other:'det',operation:'multiply'},
    {command:'apply',id:'recovered',source:'scaled',operation:'inverse_fourier',variable:'k',frequency:'x'}
  ]
};

export function setupStudio({request,renderMath}){
  let nodes=[],signatures={},ready=false,busy=false,selected='',saveFailed=false;
  const status=text=>{$('#studio-status').textContent=text;};
  const send=payload=>request({action:'workspace',...payload});
  function controls(){
    for(const button of document.querySelectorAll('#studio-view button'))button.disabled=!ready||busy;
    $('#studio-apply button').disabled=!ready||busy||!nodes.length;
    $('#studio-export').disabled=!ready||busy||!nodes.length;
    $('#studio-reset').disabled=!ready||busy||!nodes.length;
  }
  function nextId(prefix){let n=1;while(nodes.some(node=>node.id===`${prefix}_${n}`))n++;return `${prefix}_${n}`;}
  function renderParameters(){
    const op=$('#studio-operation').value,container=$('#studio-parameters');container.replaceChildren();
    const add=(key,name,value,kind='text')=>{
      const wrapper=element('div');const title=element('label','field-label',name);title.htmlFor='studio-param-'+key;
      const input=element(kind==='textarea'?'textarea':'input','field-input');
      input.id=title.htmlFor;input.dataset.parameter=key;input.value=value;
      if(kind==='number'){input.type='number';input.min='1';input.max='12';}
      else if(kind==='textarea')input.rows=2;
      wrapper.append(title,input);container.append(wrapper);
    };
    if(['differentiate','integrate','residue','substitute','fourier','inverse_fourier','laplace','inverse_laplace','limit','series'].includes(op))add('variable','Variable',op==='residue'?'z':'x');
    if(['differentiate','series'].includes(op))add('order','Order',op==='series'?'6':'1','number');
    if(['residue','limit','series'].includes(op))add('point','Point','0');
    if(op==='limit')add('direction','Direction (+, −, or +-)','+-');
    if(['fourier','inverse_fourier','laplace','inverse_laplace'].includes(op))add('frequency','Output variable',op.includes('laplace')?'s':'k');
    if(op==='substitute')add('expression','Replacement','2');
    if(op==='integrate'){add('lower','Lower bound (optional)','');add('upper','Upper bound (optional)','');}
    if(['add','multiply','pair','tensor_product','matrix_multiply'].includes(op)){
      const title=element('label','field-label','Other object');title.htmlFor='studio-param-other';
      const select=element('select','field-input');select.id=title.htmlFor;select.dataset.parameter='other';
      for(const node of nodes){const option=element('option','',`${node.id} · ${label(node.kind)}`);option.value=node.id;select.append(option);}
      container.append(title,select);
    }
    if(op==='expectation'){
      add('normals','Normal distributions (JSON)','{"x":{"mean":"0","std":"1"},"y":{"mean":"0","std":"1"}}','textarea');
      const title=element('label','studio-check');const check=element('input');check.type='checkbox';check.dataset.parameter='independent';
      title.append(check,document.createTextNode('Assume these random variables are independent'));container.append(title);
    }
    if(op==='change_coordinates'){
      add('coordinates','New coordinates','r, theta');
      add('mapping','Old coordinates in new coordinates (JSON)','["r*cos(theta)","r*sin(theta)"]','textarea');
    }
  }
  function renderOperations(){
    const source=nodes.find(node=>node.id===$('#studio-source').value),select=$('#studio-operation'),previous=select.value;
    select.replaceChildren();
    for(const [name,kinds] of Object.entries(signatures))if(source&&kinds.includes(source.kind)){
      const option=element('option','',label(name));option.value=name;select.append(option);
    }
    if([...select.options].some(option=>option.value===previous))select.value=previous;
    renderParameters();
  }
  function selectNode(id){selected=id;render();}
  function render(){
    const list=$('#studio-nodes'),source=$('#studio-source');list.replaceChildren();source.replaceChildren();
    $('#studio-node-count').textContent=`${nodes.length} object${nodes.length===1?'':'s'}`;
    for(const [index,node] of nodes.entries()){
      const card=element('article','math-node'+(node.id===selected?' selected':''));card.dataset.nodeId=node.id;
      const head=element('div','math-node-head');
      const select=element('button','node-name',node.id);select.type='button';select.addEventListener('click',()=>selectNode(node.id));
      head.append(element('span','node-index',String(index+1).padStart(2,'0')),select,element('span','node-kind',label(node.kind)));
      const math=element('div','node-math');renderMath(node.latex,math);
      const raw=element('code','node-raw',node.expr);
      const trail=element('div','node-trail',`${label(node.operation)}${node.parents.length?' ← '+node.parents.join(' + '):' · input'}`);
      card.append(head,math,raw,trail);list.append(card);
      const option=element('option','',`${node.id} · ${label(node.kind)}`);option.value=node.id;source.append(option);
    }
    if(!nodes.length)list.append(element('p','studio-empty','Start with an expression, or load an example to explore a complete calculation.'));
    if(selected)source.value=selected;
    renderOperations();
    const inspected=nodes.find(node=>node.id===selected),inspector=$('#studio-inspector');inspector.replaceChildren();inspector.hidden=!inspected;
    if(inspected){
      inspector.append(element('p','eyebrow','OBJECT CONTEXT / '+inspected.id));
      inspector.append(element('p','',`Coordinates: ${inspected.context.coordinates.join(', ')||'unscoped symbolic expression'}`));
      if(inspected.context.metric)inspector.append(element('code','node-raw','Metric: '+inspected.context.metric));
      inspector.append(element('p','',`Parents: ${inspected.parents.join(', ')||'original input'}. Operation: ${label(inspected.operation)}.`));
      if(inspected.operation==='expectation')inspector.append(element('p','','Assumptions: independent normal random variables as declared in the saved command.'));
    }
    controls();
  }
  async function refresh(){
    const result=await send({command:'graph'});
    if(result.ok){nodes=result.nodes;if(!nodes.some(node=>node.id===selected))selected=nodes.at(-1)?.id||'';render();}
    else status(result.error);
  }
  async function perform(payload,message){
    if(!ready||busy)return;
    busy=true;saveFailed=false;controls();status('Calculating…');
    try{
      const result=await send(payload);
      if(!result.ok){status(result.error);return;}
      selected=result.node?.id||result.nodes?.at(-1)?.id||'';
      await refresh();
      $('#studio-result-id').value=nextId('result');
      status(`${message}. ${saveFailed?'Device storage unavailable; export JSON to keep your work.':'Workspace saved on this device.'}`);
    }catch(error){status(error.message||String(error));}
    finally{busy=false;controls();}
  }
  $('#studio-define').addEventListener('submit',event=>{
    event.preventDefault();const kind=$('#object-kind').value;
    const payload={command:'define',id:$('#object-id').value.trim(),kind};
    payload[kind==='matrix'?'matrix':['vector','covector'].includes(kind)?'components':'expression']=$('#object-expression').value;
    const coords=$('#object-coordinates').value.trim(),metric=$('#object-metric').value.trim();
    if(coords)payload.coordinates=coords.split(',').map(item=>item.trim());
    if(metric)payload.metric=metric;
    perform(payload,'Object created');
  });
  $('#studio-apply').addEventListener('submit',event=>{
    event.preventDefault();
    try{
      const payload={command:'apply',id:$('#studio-result-id').value.trim(),source:$('#studio-source').value,operation:$('#studio-operation').value};
      for(const input of document.querySelectorAll('#studio-parameters [data-parameter]')){
        const key=input.dataset.parameter,value=input.value.trim();
        if(['lower','upper'].includes(key)&&!value)continue;
        payload[key]=input.type==='checkbox'?input.checked:key==='order'?Number(value):
          ['normals','mapping'].includes(key)?JSON.parse(value):key==='coordinates'?value.split(',').map(part=>part.trim()):value;
      }
      perform(payload,'Operation complete');
    }catch(error){status('Check the operation parameters: '+error.message);}
  });
  $('#studio-source').addEventListener('change',()=>{selected=$('#studio-source').value;render();});
  $('#studio-operation').addEventListener('change',renderParameters);
  $('#studio-load').addEventListener('click',()=>{
    if(nodes.length&&!window.confirm('Replace this workspace with the example? Export JSON first to keep a separate copy.'))return;
    perform({command:'import',snapshot:{format:'calculator2.workspace',version:1,steps:EXAMPLES[$('#studio-example').value]}},'Example calculated');
  });
  $('#studio-reset').addEventListener('click',()=>{
    if(window.confirm('Clear all objects from this workspace?'))perform({command:'reset'},'Workspace cleared');
  });
  $('#studio-export').addEventListener('click',async()=>{
    const result=await send({command:'export'});if(!result.ok){status(result.error);return;}
    const url=URL.createObjectURL(new Blob([JSON.stringify(result.snapshot,null,2)],{type:'application/json'}));
    const link=element('a');link.href=url;link.download='calculator-workspace.json';link.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
  });
  $('#studio-import-button').addEventListener('click',()=>$('#studio-import').click());
  $('#studio-import').addEventListener('change',async event=>{
    try{
      const file=event.target.files[0];if(!file)return;
      if(file.size>75000)throw new Error('File exceeds the 75 KB workspace limit.');
      const snapshot=JSON.parse(await file.text());
      if(nodes.length&&!window.confirm('Replace the current workspace with the imported file?'))return;
      await perform({command:'import',snapshot},'Workspace imported');
    }catch(error){status('Import failed: '+error.message);}
    finally{event.target.value='';}
  });
  for(const button of document.querySelectorAll('[data-view]'))button.addEventListener('click',()=>{
    const studio=button.dataset.view==='studio';
    $('#studio-view').hidden=!studio;$('#calculator-view').hidden=studio;$('#calculator-intro').hidden=studio;
    for(const item of document.querySelectorAll('[data-view]'))item.setAttribute('aria-pressed',String(item===button));
    if(studio&&ready)refresh();
  });
  return {
    async ready(){ready=true;const result=await send({command:'operations'});signatures=result.operations||{};await refresh();controls();},
    setStatus(state){ready=state==='ready';$('#studio-engine').textContent=ready?'● Engine ready · on this device':state==='error'?'Engine unavailable':'Starting engine…';controls();},
    saved(ok){saveFailed=!ok;},
    restoreError(error){status('Saved workspace could not be restored: '+error);}
  };
}
