"""Unit tests for the board data model. Run: pnpm test:skills"""
import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))
import model  # noqa: E402


def board_with_pins(language="en"):
    b = model.new_board("Website", language)
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

    def test_new_board_starts_without_sections(self):
        b = model.new_board("Logo", None)
        self.assertEqual((b["language"], b["categories"]), ("en", []))
        self.assertEqual(model.pending_round(b), 1)

    def test_suggestions_follow_language(self):
        self.assertEqual(model.suggested_categories("en")[1], {"id": "color", "name": "Color"})
        self.assertEqual(model.suggested_categories("pl")[1], {"id": "color", "name": "Kolor"})

    def test_item_ids_and_frames(self):
        b = model.new_board("X")
        a = model.add_item(b, "s", ["images/a.png"])
        a["removed"] = True
        c = model.add_item(b, "s", ["images/c.png"])
        self.assertEqual((a["id"], c["id"], c["category"]), ("i1", "i2", model.UNSORTED))
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


class Sections(unittest.TestCase):
    def test_add_uses_vocabulary_ids_and_dedupes(self):
        b = model.new_board("X", "pl")
        self.assertEqual(model.add_category(b, "Kolor"), "color")
        self.assertEqual(model.add_category(b, "", "typography"), "typography")
        self.assertEqual(model.add_category(b, "Patterns"), "patterns")
        self.assertEqual(model.add_category(b, "patterns"), "patterns")
        self.assertEqual([c["name"] for c in b["categories"]], ["Kolor", "Typografia", "Patterns"])

    def test_ops_add_rename_delete(self):
        b, item = board_with_pins()
        n = model.apply_ops(b, [{"op": "category.add", "name": "Hero"}, {"op": "category.add", "name": " "},
                                {"op": "category.rename", "id": "hero", "name": "Hero section"},
                                {"op": "category.rename", "id": "nope", "name": "x"},
                                {"op": "category.delete", "id": "nope"}, {"op": "unknown"}])
        self.assertEqual(n, 2)
        self.assertEqual(b["categories"], [{"id": "hero", "name": "Hero section"}])
        item["category"] = "hero"
        model.apply_ops(b, [{"op": "category.delete", "id": "hero"}])
        self.assertEqual((b["categories"], item["category"]), ([], model.UNSORTED))

    def test_category_name_falls_back(self):
        b = model.new_board("X", "pl")
        model.add_category(b, "Mine")
        self.assertEqual(model.category_name(b, "mine"), "Mine")
        self.assertEqual(model.category_name(b, "color"), "Kolor")
        self.assertEqual(model.category_name(b, "weird"), "weird")


class MergeClient(unittest.TestCase):
    def test_keeps_server_fields_unknown_items_and_moves_sections(self):
        b, item = board_with_pins()
        first_round(b)
        model.add_item(b, "added from chat", ["images/02.png"])
        incoming = {"ops": [{"op": "category.add", "name": "Hero"}],
                    "items": [{"id": "i1", "note": "hi", "removed": False, "category": "hero", "pins": [
                        {"id": "p1", "kind": "like", "note": "tight headings", "frame": 9, "x": .1, "y": .1, "w": .2, "h": .1},
                        {"id": "p3", "kind": "weird", "note": "new", "frame": 0, "x": .3, "y": .3},
                        {"id": "bad"}]},
                              {"id": "i2", "category": "missing", "pins": []}, {"id": "nope"}]}
        self.assertEqual(model.merge_client(b, incoming), 1)
        i1, i2 = b["items"]
        self.assertEqual(i1["category"], "hero")              # section created in the same save
        self.assertEqual(i2["category"], model.UNSORTED)      # unknown section ignored
        self.assertEqual([p["id"] for p in i1["pins"]], ["p1", "p3"])
        self.assertEqual(i1["pins"][0]["frame"], 1)           # clamped to the last frame
        self.assertEqual(i1["pins"][0]["feature_ids"], ["f1"])
        self.assertEqual(i1["pins"][0]["named_note"], "tight headings")
        self.assertEqual(i1["pins"][1]["kind"], "like")
        self.assertIsNone(i1["pins"][1]["named_note"])

    def test_item_without_category_field_keeps_its_section(self):
        b, item = board_with_pins()
        model.add_category(b, "Hero")
        item["category"] = "hero"
        model.merge_items(b, [{"id": "i1", "pins": []}])
        self.assertEqual(item["category"], "hero")


