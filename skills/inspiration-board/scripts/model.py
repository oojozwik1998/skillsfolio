"""Data model of a topic board. Pure functions plus small file helpers.
Stdlib only, Python 3.9+. No Pillow, no HTTP - so it can be unit-tested.

A topic lives in <inspirations_dir>/<slug>/board.json. A board holds the
inspirations (items with frames and pins), sections (categories) that the
user sorts inspirations into, the features the agent named, the direction
text and the round history. The user edits items, pins and sections on the
board; features and the direction are written only by analysis rounds.
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
UNSORTED = ""  # item["category"] for inspirations not in any section
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
        "categories": [],
        "direction": {"text": "", "updated_round": 0},
        "features": [],
        "rounds": [],
        "items": [],
    }


def suggested_categories(language):
    """The skill vocabulary, offered as one-click sections on the board."""
    names = CATEGORY_NAMES.get(language, {})
    return [{"id": cid, "name": names.get(cid, name)} for cid, name in DEFAULT_CATEGORIES]


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
            "w": w, "h": h, "note": "", "named_note": "", "removed": False, "category": UNSORTED,
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
        cat = inc.get("category", cur.get("category", UNSORTED))
        cur["category"] = cat if cat in _category_ids(board) else UNSORTED
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


# ---------------- sections (categories) ----------------
def _category_ids(board):
    return {c["id"] for c in board["categories"]}


def category_name(board, cid):
    for c in board["categories"]:
        if c["id"] == cid:
            return c["name"]
    return next((c["name"] for c in suggested_categories(board.get("language")) if c["id"] == cid), cid)


def add_category(board, name, cid=None):
    """Add a section. A name or id from the vocabulary reuses its id. Returns the id."""
    name = str(name or "").strip()
    for sug in suggested_categories(board.get("language")):
        if cid == sug["id"] or slugify(name, 32) in (sug["id"], slugify(sug["name"], 32)):
            cid, name = sug["id"], name or sug["name"]
            break
    cid = cid or slugify(name, 32)
    if cid in _category_ids(board):
        return cid
    base, k = cid, 2
    while cid in _category_ids(board):
        cid, k = "%s-%d" % (base, k), k + 1
    board["categories"].append({"id": cid, "name": name or cid})
    return cid


def apply_ops(board, ops):
    """Section edits from the board. Returns the number of ops applied; invalid ops are skipped."""
    applied = 0
    for op in ops or []:
        kind = op.get("op")
        if kind == "category.add" and (str(op.get("name", "")).strip() or op.get("id")):
            add_category(board, op.get("name"), op.get("id"))
            applied += 1
        elif kind == "category.rename" and str(op.get("name", "")).strip():
            for c in board["categories"]:
                if c["id"] == op.get("id"):
                    c["name"] = op["name"].strip()
                    applied += 1
        elif kind == "category.delete" and op.get("id") in _category_ids(board):
            board["categories"] = [c for c in board["categories"] if c["id"] != op["id"]]
            for item in board["items"]:
                if item.get("category") == op["id"]:
                    item["category"] = UNSORTED
            applied += 1
    return applied


def merge_client(board, incoming):
    applied = apply_ops(board, incoming.get("ops"))  # sections first, so items can move into new ones
    merge_items(board, incoming.get("items"))
    return applied


# ---------------- analysis round (written by the agent) ----------------
def next_feature_id(board):
    nums = [int(f["id"][1:]) for f in board["features"] if re.match(r"^f\d+$", f["id"])]
    return "f%d" % (max(nums or [0]) + 1)


def _merge_sources(old, new):
    seen = {(s["item"], s.get("pin")) for s in old}
    for s in new or []:
        key = (s["item"], s.get("pin"))
        if key not in seen:
            old.append({"item": s["item"], "pin": s.get("pin")})
            seen.add(key)
    return old


def _feature_category(board, pf):
    """Agent's category, else the section of the first source inspiration."""
    cat = pf.get("category")
    if not cat:
        by_item = {i["id"]: i for i in board["items"]}
        cat = next((by_item[s["item"]].get("category") for s in pf.get("sources", [])
                    if s["item"] in by_item and by_item[s["item"]].get("category")), UNSORTED)
    if cat and cat not in _category_ids(board):
        cat = add_category(board, category_name(board, cat), cat)
    return cat


