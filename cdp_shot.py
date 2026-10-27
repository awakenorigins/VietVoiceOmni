# -*- coding: utf-8 -*-
"""Click tab qua CDP roi chup. Dung websocket-client."""
import json, base64, sys, time
import urllib.request
try:
    from websocket import create_connection
except Exception:
    print("NO websocket-client"); sys.exit(2)

tab_text = sys.argv[1] if len(sys.argv) > 1 else "Podcast"
out = sys.argv[2] if len(sys.argv) > 2 else "shot.png"

tabs = json.load(urllib.request.urlopen("http://localhost:9333/json"))
page = [t for t in tabs if t["type"] == "page"][0]
ws = create_connection(page["webSocketDebuggerUrl"], timeout=30)
_id = 0
def cmd(method, params=None):
    global _id; _id += 1
    ws.send(json.dumps({"id": _id, "method": method, "params": params or {}}))
    while True:
        m = json.loads(ws.recv())
        if m.get("id") == _id:
            return m

cmd("Page.enable"); cmd("Runtime.enable")
# click vao phan tu chua chu tab_text trong sidebar
js = f"""
(() => {{
  const els = [...document.querySelectorAll('*')].filter(e =>
    e.children.length <= 3 && e.textContent && e.textContent.trim().includes({json.dumps(tab_text)}));
  // chon phan tu nho nhat (sat text)
  els.sort((a,b)=>a.textContent.length-b.textContent.length);
  for (const el of els) {{
    const r = el.getBoundingClientRect();
    if (r.width>0 && r.height>0 && r.left<300) {{ el.click(); return 'clicked '+el.tagName; }}
  }}
  return 'notfound';
}})()
"""
r = cmd("Runtime.evaluate", {"expression": js, "returnByValue": True})
print("click:", r.get("result", {}).get("result", {}).get("value"))
time.sleep(2.5)
shot = cmd("Page.captureScreenshot", {"format": "png"})
data = shot["result"]["data"]
with open(out, "wb") as f:
    f.write(base64.b64decode(data))
print("saved", out)
ws.close()
