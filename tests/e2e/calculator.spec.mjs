import {test,expect} from '@playwright/test';
test('offline-vendored runtime computes a symbolic derivative',async({page})=>{
  await page.goto('/');
  await expect(page.locator('#engine-indicator')).toHaveAttribute('data-state','ready',{timeout:150_000});
  await page.getByRole('tab',{name:'Calculus'}).click();
  await page.locator('#operation').selectOption('differentiate');
  const first=page.locator('#fields [data-field-key]').first();
  await first.fill('x^2');
  await page.locator('#run').click();
  await expect(page.locator('#result-state')).toContainText('Exact symbolic output');
  await expect(page.locator('#result-text')).toContainText('2*x');
});

test('entered fractions are typeset separately and results can be reused as steps',async({page})=>{
  await page.goto('/');
  await expect(page.locator('#engine-indicator')).toHaveAttribute('data-state','ready',{timeout:150_000});
  await page.locator('#operation').selectOption('evaluate');
  await page.locator('#fields [data-field-key="expression"]').fill('2/4');
  await page.getByRole('button',{name:/Done/}).click();
  await expect(page.locator('#input-math .katex')).toHaveCount(1);
  await expect(page.locator('#result-math .katex')).toHaveCount(1);
  await expect(page.locator('#result-text')).toHaveText('1/2');
  await expect(page.locator('#result-section')).toHaveClass(/has-typeset/);
  await page.locator('#add-step').click();
  await expect(page.locator('#worksheet-steps .worksheet-step')).toHaveCount(1);
  await expect(page.locator('#print')).toBeEnabled();
  await page.locator('#reuse').click();
  await expect(page.locator('#fields [data-field-key="expression"]')).toHaveValue('(1/2)');
});

test('Riccati solver gives an Euler basis and a Bessel reduction in the actual worker', async ({page}) => {
  await page.goto('/');
  await expect(page.locator('#engine-indicator')).toHaveAttribute('data-state','ready');
  await page.getByRole('tab',{name:'Differential equations'}).click();
  await page.locator('#operation').selectOption('linear_second_order');
  await page.locator('#run').click();
  await expect(page.locator('#result-lines')).toContainText('Euler — solved');
  await expect(page.locator('#result-math .katex')).toHaveCount(1);
  for (const [key,value] of Object.entries({a:'x^2', b:'x', c:'x^2-4'})) {
    await page.locator(`#fields [data-field-key="${key}"]`).fill(value);
  }
  await page.locator('#run').click();
  await expect(page.locator('#result-lines')).toContainText('Bessel — reduced');
  await expect(page.locator('#result-lines')).toContainText('dz/dx');
});
