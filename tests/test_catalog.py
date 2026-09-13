#!/usr/bin/env python3
"""Test cases for catalog/filters.json.

Standard library only — no pytest, no dependencies, so this runs anywhere Python does.

    python tests/test_catalog.py          # run everything
    python -m unittest discover tests     # same, via unittest

Two kinds of tests live here, and they guard different failure modes:

1. Invariants (TestRegistry, TestParameters, TestProvenance)
   Structural rules that must hold for *every* filter, present and future. They catch
   a malformed entry the moment it is added, with no maintenance cost.

2. Pinned cases (TestCaseBook, loaded from tests/cases.json)
   Exact expected values for the recipes this repository authors itself. Upstream
   recipes are already locked by tools/check_fidelity.py against the upstream Java;
   the ones we invent have no upstream to compare against, so this file *is* their
   specification. Change a value here and in filters.json at the same time, on purpose.

   TestAuthoredHaveCases enforces the rule that makes this stick: an entry marked
   source=authored-here with no pinned case fails the suite. You cannot add a
   home-grown recipe without also writing down what it is supposed to be.
"""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CATALOG = ROOT / "catalog" / "filters.json"
CASES = ROOT / "tests" / "cases.json"

# --- constraint tables, mirrored from tools/validate_catalog.py ------------------
# Duplicated on purpose: a test that imports the validator's table would go green
# if someone "fixed" the table to match a bad catalog. The test has to be able to
# disagree with the code it tests.
VALID_STYLES = {
    "STD", "VIVID", "NEUTRAL", "PORTRAIT", "LANDSCAPE", "MONO",
    "CLEAR", "DEEP", "LIGHT", "SUNSET", "NIGHT", "AUTUMN", "SEPIA",
}
CORE_SLIDER_RANGE = (-16, 16)
WB_MODES = {"AUTO", "K"}
KELVIN_RANGE = (2500, 9900)
AB_RANGE = (-7, 7)
GM_RANGE = (-7, 7)
PE_SUB_COUNT = {5: 3, 1: 5, 6: 4, 3: 2}
EV_RANGE = (-5, 5)
DRO_VALUES = {0, 1, 2, 3, 4, 5, 6}
ENGINES = {"recipe-lab", "film-studio-matrix"}
SOURCES = {"recipe-lab", "film-studio", "authored-here"}
TONES = {"color", "mono"}

with CATALOG.open(encoding="utf-8") as fh:
    CATALOG_DATA = json.load(fh)

FILTERS = CATALOG_DATA["filters"]
BY_ID = {f["id"]: f for f in FILTERS}
RECIPE_LAB = [f for f in FILTERS if f["engine"] == "recipe-lab"]


def _load_cases() -> dict:
    if not CASES.exists():
        return {}
    with CASES.open(encoding="utf-8") as fh:
        return json.load(fh)


CASES_DATA = _load_cases()


class TestRegistry(unittest.TestCase):
    """The file has to be a well-formed registry before it can be anything else."""

    def test_ids_are_unique(self):
        seen = {}
        for i, f in enumerate(FILTERS):
            self.assertNotIn(f["id"], seen, f"duplicate id at index {i}")
            seen[f["id"]] = i

    def test_required_fields_present(self):
        for f in FILTERS:
            with self.subTest(id=f["id"]):
                for field in ("id", "name", "group", "engine", "source", "tone"):
                    self.assertIn(field, f, f"{f['id']} is missing {field}")
                    self.assertTrue(str(f[field]).strip())
                self.assertIsInstance(f["verified"], bool)

    def test_enumerations_are_valid(self):
        for f in FILTERS:
            with self.subTest(id=f["id"]):
                self.assertIn(f["engine"], ENGINES)
                self.assertIn(f["source"], SOURCES)
                self.assertIn(f["tone"], TONES)

    def test_groups_are_declared(self):
        declared = {g["id"] for g in CATALOG_DATA["groups"]}
        for f in FILTERS:
            with self.subTest(id=f["id"]):
                self.assertIn(f["group"], declared,
                              f"{f['id']} uses undeclared group {f['group']!r}")

    def test_declared_groups_are_not_empty(self):
        used = {f["group"] for f in FILTERS}
        for g in CATALOG_DATA["groups"]:
            with self.subTest(group=g["id"]):
                self.assertIn(g["id"], used,
                              f"group {g['id']!r} is declared but has no filters")

    def test_cross_refs_resolve_both_ways(self):
        for f in FILTERS:
            ref = f.get("cross_ref")
            if ref is None:
                continue
            with self.subTest(id=f["id"]):
                self.assertIn(ref, BY_ID, f"cross_ref {ref!r} does not exist")
                self.assertEqual(BY_ID[ref].get("cross_ref"), f["id"],
                                 f"cross_ref to {ref!r} is not reciprocated")

    def test_recipe_lab_entries_are_contiguous_per_group(self):
        """The generator emits one Java array per group run; interleaving would
        silently duplicate a group header."""
        order = []
        for f in RECIPE_LAB:
            if not order or order[-1] != f["group"]:
                self.assertNotIn(f["group"], order,
                                 f"group {f['group']!r} appears in two separate runs")
                order.append(f["group"])


