#!/usr/bin/env python3
"""Run every gate, in the order they matter, and stop at the first one that fails.

This is the pre-push script. CI runs the same checks, but CI only tells you after
the fact; this tells you before the commit leaves the machine.

    python tests/run_all.py

Gates, cheapest and most informative first:

  1. validate       catalog is internally legal and honest about provenance
  2. test cases     structural invariants + pinned values for recipes we authored
  3. generated Java Recipes.java on disk is what the catalog would produce
  4. browser        index.html is regenerated and renders (needs node)
  5. readme counts  the numbers in README.md match the catalog

Gates 3-5 are skipped rather than failed when their prerequisite is missing (no
upstream checkout, no node on PATH) — a missing tool is not a broken catalog. The
skip is printed loudly so it cannot be mistaken for a pass.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PY = sys.executable


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

    def gate(label: str, cmd: list[str]) -> None:
        ok, _ = run(label, cmd)
        if not ok:
            failures.append(label)

    gate("1/5  validate catalog", [PY, "tools/validate_catalog.py"])
    gate("2/5  catalog test cases", [PY, "tests/test_catalog.py"])

    fork = ROOT / "build" / "recipe-lab-sony-pmca"
    if fork.exists():
        gate("3/5  generated Java is current",
             [PY, "tools/gen_recipes.py", "--check", "--fork", str(fork)])
    else:
        skipped.append("3/5  generated Java is current (no build/recipe-lab-sony-pmca checkout)")
        skipped.append("     also skipped: fidelity check, needs upstream Recipes.java")

    node = shutil.which("node")
    if node:
        ok, _ = run("4/5  regenerate browser", [PY, "tools/gen_browser.py"])
        if not ok:
            failures.append("4/5  regenerate browser")
        else:
            diff = subprocess.run(["git", "diff", "--exit-code", "catalog/index.html"],
                                  cwd=ROOT, capture_output=True, text=True)
            if diff.returncode != 0:
                print("catalog/index.html changed — it was stale. Commit the new one.")
                failures.append("4/5  browser was stale")
            gate("4/5  browser smoke test", [node, "tests/smoke_browser.js"])
    else:
        skipped.append("4/5  browser smoke test (node is not on PATH)")

    gate("5/5  README counts", [PY, "tools/check_readme_counts.py"])

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
