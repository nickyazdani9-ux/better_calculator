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
