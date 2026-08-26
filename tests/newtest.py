# -*- coding: utf-8 -*-
"""Browser test for pack sizes, the receipt reader, past trips and the PDF."""
import base64, json, os, re, subprocess, sys
BASE = os.path.dirname(os.path.abspath(__file__))
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
src = open(os.path.join(BASE, "..", "index.html"), encoding="utf-8").read()

RECEIPT = r"""LOTUS'S STORES (M) SDN BHD
TAX INVOICE
9556123456789 LOTUSS TOMATO 600G       4.69 S
BAWANG PUTIH -500G (PURE WHITE)
  1 X 4.99                             4.99 Z
LOBAK MERAH AUST/AUST CARROTS 1KG      5.20 Z
GARDENIA ORIGINAL CLASSIC JUMBO        4.30 Z
FARM FRESH MILK 2L                    16.70 S
TELUR GRED B 10S                       7.90 Z
SOMETHING NOT ON MY LIST 250G          9.99 S
TOTAL RM                              53.77
CASH                                  60.00
CHANGE                                 6.23
"""

PROBE = r"""
<script>
window.addEventListener("load",function(){setTimeout(async function(){
 var r={}, q=function(s){return document.querySelector(s)}, qa=function(s){return [...document.querySelectorAll(s)]};
 var wait=function(ms){return new Promise(function(res){setTimeout(res,ms)})};
 try{
  // ---------- 1. the Size field ----------
  var tom = qa('.item').find(e=>e.dataset.id==='vegetables-fresh-cooking-ingredients-tomato');
  var milk = qa('.item').find(e=>e.dataset.id==='dairy-chilled-breakfast-susu-fresh-milk');
  var garlic = qa('.item').find(e=>e.dataset.id==='vegetables-fresh-cooking-ingredients-bawang-putih');
  var carrot = qa('.item').find(e=>e.dataset.id==='vegetables-fresh-cooking-ingredients-carrot');
  var bread = qa('.item').find(e=>e.dataset.id==='rice-noodles-pasta-dry-food-roti-bread');
  var eggs = qa('.item').find(e=>e.dataset.id==='chicken-meat-fish-seafood-telur-ayam');
  r.sizeFieldOnEveryCard = qa('.item').every(e=>!!e.querySelector('.wput'));
  r.sizeDefaultTomato = tom.querySelector('.wput').placeholder;
  r.sizeDefaultMilk = milk.querySelector('.wput').placeholder;
  r.sizeBoxStartsEmpty = tom.querySelector('.wput').value === '';

  // an override sticks
  var wp = garlic.querySelector('.wput');
  wp.value = '750 g'; wp.dispatchEvent(new Event('input',{bubbles:true}));
  r.sizeOverrideTicks = garlic.classList.contains('on') === false;   // typing a size must NOT tick

  // ---------- 2. tick a few things ----------
  [tom, milk, carrot, bread, eggs, garlic].forEach(function(el){
    el.querySelector('.cb').checked = true;
    el.querySelector('.cb').dispatchEvent(new Event('change',{bubbles:true}));
  });
  var qi = tom.querySelector('.q'); qi.value='2'; qi.dispatchEvent(new Event('input',{bubbles:true}));
  r.ticked = qa('.item.on').length;

  // ---------- 3. the shopping list ----------
  q('#makelist').click(); await wait(200);
  r.listHasSizeCol = !!q('#listbody th.sz');
  var rows = qa('#listbody tbody tr[data-id]');
  var tomRow = rows.find(t=>t.dataset.id==='vegetables-fresh-cooking-ingredients-tomato');
  r.listTomatoSize = tomRow.querySelector('td.sz').textContent;
  var garlicRow = rows.find(t=>t.dataset.id==='vegetables-fresh-cooking-ingredients-bawang-putih');
  r.listGarlicSize = garlicRow.querySelector('td.sz').textContent;   // the override
  r.weightLine = q('#estwt').textContent;
  r.estLine = q('#estsum').textContent;
  r.printBoxes = qa('#listbody .pbox').length;

  // ---------- 4. the receipt ----------
  q('#tobought').click(); await wait(150);
  r.hasReceiptPanel = !!q('#receipt');
  var ta = q('#rctext'); ta.value = %RECEIPT%; ta.dispatchEvent(new Event('input',{bubbles:true}));
  q('#rcscan').click(); await wait(150);
  var mrows = qa('#rcmatch tbody tr');
  r.linesRead = mrows.length;
  r.matches = mrows.map(function(t){
    var s=t.querySelector('.rcsel');
    return [t.querySelector('.rcline').textContent,
            s.value ? s.options[s.selectedIndex].textContent : '(skip)',
            t.querySelector('.rcprice').value,
            t.querySelector('.rcuse').checked,
            t.querySelector('.rcsure').textContent];
  });
  q('#rcapply').click(); await wait(200);
  var brows = qa('#boughtbody tbody tr[data-id]');
  r.pricesFilled = brows.filter(t=>t.querySelector('.pinput').value).length;
  r.tomatoPaid = brows.find(t=>t.dataset.id==='vegetables-fresh-cooking-ingredients-tomato').querySelector('.pinput').value;
  r.garlicPaid = brows.find(t=>t.dataset.id==='vegetables-fresh-cooking-ingredients-bawang-putih').querySelector('.pinput').value;
  r.boughtTotal = q('#boughtsum').textContent;

  // ---------- 5. a receipt photo ----------
  var cv=document.createElement('canvas'); cv.width=420; cv.height=760;
  var cx=cv.getContext('2d'); cx.fillStyle='#fff'; cx.fillRect(0,0,420,760);
  cx.fillStyle='#111'; cx.font='20px monospace'; cx.fillText('LOTUSS RECEIPT',20,40);
  cx.fillText('TOMATO 600G   4.69',20,80);
  try{
    var blob = await new Promise(function(res){ cv.toBlob(res,'image/jpeg',0.8); });
    r.blobSize = blob ? blob.size : 0;
    var dt = new DataTransfer(); dt.items.add(new File([blob],'r.jpg',{type:'image/jpeg'}));
    q('#rcfile').files = dt.files;
    r.fileSet = q('#rcfile').files.length;
    q('#rcfile').dispatchEvent(new Event('change',{bubbles:true}));
    for(var k=0;k<60 && q('#rcimg').hidden;k++) await wait(100);
  }catch(e){ r.photoErr = String(e).slice(0,160); }
  r.photoShown = !q('#rcimg').hidden;
  r.photoSrcLen = (q('#rcimg').getAttribute('src')||'').length;
  r.toast = q('#toast').textContent;
  try{ localStorage.setItem('__t','1'); r.lsOk = localStorage.getItem('__t')==='1'; localStorage.removeItem('__t'); }
  catch(e){ r.lsOk = 'throws: '+String(e).slice(0,60); }
  try{ r.lsBytes = (localStorage.getItem('dapurRun.v1')||'').length; }catch(e){ r.lsBytes='n/a'; }

  // ---------- 6. finish the trip ----------
  window.confirm = function(){ return true; };
  q('#savetrip').click(); await wait(600);
  r.viewIsHistory = !q('#histview').hidden;
  r.tripCount = qa('#histbody .trip').length;
  r.tripSummary = q('#histbody .trip summary').textContent;
  r.tripRows = qa('#histbody .trip tbody tr').length;
  r.tripHasReceipt = !!q('#histbody .rcthumb');
  r.listClearedAfterSave = qa('.item.on').length;

  // ---------- 7. put the trip back ----------
  q('#histbody .trip [data-act="repeat"]').click(); await wait(400);
  r.repeatTicked = qa('.item.on').length;
  r.repeatKeptQty = qa('.item').find(e=>e.dataset.id==='vegetables-fresh-cooking-ingredients-tomato').querySelector('.q').value;
  r.repeatClearedPrices = qa('#boughtbody .pinput').filter(i=>i.value).length;

  // ---------- 8. the PDF ----------
  var cap=null; URL.createObjectURL=function(b){cap=b;return "blob:x";};
  q('#listview .js-pdf').click();
  for(var t=0;t<120 && !cap;t++) await wait(100);
  r.pdfBuilt=!!cap; r.pdfBytes=cap?cap.size:0;
  if(cap){
    var buf = await cap.arrayBuffer();
    var bin='', u8=new Uint8Array(buf);
    for(var i=0;i<u8.length;i++) bin += String.fromCharCode(u8[i]);
    document.getElementById('pdfout').textContent = btoa(bin);
  }
  document.title="R|"+JSON.stringify(r);
 }catch(e){ document.title="R|"+JSON.stringify({error:String(e&&e.stack||e).slice(0,400)}); }
},900)});
</script>
<div id="pdfout" style="display:none"></div>"""

