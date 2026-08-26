import base64, json, os, re, subprocess
BASE = os.path.dirname(os.path.abspath(__file__))
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
src = open(os.path.join(BASE, "..", "index.html"), encoding="utf-8").read()
PROBE = r"""
<script>
window.addEventListener("load",function(){setTimeout(async function(){
 var q=s=>document.querySelector(s), qa=s=>[...document.querySelectorAll(s)];
 var wait=ms=>new Promise(r=>setTimeout(r,ms));
 window.confirm=()=>true; var r={};
 try{
  q('#selall').click(); await wait(400);
  r.ticked=qa('.item.on').length;
  q('#makelist').click(); await wait(400);
  // pay for every third item so the bought page appears
  q('#tobought').click(); await wait(300);
  var ins=qa('#boughtbody .pinput');
  ins.forEach(function(i,n){ if(n%3===0){ i.value=(2+n%7)+'.50'; i.dispatchEvent(new Event('input',{bubbles:true})); } });
  await wait(300);
  // save three trips
  for(var t=0;t<3;t++){ q('#savetrip').click(); await wait(500);
    if(t<2){ q('#histback').click(); await wait(200);
      q('#selall').click(); await wait(400); q('#makelist').click(); await wait(300);
      q('#tobought').click(); await wait(300);
      var i2=qa('#boughtbody .pinput'); i2.forEach(function(i,n){ if(n%4===0){ i.value='3.20'; i.dispatchEvent(new Event('input',{bubbles:true})); } });
      await wait(300); } }
  r.trips=qa('#histbody .trip').length;
  var cap=null; URL.createObjectURL=function(b){cap=b;return "blob:x";};
  q('#histback').click(); await wait(200);
  q('#selall').click(); await wait(400);
  q('#makelist').click(); await wait(400);
  r.reticked=qa('.item.on').length;
  q('#listview .js-pdf').click();
  for(var k=0;k<200 && !cap;k++) await wait(100);
  r.pdfBytes=cap?cap.size:0;
  if(cap){ var buf=await cap.arrayBuffer(), u8=new Uint8Array(buf), bin='';
    for(var i=0;i<u8.length;i++) bin+=String.fromCharCode(u8[i]);
    document.getElementById('pdfout').textContent=btoa(bin); }
  document.title="R|"+JSON.stringify(r);
 }catch(e){ document.title="R|"+JSON.stringify({error:String(e&&e.stack||e).slice(0,300)}); }
},900)});
</script><div id="pdfout" style="display:none"></div>"""
p = os.path.join(BASE, "_st2.html")
open(p, "w", encoding="utf-8").write(src.replace("</style>", "</style>" + PROBE, 1))
out = subprocess.run([CHROME, "--headless", "--disable-gpu", "--no-sandbox",
                      "--window-size=1200,900", "--virtual-time-budget=120000",
                      "--dump-dom", "file://" + p], capture_output=True, text=True).stdout
m = re.search(r"<title>R\|(.*?)</title>", out, re.S)
r = json.loads(m.group(1))
print(r if "error" in r else json.dumps(r))
mp = re.search(r'<div id="pdfout"[^>]*>([A-Za-z0-9+/=]+)</div>', out)
if mp:
    open(os.path.join(BASE, "_st2.pdf"), "wb").write(base64.b64decode(mp.group(1)))
    from pypdf import PdfReader
    rd = PdfReader(os.path.join(BASE, "_st2.pdf"))
    print("pages:", len(rd.pages))
    names, blank = set(), 0
    for pg in rd.pages:
        t = " ".join((pg.extract_text() or "").split())
        if not t: blank += 1
        for n in ["Bawang putih", "Susu fresh milk", "Baby diapers", "Hair oil / serum"]:
            if n in t: names.add(n)
    print("blank pages:", blank, "| landmark items found:", sorted(names))
    heads = [" ".join((pg.extract_text() or "").split())[:60] for pg in rd.pages[:4]]
    for i, h in enumerate(heads): print("  p%d %s" % (i+1, h))
