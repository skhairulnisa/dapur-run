# -*- coding: utf-8 -*-
import json, os, re, subprocess
BASE = os.path.dirname(os.path.abspath(__file__))
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
src = open(os.path.join(BASE, "..", "index.html"), encoding="utf-8").read()
PROBE = r"""
<script>
window.addEventListener("load",function(){setTimeout(async function(){
 try{
 var r={}, q=(s,x)=>(x||document).querySelector(s);
 var wait=ms=>new Promise(res=>setTimeout(res,ms));
 var named=n=>[...document.querySelectorAll('.item')].find(e=>e.querySelector('.nm').textContent===n);
 var type=(el,v)=>{el.value=v; el.dispatchEvent(new Event('input',{bubbles:true}));};

 // 1. a cleared estimate must stay cleared after a reload
 var tom=named('Tomato');
 r.seededValue = tom.querySelector('.eput').value;
 type(tom.querySelector('.eput'), '');
 await wait(400);
 var saved = JSON.parse(localStorage.getItem('dapurRun.v1'));
 r.clearedInStorage = saved.est[tom.dataset.id] === undefined;
 r.seededFlag = !!saved.seeded;

 // 2. the estimate column must lay out as a real table cell
 q('.box', named('Kentang')).click();
 q('.box', tom).click();
 q('#makelist').click(); await wait(250);
 var cells=[...document.querySelectorAll('#listbody td.est')];
 r.estCellCount = cells.length;
 r.estCellDisplay = cells.length ? getComputedStyle(cells[0]).display : 'none';
 var lefts = cells.map(c=>Math.round(c.getBoundingClientRect().left));
 r.estColumnAligned = new Set(lefts).size === 1;
 var hdr=[...document.querySelectorAll('#listbody thead th')].map(t=>t.textContent);
 r.headers = hdr.join('|');
 // every row must have the same number of cells as there are headers
 var rows=[...document.querySelectorAll('#listbody tbody tr:not(.grouprow)')];
 r.cellsPerRow = [...new Set(rows.map(t=>t.children.length))].join(',');
 r.cardFieldClass = named('Kentang').querySelector('.estfield') ? 'estfield' : 'MISSING';
 document.title="R|"+JSON.stringify(r);
 }catch(e){document.title="R|"+JSON.stringify({error:String(e&&e.stack||e).slice(0,220)})}
},700)});
</script>"""
p = os.path.join(BASE, "_fix.html")
open(p, "w", encoding="utf-8").write(src.replace("</style>", "</style>" + PROBE, 1))
out = subprocess.run([CHROME, "--headless", "--disable-gpu", "--no-sandbox",
                      "--window-size=1300,900", "--virtual-time-budget=15000",
                      "--dump-dom", "file://" + p], capture_output=True, text=True).stdout
m = re.search(r"<title>R\|(.*?)</title>", out, re.S)
for k, v in json.loads(m.group(1).replace("&quot;", '"').replace("&amp;", "&")).items():
    print("  %-18s %s" % (k, v))
