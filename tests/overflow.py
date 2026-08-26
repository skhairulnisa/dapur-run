# -*- coding: utf-8 -*-
"""Every view must fit a 375px phone with no sideways scrolling."""
import json, os, re, subprocess
BASE = os.path.dirname(os.path.abspath(__file__))
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
src = open(os.path.join(BASE, "..", "index.html"), encoding="utf-8").read()
RECEIPT = """LOTUS'S STORES (M) SDN BHD
9556123456789 LOTUSS TOMATO 600G       4.69 S
BAWANG PUTIH -500G (PURE WHITE)
  1 X 4.99                             4.99 Z
LOBAK MERAH AUST/AUST CARROTS 1KG      5.20 Z
GARDENIA ORIGINAL CLASSIC JUMBO        4.30 Z
FARM FRESH MILK 2L                    16.70 S
TOTAL RM                              53.77
"""
PROBE = r"""
<script>
window.addEventListener("load",function(){setTimeout(async function(){
 var q=s=>document.querySelector(s), qa=s=>[...document.querySelectorAll(s)];
 var wait=ms=>new Promise(r=>setTimeout(r,ms));
 window.confirm=()=>true;
 var r={vw:innerWidth}, wide=function(tag){
   r[tag]=document.documentElement.scrollWidth;
   r[tag+"_who"]=qa('*').filter(function(e){
     var b=e.getBoundingClientRect();
     return b.right > innerWidth+1 && getComputedStyle(e).position!=='fixed'
            && !e.closest('[style*="overflow"], .rctable, .ttable, #listbody, #boughtbody, .shotov');
   }).slice(0,4).map(function(e){
     return (e.tagName+"."+(e.className||"")).slice(0,44)+"@"+Math.round(e.getBoundingClientRect().right);
   });
 };
 try{
  wide('edit');
  var ids=['vegetables-fresh-cooking-ingredients-tomato','dairy-chilled-breakfast-susu-fresh-milk',
           'vegetables-fresh-cooking-ingredients-bawang-putih','vegetables-fresh-cooking-ingredients-carrot',
           'rice-noodles-pasta-dry-food-roti-bread','chicken-meat-fish-seafood-telur-ayam'];
  ids.forEach(function(id){ var e=qa('.item').find(x=>x.dataset.id===id);
    e.querySelector('.cb').checked=true; e.querySelector('.cb').dispatchEvent(new Event('change',{bubbles:true})); });
  q('#makelist').click(); await wait(200); wide('list');
  q('#tobought').click(); await wait(200);
  var ta=q('#rctext'); ta.value=%R%; ta.dispatchEvent(new Event('input',{bubbles:true}));
  q('#rcscan').click(); await wait(250); wide('bought');
  q('#rcapply').click(); await wait(200);
  var cv=document.createElement('canvas'); cv.width=380; cv.height=620;
  var cx=cv.getContext('2d'); cx.fillStyle='#eee'; cx.fillRect(0,0,380,620);
  var blob=await new Promise(res=>cv.toBlob(res,'image/jpeg',0.8));
  var dt=new DataTransfer(); dt.items.add(new File([blob],'r.jpg',{type:'image/jpeg'}));
  q('#rcfile').files=dt.files; q('#rcfile').dispatchEvent(new Event('change',{bubbles:true}));
  for(var k=0;k<60 && q('#rcimg').hidden;k++) await wait(100);
  q('#savetrip').click(); await wait(700); wide('history');
  document.title="R|"+JSON.stringify(r);
 }catch(e){ document.title="R|"+JSON.stringify({error:String(e&&e.stack||e).slice(0,300)}); }
},900)});
</script>"""
PROBE = PROBE.replace("%R%", json.dumps(RECEIPT))
p = os.path.join(BASE, "_o.html")
open(p, "w", encoding="utf-8").write(src.replace("</style>", "</style>" + PROBE, 1))
# headless Chrome will not go below a 500px window, so run the page inside a 375px iframe
host = os.path.join(BASE, "_oh.html")
open(host, "w").write('<body style="margin:0">'
  '<iframe src="_o.html" style="width:375px;height:900px;border:0;display:block"></iframe>'
  '<script>window.addEventListener("load",function(){var n=0,t=setInterval(function(){'
  'var d=document.querySelector("iframe").contentDocument;'
  'if(d && /^R\\|/.test(d.title||"")){document.title=d.title;clearInterval(t);}'
  'if(++n>300)clearInterval(t);},200)});</script></body>')
out = subprocess.run([CHROME, "--headless", "--disable-gpu", "--no-sandbox", "--hide-scrollbars",
                      "--allow-file-access-from-files", "--window-size=900,900",
                      "--virtual-time-budget=60000",
                      "--dump-dom", "file://" + host], capture_output=True, text=True).stdout
m = re.search(r"<title>R\|(.*?)</title>", out, re.S)
if not m: print("NO RESULT"); raise SystemExit(1)
r = json.loads(m.group(1))
if "error" in r: print("PAGE ERROR:", r["error"]); raise SystemExit(1)
vw = r.pop("vw"); bad = 0
print("viewport", vw)
for k in ["edit", "list", "bought", "history"]:
    over = r[k] > vw
    if over: bad += 1
    print("  %-9s scrollWidth %4d  %s" % (k, r[k], "OVERFLOWS" if over else "ok"))
    if r.get(k + "_who"): print("      widest:", ", ".join(r[k + "_who"]))
raise SystemExit(1 if bad else 0)
