# -*- coding: utf-8 -*-
"""Make a backup on 'device A', then restore it onto a clean 'device B'."""
import json, os, re, subprocess
BASE = os.path.dirname(os.path.abspath(__file__))
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
src = open(os.path.join(BASE, "..", "index.html"), encoding="utf-8").read()

PROBE = r"""
<script>
window.addEventListener("load",function(){setTimeout(async function(){
 try{
 var r={}, q=function(s,x){return (x||document).querySelector(s)};
 var wait=function(ms){return new Promise(res=>setTimeout(res,ms))};
 var named=function(n){return [...document.querySelectorAll('.item')].find(e=>e.querySelector('.nm').textContent===n)};

 // ---- device A: build up a real list ----
 var t=named('Tomato'); q('.box',t).click();
 var tq=t.querySelector('.q'); tq.value='3'; tq.dispatchEvent(new Event('input',{bubbles:true}));
 var f=q('.additem[data-key="veg"]'); q('input',f).value='Petai';
 f.dispatchEvent(new Event('submit',{bubbles:true,cancelable:true}));
 await wait(200);
 q('#mstore').value='Pasar Besar'; q('#mstore').dispatchEvent(new Event('input',{bubbles:true}));
 q('#makelist').click(); await wait(150);
 q('#tobought').click(); await wait(150);
 var p=q('#boughtbody .pinput'); p.value='9.90'; p.dispatchEvent(new Event('input',{bubbles:true}));
 await wait(300);
 r.A_tally=q('#tally').textContent; r.A_total=q('#boughtsum').textContent.trim();

 // ---- capture what Backup produces ----
 var cap=null; URL.createObjectURL=function(b){cap=b;return "blob:x"};
 q('#tolist').click(); await wait(120); q('#backedit').click(); await wait(120);
 q('#backup').click();
 for(var i=0;i<60 && !cap;i++) await wait(100);
 r.backupMade=!!cap; r.backupBytes=cap?cap.size:0;
 var text = cap ? await cap.text() : "";
 var parsed = text ? JSON.parse(text) : null;
 r.hasWrapper = !!(parsed && parsed.app==='dapur-run' && parsed.state);
 r.backupTicked = parsed ? Object.keys(parsed.state.sel).length : -1;
 r.backupCustom = parsed ? parsed.state.custom.length : -1;

 // ---- device B: wipe this browser, then restore the file ----
 localStorage.removeItem('dapurRun.v1');
 location.hash='#restored';
 window.__backup = text;
 document.title="R|"+JSON.stringify(r)+"|SPLIT|"+text;
 }catch(e){document.title="R|"+JSON.stringify({error:String(e&&e.stack||e).slice(0,250)})}
},700)});
</script>"""
p1 = os.path.join(BASE, "_bk1.html")
open(p1, "w", encoding="utf-8").write(src.replace("</style>", "</style>" + PROBE, 1))
out = subprocess.run([CHROME, "--headless", "--disable-gpu", "--no-sandbox",
                      "--window-size=1200,900", "--virtual-time-budget=20000",
                      "--dump-dom", "file://" + p1], capture_output=True, text=True).stdout
m = re.search(r"<title>R\|(.*?)</title>", out, re.S)
raw = m.group(1).replace("&quot;", '"').replace("&amp;", "&")
head, _, backup = raw.partition("|SPLIT|")
res = json.loads(head)
print("device A:")
for k, v in res.items(): print("   %-16s %s" % (k, v))
open(os.path.join(BASE, "backup.json"), "w").write(backup)

# ---- device B: a fresh browser profile, restore the file ----
RESTORE = r"""
<script>
window.addEventListener("load",function(){setTimeout(async function(){
 try{
 var r={}, q=function(s,x){return (x||document).querySelector(s)};
 var wait=function(ms){return new Promise(res=>setTimeout(res,ms))};
 r.beforeTally=q('#tally').textContent;
 r.beforeItems=document.querySelectorAll('.item').length;
 var file=new File([__BACKUP__],'dapur-run-backup.json',{type:'application/json'});
 var dt=new DataTransfer(); dt.items.add(file);
 var fi=q('#backupfile'); fi.files=dt.files;
 window.confirm=function(){return true};
 fi.dispatchEvent(new Event('change',{bubbles:true}));
 await wait(600);
 var named=function(n){return [...document.querySelectorAll('.item')].find(e=>e.querySelector('.nm').textContent===n)};
 r.afterTally=q('#tally').textContent;
 r.afterItems=document.querySelectorAll('.item').length;
 var t=named('Tomato'); r.tomatoTicked=!!t&&t.classList.contains('on'); r.tomatoQty=t?t.querySelector('.q').value:'';
 var pt=named('Petai'); r.customBack=!!pt; r.customTicked=!!pt&&pt.classList.contains('on');
 r.store=q('#mstore').value;
 q('#makelist').click(); await wait(150); q('#tobought').click(); await wait(200);
 r.total=q('#boughtsum').textContent.trim();
 document.title="R|"+JSON.stringify(r);
 }catch(e){document.title="R|"+JSON.stringify({error:String(e&&e.stack||e).slice(0,250)})}
},700)});
</script>"""
p2 = os.path.join(BASE, "_bk2.html")
open(p2, "w", encoding="utf-8").write(
    src.replace("</style>", "</style>" + RESTORE.replace("__BACKUP__", json.dumps(backup)), 1))
out2 = subprocess.run([CHROME, "--headless", "--disable-gpu", "--no-sandbox",
                       "--window-size=1200,900", "--virtual-time-budget=20000",
                       "--dump-dom", "file://" + p2], capture_output=True, text=True).stdout
m2 = re.search(r"<title>R\|(.*?)</title>", out2, re.S)
print("device B (clean browser, restored from the file):")
for k, v in json.loads(m2.group(1).replace("&quot;", '"').replace("&amp;", "&")).items():
    print("   %-16s %s" % (k, v))
