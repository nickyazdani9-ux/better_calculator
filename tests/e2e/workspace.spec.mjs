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
