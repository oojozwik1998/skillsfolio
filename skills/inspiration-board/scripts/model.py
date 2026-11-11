"""Data model of a topic board. Pure functions plus small file helpers.
Stdlib only, Python 3.9+. No Pillow, no HTTP - so it can be unit-tested.

A topic lives in <inspirations_dir>/<slug>/board.json. A board holds the
inspirations (items with frames and pins), the named features, the direction
text, categories and the round history.

Ownership rule: fields the user edited on the board are listed in
feature["user_edited"] (or direction["user_edited"]). An analysis round never
overwrites them; it returns a conflict ("was / proposed / why") that the agent
shows to the user, and only `apply_accept` writes it.
"""
import datetime
import json
import os
import re

SCHEMA_VERSION = 2
BOARD_FILE = "board.json"
LEGACY_FILE = "pins.json"
RESULT_FILE = "inspirations.md"

DEFAULT_CATEGORIES = (
    ("typography", "Typography"),
    ("color", "Color"),
    ("layout", "Layout & composition"),
    ("logo", "Logo & mark"),
    ("image", "Image & illustration"),
    ("ui", "Web / UI"),
    ("motion", "Motion"),
    ("material", "Material & print"),
)
CATEGORY_NAMES = {  # default category names per board language; the board UI itself is English
    "pl": {"typography": "Typografia", "color": "Kolor", "layout": "Layout i kompozycja", "logo": "Logo i znak",
           "image": "Obraz i ilustracja", "ui": "Web / UI", "motion": "Ruch", "material": "Materiał i druk"},
}
FEATURE_FIELDS = ("name", "plain", "scope", "category", "list", "status")
LISTS = ("take", "avoid")
STATUSES = ("active", "dropped")


# ---------------- basics ----------------
def today():
    return datetime.date.today().isoformat()


def slugify(text, n=48):
    text = text.lower()
    for a, b in (("ą", "a"), ("ć", "c"), ("ę", "e"), ("ł", "l"), ("ń", "n"), ("ó", "o"),
                 ("ś", "s"), ("ź", "z"), ("ż", "z"), ("ä", "a"), ("ö", "o"), ("ü", "u"), ("ß", "ss")):
        text = text.replace(a, b)
    s = re.sub(r"[^a-z0-9]+", "-", text).strip("-")
    return s[:n].strip("-") or "topic"


def new_board(topic, language="en"):
    return {
        "version": SCHEMA_VERSION,
        "topic": topic,
        "language": language or "en",
        "created": today(),
        "categories": [{"id": cid, "name": CATEGORY_NAMES.get(language, {}).get(cid, name), "custom": False}
                       for cid, name in DEFAULT_CATEGORIES],
        "direction": {"text": "", "user_edited": False, "updated_round": 0},
        "features": [],
        "rounds": [],
        "items": [],
    }


def frames_of(item):
    return item.get("frames") or [item["image"]]


def live_items(board):
    return [i for i in board["items"] if not i.get("removed")]


def item_number(item_id):
    m = re.match(r"^i(\d+)$", str(item_id))
    return int(m.group(1)) if m else 0


def pending_round(board):
    """Number of the round that has not been analyzed yet."""
    return len(board["rounds"]) + 1


# ---------------- files ----------------
def load_json(path, default=None):
    if not os.path.exists(path):
        return default
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_json(path, data):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(tmp, path)


def board_path(topic_dir):
    return os.path.join(topic_dir, BOARD_FILE)


def is_board(topic_dir):
    return os.path.isfile(board_path(topic_dir))


def is_legacy(topic_dir):
    return not is_board(topic_dir) and os.path.isfile(os.path.join(topic_dir, LEGACY_FILE))


def load_board(topic_dir):
    return load_json(board_path(topic_dir))


def save_board(topic_dir, board):
    save_json(board_path(topic_dir), board)


def load_legacy(topic_dir):
    """Old dated session (pins.json) as a read-only board. Never written back."""
    old = load_json(os.path.join(topic_dir, LEGACY_FILE), {})
    board = new_board(old.get("topic") or os.path.basename(topic_dir))
    board["created"] = old.get("created", "")
    board["items"] = old.get("items", [])
    board["legacy"] = True
    return board


# ---------------- topics ----------------
def topic_summary(topic_dir):
    legacy = is_legacy(topic_dir)
    board = load_legacy(topic_dir) if legacy else load_board(topic_dir)
    items = live_items(board)
    thumb = frames_of(items[0])[0] if items else None
    return {
        "slug": os.path.basename(topic_dir),
        "topic": board["topic"],
        "items": len(items),
        "waiting": 0 if legacy else len(waiting(board)),
        "last_round": board["rounds"][-1]["date"] if board["rounds"] else None,
        "created": board.get("created", ""),
        "thumb": thumb,
        "legacy": legacy,
    }


