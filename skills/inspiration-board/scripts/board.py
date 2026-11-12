#!/usr/bin/env python3
"""Inspiration boards: one permanent board per topic. Stdlib only, Python 3.9+
(Pillow is optional here and only used for image sizes).

Layout:
  <inspirations>/Open board.command   double-click launcher (macOS)
  <inspirations>/<topic-slug>/board.json        single source of truth
  <inspirations>/<topic-slug>/inspirations.md   generated from board.json
  <inspirations>/<topic-slug>/images/

Commands (all print JSON unless noted):
  where     [--cwd DIR]                     where the inspirations folder for this place is
  config    --library DIR                   remember the folder for topics outside projects
  topics    <inspirations>                  list topics with counts
  find      <inspirations> <name>           match a topic typed in chat
  init      <inspirations> --topic T [--language pl]   create a topic (+ launcher file)
  add       <topic_dir> <url_or_file> [...] [--frames]
  recapture <topic_dir> <item_id> [...]
  status    <topic_dir>                     items, rounds, waiting pins
  round     <topic_dir> <payload.json>      apply an analysis round, regenerate markdown
  render    <topic_dir>                     regenerate inspirations.md
  serve     <topic_dir>                     board for an agent session; exits on "Done"
  open      <inspirations>                  board without the agent; exits when the tab closes
"""
import argparse
import json
import os
import re
import shutil
import socket
import stat
import subprocess
import sys
import threading
import time
import urllib.parse
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HERE = os.path.dirname(os.path.abspath(__file__))
BOARD_HTML = os.path.join(HERE, "..", "assets", "board.html")
FONTS_DIR = os.path.join(HERE, "..", "assets", "fonts")  # Poppins + Mona Sans, SIL Open Font License
sys.path.insert(0, HERE)
import capture  # noqa: E402
import model  # noqa: E402

LOCK = threading.Lock()
BROWSER_UNFRIENDLY = (".heic", ".heif", ".tif", ".tiff")
CONFIG = os.path.join(os.path.expanduser("~"), ".config", "inspiration-board", "config.json")
LAUNCHER = "Open board.command"
IDLE_SECONDS = 60      # standalone server stops this long after the last open tab
START_GRACE = 180      # ...or this long after start if no tab ever connected
CTYPES = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".webp": "image/webp",
          ".gif": "image/gif", ".avif": "image/avif"}


def out(data):
    print(json.dumps(data, ensure_ascii=False, indent=2))


# ---------------- images ----------------
def image_size(path):
    try:
        from PIL import Image
        with Image.open(path) as im:
            return im.size
    except Exception:  # noqa: BLE001 - Pillow missing or unreadable image
        return (0, 0)


def _base(d, board, source):
    n = model.item_number(model.next_item_id(board))
    u = urllib.parse.urlparse(source)
    return os.path.join(d, "images", "%02d-%s" % (n, model.slugify(u.netloc.replace("www.", "") + u.path, 40)))


def add_url(d, board, url):
    res = capture.capture(url, _base(d, board, url))
    if not res["ok"]:
        res["url"] = url
        return res
    frames = [os.path.relpath(p, d) for p in res["paths"]]
    w, h = image_size(os.path.join(d, frames[0]))
    item = model.add_item(board, url, frames, w, h)
    return {"ok": True, "url": url, "id": item["id"], "method": res["method"], "frames": len(frames)}


