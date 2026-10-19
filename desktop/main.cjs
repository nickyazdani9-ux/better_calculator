'use strict';
const {app,BrowserWindow,shell}=require('electron');
const path=require('node:path');
const {createStaticServer}=require('./static-server.cjs');
let server;
let origin;
function createWindow(){
  const win=new BrowserWindow({width:1120,height:840,minWidth:360,minHeight:500,
    title:'Calculator 2.0',backgroundColor:'#0b101a',
    webPreferences:{nodeIntegration:false,contextIsolation:true,sandbox:true,webSecurity:true}});
  win.webContents.setWindowOpenHandler(()=>({action:'deny'}));
  win.webContents.on('will-navigate',(event,url)=>{
    if(!url.startsWith(origin+'/'))event.preventDefault();
  });
  win.loadURL(origin+'/');
}
app.whenReady().then(async()=>{
  server=createStaticServer(path.resolve(__dirname,'../dist'));
  await new Promise((resolve,reject)=>{
    server.once('error',reject);
    server.listen(0,'127.0.0.1',resolve);
  });
  origin=`http://127.0.0.1:${server.address().port}`;
  createWindow();
  app.on('activate',()=>{if(BrowserWindow.getAllWindows().length===0)createWindow();});
}).catch(error=>{console.error(error);app.quit();});
app.on('window-all-closed',()=>{if(process.platform!=='darwin')app.quit();});
app.on('before-quit',()=>server?.close());