def list_topics(root):
    if not os.path.isdir(root):
        return []
    out = []
    for name in sorted(os.listdir(root)):
        d = os.path.join(root, name)
        if os.path.isdir(d) and (is_board(d) or is_legacy(d)):
            out.append(topic_summary(d))
    out.sort(key=lambda t: (t["last_round"] or t["created"] or ""), reverse=True)
    return out


def find_topic(root, query):
    """Best match for a topic name typed in chat: exact slug, then slug prefix, then words."""
    topics = [t for t in list_topics(root) if not t["legacy"]]
    q = slugify(query)
    for t in topics:
        if t["slug"] == q:
            return t
    starts = [t for t in topics if t["slug"].startswith(q) or q.startswith(t["slug"])]
    if len(starts) == 1:
        return starts[0]
    words = set(q.split("-"))
    scored = sorted(((len(words & set(t["slug"].split("-"))), t) for t in topics), key=lambda x: -x[0])
    if scored and scored[0][0] > 0 and (len(scored) == 1 or scored[0][0] > scored[1][0]):
        return scored[0][1]
    return None


def create_topic(root, topic, language="en"):
    slug = slugify(topic)
    d = os.path.join(root, slug)
    if is_board(d):
        return d, False
    os.makedirs(os.path.join(d, "images"), exist_ok=True)
    save_board(d, new_board(topic, language))
    return d, True


# ---------------- where the inspirations folder lives ----------------
def find_inspirations_dir(cwd, git_root, library_dir):
    """Project folder if there is one, otherwise the library folder.

    1. an existing inspirations/ in cwd or a parent (up to the git root),
    2. the git root,
    3. cwd when it looks like a project (has CLAUDE.md or AGENTS.md),
    4. the library folder (None = ask the user once).
    """
    cwd = os.path.abspath(cwd)
    stop = os.path.abspath(git_root) if git_root else cwd
    d = cwd
    while True:
        if os.path.isdir(os.path.join(d, "inspirations")):
            return os.path.join(d, "inspirations"), "existing"
        if d == stop or os.path.dirname(d) == d:
            break
        d = os.path.dirname(d)
    if git_root:
        return os.path.join(os.path.abspath(git_root), "inspirations"), "git"
    if any(os.path.isfile(os.path.join(cwd, f)) for f in ("CLAUDE.md", "AGENTS.md")):
        return os.path.join(os.path.abspath(cwd), "inspirations"), "project"
    if library_dir:
        return os.path.expanduser(library_dir), "library"
    return None, "ask"


# ---------------- items ----------------
def next_item_id(board):
    return "i%d" % (max([item_number(i["id"]) for i in board["items"]] or [0]) + 1)


def add_item(board, source, frames, w=0, h=0):
    item = {"id": next_item_id(board), "source": source, "image": frames[0], "frames": list(frames),
            "w": w, "h": h, "note": "", "named_note": "", "removed": False,
            "added_round": pending_round(board), "pins": []}
    board["items"].append(item)
    return item


def _clean_pin(p, old):
    pin = {"id": str(p["id"]), "kind": "dislike" if p.get("kind") == "dislike" else "like",
           "note": str(p.get("note", "")), "frame": int(p.get("frame", 0)),
           "x": float(p["x"]), "y": float(p["y"]), "w": float(p.get("w", 0)), "h": float(p.get("h", 0))}
    # server-only fields survive a save from the board
    pin["named_note"] = old.get("named_note") if old else None
    pin["feature_ids"] = list(old.get("feature_ids", [])) if old else []
    return pin


def merge_items(board, incoming_items):
    """Take the user-editable fields of items sent by the board, by id.
    Items the board does not know yet (added from chat meanwhile) are kept."""
    by_id = {i["id"]: i for i in board["items"]}
    for inc in incoming_items or []:
        cur = by_id.get(inc.get("id"))
        if not cur:
            continue
        cur["note"] = str(inc.get("note", ""))
        cur["removed"] = bool(inc.get("removed", False))
        old_pins = {p["id"]: p for p in cur.get("pins", [])}
        pins = []
        for p in inc.get("pins", []):
            try:
                pins.append(_clean_pin(p, old_pins.get(str(p.get("id")))))
            except (KeyError, TypeError, ValueError):
                continue
        nf = len(frames_of(cur))
        for p in pins:
            p["frame"] = min(max(p["frame"], 0), nf - 1)
        cur["pins"] = pins


