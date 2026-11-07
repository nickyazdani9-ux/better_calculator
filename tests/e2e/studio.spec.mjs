import {test,expect} from '@playwright/test';

async function openStudio(page){
  await page.goto('/');
  await expect(page.locator('#engine-indicator')).toHaveAttribute('data-state','ready');
  await page.getByRole('button',{name:'Workspace',exact:true}).click();
}

test('visible workspace composes typed results and restores after reload',async({page})=>{
  await openStudio(page);
  await page.getByLabel('Object name').fill('f');
  await page.getByLabel('Object expression').fill('x^3');
  await page.getByRole('button',{name:'Create object',exact:true}).click();
  await expect(page.locator('[data-node-id="f"]')).toContainText('f');
  await page.getByLabel('Workspace operation').selectOption('differentiate');
  await page.getByLabel('Result name').fill('df');
  await page.getByRole('button',{name:'Apply operation',exact:true}).click();
  await expect(page.locator('[data-node-id="df"]')).toContainText('3*x**2');
  await expect(page.locator('#studio-status')).toContainText('saved');
  await page.reload();
  await page.getByRole('button',{name:'Workspace',exact:true}).click();
  await expect(page.locator('[data-node-id="df"]')).toContainText('3*x**2');
  await expect(page.locator('[data-node-id="df"]')).toContainText('f');
});

test('cross-domain example is calculated locally and works without external requests',async({page})=>{
  await page.route(/^https:\/\//,route=>route.abort());
  await openStudio(page);
  await page.getByRole('button',{name:'Load example',exact:true}).click();
  await expect(page.locator('[data-node-id="expected"]')).toContainText('16');
  await expect(page.locator('[data-node-id="df"] .katex')).toHaveCount(1);
  await page.reload();
  await page.getByRole('button',{name:'Workspace',exact:true}).click();
  await expect(page.locator('[data-node-id="expected"]')).toContainText('16');
});

test('invalid JSON import preserves the last valid workspace',async({page})=>{
  await openStudio(page);
  await page.getByRole('button',{name:'Load example',exact:true}).click();
  await expect(page.locator('[data-node-id="expected"]')).toBeVisible();
  await page.locator('#studio-import').setInputFiles({
    name:'bad.json',mimeType:'application/json',buffer:Buffer.from('{bad json')
  });
  await expect(page.locator('#studio-status')).toContainText('Import failed');
  await expect(page.locator('[data-node-id="expected"]')).toBeVisible();
});

test('mobile workspace fits the viewport and exposes the calculated result',async({page})=>{
  await page.setViewportSize({width:390,height:844});
  await openStudio(page);
  await page.getByRole('button',{name:'Load example',exact:true}).click();
  await expect(page.locator('[data-node-id="expected"]')).toContainText('16');
  expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);
});
