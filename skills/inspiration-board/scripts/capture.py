#!/usr/bin/env python3
"""Turn a link into an image file: download direct images, pull og:image from
image-hosting pages, otherwise scroll the page in headless Chrome and save
up to MAX_SCREENS viewport screenshots (one per screen)
(Chrome DevTools Protocol over a tiny stdlib websocket client - no installs).

CLI:  capture.py <url> <out_path_without_ext>
Prints JSON: {"ok": true, "path": "<first>", "paths": [...], "method": "..."} or
             {"ok": false, "blocked": true/false, "error": "..."}
Python 3.9 compatible, stdlib only.
"""
import base64
import hashlib
import json
import os
import random
import re
import shutil
import socket
import struct
import subprocess
import sys
import tempfile
import time
import urllib.parse
import urllib.request

CHROME_CANDIDATES = (
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
)
CHROME_NAMES = ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "microsoft-edge")


def find_chrome():
    """Chrome (or Chromium / Edge) on macOS, Linux or Windows. CHROME_PATH overrides."""
    env = os.environ.get("CHROME_PATH")
    if env and os.path.exists(env):
        return env
    for c in CHROME_CANDIDATES:
        if os.path.exists(c):
            return c
    for name in CHROME_NAMES:
        found = shutil.which(name)
        if found:
            return found
    return None


UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36")
WIDTH = 1440
VIEW_H = 900
MAX_SCREENS = 8   # 1440x900 screens per website
SETTLE = 1.3      # seconds after each scroll step (smooth scroll, reveal animations)
# Pages that are wrappers around one image - take og:image instead of a screenshot.
IMAGE_HOSTS = ("pinterest.", "pin.it", "dribbble.com/shots", "behance.net/gallery",
               "savee.it", "cosmos.so", "are.na/block", "unsplash.com/photos")
IMG_EXT = {"image/png": ".png", "image/jpeg": ".jpg", "image/webp": ".webp",
           "image/gif": ".gif", "image/avif": ".avif"}
BLOCK_MARKERS = ("just a moment", "access denied", "attention required",
                 "verify you are human", "are you a robot", "403 forbidden",
                 "captcha")


def _get(url, timeout=20):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
    return urllib.request.urlopen(req, timeout=timeout)


def try_direct_image(url, out_base):
    try:
        with _get(url) as r:
            ctype = (r.headers.get("Content-Type") or "").split(";")[0].strip().lower()
            if ctype not in IMG_EXT:
                return None, ctype
            path = out_base + IMG_EXT[ctype]
            with open(path, "wb") as f:
                shutil.copyfileobj(r, f)
            return path, ctype
    except Exception:
        return None, ""