PROBE = PROBE.replace("%RECEIPT%", json.dumps(RECEIPT))
p = os.path.join(BASE, "_n.html")
open(p, "w", encoding="utf-8").write(src.replace("</style>", "</style>" + PROBE, 1))
out = subprocess.run([CHROME, "--headless", "--disable-gpu", "--no-sandbox",
                      "--window-size=1200,900", "--virtual-time-budget=60000",
                      "--dump-dom", "file://" + p], capture_output=True, text=True).stdout
m = re.search(r"<title>R\|(.*?)</title>", out, re.S)
if not m:
    print("NO RESULT"); print(out[:2000]); raise SystemExit(1)
r = json.loads(m.group(1))
if "error" in r:
    print("PAGE ERROR:\n" + r["error"]); raise SystemExit(1)
for k in r:
    if k != "matches":
        print("%-24s %s" % (k, r[k]))
print("\nreceipt matches:")
for row in r.get("matches", []):
    print("   %-38s -> %-26s %8s  use=%-5s %s" % (row[0][:38], row[1][:26], row[2], row[3], row[4]))

mp = re.search(r'<div id="pdfout"[^>]*>([A-Za-z0-9+/=]+)</div>', out)
if mp:
    pdf = base64.b64decode(mp.group(1))
    open(os.path.join(BASE, "_n.pdf"), "wb").write(pdf)
    try:
        from pypdf import PdfReader
        rd = PdfReader(os.path.join(BASE, "_n.pdf"))
        print("\nPDF pages:", len(rd.pages))
        for i, pg in enumerate(rd.pages):
            t = " ".join((pg.extract_text() or "").split())
            print("  p%d: %s" % (i + 1, t[:200]))
    except Exception as e:
        print("pdf read failed:", e)
