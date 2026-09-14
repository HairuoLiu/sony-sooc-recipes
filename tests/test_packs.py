#!/usr/bin/env python3
"""Tests for the brand packs — catalog/packs.json, the generator, and the transform.

Standard library only, same as test_catalog.py.

    python tests/test_packs.py                 # run everything
    python -m unittest discover tests          # same, via unittest

A pack is the same app packaged per brand (see docs/BRAND-PACKS.md). Three classes,
guarding three different failure modes:

1. TestPackDefinitions — packs.json is data, so the constraints on it are checked rather
   than documented. The interesting one is `test_no_id_is_a_prefix_of_another`: the rename
   in tools/apply_pack.py tells packs apart by id, so `fuji` and `fujifilm` cannot coexist.

2. TestPackOutput — every pack emits Java that compiles, carries the pack's package, holds
   only its own groups, and preserves the recipe values *exactly* as the all-in-one app
   emits them. That last assertion is what makes a pack a subset rather than a re-fitting:
   if a pack ever ships a different value for the same look, this fails.

3. TestApplyPack — the in-place transform, run against a throwaway copy of the upstream
   checkout. Skipped (loudly) when the checkout is absent, because a missing clone is not
   a broken pack.

4. TestBuildMatrix — tools/build_matrix.py feeds the release workflow, where a wrong answer
   fails late and quietly (a wrapped JSON value truncates in $GITHUB_OUTPUT; a stale APK
   filename fails a ten-minute build at the final step).
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CATALOG = ROOT / "catalog" / "filters.json"
PACKS = ROOT / "catalog" / "packs.json"
FORK = ROOT / "build" / "recipe-lab-sony-pmca"
TOOLS = ROOT / "tools"

CATALOG_DATA = json.loads(CATALOG.read_text(encoding="utf-8"))
PACKS_DATA = json.loads(PACKS.read_text(encoding="utf-8"))
PACK_LIST = PACKS_DATA["packs"]


def _load_tool(name: str):
    """Import a tool script by name. tools/ is not a package, so tests borrow the same
    sys.path trick check_fidelity.py uses to import gen_recipes."""
    sys.path.insert(0, str(TOOLS))
    try:
        return __import__(name)  # noqa: PLC0415
    finally:
        sys.path.remove(str(TOOLS))


GEN = _load_tool("gen_recipes")
APPLY = _load_tool("apply_pack")

RECIPE_LINE = re.compile(r"new Recipe\(")


def recipes_in(java: str) -> set[str]:
    """The `new Recipe(...)` statements, normalised to one line each.

    Keyed on the statement text, not on the recipe name: two groups are allowed to hold a
    look with the same name, and comparing statements is what proves the values match.
    """
    out = set()
    for line in java.splitlines():
        s = line.strip()
        if RECIPE_LINE.search(s):
            out.add(s.split("//")[0].strip().rstrip(","))
    return out


def groups_in(java: str) -> list[str]:
    m = re.search(r"String\[\] GROUPS = \{([^}]*)\};", java)
    return re.findall(r'"([^"]*)"', m.group(1)) if m else []


class TestPackDefinitions(unittest.TestCase):
    """packs.json is data the next person edits; hold it to its constraints."""

    def test_parses(self):
        self.assertIn("packs", PACKS_DATA)
        self.assertTrue(PACK_LIST, "packs.json declares no packs")

    def test_ids_are_unique(self):
        ids = [p["id"] for p in PACK_LIST]
        dupes = {i for i in ids if ids.count(i) > 1}
        self.assertFalse(dupes, f"duplicate pack ids: {sorted(dupes)}")

    def test_required_fields(self):
        for p in PACK_LIST:
            for field in ("id", "app_name", "groups", "icon_set"):
                self.assertIn(field, p, f"pack {p.get('id')!r} has no {field!r}")

    def test_no_id_is_a_prefix_of_another(self):
        """tools/apply_pack.py anchors its rename on the pack id.

        If one id were a prefix of another, applying `fuji` to a checkout that already
        carries `fujifilm` would rewrite into `...fuji.fujifilm`. The transform refuses
        this at runtime; the check belongs here too, where the error is cheap.
        """
        ordered = sorted((p["id"] for p in PACK_LIST), key=len)
        for i, a in enumerate(ordered):
            for b in ordered[i + 1:]:
                self.assertFalse(b.startswith(a),
                                 f"pack id {a!r} is a prefix of {b!r} — the rename "
                                 "cannot tell them apart")

    def test_groups_exist_in_catalog(self):
        known = {g["id"] for g in CATALOG_DATA["groups"]}
        for p in PACK_LIST:
            for g in p["groups"]:
                self.assertIn(g, known, f"pack {p['id']!r} names unknown group {g!r}")

    def test_groups_are_not_empty(self):
        for p in PACK_LIST:
            self.assertTrue(p["groups"], f"pack {p['id']!r} lists no groups")

    def test_no_group_is_claimed_by_two_packs(self):
        """One group, one pack: a recipe shipped in two packs is a support question
        ("why do Leica Looks and Kodak Looks both have this?") with no good answer."""
        seen: dict[str, str] = {}
        for p in PACK_LIST:
            for g in p["groups"]:
                self.assertNotIn(g, seen,
                                 f"group {g!r} is in both {seen.get(g)!r} and {p['id']!r}")
                seen[g] = p["id"]

    def test_every_catalog_group_is_accounted_for(self):
        """Assigned to a pack, or listed in unassigned_groups — never silently dropped."""
        assigned = {g for p in PACK_LIST for g in p["groups"]}
        unassigned = set(PACKS_DATA.get("unassigned_groups", {}))
        unassigned.discard("$comment")
        for g in CATALOG_DATA["groups"]:
            self.assertTrue(g["id"] in assigned or g["id"] in unassigned,
                            f"group {g['id']!r} is in neither a pack nor unassigned_groups")

    def test_unassigned_groups_do_not_overlap_packs(self):
        assigned = {g for p in PACK_LIST for g in p["groups"]}
        unassigned = set(PACKS_DATA.get("unassigned_groups", {}))
        unassigned.discard("$comment")
        self.assertFalse(assigned & unassigned,
                         f"groups listed both ways: {sorted(assigned & unassigned)}")

    def test_package_base_matches_the_tools(self):
        """Two places know the base package. They must not drift — the same trap the
        upstream SHA has (see test_catalog.py::TestPinnedUpstream)."""
        self.assertEqual(PACKS_DATA["package_base"], GEN.PACKAGE_BASE,
                         "catalog/packs.json package_base and tools/gen_recipes.py "
                         "PACKAGE_BASE disagree; update both")


class TestPackOutput(unittest.TestCase):
    """What the generator actually emits for each pack."""

    @classmethod
    def setUpClass(cls):
        cls.all_in_one = GEN.generate(CATALOG_DATA)
        cls.pack_java = {
            p["id"]: GEN.generate(CATALOG_DATA, group_ids=p["groups"],
                                  package=GEN.package_for(p))
            for p in PACK_LIST
        }

    def test_package_carries_the_pack_id(self):
        for p in PACK_LIST:
            first = self.pack_java[p["id"]].splitlines()[0]
            self.assertEqual(first, f"package {PACKS_DATA['package_base']}.{p['id']};",
                             f"pack {p['id']!r} emits the wrong package line")

    def test_packages_are_distinct(self):
        """The whole point: Android identifies an app by package name, so identical
        package names cannot be installed side by side."""
        pkgs = [self.pack_java[p["id"]].splitlines()[0] for p in PACK_LIST]
        self.assertEqual(len(pkgs), len(set(pkgs)), "two packs emit the same package")

    def test_groups_are_a_subset_of_the_request(self):
        label_of = {g["id"]: g["label"] for g in CATALOG_DATA["groups"]}
        for p in PACK_LIST:
            asked = {label_of[g] for g in p["groups"]}
            emitted = set(groups_in(self.pack_java[p["id"]]))
            self.assertTrue(emitted <= asked,
                            f"pack {p['id']!r} emitted unexpected groups: "
                            f"{sorted(emitted - asked)}")

    def test_no_group_is_emitted_empty(self):
        """GROUP_START stays -1 for an empty group and MainActivity's prev/next-group walk
        assumes a group can be entered, so an empty group is a crash waiting for a
        button press."""
        for p in PACK_LIST:
            java = self.pack_java[p["id"]]
            labels = groups_in(java)
            for label in labels:
                block = java.split(f"// ---- {label}", 1)[1].split("// ----")[0]
                self.assertGreater(len(RECIPE_LINE.findall(block)), 0,
                                   f"pack {p['id']!r} emits empty group {label!r}")

    def test_recipes_belong_to_the_pack(self):
        """A recipe may only appear in a pack if its group belongs to that pack."""
        group_of_filter = {f["id"]: f["group"] for f in CATALOG_DATA["filters"]}
        for p in PACK_LIST:
            wanted = set(p["groups"])
            java = self.pack_java[p["id"]]
            labels = set(groups_in(java))
            label_of = {g["id"]: g["label"] for g in CATALOG_DATA["groups"]}
            allowed_labels = {label_of[g] for g in wanted}
            self.assertTrue(labels <= allowed_labels)
            # and every group the pack claims must exist
            for g in wanted:
                self.assertIn(g, group_of_filter.values(),
                              f"pack {p['id']!r} names group {g!r} that holds no filter")

    def test_no_reference_only_entry_is_compiled(self):
        """film-studio entries are recorded by name and orientation only — they carry no
        recipe and must never be emitted as one."""
        no_recipe = {f["id"] for f in CATALOG_DATA["filters"] if "recipe" not in f}
        self.assertTrue(no_recipe, "expected some reference-only entries in the catalog")
        for p in PACK_LIST:
            java = self.pack_java[p["id"]]
            for fid in no_recipe:
                self.assertNotIn(f'"{fid}"', java,
                                 f"pack {p['id']!r} compiled {fid}, which has no recipe")

    def test_pack_values_match_the_all_in_one_exactly(self):
        """A pack must be a *subset*, not a re-derivation.

        If a pack ever emits a different value for the same look, the two APKs disagree
        about what that look is, and the catalog stops being a single source of truth.
        """
        base = recipes_in(self.all_in_one)
        for p in PACK_LIST:
            mine = recipes_in(self.pack_java[p["id"]])
            self.assertTrue(mine <= base,
                            f"pack {p['id']!r} emits recipe lines absent from the "
                            f"all-in-one app: {sorted(mine - base)[:3]}")

    def test_packs_plus_the_all_in_one_lose_nothing(self):
        """Every compilable recipe is either in exactly one pack, or in no pack and still
        reachable in the all-in-one app. No recipe may be duplicated across packs."""
        label_of = {g["id"]: g["label"] for g in CATALOG_DATA["groups"]}
        assigned_labels = {label_of[g] for p in PACK_LIST for g in p["groups"]}

        covered = 0
        for p in PACK_LIST:
            covered += len(RECIPE_LINE.findall(self.pack_java[p["id"]]))
        # each pack's count must equal the all-in-one recipes in its own groups
        expected = 0
        group_blocks = {}
        for label in groups_in(self.all_in_one):
            block = self.all_in_one.split(f"// ---- {label}", 1)[1].split("// ----")[0]
            group_blocks[label] = len(RECIPE_LINE.findall(block))
        for p in PACK_LIST:
            for g in p["groups"]:
                expected += group_blocks.get(label_of[g], 0)
        self.assertEqual(covered, expected,
                         f"packs hold {covered} recipes but their groups hold {expected} "
                         "in the all-in-one app — a recipe was lost or duplicated")
        self.assertGreater(covered, 0, "packs cover no recipes at all")

        total = len(RECIPE_LINE.findall(self.all_in_one))
        self.assertLessEqual(covered, total,
                             "packs claim more recipes than the catalog compiles")


class TestApplyPack(unittest.TestCase):
    """The in-place transform, on a throwaway copy of the upstream checkout."""

    @classmethod
    def setUpClass(cls):
        if not (FORK / "AndroidManifest.xml").is_file():
            raise unittest.SkipTest(
                f"no upstream checkout at {FORK.relative_to(ROOT)} — the transform tests "
                "need one; run tools/build_apk.sh once, or ignore this skip"
            )

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="pack-test-"))
        self.fork = self.tmp / "fork"
        shutil.copytree(FORK, self.fork,
                        ignore=shutil.ignore_patterns(".git", "out", "obj"))

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _run(self, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run([sys.executable, str(TOOLS / "apply_pack.py"),
                               "--fork", str(self.fork), *args],
                              capture_output=True, text=True, encoding="utf-8",
                              cwd=ROOT)

    def test_apply_then_check_passes(self):
        pack = PACK_LIST[0]
        r = self._run("--pack", pack["id"])
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        r = self._run("--pack", pack["id"], "--check")
        self.assertEqual(r.returncode, 0,
                         "the transform does not verify after running:\n" + r.stdout)

    def test_every_pack_passes_its_own_check(self):
        for pack in PACK_LIST:
            with self.subTest(pack=pack["id"]):
                shutil.rmtree(self.fork)
                shutil.copytree(FORK, self.fork,
                                ignore=shutil.ignore_patterns(".git", "out", "obj"))
                r = self._run("--pack", pack["id"])
                self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
                r = self._run("--pack", pack["id"], "--check")
                self.assertEqual(r.returncode, 0, r.stdout)

    def test_second_run_changes_nothing(self):
        """The transform is idempotent. A re-run after a partial failure has to finish
        the job, not nest the source tree one level deeper."""
        pack = PACK_LIST[0]
        self._run("--pack", pack["id"])
        before = sorted(str(p.relative_to(self.fork))
                        for p in self.fork.rglob("*") if p.is_file())
        r = self._run("--pack", pack["id"])
        self.assertIn("in 0 file(s)", r.stdout,
                      "a second run rewrote files it had already rewritten")
        after = sorted(str(p.relative_to(self.fork))
                       for p in self.fork.rglob("*") if p.is_file())
        self.assertEqual(before, after, "a second run changed the file tree")

    def test_library_name_survives_the_rename(self):
        """`sonysoocrecipes` is also the native library name. If the rename appends the
        pack id to it, the result is libsonysoocrecipes.<id>.so — not a loadable library
        name, and the app dies with UnsatisfiedLinkError."""
        pack = PACK_LIST[0]
        self._run("--pack", pack["id"])
        for f in ("jni/Android.mk", "build.sh", "build.cmd"):
            p = self.fork / f
            if not p.is_file():
                continue
            t = p.read_text(encoding="utf-8", errors="replace")
            self.assertNotIn(f".{pack['id']}.so", t,
                             f"{f}: the library name was rewritten")

    def test_manifest_and_app_name_take_the_pack(self):
        pack = PACK_LIST[0]
        self._run("--pack", pack["id"])
        manifest = (self.fork / "AndroidManifest.xml").read_text(encoding="utf-8")
        self.assertIn(f'package="{PACKS_DATA["package_base"]}.{pack["id"]}"', manifest)
        strings = (self.fork / "res" / "values" / "strings.xml").read_text(encoding="utf-8")
        self.assertIn(pack["app_name"], strings)

    def test_jni_symbols_follow_the_package(self):
        """jni.cpp exports `Java_<package with _ separators>_NativeBackup_read`. Leave it
        alone and the app starts, then dies the first time it reads the camera settings."""
        pack = PACK_LIST[0]
        self._run("--pack", pack["id"])
        jni = (self.fork / "jni" / "jni.cpp").read_text(encoding="utf-8", errors="replace")
        mangled = PACKS_DATA["package_base"].replace(".", "_") + "_" + pack["id"]
        self.assertIn(f"Java_{mangled}_NativeBackup_read", jni)
        self.assertNotIn(f"_{pack['id']}_{pack['id']}_", jni,
                         "the pack segment was appended twice")


class TestBuildMatrix(unittest.TestCase):
    """tools/build_matrix.py feeds the release workflow, so its output is a contract.

    The workflow consumes this through `$GITHUB_OUTPUT`, which takes one line per key, and
    the matrix then decides the APK filename the `collect` step asserts exists. Both are
    silent failures when they break: a multi-line value truncates the JSON, and a renamed
    APK fails a ten-minute build at the last step. Hence the checks below.
    """

    def run_tool(self, *args: str) -> str:
        r = subprocess.run([sys.executable, str(TOOLS / "build_matrix.py"), *args],
                           cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, f"build_matrix.py {args} failed:\n{r.stderr}")
        return r.stdout

    def test_json_is_a_single_line(self):
        out = self.run_tool()
        self.assertEqual(out.count("\n"), 1, "$GITHUB_OUTPUT would truncate a wrapped matrix")
        self.assertTrue(out.rstrip("\n").startswith("["), out[:80])

    def test_every_pack_has_exactly_one_entry(self):
        rows = json.loads(self.run_tool())
        self.assertEqual(len(rows), len(PACK_LIST) + 1, "expected the all-in-one plus one per pack")
        ids = [r["id"] for r in rows]
        self.assertEqual(len(ids), len(set(ids)), f"duplicate matrix ids: {ids}")
        for p in PACK_LIST:
            self.assertEqual(ids.count(p["id"]), 1, f"pack {p['id']} is not in the matrix exactly once")

    def test_apk_names_come_from_apply_pack(self):
        """The matrix must not carry a second copy of the APK naming rule."""
        rows = json.loads(self.run_tool())
        by_id = {p["id"]: p for p in PACK_LIST}
        for r in rows:
            if r["pack"]:
                self.assertEqual(r["apk"], APPLY.apk_name(by_id[r["pack"]]),
                                 f"matrix APK name for {r['id']} disagrees with apply_pack")
            else:
                self.assertEqual(r["apk"], "SonySOOCRecipes.apk")

    def test_all_in_one_entry_uses_the_empty_pack_id(self):
        """The workflow branches on `pack == ''`; the all-in-one must not carry a pack id."""
        alls = [r for r in json.loads(self.run_tool()) if r["id"] == "all"]
        self.assertEqual(len(alls), 1)
        self.assertEqual(alls[0]["pack"], "")

    def test_ids_exclude_the_all_in_one(self):
        """--ids drives build_apk.sh --all-packs, which builds the all-in-one separately.
        An empty id in this list would build the all-in-one twice."""
        lines = self.run_tool("--ids").splitlines()
        self.assertNotIn("", lines)
        self.assertNotIn("all", lines)
        self.assertEqual(sorted(lines), sorted(p["id"] for p in PACK_LIST))

    def test_apk_for_lookup(self):
        self.assertEqual(self.run_tool("--apk-for", "all").strip(), "SonySOOCRecipes.apk")
        for p in PACK_LIST:
            self.assertEqual(self.run_tool("--apk-for", p["id"]).strip(), APPLY.apk_name(p))

    def test_apk_for_rejects_an_unknown_id(self):
        r = subprocess.run([sys.executable, str(TOOLS / "build_matrix.py"),
                            "--apk-for", "not-a-pack"],
                           cwd=ROOT, capture_output=True, text=True)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("not-a-pack", r.stderr + r.stdout)


if __name__ == "__main__":
    result = unittest.main(verbosity=2, exit=False).result
    raise SystemExit(0 if result.wasSuccessful() else 1)
