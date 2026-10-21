const {chromium}=require('C:/Users/kdsha/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const fs=require('fs'),path=require('path');
(async()=>{
 const browser=await chromium.launch({headless:true,channel:'msedge'}), page=await browser.newPage({viewport:{width:1500,height:1000}}),errors=[];
 page.on('pageerror',e=>errors.push(String(e)));page.on('console',m=>{if(m.type()==='error')errors.push(m.text());});
 await page.goto('http://127.0.0.1:8849/');await page.waitForFunction(()=>window.modelReady,null,{timeout:60000});
 await page.waitForTimeout(600);const stats=await page.evaluate(()=>window.sceneStats);
 await page.screenshot({path:path.join(__dirname,'../renders/browser-r5-front.png')});
 await page.click('[data-angle="-45"]');await page.waitForTimeout(400);await page.click('#neutral');await page.click('#hair');
 await page.waitForTimeout(400);const neutral=await page.evaluate(()=>window.neutralMode);await page.screenshot({path:path.join(__dirname,'../renders/browser-r5-neutral.png')});
 await page.click('[data-ref="side"]');await page.waitForFunction(()=>document.querySelector('#ref').complete&&document.querySelector('#ref').naturalWidth>0);
 await page.goto('http://127.0.0.1:8849/comparison.html');await page.waitForFunction(()=>window.calibrationReady,null,{timeout:60000});
 await page.screenshot({path:path.join(__dirname,'../renders/browser-r5-comparison.png')});
 await page.click('[data-region="eyes"]');await page.click('#overlay');await page.locator('#mix').focus();await page.keyboard.press('Home');await page.keyboard.press('ArrowRight');
 const result={version:'R5',url:'http://127.0.0.1:8849/',errors,stats,neutral,comparison:true};
 fs.writeFileSync(path.join(__dirname,'../viewer-validation.json'),JSON.stringify(result,null,2));console.log(JSON.stringify(result));await browser.close();if(errors.length)process.exitCode=1;
})().catch(e=>{console.error(e);process.exitCode=1});