def add_files(d, board, paths, source=None):
    """Several local files -> one item (one frame per file)."""
    n = model.item_number(model.next_item_id(board))
    rels = []
    for k, path in enumerate(paths, 1):
        name, ext = os.path.splitext(os.path.basename(path))
        ext = ext.lower() or ".png"
        suffix = "-%d" % k if len(paths) > 1 else ""
        if ext in BROWSER_UNFRIENDLY:  # browsers cannot show HEIC/TIFF
            if sys.platform != "darwin":
                return {"ok": False, "error": "%s files are not supported here - convert to JPG or PNG first" % ext}
            rel = os.path.join("images", "%02d-%s%s.jpg" % (n, model.slugify(name, 40), suffix))
            subprocess.run(["sips", "-s", "format", "jpeg", path, "--out", os.path.join(d, rel)],
                           check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            rel = os.path.join("images", "%02d-%s%s%s" % (n, model.slugify(name, 40), suffix, ext))
            shutil.copyfile(path, os.path.join(d, rel))
        rels.append(rel)
    w, h = image_size(os.path.join(d, rels[0]))
    item = model.add_item(board, source or ("file: " + os.path.basename(paths[0])), rels, w, h)
    return {"ok": True, "id": item["id"], "frames": len(rels)}


def recapture(d, board, item_id):
    """Re-take an item's screenshots. Pins are dropped - their coordinates belonged to the old images."""
    item = next((i for i in board["items"] if i["id"] == item_id), None)
    if not item or not re.match(r"^https?://", item["source"]):
        return {"ok": False, "id": item_id, "error": "no such item or not a link"}
    u = urllib.parse.urlparse(item["source"])
    base = os.path.join(d, "images", "%02d-%s" % (model.item_number(item_id),
                                                  model.slugify(u.netloc.replace("www.", "") + u.path, 40)))
    old = list(model.frames_of(item))
    res = capture.capture(item["source"], base)
    if not res["ok"]:
        res["id"] = item_id
        return res
    new = [os.path.relpath(p, d) for p in res["paths"]]
    for f in old:
        if f not in new and os.path.isfile(os.path.join(d, f)):
            os.remove(os.path.join(d, f))
    dropped = len(item["pins"])
    w, h = image_size(os.path.join(d, new[0]))
    item.update({"image": new[0], "frames": new, "w": w, "h": h, "pins": []})
    return {"ok": True, "id": item_id, "frames": len(new), "pins_dropped": dropped}


# ---------------- files around the board ----------------
def render(d):
    board = model.load_board(d)
    md = model.render_markdown(board, exists=lambda rel: os.path.isfile(os.path.join(d, rel)))
    with open(os.path.join(d, model.RESULT_FILE), "w", encoding="utf-8") as f:
        f.write(md)
    return os.path.join(d, model.RESULT_FILE)


def write_launcher(root):
    """Double-click file that opens the boards of this folder (macOS Terminal runs .command files)."""
    path = os.path.join(root, LAUNCHER)
    me = os.path.abspath(__file__)  # keeps a symlinked skill path, so it survives moving the source
    with open(path, "w", encoding="utf-8") as f:
        f.write('#!/bin/bash\n'
                '# Opens the inspiration boards in this folder. Close the browser tab to stop.\n'
                'BOARD="%s"\n'
                'cd "$(dirname "$0")"\n'
                'if [ ! -f "$BOARD" ]; then\n'
                '  echo "The inspiration-board skill was not found at: $BOARD"\n'
                '  echo "Ask your agent to recreate this launcher (board.py init)."\n'
                '  read -n 1 -s -r -p "Press any key to close."; exit 1\n'
                'fi\n'
                'python3 "$BOARD" open "$(pwd)"\n' % me)
    os.chmod(path, os.stat(path).st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    return path


def git_root(cwd):
    try:
        r = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=cwd, capture_output=True, text=True)
        return r.stdout.strip() or None if r.returncode == 0 else None
    except OSError:
        return None


# ---------------- server ----------------
class App:
    def __init__(self, root, mode, session_slug=None):
        self.root = os.path.abspath(root)
        self.mode = mode                  # "session" | "standalone"
        self.session_slug = session_slug
        self.last_beat = None
        self.started = time.time()
        self.server = None

    def topic_dir(self, slug):
        d = os.path.realpath(os.path.join(self.root, slug))
        if os.path.dirname(d) != os.path.realpath(self.root) or not (model.is_board(d) or model.is_legacy(d)):
            return None
        return d

    def state(self, d):
        if model.is_legacy(d):
            return model.load_legacy(d)
        board = model.load_board(d)
        board["waiting"] = model.waiting(board)
        board["pending_round"] = model.pending_round(board)
        board["suggested"] = model.suggested_categories(board.get("language"))
        return board


def make_handler(app):
    class H(BaseHTTPRequestHandler):
        def log_message(self, *a):
            pass

        def _send(self, code, body, ctype="application/json; charset=utf-8"):
            if isinstance(body, (dict, list)):
                body = json.dumps(body, ensure_ascii=False).encode("utf-8")
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)

        def _json(self):
            n = int(self.headers.get("Content-Length") or 0)
            return json.loads(self.rfile.read(n) or b"{}") if n else {}

        def _topic(self, path, tail):
            m = re.match(r"^/api/t/([^/]+)/" + tail + "$", path)
            return app.topic_dir(urllib.parse.unquote(m.group(1))) if m else None

        def do_GET(self):
            path = urllib.parse.urlparse(self.path).path
            if path in ("/", "/index.html"):
                with open(BOARD_HTML, "rb") as f:
                    return self._send(200, f.read(), "text/html; charset=utf-8")
            m = re.match(r"^/fonts/([a-z0-9-]+\.woff2)$", path)
            if m:
                font = os.path.join(FONTS_DIR, m.group(1))
                if os.path.isfile(font):
                    with open(font, "rb") as f:
                        return self._send(200, f.read(), "font/woff2")
            if path == "/api/meta":
                return self._send(200, {"mode": app.mode, "session": app.session_slug,
                                        "root": os.path.basename(os.path.dirname(app.root)) or app.root})
            if path == "/api/topics":
                with LOCK:
                    return self._send(200, model.list_topics(app.root))
            d = self._topic(path, "state")
            if d:
                with LOCK:
                    return self._send(200, app.state(d))
            m = re.match(r"^/t/([^/]+)/(images/.+)$", path)
            if m:
                d = app.topic_dir(urllib.parse.unquote(m.group(1)))
                if d:
                    full = os.path.realpath(os.path.join(d, urllib.parse.unquote(m.group(2))))
                    if full.startswith(os.path.join(d, "images") + os.sep) and os.path.isfile(full):
                        with open(full, "rb") as f:
                            return self._send(200, f.read(), CTYPES.get(os.path.splitext(full)[1].lower(),
                                                                         "application/octet-stream"))
            return self._send(404, {"error": "not found"})

        def do_POST(self):
            path = urllib.parse.urlparse(self.path).path
            try:
                if path == "/api/heartbeat":
                    app.last_beat = time.time()
                    return self._send(200, {"ok": True})
                if path == "/api/topics":
                    name = str(self._json().get("topic", "")).strip()
                    if not name:
                        return self._send(400, {"ok": False, "error": "Give the topic a name"})
                    with LOCK:
                        d, created = model.create_topic(app.root, name)
                    return self._send(200, {"ok": True, "slug": os.path.basename(d), "created": created})
                d = None
                for tail in ("state", "add-url", "upload", "done"):
                    d = self._topic(path, tail)
                    if d:
                        break
                if not d:
                    return self._send(404, {"error": "not found"})
                if model.is_legacy(d):
                    return self._send(403, {"ok": False, "error": "Old-format board is read-only"})
                if tail in ("state", "done"):
                    incoming = self._json()
                    with LOCK:
                        board = model.load_board(d)
                        model.merge_client(board, incoming)
                        model.save_board(d, board)
                        state = app.state(d)
                    if tail == "done" and app.mode == "session":
                        self._send(200, {"ok": True})
                        threading.Timer(0.5, app.server.shutdown).start()
                        return None
                    return self._send(200, {"ok": True, "state": state})
                if tail == "add-url":
                    url = str(self._json().get("url", "")).strip()
                    if not re.match(r"^https?://", url):
                        return self._send(400, {"ok": False, "error": "A link has to start with http(s)://"})
                    with LOCK:
                        board = model.load_board(d)
                    res = add_url(d, board, url)  # slow; capture outside the lock
                    if res["ok"]:
                        with LOCK:
                            fresh = model.load_board(d)
                            item = board["items"][-1]
                            item["id"] = model.next_item_id(fresh)
                            fresh["items"].append(item)
                            model.save_board(d, fresh)
                            res["id"] = item["id"]
                    return self._send(200, res)
                if tail == "upload":
                    name = urllib.parse.unquote(self.headers.get("X-Filename") or "upload.png")
                    n = int(self.headers.get("Content-Length") or 0)
                    data = self.rfile.read(n)
                    stem, ext = os.path.splitext(name)
                    tmp = os.path.join(d, "images", ".upload-" + model.slugify(stem, 40) + ext.lower())
                    with open(tmp, "wb") as f:
                        f.write(data)
                    try:
                        with LOCK:
                            board = model.load_board(d)
                            res = add_files(d, board, [tmp], source="file: " + name)
                            if res["ok"]:
                                model.save_board(d, board)
                    finally:
                        os.remove(tmp)
                    return self._send(200, res)
            except Exception as e:  # noqa: BLE001 - surface errors to the board
                return self._send(500, {"ok": False, "error": str(e)})
            return self._send(404, {"error": "not found"})

    return H


