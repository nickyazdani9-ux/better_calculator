// Run on each native runner. These images come from the Electron app itself.
const {_electron:electron}=require('playwright');
const {mkdir}=require('node:fs/promises');
const path=require('node:path');
const assert=require('node:assert/strict');
async function launch(){
  const app=await electron.launch({args:[path.resolve(__dirname,'..'),'--no-sandbox'],timeout:60000});
  const page=await app.firstWindow();
  await page.setViewportSize({width:1440,height:1000});
  await page.locator('#engine-indicator[data-state="ready"]').waitFor({state:'attached',timeout:150000});
  return {app,page};
}
(async()=>{
  const output=path.resolve('release/screens');await mkdir(output,{recursive:true});
  let {app,page}=await launch();
  try{
    await page.getByRole('tab',{name:'Calculus',exact:true}).click();
    await page.locator('#operation').selectOption('differentiate');
    await page.locator('#math-expression').fill('x^3+sin(x)');
    await page.locator('#run').click();
    await page.locator('#result-state').filter({hasText:'Exact symbolic output'}).waitFor();
    await page.screenshot({path:path.join(output,`calculator2-${process.platform}-calculator.png`)});
    await page.getByRole('button',{name:'Workspace',exact:true}).click();
    page.on('dialog',dialog=>dialog.accept());
    await page.getByRole('button',{name:'Load example',exact:true}).click();
    await page.locator('[data-node-id="expected"]').waitFor();
    assert.match(await page.locator('[data-node-id="expected"]').innerText(),/16/);
    await page.locator('#studio-status').filter({hasText:'saved'}).waitFor();
    await page.screenshot({path:path.join(output,`calculator2-${process.platform}-workspace.png`)});
  }finally{await app.close();}
  // Regression: native relaunch must restore the same workspace and origin.
  ({app,page}=await launch());
  try{
    await page.getByRole('button',{name:'Workspace',exact:true}).click();
    await page.locator('[data-node-id="expected"]').waitFor({timeout:60000});
    assert.match(await page.locator('[data-node-id="expected"]').innerText(),/16/);
    console.log(`Native ${process.platform}: calculation, screenshot and relaunch persistence passed.`);
  }finally{await app.close();}
})().catch(error=>{console.error(error);process.exitCode=1;});
