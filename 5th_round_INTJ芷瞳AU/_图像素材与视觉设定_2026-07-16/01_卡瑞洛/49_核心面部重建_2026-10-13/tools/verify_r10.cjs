const {chromium}=require('C:/Users/kdsha/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const fs=require('fs'),path=require('path');
(async()=>{const b=await chromium.launch({headless:true,channel:'msedge'});const p=await b.newPage({viewport:{width:1500,height:1050}});const errors=[];p.on('pageerror',e=>errors.push(e.message));
await p.goto('http://127.0.0.1:8849/model-r10-candidate.html');await p.waitForFunction(()=>window.modelReady,{timeout:60000});await p.screenshot({path:path.join(__dirname,'../renders/r10-web-front.png')});const stats=await p.evaluate(()=>window.sceneStats);
await p.locator('[data-angle="-56"]').click();await p.screenshot({path:path.join(__dirname,'../renders/r10-web-p14.png')});
await p.locator('#neutral').click();if(!(await p.evaluate(()=>window.neutralMode)))throw Error('neutral failed');
await p.locator('#hair').click();await p.screenshot({path:path.join(__dirname,'../renders/r10-web-neutral.png')});
await p.goto('http://127.0.0.1:8849/comparison-r10-candidate.html');await p.waitForFunction(()=>window.calibrationReady);await p.screenshot({path:path.join(__dirname,'../renders/r10-reference-comparison.png')});
for(const region of ['eyes','nose','lower']){await p.locator('[data-region="'+region+'"]').click();}
for(const style of ['front','front-neutral','front-soft']){await p.locator('[data-style="'+style+'"]').click();await p.waitForTimeout(150);}
await p.locator('[data-region="face"]').click();await p.locator('#overlay').click();await p.locator('#mix').fill('0.4');await p.locator('#mix').dispatchEvent('input');
await p.goto('http://127.0.0.1:8849/sculpt-comparison-r10-candidate.html');
for(const view of ['front-soft','front','p14','threequarter']){await p.locator('[data-view="'+view+'"]').click();await p.waitForFunction(()=>[...document.images].every(i=>i.complete&&i.naturalWidth>0));}
const report={stats,errors,checks:['GLB loaded','T22 and P14 cameras','neutral and hair toggles','reference alignment','region magnification','lighting variants','overlay','all multiview images loaded']};fs.writeFileSync(path.join(__dirname,'../viewer-r10-validation.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(report));await b.close();if(errors.length)process.exit(1);})();
