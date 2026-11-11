"""Unit tests for the board data model. Run: python3 -m unittest discover -s skills -p 'test_*.py'"""
import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))
import model  # noqa: E402


def board_with_pins():
    b = model.new_board("Website", "en")
    item = model.add_item(b, "https://example.com/", ["images/01-a.png", "images/01-b.png"])
    item["pins"] = [{"id": "p1", "kind": "like", "note": "tight headings", "frame": 0, "x": .1, "y": .1, "w": .2, "h": .1,
                     "named_note": None, "feature_ids": []},
                    {"id": "p2", "kind": "dislike", "note": "", "frame": 1, "x": .5, "y": .5, "w": 0, "h": 0,
                     "named_note": None, "feature_ids": []}]
    return b, item


def first_round(b):
    return model.apply_round(b, {
        "focus": "typography", "summary": "first",
        "features": [{"name": "Tight tracking", "plain": "letters close", "scope": "headings", "category": "typography",
                      "list": "take", "sources": [{"item": "i1", "pin": "p1"}]}],
        "reviewed": [{"item": "i1", "pin": "p1"}, {"item": "i1", "pin": "p2"}],
        "direction": "Calm editorial site.",
    })


class Basics(unittest.TestCase):
    def test_slugify(self):
        self.assertEqual(model.slugify("Strona Alpine (web)"), "strona-alpine-web")
        self.assertEqual(model.slugify("Łódź żółć"), "lodz-zolc")
        self.assertEqual(model.slugify("!!!"), "topic")

    def test_new_board_defaults(self):
        b = model.new_board("Logo", None)
        self.assertEqual(b["language"], "en")
        self.assertEqual(len(b["categories"]), len(model.DEFAULT_CATEGORIES))
        self.assertEqual(model.pending_round(b), 1)
        self.assertEqual(b["categories"][1]["name"], "Color")
        self.assertEqual(model.new_board("Logo", "pl")["categories"][1]["name"], "Kolor")

    def test_item_ids_and_frames(self):
        b = model.new_board("X")
        a = model.add_item(b, "s", ["images/a.png"])
        a["removed"] = True
        c = model.add_item(b, "s", ["images/c.png"])
        self.assertEqual((a["id"], c["id"]), ("i1", "i2"))
        self.assertEqual(model.live_items(b), [c])
        self.assertEqual(model.frames_of({"image": "x.png"}), ["x.png"])
        self.assertEqual(model.item_number("i12"), 12)
        self.assertEqual(model.item_number("bad"), 0)


class Waiting(unittest.TestCase):
    def test_new_pins_and_notes_wait(self):
        b, item = board_with_pins()
        item["note"] = "nice vibe"
        self.assertEqual(model.waiting(b), [{"item": "i1", "pin": None}, {"item": "i1", "pin": "p1"},
                                            {"item": "i1", "pin": "p2"}])

    def test_named_pin_waits_again_after_edit(self):
        b, item = board_with_pins()
        first_round(b)
        self.assertEqual(model.waiting(b), [])
        item["pins"][0]["note"] = "tight headings, only display"
        self.assertEqual(model.waiting(b), [{"item": "i1", "pin": "p1"}])

    def test_removed_items_do_not_wait(self):
        b, item = board_with_pins()
        item["removed"] = True
        self.assertEqual(model.waiting(b), [])


class MergeItems(unittest.TestCase):
    def test_keeps_server_fields_and_unknown_items(self):
        b, item = board_with_pins()
        first_round(b)
        model.add_item(b, "added from chat", ["images/02.png"])
        incoming = {"items": [{"id": "i1", "note": "hi", "removed": False, "pins": [
            {"id": "p1", "kind": "like", "note": "tight headings", "frame": 9, "x": .1, "y": .1, "w": .2, "h": .1},
            {"id": "p3", "kind": "weird", "note": "new", "frame": 0, "x": .3, "y": .3},
            {"id": "bad"}]}, {"id": "nope"}]}
        model.merge_client(b, incoming)
        pins = b["items"][0]["pins"]
        self.assertEqual([p["id"] for p in pins], ["p1", "p3"])
        self.assertEqual(pins[0]["frame"], 1)                      # clamped to the last frame
        self.assertEqual(pins[0]["feature_ids"], ["f1"])            # server-only field kept
        self.assertEqual(pins[0]["named_note"], "tight headings")
        self.assertEqual(pins[1]["kind"], "like")
        self.assertIsNone(pins[1]["named_note"])
        self.assertEqual(len(b["items"]), 2)