class TestParameters(unittest.TestCase):
    """Every value has to be something the camera will actually accept.

    These mirror validate_catalog.py. The validator is the friendly explanation;
    this is the part that fails the build.
    """

    def _check_int(self, fid, field, value, lo, hi):
        self.assertIsInstance(value, int, f"{fid}: {field} must be int, got {value!r}")
        self.assertNotIsInstance(value, bool, f"{fid}: {field} must not be a bool")
        self.assertTrue(lo <= value <= hi, f"{fid}: {field}={value} outside {lo}..{hi}")

    def test_recipe_lab_entries_have_a_recipe(self):
        for f in RECIPE_LAB:
            with self.subTest(id=f["id"]):
                self.assertIsInstance(f.get("recipe"), dict)

    def test_styles_are_real(self):
        for f in RECIPE_LAB:
            with self.subTest(id=f["id"]):
                self.assertIn(f["recipe"]["style"], VALID_STYLES)

    def test_sliders_in_range(self):
        for f in RECIPE_LAB:
            r = f["recipe"]
            for field in ("sat", "con", "sharp"):
                with self.subTest(id=f["id"], field=field):
                    self._check_int(f["id"], field, r[field], *CORE_SLIDER_RANGE)

    def test_matrix_is_a_flag(self):
        for f in RECIPE_LAB:
            with self.subTest(id=f["id"]):
                self.assertIn(f["recipe"]["matrix"], (0, 1))

    def test_white_balance_is_consistent(self):
        for f in RECIPE_LAB:
            wb = f["recipe"]["wb"]
            with self.subTest(id=f["id"]):
                self.assertIn(wb["mode"], WB_MODES)
                if wb["mode"] == "AUTO":
                    self.assertEqual(wb["kelvin"], 0,
                                     "AUTO white balance must not carry a kelvin value")
                else:
                    self._check_int(f["id"], "wb.kelvin", wb["kelvin"], *KELVIN_RANGE)
                self._check_int(f["id"], "wb.ab", wb["ab"], *AB_RANGE)
                self._check_int(f["id"], "wb.gm", wb["gm"], *GM_RANGE)

    def test_picture_effect_and_sub_agree(self):
        """A sub-value on an effect that has no sub-parameter is a stored setting
        that does nothing — confusing, and a sign the author guessed."""
        for f in RECIPE_LAB:
            r = f["recipe"]
            pe, sub = r["pe"], r["sub"]
            with self.subTest(id=f["id"]):
                self.assertIsInstance(pe, int)
                self.assertTrue(0 <= pe <= 13, f"pe={pe} is not a known effect index")
                self.assertIsInstance(sub, int)
                if pe == 0:
                    self.assertEqual(sub, 0, "pe=off cannot carry a sub value")
                else:
                    expected = PE_SUB_COUNT.get(pe)
                    if expected is None:
                        self.assertEqual(sub, 0, f"pe={pe} has no sub-parameter")
                    else:
                        self.assertTrue(0 <= sub < expected,
                                        f"pe={pe} takes sub 0..{expected - 1}, got {sub}")

    def test_exposure_and_dro(self):
        for f in RECIPE_LAB:
            r = f["recipe"]
            with self.subTest(id=f["id"]):
                self._check_int(f["id"], "ev", r["ev"], *EV_RANGE)
                self.assertIn(r["dro"], DRO_VALUES)

    def test_film_studio_entries_carry_no_parameters(self):
        """Hard rule, not a style preference: see the note in TestProvenance."""
        for f in FILTERS:
            if f["engine"] != "film-studio-matrix":
                continue
            with self.subTest(id=f["id"]):
                self.assertIsNone(f.get("recipe"),
                                  "matrix looks are catalogued by name only")
                self.assertEqual(f.get("strengths"), [30, 50, 70, 100])


