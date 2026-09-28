#!/usr/bin/env python3
"""Run every gate, in the order they matter, and report every failure together.

This is the pre-push script. CI runs the same checks, but CI only tells you after
the fact; this tells you before the commit leaves the machine.

    python tests/run_all.py

Gates, cheapest and most informative first:

  validate        catalog is internally legal and honest about provenance
  test cases      structural invariants + pinned values for recipes we authored
  UI theme        the two-bar layout keeps every id MainActivity binds, every colour
                  and on-screen toggle in catalog/ui-theme.json is legal, and the Java
                  colour anchors still match upstream
  generated Java  Recipes.java on disk is what the catalog would produce
  browser         index.html is regenerated and renders (needs node)
  readme counts   the numbers in README.md match the catalog
  assets          every image a document points at exists, and nothing is hotlinked
  bilingual docs  twin coverage, shared diagrams, numbers drawn inside diagrams
  self-test       the gates themselves still fail on broken input (tests/test_gates.py)

All gates run even after one fails — one broken gate never hides another. The
generated-Java and browser gates are skipped rather than failed when their
prerequisite is missing (no upstream checkout, no node on PATH) — a missing tool is
not a broken catalog. The skip is printed loudly so it cannot be mistaken for a pass.

The labels are deliberately unnumbered: a "4/7" label goes stale the moment an eighth
gate lands, and nothing forces whoever adds it to renumber the other seven. Refer to a
gate by its name — the number is the one part of the label with no meaning of its own.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PY = sys.executable


def sweep_probe_artifacts() -> None:
    """Remove leftover _gate_probe_* artifacts from an interrupted or leaky prior run so
    the assets and bilingual-docs gates don't mistake them for real repository content.

    The gate self-test drops a real orphan icon set and a stray translation into the repo
    to prove those gates reject them; if its cleanup is ever interrupted, those artifacts
    would otherwise fail the assets and docs gates on the *next* run, and the failure would
    point at the sweep's leftovers rather than at anything anyone changed. Sweeping here
    makes the pre-push script idempotent regardless of how the previous run ended.
    """
    pack_icons = ROOT / "assets" / "app-icon-packs"
    if pack_icons.is_dir():
        for stray in pack_icons.glob("_gate_probe_*"):
            if stray.is_dir():
                shutil.rmtree(stray, ignore_errors=True)
    docs = ROOT / "docs"
    if docs.is_dir():
        for stray in docs.glob("_gate_probe_*"):
            stray.unlink(missing_ok=True)


def run(label: str, cmd: list[str], cwd: Path = ROOT) -> tuple[bool, str]:
    print(f"\n=== {label} " + "=" * max(0, 62 - len(label)))
    print(f"$ {' '.join(cmd)}")
    try:
        proc = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True,
                              encoding="utf-8", errors="replace")
    except FileNotFoundError:
        return False, f"command not found: {cmd[0]}"
    out = (proc.stdout or "") + (proc.stderr or "")
    if out.strip():
        print(out.rstrip())
    return proc.returncode == 0, out


def main() -> int:
    failures: list[str] = []
    skipped: list[str] = []
    sweep_probe_artifacts()

    def gate(label: str, cmd: list[str]) -> None:
        ok, _ = run(label, cmd)
        if not ok:
            failures.append(label)

    gate("validate catalog", [PY, "tools/validate_catalog.py"])
    gate("catalog test cases", [PY, "tests/test_catalog.py"])
    # The main screen is a replayed patch (tools/patch_ui.py), not committed source, so
    # nothing else in this run would notice a broken theme: build/ is gitignored and
    # build_apk.sh resets it before every build. This gate is the only thing standing
    # between a bad colour or a dropped view id in catalog/ui-theme.json / assets/ui/
    # and an APK that fails to inflate its layout on the camera.
    gate("UI theme", [PY, "tests/test_ui_theme.py"])

    fork = ROOT / "build" / "recipe-lab-sony-pmca"
    if fork.exists():
        gate("generated Java is current",
             [PY, "tools/gen_recipes.py", "--check", "--fork", str(fork)])
    else:
        skipped.append("generated Java is current (no build/recipe-lab-sony-pmca checkout)")
        skipped.append("fidelity check, needs upstream Recipes.java")

    node = shutil.which("node")
    if node:
        ok, _ = run("browser — regenerate", [PY, "tools/gen_browser.py"])
        if not ok:
            failures.append("browser — regenerate")
        else:
            diff = subprocess.run(["git", "diff", "--exit-code", "catalog/index.html"],
                                  cwd=ROOT, capture_output=True, text=True)
            if diff.returncode != 0:
                print("catalog/index.html changed — it was stale. Commit the new one.")
                failures.append("browser was stale")
            gate("browser — smoke test", [node, "tests/smoke_browser.js"])
    else:
        skipped.append("browser smoke test (node is not on PATH)")

    gate("README counts", [PY, "tools/check_readme_counts.py"])
    gate("assets", [PY, "tools/check_assets.py"])
    gate("bilingual docs", [PY, "tools/check_docs.py"])
    # Last, and deliberately so: it temporarily breaks inputs and runs gates as
    # subprocesses, so it is the slowest and the only one that mutates the working
    # tree (probe files only, restored in finally). Running it after the real gates
    # also means a broken tree is reported by its own gate first, with a real message.
    gate("gate self-test", [PY, "tests/test_gates.py"])

    print("\n" + "=" * 66)
    for s in skipped:
        print(f"  SKIP  {s}")
    if failures:
        for f in failures:
            print(f"  FAIL  {f}")
        print(f"\n{len(failures)} gate(s) failed — do not push.")
        return 1
    print("  all gates passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