class UserEdits(unittest.TestCase):
    def test_feature_set_marks_user_owned(self):
        b, _ = board_with_pins()
        first_round(b)
        n = model.apply_ops(b, [{"op": "feature.set", "id": "f1", "field": "name", "value": "Display tracking"},
                                {"op": "feature.set", "id": "f1", "field": "name", "value": "Display tracking!"},
                                {"op": "feature.set", "id": "f1", "field": "list", "value": "nope"},
                                {"op": "feature.set", "id": "f1", "field": "category", "value": "missing"},
                                {"op": "feature.set", "id": "zz", "field": "name", "value": "x"},
                                {"op": "feature.set", "id": "f1", "field": "sources", "value": []}])
        f = b["features"][0]
        self.assertEqual(n, 2)
        self.assertEqual(f["name"], "Display tracking!")
        self.assertEqual(f["user_edited"], ["name"])

    def test_feature_add_and_direction(self):
        b = model.new_board("X")
        model.apply_ops(b, [{"op": "feature.add", "client_id": "c1", "feature": {"name": "Grain", "category": "bad", "list": "x"}},
                            {"op": "feature.add", "feature": {"name": "Dots", "category": "color", "list": "avoid"}},
                            {"op": "direction.set", "text": "Mine"},
                            {"op": "direction.set", "text": 3}])
        f1, f2 = b["features"]
        self.assertEqual((f1["id"], f1["category"], f1["list"], f1["client_id"]), ("f1", "typography", "take", "c1"))
        self.assertEqual((f2["id"], f2["category"], f2["list"]), ("f2", "color", "avoid"))
        self.assertEqual(set(f1["user_edited"]), set(model.FEATURE_FIELDS))
        self.assertEqual(b["direction"], {"text": "Mine", "user_edited": True, "updated_round": 0})

    def test_categories(self):
        b = model.new_board("X")
        model.apply_ops(b, [{"op": "category.add", "name": "Patterns"}, {"op": "category.add", "name": "Patterns"},
                            {"op": "category.add", "name": "  "}, {"op": "category.rename", "id": "patterns", "name": "Dot patterns"},
                            {"op": "feature.add", "feature": {"name": "a", "category": "color"}},
                            {"op": "category.delete", "id": "color"}, {"op": "category.delete", "id": "patterns-2"}])
        ids = [c["id"] for c in b["categories"]]
        self.assertIn("color", ids)                    # used -> not deleted
        self.assertIn("patterns", ids)
        self.assertNotIn("patterns-2", ids)
        self.assertEqual(next(c for c in b["categories"] if c["id"] == "patterns")["name"], "Dot patterns")

    def test_last_category_is_not_deleted(self):
        b = model.new_board("X")
        b["categories"] = b["categories"][:1]
        self.assertEqual(model.apply_ops(b, [{"op": "category.delete", "id": "typography"}]), 0)


