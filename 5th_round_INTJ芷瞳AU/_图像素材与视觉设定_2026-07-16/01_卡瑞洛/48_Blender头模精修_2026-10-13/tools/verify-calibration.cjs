const {chromium}=require('C:/Users/kdsha/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const fs=require('fs'),path=require('path');
(async()=>{
const browser=await chromium.launch({headless:true,channel:'msedge'});
const page=await browser.newPage({viewport:{width:1440,height:1050}});
const errors=[];page.on('pageerror',e=>errors.push(String(e)));page.on('console',m=>{if(m.type()==='error')errors.push(m.text())});
await page.goto('http://127.0.0.1:8848/?calibration=1');await page.waitForFunction(()=>window.calibrationReady,null,{timeout:30000});
await page.screenshot({path:path.join(__dirname,'../renders/likeness-alignment-face.png')});
await page.click('[data-region="eyes"]');await page.screenshot({path:path.join(__dirname,'../renders/likeness-alignment-eyes.png')});
await page.check('#lines');await page.click('#overlay');await page.locator('#mix').press('ArrowRight');
const overlay=await page.locator('#grid').evaluate(e=>e.classList.contains('overlay'));
await page.screenshot({path:path.join(__dirname,'../renders/likeness-alignment-overlay.png')});
await page.goto('http://127.0.0.1:8848/model-v9.html');await page.waitForFunction(()=>window.modelReady,null,{timeout:60000});
const out={errors,overlay,preserved_model:await page.evaluate(()=>window.sceneStats),default_view:'likeness-calibration',author_feedback:'V9 still unlike'};
fs.writeFileSync(path.join(__dirname,'../calibration-validation.json'),JSON.stringify(out,null,2));
console.log(JSON.stringify(out));await browser.close();if(errors.length)process.exitCode=1;
})();