def free_port(start):
    for p in range(start, start + 50):
        with socket.socket() as s:
            try:
                s.bind(("127.0.0.1", p))
                return p
            except OSError:
                continue
    raise RuntimeError("no free port")


def run_server(app, port, open_browser, url_hash=""):
    port = free_port(port)
    app.server = ThreadingHTTPServer(("127.0.0.1", port), make_handler(app))
    url = "http://127.0.0.1:%d/%s" % (port, url_hash)
    print("BOARD_URL %s" % url, flush=True)
    if app.mode == "standalone":
        def watchdog():
            while True:
                time.sleep(5)
                idle = time.time() - (app.last_beat or app.started)
                if idle > (IDLE_SECONDS if app.last_beat else START_GRACE):
                    app.server.shutdown()
                    return
        threading.Thread(target=watchdog, daemon=True).start()
    if open_browser:
        webbrowser.open(url)
    app.server.serve_forever()


# ---------------- CLI ----------------
def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("where")
    s.add_argument("--cwd", default=os.getcwd())
    s = sub.add_parser("config")
    s.add_argument("--library", required=True)
    s = sub.add_parser("topics")
    s.add_argument("root")
    s = sub.add_parser("find")
    s.add_argument("root")
    s.add_argument("name")
    s = sub.add_parser("init")
    s.add_argument("root")
    s.add_argument("--topic", required=True)
    s.add_argument("--language", default="en")
    s = sub.add_parser("add")
    s.add_argument("dir")
    s.add_argument("sources", nargs="+")
    s.add_argument("--frames", action="store_true",
                   help="local files = consecutive screens of ONE inspiration (e.g. scrolled screenshots)")
    s = sub.add_parser("recapture")
    s.add_argument("dir")
    s.add_argument("ids", nargs="+")
    for name in ("status", "render"):
        s = sub.add_parser(name)
        s.add_argument("dir")
    s = sub.add_parser("round")
    s.add_argument("dir")
    s.add_argument("payload")
    s = sub.add_parser("serve")
    s.add_argument("dir")
    s.add_argument("--port", type=int, default=4777)
    s.add_argument("--no-open", action="store_true")
    s = sub.add_parser("open")
    s.add_argument("root")
    s.add_argument("--port", type=int, default=4777)
    s.add_argument("--no-open", action="store_true")
    a = ap.parse_args()

    if a.cmd == "where":
        cfg = model.load_json(CONFIG, {}) or {}
        d, reason = model.find_inspirations_dir(a.cwd, git_root(a.cwd), cfg.get("library_dir"))
        info = {"dir": d, "reason": reason, "default_library": os.path.join("~", "Inspirations")}
        if d and reason in ("git", "existing") and git_root(a.cwd):
            r = subprocess.run(["git", "check-ignore", "-q", d], cwd=a.cwd)
            info["git_ignored"] = r.returncode == 0
        return out(info)
    if a.cmd == "config":
        os.makedirs(os.path.dirname(CONFIG), exist_ok=True)
        cfg = model.load_json(CONFIG, {}) or {}
        cfg["library_dir"] = a.library
        model.save_json(CONFIG, cfg)
        return out({"ok": True, "config": CONFIG, "library_dir": a.library})
    if a.cmd == "topics":
        return out(model.list_topics(os.path.abspath(a.root)))
    if a.cmd == "find":
        return out({"match": model.find_topic(os.path.abspath(a.root), a.name)})
    if a.cmd == "init":
        root = os.path.abspath(os.path.expanduser(a.root))
        os.makedirs(root, exist_ok=True)
        d, created = model.create_topic(root, a.topic, a.language)
        return out({"ok": True, "dir": d, "created": created, "launcher": write_launcher(root)})
    if a.cmd == "open":
        root = os.path.abspath(os.path.expanduser(a.root))
        print("Inspiration boards are open in your browser. Close the tab to stop.", flush=True)
        run_server(App(root, "standalone"), a.port, not a.no_open)
        print("Board closed. You can close this window.", flush=True)
        return None

    d = os.path.abspath(a.dir)
    if not model.is_board(d):
        return out({"ok": False, "error": "no board.json in %s - create the topic with init first" % d})
    if a.cmd == "add":
        board = model.load_board(d)
        before = {i["id"] for i in board["items"]}
        results = []
        if a.frames:
            results.append(add_files(d, board, a.sources, source="screenshots"))
        else:
            for src in a.sources:
                if re.match(r"^https?://", src):
                    results.append(add_url(d, board, src))
                elif os.path.isfile(src):
                    results.append(add_files(d, board, [src]))
                else:
                    results.append({"ok": False, "url": src, "error": "not a link or file"})
        with LOCK:  # the board may have saved meanwhile: append only the new items, with fresh ids
            fresh = model.load_board(d)
            renamed = {}
            for item in board["items"]:
                if item["id"] not in before:
                    new_id = model.next_item_id(fresh)
                    renamed[item["id"]] = new_id
                    item["id"] = new_id
                    fresh["items"].append(item)
            model.save_board(d, fresh)
        for r in results:
            if r.get("id") in renamed:
                r["id"] = renamed[r["id"]]
        return out(results)
    if a.cmd == "recapture":
        results = []
        for item_id in a.ids:
            board = model.load_board(d)
            res = recapture(d, board, item_id)
            if res["ok"]:
                fresh = model.load_board(d)
                fresh["items"] = [next(x for x in board["items"] if x["id"] == item_id) if i["id"] == item_id else i
                                  for i in fresh["items"]]
                model.save_board(d, fresh)
            results.append(res)
        return out(results)
    if a.cmd == "status":
        board = model.load_board(d)
        return out({"topic": board["topic"], "items": len(model.live_items(board)), "rounds": len(board["rounds"]),
                    "features": sum(1 for f in board["features"] if f["status"] == "active"),
                    "waiting": model.waiting(board)})
    if a.cmd == "render":
        return out({"ok": True, "file": render(d)})
    if a.cmd == "round":
        payload = model.load_json(a.payload, {})
        with LOCK:
            board = model.load_board(d)
            res = model.apply_round(board, payload)
            model.save_board(d, board)
        res["file"] = render(d)
        return out(res)
    if a.cmd == "serve":
        slug = os.path.basename(d)
        run_server(App(os.path.dirname(d), "session", slug), a.port, not a.no_open, "#/t/" + slug)
        board = model.load_board(d)
        live = model.live_items(board)
        print("BOARD_DONE items=%d pins=%d waiting=%d" % (len(live), sum(len(i["pins"]) for i in live),
                                                         len(model.waiting(board))), flush=True)
    return None


if __name__ == "__main__":
    main()
