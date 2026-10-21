const {chromium}=require('C:/Users/kdsha/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const fs=require('fs'),path=require('path');
(async()=>{const browser=await chromium.launch({headless:true,channel:'msedge'});try{
 const page=await browser.newPage({viewport:{width:1500,height:1000}}),errors=[];page.on('pageerror',e=>errors.push(String(e)));page.on('console',m=>{if(m.type()==='error')errors.push(m.text());});
 await page.goto('http://127.0.0.1:8849/');await page.waitForFunction(()=>window.modelReady,null,{timeout:60000});
 const stats=await page.evaluate(()=>window.sceneStats),modelResource=await page.evaluate(()=>performance.getEntriesByType('resource').filter(x=>x.name.endsWith('.glb')).map(x=>x.name));
 if(!modelResource.some(x=>x.endsWith('/carrillo-core-r9.glb')))throw Error('Wrong model version');
 await page.screenshot({path:path.join(__dirname,'../renders/browser-r9-front.png')});await page.click('[data-angle="-45"]');await page.click('#neutral');await page.click('#hair');await page.waitForTimeout(400);
 await page.screenshot({path:path.join(__dirname,'../renders/browser-r9-neutral.png')});
 await page.goto('http://127.0.0.1:8849/comparison.html');await page.waitForFunction(()=>window.calibrationReady);await page.screenshot({path:path.join(__dirname,'../renders/browser-r9-reference.png')});await page.click('[data-region="nose"]');await page.screenshot({path:path.join(__dirname,'../renders/browser-r9-nose-reference.png')});
 await page.goto('http://127.0.0.1:8849/sculpt-comparison.html');
 const views=['nose-neutral','nose-side-neutral','nose-profile-neutral','neutral','front-neutral','front','threequarter','near-profile'];
 for(const v of views){await page.click('[data-view="'+v+'"]');await page.waitForFunction(()=>[...document.querySelectorAll('img')].every(i=>i.complete&&i.naturalWidth>0));}
 await page.click('[data-view="nose-neutral"]');await page.waitForFunction(()=>[...document.querySelectorAll('img')].every(i=>i.complete&&i.naturalWidth>0));await page.screenshot({path:path.join(__dirname,'../renders/browser-r9-changes.png')});
 await page.click('#overlay');await page.locator('#mix').focus();await page.keyboard.press('End');
 const overlay=await page.locator('#superimposed').evaluate(e=>getComputedStyle(e).opacity);if(overlay!=='1')throw Error('Overlay control failed');
 const result={version:'R9',errors,stats,modelResource,views,overlay};fs.writeFileSync(path.join(__dirname,'../viewer-r9-validation.json'),JSON.stringify(result,null,2));console.log(JSON.stringify(result));if(errors.length)process.exitCode=1;
}finally{await browser.close();}})().catch(e=>{console.error(e);process.exitCode=1});