def apply_round(board, payload):
    """Apply the agent's analysis. Payload:
      focus, summary            - round description
      categories: [{id, name}]  - new sections, optional
      sort: [{item, category}]  - put unsorted inspirations into sections (sorted ones are left alone)
      features: [{id?, name, plain, scope, category?, list, status?, sources: [{item, pin|null}]}]
      reviewed: [{item, pin|null}] - pins / overall notes named this round (also those giving no feature)
      direction                 - direction text, optional
    Returns {"round": n, "added": [...], "changed": [...], "sorted": [...]}.
    """
    n = len(board["rounds"]) + 1
    for c in payload.get("categories") or []:
        if c.get("id") or c.get("name"):
            add_category(board, c.get("name"), c.get("id"))
    by_item = {i["id"]: i for i in board["items"]}
    sorted_items = []
    for srt in payload.get("sort") or []:
        item = by_item.get(srt.get("item"))
        if item and not item.get("category") and srt.get("category"):
            item["category"] = add_category(board, category_name(board, srt["category"]), srt["category"])
            sorted_items.append(item["id"])
    feats = {f["id"]: f for f in board["features"]}
    added, changed = [], []
    for pf in payload.get("features", []):
        cur = feats.get(pf.get("id"))
        if cur is None:
            f = {"id": next_feature_id(board), "name": pf.get("name", ""), "plain": pf.get("plain", ""),
                 "scope": pf.get("scope", ""), "category": _feature_category(board, pf),
                 "list": pf.get("list") if pf.get("list") in LISTS else "take",
                 "status": pf.get("status") if pf.get("status") in STATUSES else "active",
                 "sources": _merge_sources([], pf.get("sources")), "added_round": n, "updated_round": n}
            board["features"].append(f)
            feats[f["id"]] = f
            added.append(f["id"])
            continue
        _merge_sources(cur["sources"], pf.get("sources"))
        touched = False
        for field in FEATURE_FIELDS:
            if field not in pf or pf[field] == cur.get(field):
                continue
            value = pf[field]
            if field == "category":
                value = _feature_category(board, {"category": value})
            elif (field == "list" and value not in LISTS) or (field == "status" and value not in STATUSES):
                continue
            cur[field] = value
            touched = True
        if touched:
            cur["updated_round"] = n
            changed.append(cur["id"])
    if payload.get("direction") is not None and payload["direction"] != board["direction"]["text"]:
        board["direction"]["text"] = payload["direction"]
        board["direction"]["updated_round"] = n
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
                            "summary": payload.get("summary", ""),
                            "items_added": sum(1 for i in live_items(board) if i.get("added_round") == n),
                            "named": len(payload.get("reviewed", [])), "features_added": len(added),
                            "features_changed": len(changed)})
    return {"round": n, "added": added, "changed": changed, "sorted": sorted_items}


# ---------------- markdown ----------------
LABELS = {
    "en": {"title": "Inspirations", "direction": "Direction", "take": "What I take", "avoid": "What I avoid",
           "items": "Inspirations", "history": "Round history", "dropped": "Dropped", "feature": "Feature",
           "plain": "In plain words", "scope": "Where / scope", "source": "Source", "overall": "Overall",
           "inspirations": "inspirations", "pins": "pins", "waiting": "waiting to be named", "round": "round",
           "none": "Nothing yet.", "pin": "pin", "added": "added", "changed": "changed", "unsorted": "Unsorted",
           "other": "Other"},
    "pl": {"title": "Inspiracje", "direction": "Kierunek", "take": "Co biorę", "avoid": "Czego unikam",
           "items": "Inspiracje", "history": "Historia rund", "dropped": "Odrzucone", "feature": "Cecha",
           "plain": "Po ludzku", "scope": "Gdzie / zakres użycia", "source": "Źródło", "overall": "Ogólnie",
           "inspirations": "inspiracji", "pins": "zaznaczeń", "waiting": "czeka na nazwanie", "round": "runda",
           "none": "Jeszcze nic.", "pin": "pin", "added": "nowe", "changed": "zmienione", "unsorted": "Bez sekcji",
           "other": "Inne"},
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
    order = [c["id"] for c in board["categories"]]
    order += sorted({f["category"] for f in board["features"]} - set(order) - {UNSORTED}) + [UNSORTED]

    def cname(cid, empty):
        return category_name(board, cid) if cid else empty

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
            out += ["### " + cname(cid, lab["other"]), "",
                    "| %s | %s | %s | %s |" % (lab["feature"], lab["plain"], lab["scope"], lab["source"]),
                    "|---|---|---|---|"]
            for f in group:
                srcs = ", ".join(source_label(board, s, lab) for s in f["sources"])
                out.append("| %s | %s | %s | %s |" % (_cell(f["name"]), _cell(f["plain"]), _cell(f["scope"]), _cell(srcs)))
            out.append("")

    out.append("## " + lab["items"])
    names = {f["id"]: f["name"] for f in board["features"]}
    sections = [c["id"] for c in board["categories"]] + [UNSORTED]
    grouped = [(cid, [i for i in items if (i.get("category") or UNSORTED) == cid]) for cid in sections]
    show_sections = bool(board["categories"])
    for cid, group in grouped:
        if not group:
            continue
        if show_sections:
            out += ["", "### " + cname(cid, lab["unsorted"])]
        _render_items(out, group, names, lab, exists, "####" if show_sections else "###")
    return _render_tail(out, board, lab, cname)


def _render_items(out, group, names, lab, exists, h):
    for item in group:
        num = item_number(item["id"])
        src = item["source"]
        title = re.sub(r"^https?://(www\.)?", "", src).split("/")[0] if src.startswith("http") else src
        out += ["", "%s #%d · %s" % (h, num, title)]
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



def _render_tail(out, board, lab, cname):
    dropped = [f for f in board["features"] if f["status"] == "dropped"]
    if dropped:
        out += ["", "## " + lab["dropped"]]
        out += ["- %s (%s)" % (f["name"], cname(f["category"], lab["other"])) for f in dropped]
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