class Rounds(unittest.TestCase):
    def test_first_round_creates_features_and_links_pins(self):
        b, item = board_with_pins()
        res = first_round(b)
        self.assertEqual(res["added"], ["f1"])
        self.assertEqual(item["pins"][0]["feature_ids"], ["f1"])
        self.assertEqual(item["pins"][1]["feature_ids"], [])
        self.assertEqual(b["direction"]["text"], "Calm editorial site.")
        r = b["rounds"][0]
        self.assertEqual((r["n"], r["focus"], r["named"], r["features_added"], r["items_added"]), (1, "typography", 2, 1, 1))

    def test_user_edits_win_and_become_conflicts(self):
        b, _ = board_with_pins()
        first_round(b)
        model.apply_ops(b, [{"op": "feature.set", "id": "f1", "field": "name", "value": "Mine"},
                            {"op": "direction.set", "text": "My direction"}])
        res = model.apply_round(b, {
            "features": [{"id": "f1", "name": "Agent name", "scope": "display only", "category": "unknown",
                          "sources": [{"item": "i1", "pin": "p1"}, {"item": "i1", "pin": None}], "why": "new pin"}],
            "direction": "Agent direction", "direction_why": "more pins"})
        f = b["features"][0]
        self.assertEqual(f["name"], "Mine")                 # user-owned, not overwritten
        self.assertEqual(f["scope"], "display only")        # untouched field updated
        self.assertEqual(f["category"], "typography")       # invalid value ignored
        self.assertEqual(len(f["sources"]), 2)
        self.assertEqual(res["changed"], ["f1"])
        self.assertEqual(b["direction"]["text"], "My direction")
        self.assertEqual([(c["field"], c["proposed"], c["why"]) for c in res["conflicts"]],
                         [("name", "Agent name", "new pin"), ("direction", "Agent direction", "more pins")])
        self.assertEqual(b["rounds"][-1]["conflicts"], 2)

    def test_new_feature_with_new_category_and_reviewed_note(self):
        b, item = board_with_pins()
        item["note"] = "vibe"
        model.apply_round(b, {"categories": [{"id": "patterns", "name": "Patterns"}, {"id": "color"}],
                              "features": [{"name": "Dots", "category": "patterns", "sources": [{"item": "i1", "pin": None}]},
                                           {"name": "Bad cat", "category": "nope"}],
                              "reviewed": [{"item": "i1", "pin": None}, {"item": "zz", "pin": None}]})
        self.assertEqual(b["features"][0]["category"], "patterns")
        self.assertEqual(b["features"][1]["category"], "typography")
        self.assertEqual(item["named_note"], "vibe")
        self.assertEqual(sum(1 for c in b["categories"] if c["id"] == "color"), 1)

    def test_unchanged_direction_is_no_conflict(self):
        b, _ = board_with_pins()
        first_round(b)
        model.apply_ops(b, [{"op": "direction.set", "text": "Calm editorial site."}])
        res = model.apply_round(b, {"direction": "Calm editorial site."})
        self.assertEqual(res["conflicts"], [])

    def test_accept_returns_field_to_agent(self):
        b, _ = board_with_pins()
        first_round(b)
        model.apply_ops(b, [{"op": "feature.set", "id": "f1", "field": "name", "value": "Mine"},
                            {"op": "direction.set", "text": "Mine"}])
        done = model.apply_accept(b, [{"feature": "f1", "field": "name", "value": "Agent"},
                                      {"field": "direction", "value": "Agent dir"},
                                      {"feature": "f1", "field": "list", "value": "bad"},
                                      {"feature": "zz", "field": "name", "value": "x"}])
        self.assertEqual(done, 2)
        self.assertEqual(b["features"][0]["name"], "Agent")
        self.assertEqual(b["features"][0]["user_edited"], [])
        self.assertEqual(b["direction"], {"text": "Agent dir", "user_edited": False, "updated_round": 1})

    def test_accept_field_not_user_owned(self):
        b, _ = board_with_pins()
        first_round(b)
        self.assertEqual(model.apply_accept(b, [{"feature": "f1", "field": "scope", "value": "all"}]), 1)


class Markdown(unittest.TestCase):
    def test_render_full(self):
        b, item = board_with_pins()
        b["language"] = "pl"
        item["note"] = "spokój"
        first_round(b)
        model.apply_ops(b, [{"op": "feature.add", "feature": {"name": "Gone", "category": "color"}},
                            {"op": "feature.set", "id": "f2", "field": "status", "value": "dropped"}])
        item["pins"][1]["note"] = "too busy | loud"
        md = model.render_markdown(b, exists=lambda rel: rel in ("images/overview/i1-1-1.jpg", "images/crops/i1-p1.png"))
        self.assertIn("# Inspiracje · Website", md)
        self.assertIn("## Kierunek\nCalm editorial site.", md)
        self.assertIn("### Typography", md)  # board created in en, language switched later
        self.assertIn("| Tight tracking | letters close | headings | #1 pin 1 |", md)
        self.assertIn("## Czego unikam\nJeszcze nic.", md)
        self.assertIn("![](images/overview/i1-1-1.jpg)", md)
        self.assertIn("1. 👍 **Tight tracking** - tight headings", md)
        self.assertIn("   ![](images/crops/i1-p1.png)", md)
        self.assertIn("2. 👎 too busy | loud", md)
        self.assertIn("Ogólnie: spokój", md)
        self.assertIn("## Odrzucone\n- Gone (Color)", md)
        self.assertIn("runda 1 · typography · +1 nowe, 0 zmienione - first", md)
        self.assertIn("2 czeka na nazwanie", md)  # overall note + edited pin 2

    def test_render_empty_and_file_source(self):
        b = model.new_board("Empty", "xx")
        model.add_item(b, "file: a.png", ["images/a.png"])
        md = model.render_markdown(b)
        self.assertIn("## Direction\nNothing yet.", md)
        self.assertIn("### #1 · file: a.png", md)
        self.assertNotIn("Round history", md)

    def test_source_labels(self):
        b, _ = board_with_pins()
        lab = model.LABELS["en"]
        self.assertEqual(model.source_label(b, {"item": "i1", "pin": None}, lab), "#1")
        self.assertEqual(model.source_label(b, {"item": "i1", "pin": "p2"}, lab), "#1 pin 2")
        self.assertEqual(model.source_label(b, {"item": "i1", "pin": "gone"}, lab), "#1")
        self.assertEqual(model.source_label(b, {"item": "i9", "pin": "p1"}, lab), "#9")


