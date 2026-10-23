import test from 'node:test';
import assert from 'node:assert/strict';
import {WORKSPACE_STORAGE_KEY, readWorkspaceSnapshot, writeWorkspaceSnapshot,
        clearWorkspaceSnapshot} from '../src/workspace-storage.js';

const sample = () => ({
  format: 'calculator2.workspace', version: 1,
  steps: [{command: 'define', id: 'f', expression: '(x+I*y)^2',
           coordinates: ['x','y'], metric: '[[1,0],[0,1]]'}],
});
function memoryStorage(){
  const items = new Map();
  return {
    getItem: key => items.has(key) ? items.get(key) : null,
    setItem: (key, value) => items.set(key, String(value)),
    removeItem: key => items.delete(key),
  };
}

test('roundtrips versioned mathematical commands across sessions',()=>{
  const storage = memoryStorage();
  assert.equal(readWorkspaceSnapshot(storage), null);
  writeWorkspaceSnapshot(storage, sample());
  const restored = readWorkspaceSnapshot(storage);
  assert.deepEqual(restored, sample());
  restored.steps[0].expression = 'bad';
  assert.equal(readWorkspaceSnapshot(storage).steps[0].expression, '(x+I*y)^2');
  clearWorkspaceSnapshot(storage);
  assert.equal(storage.getItem(WORKSPACE_STORAGE_KEY), null);
});

test('does not hydrate corrupt or unsupported snapshots',()=>{
  const storage = memoryStorage();
  for (const invalid of [
    '{not json', '{}', 'null',
    JSON.stringify({format:'calculator2.workspace',version: 200,steps: []}),
    JSON.stringify({format:'calculator2.workspace',version: 1,steps: [{command:'reset'}]}),
    JSON.stringify({format:'calculator2.workspace',version: 1,steps: new Array(65).fill({command:'define',id:'x'})}),
  ]) {
    storage.setItem(WORKSPACE_STORAGE_KEY, invalid);
    assert.equal(readWorkspaceSnapshot(storage), null);
  }
  assert.throws(()=>writeWorkspaceSnapshot(storage,{format:'oops',version:1,steps:[]}));
  assert.throws(()=>writeWorkspaceSnapshot(storage,{
    format:'calculator2.workspace',version:1,steps: [{command:'import',snapshot:{}}]
  }));
});

test('rejects excessively large storage payloads',()=>{
  const storage = memoryStorage();
  assert.throws(()=>writeWorkspaceSnapshot(storage,{
    format:'calculator2.workspace', version:1,
    steps:[{command:'define',id:'f',expression:'x'.repeat(80000)}]
  }));
});