class Rounds(unittest.TestCase):
    def test_first_round_creates_features_section_and_links_pins(self):
        b, item = board_with_pins()
        res = first_round(b)
        self.assertEqual(res["added"], ["f1"])
        self.assertEqual([c["id"] for c in b["categories"]], ["typography"])   # created from the vocabulary
        self.assertEqual(item["pins"][0]["feature_ids"], ["f1"])
        self.assertEqual(item["pins"][1]["feature_ids"], [])
        self.assertEqual(b["direction"]["text"], "Calm editorial site.")
        r = b["rounds"][0]
        self.assertEqual((r["n"], r["focus"], r["named"], r["features_added"], r["items_added"]), (1, "typography", 2, 1, 1))

    def test_updates_existing_feature_directly(self):
        b, _ = board_with_pins()
        first_round(b)
        res = model.apply_round(b, {"features": [{"id": "f1", "name": "Display tracking", "list": "nope", "status": "x",
                                                  "category": "custom-area",
                                                  "sources": [{"item": "i1", "pin": "p1"}, {"item": "i1", "pin": None}]},
                                                 {"id": "f1", "scope": "headings"}],
                                    "direction": "New direction"})
        f = b["features"][0]
        self.assertEqual((f["name"], f["list"], f["status"], f["category"]), ("Display tracking", "take", "active", "custom-area"))
        self.assertEqual(len(f["sources"]), 2)
        self.assertEqual(res["changed"], ["f1"])
        self.assertEqual(b["direction"], {"text": "New direction", "updated_round": 2})

    def test_feature_category_defaults_to_source_section(self):
        b, item = board_with_pins()
        model.add_category(b, "Hero")
        item["category"] = "hero"
        model.apply_round(b, {"features": [{"name": "A", "sources": [{"item": "i1", "pin": "p1"}]},
                                           {"name": "B", "list": "avoid", "status": "dropped"}]})
        self.assertEqual(b["features"][0]["category"], "hero")
        self.assertEqual((b["features"][1]["category"], b["features"][1]["list"], b["features"][1]["status"]),
                         (model.UNSORTED, "avoid", "dropped"))

    def test_sort_only_unsorted_items_and_reviewed_note(self):
        b, item = board_with_pins()
        item["note"] = "vibe"
        other = model.add_item(b, "x", ["images/x.png"])
        model.add_category(b, "Hero")
        other["category"] = "hero"
        res = model.apply_round(b, {"categories": [{"name": "Patterns"}, {}],
                                    "sort": [{"item": "i1", "category": "color"}, {"item": "i2", "category": "color"},
                                             {"item": "zz", "category": "color"}, {"item": "i1"}],
                                    "reviewed": [{"item": "i1", "pin": None}, {"item": "zz", "pin": None}]})
        self.assertEqual(res["sorted"], ["i1"])
        self.assertEqual((item["category"], other["category"]), ("color", "hero"))
        self.assertEqual([c["id"] for c in b["categories"]], ["hero", "patterns", "color"])
        self.assertEqual(item["named_note"], "vibe")

    def test_unchanged_direction_keeps_round(self):
        b, _ = board_with_pins()
        first_round(b)
        model.apply_round(b, {"direction": "Calm editorial site."})
        self.assertEqual(b["direction"]["updated_round"], 1)


class Markdown(unittest.TestCase):
    def test_render_with_sections(self):
        b, item = board_with_pins("pl")
        item["note"] = "spokój"
        first_round(b)
        model.add_item(b, "file: b.png", ["images/b.png"])
        item["category"] = "typography"
        model.apply_round(b, {"features": [{"name": "Gone", "category": "color", "status": "dropped"},
                                           {"name": "Loose", "sources": [{"item": "i2", "pin": None}]}]})
        item["pins"][1]["note"] = "too busy | loud"
        md = model.render_markdown(b, exists=lambda rel: rel in ("images/overview/i1-1-1.jpg", "images/crops/i1-p1.png"))
        self.assertIn("# Inspiracje · Website", md)
        self.assertIn("## Kierunek\nCalm editorial site.", md)
        self.assertIn("### Typografia", md)
        self.assertIn("| Tight tracking | letters close | headings | #1 pin 1 |", md)
        self.assertIn("### Inne", md)                                   # feature without a section
        self.assertIn("## Czego unikam\nJeszcze nic.", md)
        self.assertIn("### Bez sekcji\n\n#### #2 · file: b.png", md)
        self.assertIn("#### #1 · example.com", md)
        self.assertIn("![](images/overview/i1-1-1.jpg)", md)
        self.assertIn("1. 👍 **Tight tracking** - tight headings", md)
        self.assertIn("   ![](images/crops/i1-p1.png)", md)
        self.assertIn("2. 👎 too busy | loud", md)
        self.assertIn("Ogólnie: spokój", md)
        self.assertIn("## Odrzucone\n- Gone (Kolor)", md)
        self.assertIn("runda 1 · typography · +1 nowe, 0 zmienione - first", md)
        self.assertIn("2 czeka na nazwanie", md)  # overall note + edited pin 2

    def test_render_without_sections(self):
        b = model.new_board("Empty", "xx")
        model.add_item(b, "file: a.png", ["images/a.png"])
        md = model.render_markdown(b)
        self.assertIn("## Direction\nNothing yet.", md)
        self.assertIn("### #1 · file: a.png", md)
        self.assertNotIn("Unsorted", md)
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