class Files(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = os.path.join(self.tmp.name, "inspirations")

    def tearDown(self):
        self.tmp.cleanup()

    def test_create_list_find(self):
        d, created = model.create_topic(self.root, "Strona Alpine", "pl")
        self.assertTrue(created)
        self.assertEqual(model.create_topic(self.root, "strona alpine")[1], False)
        model.create_topic(self.root, "Logo Alpine")
        model.create_topic(self.root, "Deck")
        b = model.load_board(d)
        model.add_item(b, "s", ["images/x.png"])
        model.save_board(d, b)
        topics = model.list_topics(self.root)
        self.assertEqual(sorted(t["slug"] for t in topics), ["deck", "logo-alpine", "strona-alpine"])
        t = next(t for t in topics if t["slug"] == "strona-alpine")
        self.assertEqual((t["items"], t["thumb"], t["legacy"]), (1, "images/x.png", False))
        self.assertEqual(model.find_topic(self.root, "Strona Alpine")["slug"], "strona-alpine")
        self.assertEqual(model.find_topic(self.root, "deck fm")["slug"], "deck")
        self.assertEqual(model.find_topic(self.root, "logo")["slug"], "logo-alpine")
        self.assertIsNone(model.find_topic(self.root, "alpine"))      # ambiguous
        self.assertIsNone(model.find_topic(self.root, "packaging"))
        self.assertEqual(model.list_topics(os.path.join(self.tmp.name, "missing")), [])

    def test_legacy_folder_is_listed_read_only(self):
        d = os.path.join(self.root, "2026-11-10-old")
        os.makedirs(d)
        model.save_json(os.path.join(d, "pins.json"), {"topic": "Old", "created": "2026-11-10",
                                                        "items": [{"id": "i1", "image": "images/a.png", "pins": []}]})
        os.makedirs(os.path.join(self.root, "random-folder"))
        self.assertTrue(model.is_legacy(d))
        t = model.list_topics(self.root)
        self.assertEqual(len(t), 1)
        self.assertEqual((t[0]["topic"], t[0]["legacy"], t[0]["waiting"], t[0]["thumb"]), ("Old", True, 0, "images/a.png"))
        self.assertTrue(model.load_legacy(d)["legacy"])

    def test_save_is_atomic_json(self):
        p = os.path.join(self.tmp.name, "x.json")
        model.save_json(p, {"a": "ż"})
        with open(p, encoding="utf-8") as f:
            self.assertEqual(json.load(f), {"a": "ż"})
        self.assertIsNone(model.load_json(os.path.join(self.tmp.name, "none.json")))
        self.assertFalse(os.path.exists(p + ".tmp"))

    def test_find_inspirations_dir(self):
        proj = os.path.join(self.tmp.name, "proj")
        sub = os.path.join(proj, "a", "b")
        os.makedirs(sub)
        lib = os.path.join(self.tmp.name, "lib")
        self.assertEqual(model.find_inspirations_dir(sub, proj, lib), (os.path.join(proj, "inspirations"), "git"))
        os.makedirs(os.path.join(proj, "a", "inspirations"))
        self.assertEqual(model.find_inspirations_dir(sub, proj, lib), (os.path.join(proj, "a", "inspirations"), "existing"))
        loose = os.path.join(self.tmp.name, "loose")
        os.makedirs(loose)
        self.assertEqual(model.find_inspirations_dir(loose, None, lib), (lib, "library"))
        self.assertEqual(model.find_inspirations_dir(loose, None, None), (None, "ask"))
        open(os.path.join(loose, "AGENTS.md"), "w").close()
        self.assertEqual(model.find_inspirations_dir(loose, None, None), (os.path.join(loose, "inspirations"), "project"))


if __name__ == "__main__":
    unittest.main()