def pin_waiting(pin):
    return pin.get("named_note") is None or pin.get("named_note") != pin.get("note", "")


def note_waiting(item):
    return bool((item.get("note") or "").strip()) and item.get("note") != item.get("named_note", "")


def waiting(board):
    """Pins and overall notes that the next round has to name: new or edited since last named."""
    out = []
    for item in live_items(board):
        if note_waiting(item):
            out.append({"item": item["id"], "pin": None})
        for p in item.get("pins", []):
            if pin_waiting(p):
                out.append({"item": item["id"], "pin": p["id"]})
    return out


# ---------------- user edits from the board (Direction tab) ----------------
def _category_ids(board):
    return {c["id"] for c in board["categories"]}


def next_feature_id(board):
    nums = [int(f["id"][1:]) for f in board["features"] if re.match(r"^f\d+$", f["id"])]
    return "f%d" % (max(nums or [0]) + 1)


def _valid_value(board, field, value):
    if field == "list":
        return value in LISTS
    if field == "status":
        return value in STATUSES
    if field == "category":
        return value in _category_ids(board)
    return isinstance(value, str)


def apply_ops(board, ops):
    """Edits made by the user on the board. Each changed field becomes user-owned.
    Returns the number of ops applied; invalid ops are skipped."""
    applied = 0
    feats = {f["id"]: f for f in board["features"]}
    for op in ops or []:
        kind = op.get("op")
        if kind == "feature.set":
            f, field, value = feats.get(op.get("id")), op.get("field"), op.get("value")
            if not f or field not in FEATURE_FIELDS or not _valid_value(board, field, value):
                continue
            f[field] = value
            if field not in f["user_edited"]:
                f["user_edited"].append(field)
            applied += 1
        elif kind == "feature.add":
            src = op.get("feature") or {}
            f = {"id": next_feature_id(board), "name": str(src.get("name", "")), "plain": str(src.get("plain", "")),
                 "scope": str(src.get("scope", "")),
                 "category": src.get("category") if src.get("category") in _category_ids(board) else board["categories"][0]["id"],
                 "list": src.get("list") if src.get("list") in LISTS else "take", "status": "active",
                 "sources": [], "user_edited": list(FEATURE_FIELDS),
                 "added_round": len(board["rounds"]), "updated_round": len(board["rounds"])}
            board["features"].append(f)
            feats[f["id"]] = f
            if op.get("client_id"):
                f["client_id"] = str(op["client_id"])
            applied += 1
        elif kind == "direction.set" and isinstance(op.get("text"), str):
            board["direction"]["text"] = op["text"]
            board["direction"]["user_edited"] = True
            applied += 1
        elif kind == "category.add" and str(op.get("name", "")).strip():
            cid = slugify(op["name"], 32)
            base, k = cid, 2
            while cid in _category_ids(board):
                cid, k = "%s-%d" % (base, k), k + 1
            board["categories"].append({"id": cid, "name": op["name"].strip(), "custom": True})
            applied += 1
        elif kind == "category.rename" and str(op.get("name", "")).strip():
            for c in board["categories"]:
                if c["id"] == op.get("id"):
                    c["name"] = op["name"].strip()
                    applied += 1
        elif kind == "category.delete":
            used = any(f["category"] == op.get("id") for f in board["features"])
            before = len(board["categories"])
            if not used and before > 1:
                board["categories"] = [c for c in board["categories"] if c["id"] != op.get("id")]
                applied += before - len(board["categories"])
    return applied


def merge_client(board, incoming):
    merge_items(board, incoming.get("items"))
    return apply_ops(board, incoming.get("ops"))


# ---------------- analysis round (written by the agent) ----------------
def _ensure_categories(board, cats):
    for c in cats or []:
        if c.get("id") and c["id"] not in _category_ids(board):
            board["categories"].append({"id": c["id"], "name": c.get("name") or c["id"], "custom": True})


def _merge_sources(old, new):
    seen = {(s["item"], s.get("pin")) for s in old}
    for s in new or []:
        key = (s["item"], s.get("pin"))
        if key not in seen:
            old.append({"item": s["item"], "pin": s.get("pin")})
            seen.add(key)
    return old


