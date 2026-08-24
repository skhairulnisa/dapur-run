# -*- coding: utf-8 -*-
import json, os, re, subprocess
BASE = os.path.dirname(os.path.abspath(__file__))
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
src = open(os.path.join(BASE, "..", "index.html"), encoding="utf-8").read()
PROBE = r"""
<script>
window.addEventListener("load",function(){setTimeout(async function(){
 try{
 var r={}, q=function(s){return document.querySelector(s)};
 // add an item for real
 var f=q('.additem[data-key="meat"]'), i=f.querySelector('input');
 i.value='Ikan kembung'; f.dispatchEvent(new Event('submit',{bubbles:true,cancelable:true}));
 await new Promise(res=>setTimeout(res,250));
 var mine=[...document.querySelectorAll('.item')].find(e=>e.querySelector('.nm').textContent==='Ikan kembung');
 r.added=!!mine;
 r.tileIsRealJpeg = mine && /^data:image\/jpeg/.test(mine.querySelector('.thumb').src);
 r.tileHasLetter = mine && mine.querySelector('.thumb').src.length > 900;   // canvas-drawn, not the tiny fallback
 r.ticked = mine && mine.classList.contains('on');
 r.count = document.querySelectorAll('.item').length;
 // quantity clear
 var first=document.querySelector('.item');
 var qi=first.querySelector('.q');
 qi.value='3'; qi.dispatchEvent(new Event('input',{bubbles:true}));
 r.qTicks = first.classList.contains('on');
 qi.value=''; qi.dispatchEvent(new Event('input',{bubbles:true}));
 r.qClearUnticks = !first.classList.contains('on');
 // it reaches the PDF
 q('#makelist').click();
 await new Promise(res=>setTimeout(res,200));
 var cap=null; URL.createObjectURL=function(b){cap=b;return "blob:x";};
 document.querySelector('.js-pdf').click();
 for(var t=0;t<90 && !cap;t++) await new Promise(res=>setTimeout(res,100));
 r.pdfBuilt = !!cap; r.pdfBytes = cap?cap.size:0;
 document.title="R|"+JSON.stringify(r);
 }catch(e){ document.title="R|"+JSON.stringify({error:String(e&&e.stack||e).slice(0,220)}); }
},700)});
</script>"""
p = os.path.join(BASE, "_b.html")
open(p, "w", encoding="utf-8").write(src.replace("</style>", "</style>" + PROBE, 1))
out = subprocess.run([CHROME, "--headless", "--disable-gpu", "--no-sandbox",
                      "--window-size=1200,900", "--virtual-time-budget=25000",
                      "--dump-dom", "file://" + p], capture_output=True, text=True).stdout
m = re.search(r"<title>R\|(.*?)</title>", out, re.S)
if not m: print("NO RESULT"); raise SystemExit(1)
for k, v in json.loads(m.group(1).replace("&quot;", '"')).items():
    print("  %-18s %s" % (k, v))
