# -*- coding: utf-8 -*-
import json, os, re, subprocess
BASE = os.path.dirname(os.path.abspath(__file__))
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
src = open(os.path.join(BASE, "..", "index.html"), encoding="utf-8").read()
PROBE = r"""
<script>
window.addEventListener("load",function(){setTimeout(async function(){
 try{
 var r={}, q=function(s,x){return (x||document).querySelector(s)};
 var wait=ms=>new Promise(res=>setTimeout(res,ms));
 var named=n=>[...document.querySelectorAll('.item')].find(e=>e.querySelector('.nm').textContent===n);
 var type=(el,v)=>{el.value=v; el.dispatchEvent(new Event('input',{bubbles:true}));};

 r.seeded = Object.keys(JSON.parse(localStorage.getItem('dapurRun.v1')||'{}').est||{}).length;
 var kentang=named('Kentang');
 r.kentangEst = kentang.querySelector('.eput').value;
 r.kentangNote = (kentang.querySelector('.srcnote')||{}).textContent || '';

 // tick two known-priced items
 q('.box',kentang).click();
 var tomato=named('Tomato'); q('.box',tomato).click();
 await wait(120);
 r.dockAfter2 = q('#estline').textContent;

 // quantity multiplies the estimate
 type(kentang.querySelector('.q'),'3');
 await wait(120);
 r.dockQty3 = q('#estline').textContent;

 // editing an estimate is respected
 type(kentang.querySelector('.eput'),'5.00');
 await wait(120);
 r.dockEdited = q('#estline').textContent;

 // an unpriced item is reported, not silently ignored
 var bilis=named('Ikan bilis'); r.bilisEstBlank = bilis.querySelector('.eput').value === '';
 q('.box',bilis).click(); await wait(120);
 r.dockWithUnpriced = q('#estline').textContent;

 q('#makelist').click(); await wait(200);
 r.listEstSum = q('#estsum').textContent; r.listEstNote = q('#estnote').textContent;
 r.listEstCells = [...document.querySelectorAll('#listbody td.est')].map(c=>c.textContent).join(' | ');

 q('#tobought').click(); await wait(200);
 var p=[...document.querySelectorAll('#boughtbody .pinput')];
 type(p[0],'18.00');                       // paid more than the 15.00 estimate
 await wait(200);
 r.boughtEst = q('#bestsum').textContent;
 r.boughtDiff = q('#bestdiff').textContent;
 r.boughtDiffLab = q('#bestdifflab').textContent;
 r.boughtTotal = q('#boughtsum').textContent;
 document.title="R|"+JSON.stringify(r);
 }catch(e){document.title="R|"+JSON.stringify({error:String(e&&e.stack||e).slice(0,250)})}
},800)});
</script>"""
p = os.path.join(BASE, "_est.html")
open(p, "w", encoding="utf-8").write(src.replace("</style>", "</style>" + PROBE, 1))
out = subprocess.run([CHROME, "--headless", "--disable-gpu", "--no-sandbox",
                      "--window-size=1300,900", "--virtual-time-budget=20000",
                      "--dump-dom", "file://" + p], capture_output=True, text=True).stdout
m = re.search(r"<title>R\|(.*?)</title>", out, re.S)
for k, v in json.loads(m.group(1).replace("&quot;", '"').replace("&amp;", "&")).items():
    print("  %-17s %s" % (k, v))
