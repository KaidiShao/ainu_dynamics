"""Build a self-contained local audition helper; no audio embedded or uploaded."""
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parent


def build():
    annotation=json.loads((ROOT/'annotations.json').read_text(encoding='utf-8'))
    payload=json.dumps(annotation,ensure_ascii=False).replace('<','\\u003c')
    html=r'''<!doctype html>
<html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>意难忘 · 本地试听与独立记录</title>
<style>
body{font-family:system-ui,"Microsoft YaHei",sans-serif;background:#f4f2ed;color:#243235;max-width:1100px;margin:32px auto;padding:0 24px;line-height:1.7}h1{font-size:28px;margin-bottom:8px}h2{font-size:20px}section,details{background:#fff;padding:22px;margin:20px 0;border:1px solid #deded8;border-radius:10px}button,input,textarea{font:inherit}button{background:#264f59;color:white;border:0;border-radius:5px;padding:7px 13px;margin:3px;cursor:pointer}button:focus-visible,input:focus-visible,textarea:focus-visible{outline:3px solid #b9843e}button.secondary{background:#e5eceb;color:#243235}input,textarea{padding:8px;border:1px solid #bac5c4;border-radius:4px;box-sizing:border-box;max-width:100%}textarea{width:100%;min-height:90px}audio{width:100%;margin:12px 0}.muted{color:#58696c;font-size:14px}.grid{display:grid;grid-template-columns:1fr 1fr;gap:12px}.row{padding:8px 0;border-bottom:1px solid #e8e8e4}.clock{font-variant-numeric:tabular-nums;font-size:24px}label{display:block;margin:8px 0}table{border-collapse:collapse;width:100%;font-size:14px}td,th{padding:8px;text-align:left;border-bottom:1px solid #ddd;word-break:break-word}summary{cursor:pointer;font-weight:600}#status{color:#785326} @media(max-width:650px){.grid{grid-template-columns:1fr}body{padding:0 12px}}
</style>
<h1>《意难忘》· 本地试听与独立记录</h1>
<p>先听，再记录；之后再看候选动机。研究报告尚未经过听觉复核。</p>
<section>
<label>选择你本地的录音 <input id="file" type="file" accept="audio/*,.flac"></label>
<p class="muted">音频只在当前浏览器中读取，不上传、不导出。参考录音时长 06:25.631；本页未自动核对 SHA-256。若浏览器不能解码 FLAC，可按报告时间戳在本地播放器复核。</p>
<p id="status" role="status">尚未选择文件。</p>
<audio id="player" controls preload="metadata"></audio>
<div class="clock" id="clock">00:00.0</div>
<button id="full">从头完整播放</button><button id="unlimit" class="secondary">取消片段终点限制</button><button id="mark" class="secondary">标记当前时间</button>
<div class="grid"><label>片段起点（秒） <input id="start" type="number" min="0" step="0.1" value="0"></label><label>片段终点（秒） <input id="end" type="number" min="0" step="0.1" value="385.6"></label></div>
<button id="range">播放所填范围</button><p class="muted">片段停止受浏览器 timeupdate 精度影响，可能晚约数百毫秒；不是精确音频裁切。全曲试听和片段试听请分别记录。</p>
</section>
<section><h2>独立体验记录</h2>
<p class="muted">只填实际发生的体验，可以写“无变化”或留空；无需选择任何预设身体位置。本页不会自动保存，关闭前请导出 CSV。</p>
<div class="grid"><label>体验起点/标记（秒） <input id="when" type="number" min="0" step="0.1"></label><label>体验终点（秒，可空） <input id="until" type="number" min="0" step="0.1"></label></div>
<label>自由描述体验 <textarea id="experience"></textarea></label>
<div class="grid"><label>位置，自由描述（可空） <input id="body"></label><label>强度（自选量尺或文字） <input id="intensity"></label><label>确信程度 / 时间误差 <input id="confidence"></label><label>当时预期（可空） <input id="expectation"></label></div>
<label>设备、音量、熟悉程度、当天已听次数、状态、是否看过分析 <textarea id="context"></textarea></label>
<button id="save">加入本次记录</button><button id="export" class="secondary">导出 CSV</button>
<p id="count" role="status">0 条记录</p><table><thead><tr><th>时间</th><th>体验</th><th>位置</th><th>操作</th></tr></thead><tbody id="records"></tbody></table>
</section>
<details><summary>结构复核模式：展开候选时间点（建议独立体验记录之后再看）</summary>
<p>以下均为计算候选，不是已确认旋律。每个按钮加入前后约 2 秒上下文；原始声量不作自动匹配。两遍分别记录前景旋律、背景、节奏、休止及是否同一材料。</p>
<div id="motifs"></div><h2>全曲工作分段</h2><div id="sections"></div>
</details>
<p class="muted">本地试听工具 · 候选时间点不等于听辨结论。全部资源内嵌，无外部脚本和网络请求。</p>
<script>
'use strict';
const annotation=__ANNOTATION__;
const $=id=>document.getElementById(id),audio=$('player');
let objectURL=null,stopAt=null,records=[];
function stamp(s){return `${Math.floor(s/60).toString().padStart(2,'0')}:${(s%60).toFixed(1).padStart(4,'0')}`;}
function play(a,b){if(!audio.src){$('status').textContent='请先选择本地音频。';return;}if(!Number.isFinite(a)||!Number.isFinite(b)||a<0||b<=a||a>=audio.duration){$('status').textContent='请输入有效的起止时间。';return;}stopAt=Math.min(b,audio.duration);audio.currentTime=a;audio.play().catch(e=>{$('status').textContent='无法播放：'+e.message;});}
$('file').addEventListener('change',()=>{audio.pause();stopAt=null;if(objectURL)URL.revokeObjectURL(objectURL);const f=$('file').files[0];if(!f)return;objectURL=URL.createObjectURL(f);audio.src=objectURL;$('status').textContent='已选择：'+f.name;});
audio.addEventListener('loadedmetadata',()=>{$('status').textContent=`已读取 ${stamp(audio.duration)}。`+(Math.abs(audio.duration-385.6306667)>.5?' 时长与研究录音不同，请先核对版本与偏移。':' 请核对文件身份后试听。');});
audio.addEventListener('error',()=>{$('status').textContent='浏览器无法读取此音频；请使用支持 FLAC 的本地播放器及报告时间戳。';});
audio.addEventListener('timeupdate',()=>{$('clock').textContent=stamp(audio.currentTime);if(stopAt!==null&&audio.currentTime>=stopAt){audio.pause();stopAt=null;}});
$('full').onclick=()=>{play(0,audio.duration);};$('unlimit').onclick=()=>{stopAt=null;};$('mark').onclick=()=>{$('when').value=audio.currentTime.toFixed(1);};$('range').onclick=()=>play(Number($('start').value),Number($('end').value));
function button(text,a,b,parent){const el=document.createElement('button');el.textContent=text;el.onclick=()=>{const start=Math.max(0,a-2),end=Math.min(385.6306667,b+2);$('start').value=start.toFixed(1);$('end').value=end.toFixed(1);play(start,end);};parent.appendChild(el);}
const statuses={seed:'模板',strong_candidate:'强候选',variant_candidate:'中等变形候选',weak_candidate:'弱候选',linked_candidate:'间接关联，待复核'};
for(const m of annotation.motifs){const row=document.createElement('div');row.className='row';const name=document.createElement('strong');name.textContent=m.id+' ';row.appendChild(name);for(const o of m.occurrences)button(`${stamp(o.start)}–${stamp(o.end)} · ${statuses[o.status]||o.status}`,o.start,o.end,row);$('motifs').appendChild(row);}
for(const s of annotation.sections)button(`${s.id} ${stamp(s.start)}–${stamp(s.end)}`,s.start,s.end,$('sections'));
function render(){const body=$('records');body.replaceChildren();records.forEach((r,i)=>{const tr=document.createElement('tr');for(const v of [r.start_s,r.experience,r.body_location]){const td=document.createElement('td');td.textContent=v;tr.appendChild(td);}const td=document.createElement('td'),del=document.createElement('button');del.textContent='删除';del.className='secondary';del.onclick=()=>{records.splice(i,1);render();};td.appendChild(del);tr.appendChild(td);body.appendChild(tr);});$('count').textContent=`${records.length} 条记录（关闭前请导出）`;}
$('save').onclick=()=>{records.push({recorded_at:new Date().toISOString(),audio_filename:$('file').files[0]?.name||'',start_s:$('when').value,end_s:$('until').value,experience:$('experience').value,body_location:$('body').value,intensity:$('intensity').value,confidence:$('confidence').value,expectation:$('expectation').value,context:$('context').value});render();for(const id of ['when','until','experience','body','intensity','confidence','expectation'])$(id).value='';};
$('export').onclick=()=>{if(!records.length){$('count').textContent='还没有记录。';return;}const keys=Object.keys(records[0]),escape=x=>'"'+String(x).replaceAll('"','""')+'"';const csv='\ufeff'+[keys.map(escape).join(','),...records.map(r=>keys.map(k=>escape(r[k])).join(','))].join('\r\n');const u=URL.createObjectURL(new Blob([csv],{type:'text/csv;charset=utf-8'}));const a=document.createElement('a');a.href=u;a.download='independent_listening_notes.csv';a.click();setTimeout(()=>URL.revokeObjectURL(u),1000);};
</script></html>'''
    (ROOT/'listening_review.html').write_text(html.replace('__ANNOTATION__',payload),encoding='utf-8')


if __name__=='__main__':build()
