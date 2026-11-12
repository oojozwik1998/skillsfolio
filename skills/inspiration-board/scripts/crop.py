#!/usr/bin/env python3
"""Cut pins out of their images so the agent can look at them up close, and
draw an overview per inspiration with numbered pins. Needs Pillow.

  crop.py <topic_dir> [--all]

By default only what waits to be named (new or edited pins and overall notes).
--all processes every pin.

Writes  images/crops/<item>-<pin>.png        (pin + margin, upscaled if tiny)
        images/overview/<item>-<frame>.jpg   (one tile per screen, pins drawn)
Prints a JSON manifest: waiting pins with notes and crop paths, overviews,
the sections, and the existing features for the merge step.
"""
import json
import os
import sys

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import model  # noqa: E402

LIKE = (22, 163, 74)
DISLIKE = (220, 38, 38)
MAX_OVERVIEW_W = 900
FONTS = ("/System/Library/Fonts/Helvetica.ttc", "DejaVuSans.ttf", "Arial.ttf")


def font(size):
    for f in FONTS:
        try:
            return ImageFont.truetype(f, size)
        except OSError:
            continue
    return ImageFont.load_default()


def draw_tag(draw, x0, y0, n, color, W):
    tag = max(32, W // 30)
    draw.rectangle((x0, y0, x0 + tag, y0 + tag), fill=color)
    draw.text((x0 + tag / 2, y0 + tag / 2), str(n), fill="white", font=font(int(tag * 0.7)), anchor="mm")


def crop_pin(im, p, color):
    W, H = im.size
    if not p.get("w") and not p.get("h"):  # comment on a spot: neighbourhood with a ring on the spot
        cx, cy = int(p["x"] * W), int(p["y"] * H)
        hw = max(200, W // 7)
        hh = int(hw * 0.7)
        box = (max(0, cx - hw), max(0, cy - hh), min(W, cx + hw), min(H, cy + hh))
        crop = im.crop(box)
        rr = max(10, W // 120)
        ImageDraw.Draw(crop).ellipse((cx - box[0] - rr, cy - box[1] - rr, cx - box[0] + rr, cy - box[1] + rr),
                                     outline=color, width=max(3, rr // 3))
        return crop, (cx, cy, cx, cy), True
    x0, y0 = int(p["x"] * W), int(p["y"] * H)
    x1, y1 = int((p["x"] + p["w"]) * W), int((p["y"] + p["h"]) * H)
    m = max(12, int(0.06 * max(x1 - x0, y1 - y0)))
    return im.crop((max(0, x0 - m), max(0, y0 - m), min(W, x1 + m), min(H, y1 + m))), (x0, y0, x1, y1), False


def main(d, everything=False):
    board = model.load_board(d)
    for sub in ("crops", "overview"):
        os.makedirs(os.path.join(d, "images", sub), exist_ok=True)
    wait = {(w["item"], w["pin"]) for w in model.waiting(board)}
    manifest = {"topic": board["topic"], "language": board["language"], "round": model.pending_round(board),
                "categories": board["categories"], "direction": board["direction"],
                "features": [{k: f[k] for k in ("id", "name", "plain", "scope", "category", "list", "status")}
                             for f in board["features"]],
                "items": []}
    for item in model.live_items(board):
        todo = [p for p in item["pins"] if everything or (item["id"], p["id"]) in wait]
        note_todo = everything or (item["id"], None) in wait
        if not todo and not note_todo:
            continue
        frames = model.frames_of(item)
        ims = [Image.open(os.path.join(d, f)).convert("RGB") for f in frames]
        ovs = [im.copy() for im in ims]
        draws = [ImageDraw.Draw(o) for o in ovs]
        entry = {"id": item["id"], "number": model.item_number(item["id"]), "source": item["source"],
                 "section": item.get("category") or None,
                 "frames": len(frames), "note": item.get("note", ""), "note_waiting": note_todo, "pins": []}
        for n, p in enumerate(item["pins"], 1):
            k = min(max(int(p.get("frame", 0)), 0), len(ims) - 1)
            color = DISLIKE if p.get("kind") == "dislike" else LIKE
            crop, box, point = crop_pin(ims[k], p, color)
            W = ims[k].size[0]
            if point:
                tag = max(32, W // 30)
                draw_tag(draws[k], box[0] - tag // 2, box[1] - tag // 2, n, color, W)
            else:
                draws[k].rectangle(box, outline=color, width=max(3, W // 300))
                draw_tag(draws[k], box[0], box[1], n, color, W)
            if p not in todo:
                continue
            if max(crop.size) < 500:
                z = 500 / float(max(crop.size))
                crop = crop.resize((int(crop.width * z), int(crop.height * z)), Image.LANCZOS)
            rel = os.path.join("images", "crops", "%s-%s.png" % (item["id"], p["id"]))
            crop.save(os.path.join(d, rel))
            entry["pins"].append({"pin": p["id"], "n": n, "kind": p.get("kind", "like"), "note": p.get("note", ""),
                                  "type": "point" if point else "area", "frame": k + 1, "crop": rel,
                                  "edited": p.get("named_note") is not None,
                                  "features": p.get("feature_ids", [])})
        tiles, tile_h = [], 1600
        for k, ov in enumerate(ovs):
            if ov.width > MAX_OVERVIEW_W:
                ov = ov.resize((MAX_OVERVIEW_W, int(ov.height * MAX_OVERVIEW_W / ov.width)), Image.LANCZOS)
            for t, top in enumerate(range(0, ov.height, tile_h)):
                name = "%s-%d.jpg" % (item["id"], k + 1) if ov.height <= tile_h else "%s-%d-%d.jpg" % (item["id"], k + 1, t + 1)
                rel = os.path.join("images", "overview", name)
                ov.crop((0, top, ov.width, min(ov.height, top + tile_h))).save(os.path.join(d, rel), quality=82)
                tiles.append(rel)
        entry["overview"] = tiles
        manifest["items"].append(entry)
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main(os.path.abspath(sys.argv[1]), "--all" in sys.argv[2:])