def apply_round(board, payload):
    """Apply the agent's analysis. Payload:
      focus, summary            - round description
      categories: [{id, name}]  - new categories, optional
      features: [{id? , name, plain, scope, category, list, status?, sources: [{item, pin|null}], why?}]
      reviewed: [{item, pin|null}] - pins / overall notes named this round (also those giving no feature)
      direction, direction_why  - proposed direction text, optional
    Returns {"round": n, "conflicts": [...], "added": [...], "changed": [...]}.
    """
    n = len(board["rounds"]) + 1
    _ensure_categories(board, payload.get("categories"))
    feats = {f["id"]: f for f in board["features"]}
    conflicts, added, changed = [], [], []
    for pf in payload.get("features", []):
        cur = feats.get(pf.get("id"))
        if cur is None:
            f = {"id": next_feature_id(board), "name": pf.get("name", ""), "plain": pf.get("plain", ""),
                 "scope": pf.get("scope", ""), "category": pf.get("category", board["categories"][0]["id"]),
                 "list": pf.get("list", "take"), "status": pf.get("status", "active"),
                 "sources": _merge_sources([], pf.get("sources")), "user_edited": [],
                 "added_round": n, "updated_round": n}
            if f["category"] not in _category_ids(board):
                f["category"] = board["categories"][0]["id"]
            board["features"].append(f)
            feats[f["id"]] = f
            added.append(f["id"])
            continue
        _merge_sources(cur["sources"], pf.get("sources"))
        touched = False
        for field in FEATURE_FIELDS:
            if field not in pf or pf[field] == cur.get(field) or not _valid_value(board, field, pf[field]):
                continue
            if field in cur["user_edited"]:
                conflicts.append({"feature": cur["id"], "field": field, "was": cur.get(field),
                                  "proposed": pf[field], "why": pf.get("why", "")})
            else:
                cur[field] = pf[field]
                touched = True
        if touched:
            cur["updated_round"] = n
            changed.append(cur["id"])
    if payload.get("direction") is not None and payload["direction"] != board["direction"]["text"]:
        if board["direction"]["user_edited"]:
            conflicts.append({"feature": None, "field": "direction", "was": board["direction"]["text"],
                              "proposed": payload["direction"], "why": payload.get("direction_why", "")})
        else:
            board["direction"]["text"] = payload["direction"]
            board["direction"]["updated_round"] = n
    # mark what was named, and link pins to their features
    by_item = {i["id"]: i for i in board["items"]}
    for r in payload.get("reviewed", []):
        item = by_item.get(r.get("item"))
        if not item:
            continue
        if r.get("pin") is None:
            item["named_note"] = item.get("note", "")
            continue
        for p in item["pins"]:
            if p["id"] == r["pin"]:
                p["named_note"] = p.get("note", "")
                p["feature_ids"] = [f["id"] for f in board["features"]
                                    if {"item": item["id"], "pin": p["id"]} in f["sources"]]
    board["rounds"].append({"n": n, "date": payload.get("date") or today(), "focus": payload.get("focus", ""),
                            "summary": payload.get("summary", ""), "items_added":
                            sum(1 for i in live_items(board) if i.get("added_round") == n),
                            "named": len(payload.get("reviewed", [])), "features_added": len(added),
                            "features_changed": len(changed), "conflicts": len(conflicts)})
    return {"round": n, "conflicts": conflicts, "added": added, "changed": changed}


def apply_accept(board, accepted):
    """Write proposals the user accepted. The field goes back to the agent (no longer user-owned)."""
    feats = {f["id"]: f for f in board["features"]}
    done = 0
    for a in accepted or []:
        if a.get("field") == "direction":
            board["direction"]["text"] = a.get("value", "")
            board["direction"]["user_edited"] = False
            done += 1
            continue
        f = feats.get(a.get("feature"))
        if not f or a.get("field") not in FEATURE_FIELDS or not _valid_value(board, a["field"], a.get("value")):
            continue
        f[a["field"]] = a["value"]
        if a["field"] in f["user_edited"]:
            f["user_edited"].remove(a["field"])
        done += 1
    return done


# ---------------- markdown ----------------
LABELS = {
    "en": {"title": "Inspirations", "direction": "Direction", "take": "What I take", "avoid": "What I avoid",
           "items": "Inspirations", "history": "Round history", "dropped": "Dropped", "feature": "Feature",
           "plain": "In plain words", "scope": "Where / scope", "source": "Source", "overall": "Overall",
           "inspirations": "inspirations", "pins": "pins", "waiting": "waiting to be named", "round": "round",
           "none": "Nothing yet.", "pin": "pin", "added": "added", "changed": "changed"},
    "pl": {"title": "Inspiracje", "direction": "Kierunek", "take": "Co biorę", "avoid": "Czego unikam",
           "items": "Inspiracje", "history": "Historia rund", "dropped": "Odrzucone", "feature": "Cecha",
           "plain": "Po ludzku", "scope": "Gdzie / zakres użycia", "source": "Źródło", "overall": "Ogólnie",
           "inspirations": "inspiracji", "pins": "zaznaczeń", "waiting": "czeka na nazwanie", "round": "runda",
           "none": "Jeszcze nic.", "pin": "pin", "added": "nowe", "changed": "zmienione"},
}


