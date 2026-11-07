import {test, expect} from '@playwright/test';

async function attachWorker(page) {
  await page.addInitScript(() => {
    const NativeWorker = window.Worker;
    window.Worker = class extends NativeWorker {
      constructor(...args) {
        super(...args);
        window.mathWorker = this;
      }
    };
  });
}

async function workspaceCommand(page, payload) {
  return page.evaluate(data => new Promise((resolve, reject) => {
    const worker = window.mathWorker;
    if (!worker) {reject(new Error('Worker not present')); return;}
    const id = Math.floor(Math.random() * 1000000000) + 1000000;
    const timeout = setTimeout(() => {worker.removeEventListener('message', handler); reject(new Error('Worker timeout'));}, 90000);
    function handler(event) {
      const message = event.data;
      if (message.type === 'response' && message.id === id) {
        clearTimeout(timeout);
        worker.removeEventListener('message', handler);
        resolve(message.result);
      }
    }
    worker.addEventListener('message', handler);
    worker.postMessage({type: 'calculate', id, payload: {action: 'workspace', ...data}});
  }), payload);
}

test('typed mathematical workflow survives an actual browser reload', async ({page}) => {
  await attachWorker(page);
  await page.goto('/');
  await expect(page.locator('#engine-indicator')).toHaveAttribute('data-state', 'ready', {timeout: 150000});
  const before = await workspaceCommand(page, {command: 'batch', steps: [
    {command: 'define', id: 'f', expression: 'x^2'},
    {command: 'apply', id: 'derived', source: 'f', operation: 'differentiate', variable: 'x'}
  ]});
  expect(before.ok).toBe(true);
  await expect.poll(async () => page.evaluate(() => localStorage.getItem('calculator2.workspace.v1'))).not.toBeNull();
  await page.reload();
  await expect(page.locator('#engine-indicator')).toHaveAttribute('data-state', 'ready', {timeout: 150000});
  const restored = await workspaceCommand(page, {command: 'get', id: 'derived'});
  expect(restored.ok).toBe(true);
  expect(restored.node.expr).toBe('2*x');
  expect(restored.node.parents).toEqual(['f']);
  const snapshot = await workspaceCommand(page, {command: 'export'});
  expect(snapshot.ok).toBe(true);
  expect(snapshot.snapshot.steps).toHaveLength(2);
});


test('cross-domain workflow keeps metric, provenance and result after reload', async ({page}) => {
  await attachWorker(page);
  await page.goto('/');
  await expect(page.locator('#engine-indicator')).toHaveAttribute('data-state', 'ready', {timeout: 150000});
  const before = await workspaceCommand(page, {command: 'batch', steps: [
    {command: 'define', id: 'f', expression: '(x+I*y)^2',
     coordinates: ['x', 'y'], metric: '[[1,0],[0,1]]'},
    {command: 'apply', id: 'df', source: 'f', operation: 'exterior_derivative'},
    {command: 'apply', id: 'norm', source: 'df', operation: 'norm_squared'},
    {command: 'apply', id: 'expected', source: 'norm', operation: 'expectation',
     independent: true, normals: {
       x: {mean: '0', std: '1'}, y: {mean: '0', std: '1'}
     }}
  ]});
  expect(before.ok).toBe(true);
  expect(before.results[3].node.expr).toBe('16');
  await expect.poll(async () => page.evaluate(
    () => JSON.parse(localStorage.getItem('calculator2.workspace.v1') || '{}').steps?.length ?? 0
  )).toBe(4);

  await page.reload();
  await expect(page.locator('#engine-indicator')).toHaveAttribute('data-state', 'ready', {timeout: 150000});
  const restored = await workspaceCommand(page, {command: 'graph'});
  expect(restored.ok).toBe(true);
  const nodes = restored.nodes;
  expect(nodes.map(node => node.id)).toEqual(['f', 'df', 'norm', 'expected']);
  expect(nodes[0].context.coordinates).toEqual(['x', 'y']);
  expect(nodes[0].context.metric.replace(/\s+/g, '')).toBe('Matrix([[1,0],[0,1]])');
  expect(nodes[1].kind).toBe('covector');
  expect(nodes[1].parents).toEqual(['f']);
  expect(nodes[2].parents).toEqual(['df']);
  expect(nodes[3].expr).toBe('16');
  expect(nodes[3].parents).toEqual(['norm']);
});


test('unified worker composes Fourier transforms with matrix determinant', async ({page}) => {
  await attachWorker(page);
  await page.goto('/');
  await expect(page.locator('#engine-indicator')).toHaveAttribute('data-state', 'ready', {timeout: 150000});
  const result=await workspaceCommand(page, {command: 'batch',steps:[
    {command:'define',id:'gaussian',expression:'exp(-pi*x^2)'},
    {command:'apply',id:'spectrum',source:'gaussian',operation:'fourier',
     variable:'x',frequency:'k'},
    {command:'define',id:'m',kind:'matrix',matrix:'[[2,0],[0,1]]'},
    {command:'apply',id:'det',source:'m',operation:'determinant'},
    {command:'apply',id:'scaled',source:'spectrum',other:'det',operation:'multiply'},
    {command:'apply',id:'recovered',source:'scaled',operation:'inverse_fourier',
     variable:'k',frequency:'x'}
  ]});
  expect(result.ok).toBe(true);
  expect(result.results[1].node.expr).toContain('exp(-pi*k**2)');
  expect(result.results[5].node.expr).toContain('exp(-pi*x**2)');
  expect(result.results[5].node.parents).toEqual(['scaled']);
});