class TestProvenance(unittest.TestCase):
    """Keep the repository honest about where each look came from.

    Two upstreams, two very different licences. Recipe Lab is MIT and its numbers
    are transcribed verbatim (locked by check_fidelity.py). The film-studio project
    is PolyForm Noncommercial and ships no base APK, so its looks are recorded by
    name and never by parameter. Blurring that line is the one mistake that would
    make this repository unsafe to host, so it is tested rather than documented.
    """

    def test_film_studio_is_never_described_as_mit(self):
        license_ = CATALOG_DATA["engines"]["film-studio-matrix"].get("license", "")
        self.assertFalse(license_.startswith("MIT"),
                         "the matrix engine is not MIT — do not relabel it")

    def test_no_film_studio_parameters_anywhere(self):
        for f in FILTERS:
            if f.get("source") == "film-studio":
                with self.subTest(id=f["id"]):
                    self.assertIsNone(f.get("recipe"),
                                      "noncommercial upstream: name only, no parameters")

    def test_authored_entries_are_marked_unverified(self):
        """Anything we invent has not been on a camera. Say so, in the data."""
        for f in FILTERS:
            if f.get("source") != "authored-here":
                continue
            with self.subTest(id=f["id"]):
                self.assertFalse(f["verified"],
                                 f"{f['id']} is ours and unverified — verified must stay false")
                self.assertTrue(f.get("note", "").strip(),
                                f"{f['id']} needs a note explaining what it approximates")

    def test_upstream_recipe_count_is_stable(self):
        """77 is the number Recipe Lab ships. A different number means a merge
        dropped or duplicated something, not that the project grew."""
        n = sum(1 for f in FILTERS if f.get("source") == "recipe-lab")
        self.assertEqual(n, 77, "upstream-sourced recipe count changed unexpectedly")


class TestCaseBook(unittest.TestCase):
    """Pinned expected values, loaded from tests/cases.json.

    These are the recipes we wrote ourselves. Nothing upstream pins them, so this
    file is the specification: if a value here and in the catalog disagree, one of
    them was changed without the other, and that is always worth stopping for.
    """

    @classmethod
    def setUpClass(cls):
        cls.cases = CASES_DATA.get("cases", [])

    def test_case_file_parses(self):
        self.assertTrue(CASES.exists(), f"missing {CASES}")
        self.assertIsInstance(self.cases, list)

    def test_case_ids_are_unique(self):
        seen = set()
        for c in self.cases:
            with self.subTest(id=c.get("id")):
                self.assertNotIn(c["id"], seen)
                seen.add(c["id"])

    def test_every_case_matches_the_catalog(self):
        self.assertTrue(self.cases, "no test cases defined")
        for c in self.cases:
            with self.subTest(case=c["id"]):
                self.assertIn(c["id"], BY_ID, f"{c['id']} is not in the catalog")
                actual = BY_ID[c["id"]]
                for key, want in c.get("fields", {}).items():
                    self.assertEqual(actual.get(key), want, f"{c['id']}.{key}")
                for key, want in c.get("recipe", {}).items():
                    self.assertEqual(actual.get("recipe", {}).get(key), want,
                                     f"{c['id']}.recipe.{key}")

    def test_case_recipes_are_complete(self):
        """A pinned recipe that lists only some fields would pass while letting
        the rest drift. Pin the whole thing."""
        full = {"style", "sat", "con", "sharp", "matrix", "wb", "pe", "sub", "ev", "dro"}
        for c in self.cases:
            if "recipe" not in c:
                continue
            with self.subTest(case=c["id"]):
                self.assertEqual(set(c["recipe"]), full,
                                 f"{c['id']} pins a partial recipe")


class TestAuthoredHaveCases(unittest.TestCase):
    """The rule that makes the test-case requirement self-enforcing.

    Adding a home-grown recipe without writing a case for it fails the suite. This
    is deliberately stricter than the validator: it is the difference between
    "this recipe is legal" and "someone wrote down what this recipe is".
    """

    def test_every_authored_filter_has_a_pinned_case(self):
        pinned = {c["id"] for c in CASES_DATA.get("cases", [])}
        for f in FILTERS:
            if f.get("source") != "authored-here":
                continue
            with self.subTest(id=f["id"]):
                self.assertIn(f["id"], pinned,
                              f"{f['id']} is authored here but has no case in tests/cases.json")

    def test_every_pinned_case_points_at_an_authored_filter(self):
        """A case for an upstream recipe is dead weight — check_fidelity.py already
        covers those against the upstream Java."""
        for c in CASES_DATA.get("cases", []):
            with self.subTest(case=c["id"]):
                self.assertIn(c["id"], BY_ID)
                self.assertEqual(BY_ID[c["id"]].get("source"), "authored-here",
                                 f"{c['id']} is not authored here; drop its pinned case")


