#!/usr/bin/env python3
"""Prove that the gates actually fail.

Every other test in this directory asserts that good input passes. Nothing asserted
that bad input FAILS — and a gate that has never been seen failing is not a gate, it is
a decoration. A refactor that made `check_assets.py` accept a wrong-sized icon, or made
`validate_catalog.py` swallow an unknown style, would have sailed through CI green.

So each test here deliberately breaks one thing, runs the gate as a subprocess, and
asserts a non-zero exit:

    validate_catalog.py     -- a catalog with an unknown group
    check_readme_counts.py  -- a README marker advertising a number the catalog rejects
    check_assets.py         -- an icon-set directory belonging to no pack
    check_docs.py           -- a zh-CN file whose English original is gone
    check_docs.py           -- a FAQ question only one of the two languages answers
    check_docs.py           -- a link into a heading that is not there
    check_docs.py           -- a link to a file that is not there
    cataloglib.load_pack    -- a pack listing no groups, and an unknown pack id

The other three are skipped by design, and the reason matters: `gen_recipes.py --check`
and `check_fidelity.py` need an upstream checkout, and the browser smoke test needs
node — their failure paths are environment-dependent in ways a fixture cannot pin
cheaply. That gap is stated here rather than silently ignored.

The breakage is done by ADDING a probe file (or, for the README marker, rewriting one
line and restoring it in a `finally`). Nothing here deletes or moves repository files,
and every probe name is distinctive so a crashed run cannot leave anything that looks
like real content.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TOOLS = ROOT / "tools"

PROBE = "_gate_probe_"


def _rmtree_clear_readonly(func, path, exc_info):
    """onerror handler: clear the read-only bit and retry the removal."""
    try:
        os.chmod(path, 0o777)
        func(path)
    except OSError:
        pass


def _remove_probe(path: Path) -> None:
    """Best-effort removal of a gate probe, retrying past transient Windows lock/AV races.

    The self-tests below drop a real artifact into the repo (an orphan icon set, a stray
    translation) so the gates can be proven to reject it; the artifact has to be gone
    before the suite returns, or it pollutes the next run's assets/docs gates. A bare
    shutil.rmtree(..., ignore_errors=True) silently leaves the directory behind when a
    subprocess that just read it still holds a handle — so retry, clearing read-only bits.
    """
    for _ in range(40):  # up to ~2 s
        try:
            if path.is_dir():
                shutil.rmtree(path, onerror=_rmtree_clear_readonly)
            else:
                path.unlink()
            return
        except OSError:
            time.sleep(0.05)
    # last resort: don't fail the self-test over a cleanup hiccup, but try once more quietly
    try:
        if path.is_dir():
            shutil.rmtree(path, ignore_errors=True)
        else:
            path.unlink(missing_ok=True)
    except OSError:
        pass


def run_gate(script: str, *args: str):
    return subprocess.run([sys.executable, str(TOOLS / script), *args],
                          cwd=ROOT, capture_output=True, text=True)


def tools_on_path():
    sys.path.insert(0, str(TOOLS))
    try:
        import cataloglib  # noqa: PLC0415
    finally:
        sys.path.remove(str(TOOLS))
    return cataloglib


class TestValidateCatalogFails(unittest.TestCase):
    def test_unknown_group_is_rejected(self):
        # Minimal but structurally plausible: the filter references a group that is not
        # declared. Everything else about it is legal, so the ONLY reason this fails is
        # the one under test.
        catalog = {
            "version": "0",
            "engines": {"recipe-lab": {"license": "upstream"}},
            "groups": [{"id": "g", "label": "G"}],
            "filters": [{
                "id": "probe", "name": "Probe", "group": "not-a-group",
                "engine": "recipe-lab", "source": "recipe-lab", "tone": "color",
                "verified": False,
                "recipe": {"style": "STD", "sat": 0, "con": 0, "sharp": 0,
                           "matrix": 0, "wb": {"mode": "AUTO", "ab": 0, "gm": 0},
                           "pe": 0, "sub": 0, "ev": 0, "dro": 6},
            }],
        }
        with tempfile.TemporaryDirectory() as td:
            bad = Path(td) / "bad-catalog.json"
            bad.write_text(json.dumps(catalog), encoding="utf-8")
            r = run_gate("validate_catalog.py", str(bad))
        self.assertEqual(r.returncode, 1, f"gate passed a catalog it must reject:\n{r.stdout}")
        self.assertIn("unknown group", r.stdout)


class TestCheckReadmeCountsFails(unittest.TestCase):
    def test_a_stale_marker_is_rejected(self):
        readme = ROOT / "README.md"
        original = readme.read_text(encoding="utf-8")
        import re
        m = re.search(r"<!--\s*counts:\s*total=(\d+)\s+compiled=(\d+)\s*-->", original)
        self.assertIsNotNone(m, "README.md has no counts marker to corrupt")
        poisoned = original.replace(
            m.group(0), f"<!-- counts: total=99999 compiled=99999 -->")
        try:
            readme.write_text(poisoned, encoding="utf-8")
            r = run_gate("check_readme_counts.py")
        finally:
            readme.write_text(original, encoding="utf-8")
        self.assertEqual(r.returncode, 1, "gate passed a README whose numbers are wrong")
        self.assertIn("catalog has", r.stdout)


class TestCheckAssetsFails(unittest.TestCase):
    def test_an_orphan_icon_set_is_rejected(self):
        probe = ROOT / "assets" / "app-icon-packs" / f"{PROBE}not_a_pack"
        probe.mkdir(parents=True, exist_ok=True)
        try:
            (probe / "ic_launcher-mdpi.png").write_bytes(b"not a real png")
            r = run_gate("check_assets.py")
        finally:
            _remove_probe(probe)
        self.assertEqual(r.returncode, 1, "gate passed an icon set no pack references")
        self.assertIn("orphan icon set", r.stdout)


class TestCheckDocsFails(unittest.TestCase):
    def test_a_twin_without_an_original_is_rejected(self):
        probe = ROOT / "docs" / f"{PROBE}.zh-CN.md"
        probe.write_text("孤儿双生文件——它的英文原文不存在。", encoding="utf-8")
        try:
            r = run_gate("check_docs.py")
        finally:
            _remove_probe(probe)
        self.assertEqual(r.returncode, 1, "gate passed a translation with no original")
        self.assertIn("no English original", r.stdout)

    def test_a_faq_question_only_one_language_answers_is_rejected(self):
        """Twin coverage proves the twin EXISTS; it says nothing about the two files still
        covering the same ground. Drop one question from the twin and the pair looks complete
        in both languages — that is the drift, and deleting a heading is its exact shape."""
        twin = ROOT / "docs" / "FAQ.zh-CN.md"
        english = ROOT / "docs" / "FAQ.md"
        original = twin.read_text(encoding="utf-8")
        lines = original.splitlines(keepends=True)
        victim = next(i for i, l in enumerate(lines) if l.startswith("### "))
        before = len([l for l in english.read_text(encoding="utf-8").splitlines()
                      if l.startswith("### ")])
        try:
            twin.write_text("".join(lines[:victim] + lines[victim + 1:]), encoding="utf-8")
            r = run_gate("check_docs.py")
        finally:
            twin.write_text(original, encoding="utf-8")
        self.assertEqual(r.returncode, 1,
                         "gate passed a FAQ whose two languages answer different questions")
        self.assertIn(f"asks {before - 1}", r.stdout)

    def test_a_link_into_a_heading_that_is_not_there_is_rejected(self):
        """Renaming a heading silently breaks every link aimed at it. The id is invisible
        in a rendered page and the link text still reads the way it always did, so nothing
        short of resolving the id can see the break — which is why this gate has to exist
        before any document gets restructured."""
        readme = ROOT / "README.md"
        original = readme.read_text(encoding="utf-8")
        try:
            readme.write_text(
                original + "\n\n[nowhere](#this-heading-was-renamed)\n", encoding="utf-8")
            r = run_gate("check_docs.py")
        finally:
            readme.write_text(original, encoding="utf-8")
        self.assertEqual(r.returncode, 1, "gate passed a link into a missing heading")
        self.assertIn("has no matching heading", r.stdout)

    def test_a_link_to_a_file_that_is_not_there_is_rejected(self):
        """Relative links resolve against the file holding them, not the repository root.
        That difference is invisible while you write `docs/X.md` looking at a tree view,
        and it is exactly how `../README.md` came to point at a docs/README.md that never
        existed in three of the pack pages."""
        readme = ROOT / "README.md"
        original = readme.read_text(encoding="utf-8")
        try:
            readme.write_text(
                original + "\n\n[missing](docs/no-such-page.md)\n", encoding="utf-8")
            r = run_gate("check_docs.py")
        finally:
            readme.write_text(original, encoding="utf-8")
        self.assertEqual(r.returncode, 1, "gate passed a link to a file that does not exist")
        self.assertIn("does not exist", r.stdout)


class TestLoadPackGuard(unittest.TestCase):
    """The guard whose absence in apply_pack's copy was a real bug: a pack listing no
    groups used to be transformed and shipped, and no gate noticed."""

    def test_empty_groups_pack_is_rejected(self):
        lib = tools_on_path()
        with tempfile.TemporaryDirectory() as td:
            packs = Path(td) / "packs.json"
            packs.write_text(json.dumps({
                "package_base": "com.example.base",
                "packs": [{"id": "empty", "app_name": "Empty Looks",
                           "groups": [], "icon_set": "empty"}],
            }), encoding="utf-8")
            with self.assertRaises(SystemExit):
                lib.load_pack(packs, "empty")

    def test_unknown_pack_names_what_exists(self):
        lib = tools_on_path()
        real = ROOT / "catalog" / "packs.json"
        with self.assertRaises(SystemExit) as ctx:
            lib.load_pack(real, "not-a-pack")
        self.assertIn("leica", str(ctx.exception))

    def test_a_real_pack_still_loads(self):
        lib = tools_on_path()
        pack, all_ids = lib.load_pack(ROOT / "catalog" / "packs.json", "leica")
        self.assertTrue(pack["groups"])
        self.assertIn("leica", all_ids)


if __name__ == "__main__":
    unittest.main(verbosity=2)