def try_og_image(url, out_base):
    try:
        with _get(url) as r:
            html = r.read(800000).decode("utf-8", "ignore")
    except Exception:
        return None
    m = (re.search(r'<meta[^>]+property=["\']og:image(?::url)?["\'][^>]+content=["\']([^"\']+)', html)
         or re.search(r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+property=["\']og:image', html))
    if not m:
        return None
    img_url = urllib.parse.urljoin(url, m.group(1).replace("&amp;", "&"))
    path, _ = try_direct_image(img_url, out_base)
    return path


# ---------- minimal websocket client (RFC 6455, client side) ----------
class WS:
    def __init__(self, ws_url):
        u = urllib.parse.urlparse(ws_url)
        self.sock = socket.create_connection((u.hostname, u.port), timeout=60)
        key = base64.b64encode(os.urandom(16)).decode()
        req = ("GET %s HTTP/1.1\r\nHost: %s:%d\r\nUpgrade: websocket\r\n"
               "Connection: Upgrade\r\nSec-WebSocket-Key: %s\r\n"
               "Sec-WebSocket-Version: 13\r\n\r\n") % (u.path, u.hostname, u.port, key)
        self.sock.sendall(req.encode())
        resp = b""
        while b"\r\n\r\n" not in resp:
            chunk = self.sock.recv(4096)
            if not chunk:
                raise RuntimeError("websocket handshake failed")
            resp += chunk
        self.buf = resp.split(b"\r\n\r\n", 1)[1]
        self.next_id = 0
        self.events = []

    def _recv_exact(self, n):
        while len(self.buf) < n:
            chunk = self.sock.recv(1 << 20)
            if not chunk:
                raise RuntimeError("websocket closed")
            self.buf += chunk
        out, self.buf = self.buf[:n], self.buf[n:]
        return out

    def _recv_msg(self):
        data = b""
        while True:
            b1, b2 = self._recv_exact(2)
            fin, op, ln = b1 & 0x80, b1 & 0x0F, b2 & 0x7F
            if ln == 126:
                ln = struct.unpack(">H", self._recv_exact(2))[0]
            elif ln == 127:
                ln = struct.unpack(">Q", self._recv_exact(8))[0]
            payload = self._recv_exact(ln)
            if op == 8:
                raise RuntimeError("websocket closed by peer")
            if op in (0, 1, 2):
                data += payload
                if fin:
                    return json.loads(data.decode("utf-8"))

    def send(self, method, params=None, timeout=60):
        self.next_id += 1
        mid = self.next_id
        msg = json.dumps({"id": mid, "method": method, "params": params or {}}).encode()
        mask = os.urandom(4)
        hdr = bytearray([0x81])
        n = len(msg)
        if n < 126:
            hdr.append(0x80 | n)
        elif n < 65536:
            hdr.append(0x80 | 126)
            hdr += struct.pack(">H", n)
        else:
            hdr.append(0x80 | 127)
            hdr += struct.pack(">Q", n)
        masked = bytes(b ^ mask[i % 4] for i, b in enumerate(msg))
        self.sock.sendall(bytes(hdr) + mask + masked)
        deadline = time.time() + timeout
        while time.time() < deadline:
            m = self._recv_msg()
            if m.get("id") == mid:
                if "error" in m:
                    raise RuntimeError(m["error"].get("message", "cdp error"))
                return m.get("result", {})
            self.events.append(m)
        raise RuntimeError("timeout waiting for " + method)

    def wait_event(self, name, timeout):
        deadline = time.time() + timeout
        for i, e in enumerate(self.events):
            if e.get("method") == name:
                self.events.pop(i)
                return True
        self.sock.settimeout(1)
        try:
            while time.time() < deadline:
                try:
                    m = self._recv_msg()
                except socket.timeout:
                    continue
                if m.get("method") == name:
                    return True
                self.events.append(m)
        finally:
            self.sock.settimeout(60)
        return False

    def eval(self, expr, timeout=60):
        r = self.send("Runtime.evaluate", {"expression": expr, "awaitPromise": True,
                                            "returnByValue": True}, timeout)
        return r.get("result", {}).get("value")


DISMISS_JS = r"""
(() => {
  const re = /^(accept( all)?( cookies)?|allow( all)?( cookies)?|agree|i agree|got it|ok(ay)?|akceptuj(ę)?( wszystkie)?|zaakceptuj( wszystkie)?|zgadzam się|rozumiem|alle akzeptieren|tout accepter)$/i;
  let n = 0;
  for (const el of document.querySelectorAll('button, a[role=button], [role=button], input[type=button]')) {
    const t = (el.innerText || el.value || '').trim();
    if (t.length < 40 && re.test(t)) { try { el.click(); n++; } catch (e) {} }
  }
  return n;
})()
"""

STATE_JS = ("JSON.stringify([Math.round(window.scrollY), "
            "Math.max(document.documentElement.scrollHeight, document.body ? document.body.scrollHeight : 0), "
            "window.innerHeight])")


def screens(url, out_base):
    """Scroll the page like a person and grab one 1440x900 screen per step.

    Why not one full-page image: stretching the viewport to the page height
    breaks sections sized in vh (a 100vh hero becomes thousands of px tall)
    and reveal-on-scroll content never fires, so long screenshots came out
    as huge, mostly empty "wagons". Wheel events also move pages with
    smooth-scroll libraries that ignore window.scrollTo.
    Returns (paths, blocked, error).
    """
    chrome = find_chrome()
    if not chrome:
        return None, False, "Google Chrome not found (install it or set CHROME_PATH)"
    port = random.randint(20000, 40000)
    profile = tempfile.mkdtemp(prefix="insp-chrome-")
    proc = subprocess.Popen(
        [chrome, "--headless=new", "--remote-debugging-port=%d" % port,
         "--user-data-dir=" + profile, "--hide-scrollbars", "--no-first-run",
         "--no-default-browser-check", "--window-size=%d,%d" % (WIDTH, VIEW_H),
         "--user-agent=" + UA, "about:blank"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    paths = []
    try:
        ws_url = None
        for _ in range(60):
            try:
                with urllib.request.urlopen("http://127.0.0.1:%d/json" % port, timeout=2) as r:
                    targets = json.loads(r.read())
                pages = [t for t in targets if t.get("type") == "page"]
                if pages:
                    ws_url = pages[0]["webSocketDebuggerUrl"]
                    break
            except Exception:
                pass
            time.sleep(0.25)
        if not ws_url:
            return None, False, "headless Chrome did not start"
        ws = WS(ws_url)
        ws.send("Page.enable")
        ws.send("Emulation.setDeviceMetricsOverride",
                {"width": WIDTH, "height": VIEW_H, "deviceScaleFactor": 1, "mobile": False})
        ws.send("Page.navigate", {"url": url})
        ws.wait_event("Page.loadEventFired", 30)
        time.sleep(2.0)  # intro animations, lazy fonts
        ws.eval(DISMISS_JS)
        time.sleep(0.8)
        title = (ws.eval("document.title") or "").lower()
        text = (ws.eval("(document.body && document.body.innerText || '').slice(0, 600)") or "").lower()
        if any(m in title for m in BLOCK_MARKERS) or (len(text) < 400 and any(m in text for m in BLOCK_MARKERS)):
            return None, True, "page blocks automated browsers (%s)" % (title or "no title")
        prev_hash = None
        for i in range(MAX_SCREENS):
            shot = ws.send("Page.captureScreenshot", {"format": "jpeg", "quality": 85}, 60)
            data = base64.b64decode(shot["data"])
            digest = hashlib.md5(data).hexdigest()
            if digest == prev_hash:  # nothing moved - end of page
                break
            prev_hash = digest
            path = "%s-%d.jpg" % (out_base, i + 1)
            with open(path, "wb") as f:
                f.write(data)
            paths.append(path)
            y0, doc_h, view_h = json.loads(ws.eval(STATE_JS) or "[0,0,0]")
            ws.send("Input.dispatchMouseEvent", {"type": "mouseWheel", "x": WIDTH // 2, "y": VIEW_H // 2,
                                                 "deltaX": 0, "deltaY": VIEW_H})
            time.sleep(SETTLE)
            y1, doc_h, view_h = json.loads(ws.eval(STATE_JS) or "[0,0,0]")
            native = doc_h > view_h + 10
            if native and y1 <= y0:  # native scroll reached the bottom
                break
        return paths, False, None
    except Exception as e:  # noqa: BLE001 - report any failure to the caller
        return (paths or None), False, (None if paths else str(e))
    finally:
        proc.terminate()
        try:
            proc.wait(5)
        except Exception:
            proc.kill()
        shutil.rmtree(profile, ignore_errors=True)


def capture(url, out_base):
    os.makedirs(os.path.dirname(out_base) or ".", exist_ok=True)
    path, ctype = try_direct_image(url, out_base)
    if path:
        return {"ok": True, "path": path, "paths": [path], "method": "image"}
    if any(h in url for h in IMAGE_HOSTS):
        path = try_og_image(url, out_base)
        if path:
            return {"ok": True, "path": path, "paths": [path], "method": "og:image"}
    paths, blocked, err = screens(url, out_base)
    if paths:
        return {"ok": True, "path": paths[0], "paths": paths, "method": "screens"}
    return {"ok": False, "blocked": blocked, "error": err}


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("usage: capture.py <url> <out_path_without_ext>", file=sys.stderr)
        sys.exit(2)
    print(json.dumps(capture(sys.argv[1], sys.argv[2])))