class TestGenerator(unittest.TestCase):
    """The catalog is meaningless until it becomes Java the APK can compile.

    Imports the generator rather than spawning it, so a broken generator shows up
    as a test failure with a traceback instead of a silent pass.
    """

    @classmethod
    def setUpClass(cls):
        tools = str(ROOT / "tools")
        sys.path.insert(0, tools)
        try:
            import gen_recipes  # noqa: PLC0415
        finally:
            sys.path.remove(tools)
        cls.java = gen_recipes.generate(CATALOG_DATA)
        cls.lines = cls.java.splitlines()

    def test_generator_exposes_generate(self):
        self.assertIsInstance(self.java, str)
        self.assertTrue(self.java.strip())

    def test_one_java_entry_per_recipe(self):
        emitted = self.java.count("new Recipe(")
        self.assertEqual(emitted, len(RECIPE_LAB),
                         f"Java emits {emitted} entries, catalog has {len(RECIPE_LAB)}")

    def test_every_recipe_name_is_emitted(self):
        """The Java carries the display name, not the catalog id — the id never
        reaches the camera, the name is what the user picks on screen."""
        missing = [f["name"] for f in RECIPE_LAB if f'"{f["name"]}"' not in self.java]
        self.assertEqual(missing, [], f"never made it into Recipes.java: {missing}")

    def test_recipe_names_are_unique(self):
        """Two recipes with the same name are indistinguishable in the app's list.

        Scoped to recipe-lab because that is the only engine that reaches the Java
        list — a matrix look is allowed to reuse its recipe-lab twin's name, that
        pairing is the whole point of cross_ref.
        """
        seen = {}
        for f in RECIPE_LAB:
            self.assertNotIn(f["name"], seen,
                             f"{f['id']} reuses the name of {seen.get(f['name'])}")
            seen[f["name"]] = f["id"]

    def test_unverified_recipes_are_flagged_in_the_output(self):
        """A look we invented must say so in the generated Java too, not just in
        the catalog. Someone reading Recipes.java deserves the same warning."""
        for f in RECIPE_LAB:
            if f.get("verified", True):
                continue
            with self.subTest(id=f["id"]):
                hit = [ln for ln in self.lines if f'"{f["name"]}"' in ln]
                self.assertTrue(hit, f"{f['id']} has no line in the generated Java")
                self.assertIn("NOT VERIFIED ON HARDWARE", hit[0],
                              f"{f['id']} is unverified but generated without the warning")

    def test_upstream_ids_are_all_present(self):
        """The 77 upstream ids are load-bearing: check_fidelity.py matches on them."""
        upstream_ids = {f["id"] for f in FILTERS if f.get("source") == "recipe-lab"}
        self.assertEqual(len(upstream_ids), 77)


class TestPinnedUpstream(unittest.TestCase):
    """The release build clones upstream at a fixed commit.

    If that pin drifts from the revision the catalog claims to have been validated
    against, a tag can silently build against different upstream code than the one
    the recipes were checked against. The two live in different files, so nothing
    but a test can hold them together.
    """

    @staticmethod
    def _sha_in_catalog() -> str | None:
        rev = CATALOG_DATA["sources"]["recipe-lab"].get("fetched_rev", "")
        for token in rev.replace("@", " ").split():
            if len(token) == 40 and all(c in "0123456789abcdef" for c in token.lower()):
                return token.lower()
        return None

    @staticmethod
    def _sha_in_workflow() -> str | None:
        path = ROOT / ".github" / "workflows" / "release.yml"
        if not path.exists():
            return None
        for line in path.read_text(encoding="utf-8").splitlines():
            if "UPSTREAM_SHA:" in line:
                return line.split(":", 1)[1].strip().strip('"').lower()
        return None

    def test_catalog_pins_a_full_sha(self):
        self.assertIsNotNone(self._sha_in_catalog(),
                             "sources.recipe-lab.fetched_rev should carry a 40-char SHA")

    def test_release_workflow_pins_the_same_sha(self):
        cat, wf = self._sha_in_catalog(), self._sha_in_workflow()
        self.assertIsNotNone(wf, "release.yml has no UPSTREAM_SHA")
        self.assertEqual(cat, wf,
                         "upstream pin drifted: catalog says "
                         f"{cat}, release.yml builds {wf}. Update both.")


if __name__ == "__main__":
    result = unittest.main(verbosity=2, exit=False).result
    raise SystemExit(0 if result.wasSuccessful() else 1)
