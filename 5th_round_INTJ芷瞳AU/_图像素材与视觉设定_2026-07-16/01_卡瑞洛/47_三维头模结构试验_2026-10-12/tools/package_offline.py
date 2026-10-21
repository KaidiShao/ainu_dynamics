import pathlib,json,base64,re
R=pathlib.Path(__file__).resolve().parents[1]
html=(R/'index.html').read_text(encoding='utf8')
refs=json.loads((R/'landmarks.json').read_text(encoding='utf8'))
images={k:'data:image/png;base64,'+base64.b64encode(pathlib.Path(v['path']).read_bytes()).decode() for k,v in refs.items()}
html=re.sub(r'<script type="importmap">.*?</script>','',html)
for k,u in images.items():html=html.replace('/ref/'+k+'.png',u)
js=(R/'viewer.js').read_text(encoding='utf8')
js=js.replace("const fit=await (await fetch('./head-fit.json')).json();",'const fit='+ (R/'head-fit.json').read_text(encoding='utf8')+';')
js=js.replace("'/ref/T22.png'",json.dumps(images['T22']))
js=js.replace("'./assets/OrbitControls.js'","'orbit-controls'")
assets={x:(R/'assets'/x).read_text(encoding='utf8') for x in ['three.core.js','three.module.js','OrbitControls.js']}
def safe(x):return json.dumps(x,ensure_ascii=True).replace('</','<\\/')
boot='''<script>
const blobModule=s=>URL.createObjectURL(new Blob([s],{type:'text/javascript'}));
const core=blobModule(__CORE__);
const three=blobModule(__THREE__.replaceAll('./three.core.js',core));
const orbit=blobModule(__ORBIT__);
const map=document.createElement('script');map.type='importmap';map.textContent=JSON.stringify({imports:{three,'orbit-controls':orbit}});document.head.appendChild(map);
const code=document.createElement('script');code.type='module';code.textContent=__VIEWER__;document.body.appendChild(code);
</script>'''
chunks={'CORE':assets['three.core.js'],'THREE':assets['three.module.js'],'ORBIT':assets['OrbitControls.js'],'VIEWER':js}
boot=re.sub(r'__(CORE|THREE|ORBIT|VIEWER)__',lambda m:safe(chunks[m.group(1)]),boot)
html=html.replace('<script type="module" src="./viewer.js"></script>',boot)
out=R/'carrillo-head-viewer.html';out.write_text(html,encoding='utf8');print(out.name,out.stat().st_size)
