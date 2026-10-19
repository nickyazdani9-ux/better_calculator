import test from 'node:test';
import assert from 'node:assert/strict';
import { defaultsFor, findOperation, validateCatalog, formatHistoryEntry } from '../src/registry.js';

const catalog = [{id:'calculus',name:'Calculus',operations:[{id:'differentiate',label:'Differentiate', fields:[{key:'expression',label:'Expression',default:'x^2'},{key:'order',label:'Order',default:'1'}]}]}];
test('catalog validation checks metadata', () => { assert.equal(validateCatalog(catalog),true); });
test('registry resolves operations and defaults', () => {
  assert.equal(findOperation(catalog,'calculus','differentiate').id,'differentiate');
  assert.deepEqual(defaultsFor(catalog,'calculus','differentiate'),{expression:'x^2',order:'1'});
});
test('unknown operations do not execute', () => { assert.equal(findOperation(catalog,'calculus','fake'),null); });
test('history formats safely',()=> {
  assert.match(formatHistoryEntry({tab:'calculus',operation:'differentiate',values:{expression:'x^2'},result:{text:'2*x'}}),/2\*x/);
});
