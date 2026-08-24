import os, re, subprocess
from PIL import Image
BASE = os.path.dirname(os.path.abspath(__file__))
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
src = open(os.path.join(BASE, "..", "index.html"), encoding="utf-8").read()
# collapse everything except one category so the add box is visible without a long scroll
seed = ('<script>try{localStorage.setItem("dapurRun.v1",JSON.stringify({collapsed:{'
        + ",".join('"%s":1' % k for k in ["veg","meat","frozen","dry","sauce","dairy","bveg","bprot",
                                          "bfruit","bcarb","bdairy","house","care","bcare"])
        + '}}))}catch(e){}</script>')
p = os.path.join(BASE, "_p.html")
open(p, "w", encoding="utf-8").write(src.replace('<header class="masthead">', seed + '\n<header class="masthead">', 1))
host = os.path.join(BASE, "_ph.html")
open(host, "w").write('<body style="margin:0;background:#c9d2cb">'
  '<iframe src="_p.html" style="width:390px;height:2800px;border:0;display:block"></iframe>'
  '<script>window.addEventListener("load",function(){setTimeout(function(){'
  'var d=document.querySelector("iframe").contentDocument.documentElement;'
  'document.title="R|vw="+d.clientWidth+"|sw="+d.scrollWidth;},1200)});</script></body>')
out = os.path.join(BASE, "phone.png")
subprocess.run([CHROME, "--headless", "--disable-gpu", "--no-sandbox", "--allow-file-access-from-files",
                "--hide-scrollbars", "--window-size=390,2800", "--virtual-time-budget=9000",
                "--screenshot=" + out, "file://" + host], capture_output=True)
d = subprocess.run([CHROME, "--headless", "--disable-gpu", "--no-sandbox", "--allow-file-access-from-files",
                    "--window-size=390,2800", "--virtual-time-budget=9000", "--dump-dom", "file://" + host],
                   capture_output=True, text=True).stdout
print(re.search(r"<title>(R\|[^<]*)</title>", d).group(1))
im = Image.open(out)
im.crop((0, 1560, im.size[0], 2500)).save(os.path.join(BASE, "phone-add.png"))
print("full", im.size)