def _cell(text):
    return str(text or "").replace("|", "\\|").replace("\n", " ")


def source_label(board, src, lab):
    item = next((i for i in board["items"] if i["id"] == src["item"]), None)
    num = item_number(src["item"])
    if src.get("pin") is None or item is None:
        return "#%d" % num
    idx = next((k for k, p in enumerate(item["pins"], 1) if p["id"] == src["pin"]), None)
    return "#%d %s %s" % (num, lab["pin"], idx) if idx else "#%d" % num


def render_markdown(board, exists=lambda rel: False):
    lab = LABELS.get(board.get("language"), LABELS["en"])
    cats = {c["id"]: c["name"] for c in board["categories"]}
    order = [c["id"] for c in board["categories"]]
    items = live_items(board)
    n_pins = sum(len(i["pins"]) for i in items)
    out = ["# %s · %s" % (lab["title"], board["topic"]), ""]
    last = board["rounds"][-1]["date"] if board["rounds"] else board.get("created", "")
    meta = "%s · %d %s, %d %s" % (last, len(items), lab["inspirations"], n_pins, lab["pins"])
    w = len(waiting(board))
    if w:
        meta += " · %d %s" % (w, lab["waiting"])
    out += [meta, "", "## " + lab["direction"], board["direction"]["text"] or lab["none"], ""]

    active = [f for f in board["features"] if f["status"] == "active"]
    for lst in LISTS:
        out.append("## " + lab[lst])
        feats = [f for f in active if f["list"] == lst]
        if not feats:
            out += [lab["none"], ""]
            continue
        for cid in order:
            group = [f for f in feats if f["category"] == cid]
            if not group:
                continue
            out += ["### " + cats[cid], "",
                    "| %s | %s | %s | %s |" % (lab["feature"], lab["plain"], lab["scope"], lab["source"]),
                    "|---|---|---|---|"]
            for f in group:
                srcs = ", ".join(source_label(board, s, lab) for s in f["sources"])
                out.append("| %s | %s | %s | %s |" % (_cell(f["name"]), _cell(f["plain"]), _cell(f["scope"]), _cell(srcs)))
            out.append("")

    out.append("## " + lab["items"])
    names = {f["id"]: f["name"] for f in board["features"]}
    for item in items:
        num = item_number(item["id"])
        src = item["source"]
        title = re.sub(r"^https?://(www\.)?", "", src).split("/")[0] if src.startswith("http") else src
        out += ["", "### #%d · %s" % (num, title)]
        if src.startswith("http"):
            out.append(src)
        if (item.get("note") or "").strip():
            out.append("%s: %s" % (lab["overall"], item["note"].strip()))
        ov = next((p for p in ("images/overview/%s-1.jpg" % item["id"], "images/overview/%s-1-1.jpg" % item["id"])
                   if exists(p)), None)
        if ov:
            out += ["", "![](%s)" % ov, ""]
        for k, p in enumerate(item["pins"], 1):
            mark = "👎" if p.get("kind") == "dislike" else "👍"
            fn = ", ".join(names[x] for x in p.get("feature_ids", []) if x in names)
            line = "%d. %s " % (k, mark) + ("**%s** - " % fn if fn else "") + (p.get("note") or "")
            out.append(line.rstrip(" -"))
            crop = "images/crops/%s-%s.png" % (item["id"], p["id"])
            if exists(crop):
                out.append("   ![](%s)" % crop)

    dropped = [f for f in board["features"] if f["status"] == "dropped"]
    if dropped:
        out += ["", "## " + lab["dropped"]]
        out += ["- %s (%s)" % (f["name"], cats.get(f["category"], f["category"])) for f in dropped]
    if board["rounds"]:
        out += ["", "## " + lab["history"]]
        for r in reversed(board["rounds"]):
            bits = [r["date"], "%s %d" % (lab["round"], r["n"])]
            if r.get("focus"):
                bits.append(r["focus"])
            line = "- " + " · ".join(bits)
            line += " · +%d %s, %d %s" % (r["features_added"], lab["added"], r["features_changed"], lab["changed"])
            if r.get("summary"):
                line += " - " + r["summary"]
            out.append(line)
    return "\n".join(out).rstrip() + "\n"
