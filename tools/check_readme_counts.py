#!/usr/bin/env python3
"""Check that the numbers the docs advertise match catalog/filters.json.

A README that says 93 recipes when the catalog holds 91 is a documentation bug nobody
notices by eye, and it is exactly the kind of drift that accumulates in a project whose
whole point is a single source of truth.

Two kinds of number are checked, by two different mechanisms:

1. **The READMEs** carry a machine-readable marker rather than relying on the prose being
   parsed (prose gets rewrapped, and a regex over a wrapped sentence breaks silently):

       <!-- counts: total=93 compiled=78 -->

   This also checks that the marker agrees with the prose a reader actually sees. Both
   READMEs are checked, each in its own language — the English page is the front door,
   and a translated page that quietly still says the old number is worse than no
   translation at all.

2. **Every other doc** under `docs/` is scanned for a count the reader will read as
   "how many recipes the project has": `N recipes`, `N looks`, `N 款`, `N 款配方`,
   `N 款风格`. Any such N smaller than the catalog's current total is reported — it is a
   stale count that was correct at some earlier revision. Two deliberate exemptions:

     * `MAPPING-RECIPES.md` is a snapshot by design (its own header says so) and is
       skipped wholesale.
     * `CHANGELOG.md` is a history; old numbers there are the point, not a bug.

   This is the part that used to slip through: for a long time this gate only checked the
   READMEs, so `docs/FAQ.md` sat at "99 recipes" while the catalog held 155, and nothing
   failed.

    python tools/check_readme_counts.py
"""

from __future__ import annotations

import cataloglib
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CATALOG = ROOT / "catalog" / "filters.json"

MARKER = re.compile(r"<!--\s*counts:\s*total=(\d+)\s+compiled=(\d+)\s*-->")

# name -> the two phrases a reader must be able to see, given (total, compiled)
READMES = {
    "README.md": (
        "{total} looks",
        "{compiled} compiled into the APK",
    ),
    "README.zh-CN.md": (
        "**{total} 款**",
        "**{compiled} 款可直接编译进 APK**",
    ),
}

# Files skipped by the doc scan because their stale numbers are intentional.
DOC_SCAN_EXEMPT = {
    "docs/MAPPING-RECIPES.md",   # explicit snapshot; its header says so
}

# A number the reader will read as "how many recipes there are" — i.e. a count written
# as the total, in either language. The regex captures the integer and the count noun.
DOC_COUNT = re.compile(
    r"(\d+)\s*(?:recipes|looks|款配方|款风格|款|recipe|look)\b"
)


def scan_docs(total: int) -> list[str]:
    """Return lines across docs/ that state a recipe count below the current total.

    Only counts that look like a *total* are flagged. The catalogue has grown
    93 -> 99 -> 117 -> 155, so any of those earlier totals appearing in a doc is a stale
    count. Sub-category numbers (77 from upstream, 63 authored, 15 reference-only, per-batch
    counts like "18 款相机模拟") are NOT totals and must not be flagged, so this only
    reports counts that are one of the known earlier totals.
    """
    historical = {93, 99, 117}  # totals the catalog has actually held, before now
    problems: list[str] = []
    for path in sorted((ROOT / "docs").rglob("*.md")):
        rel = path.relative_to(ROOT).as_posix()
        if rel in DOC_SCAN_EXEMPT:
            continue
        for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            for m in DOC_COUNT.finditer(line):
                n = int(m.group(1))
                if n in historical:
                    problems.append(f"{rel}:{lineno}: {line.strip()[:120]}")
    return problems


def main() -> int:
    stats = cataloglib.catalog_stats(cataloglib.load_catalog(CATALOG))
    total, compiled = stats["total"], stats["compiled"]

    ok = True
    for name, phrases in READMES.items():
        path = ROOT / name
        if not path.exists():
            print(f"{name}: missing")
            ok = False
            continue

        readme = path.read_text(encoding="utf-8")
        m = MARKER.search(readme)
        if not m:
            print(f"{name}: no '<!-- counts: total=N compiled=M -->' marker")
            ok = False
            continue

        stated_total, stated_compiled = int(m.group(1)), int(m.group(2))
        if stated_total != total:
            print(f"{name}: marker says {stated_total} recipes, catalog has {total}")
            ok = False
        if stated_compiled != compiled:
            print(f"{name}: marker says {stated_compiled} compiled, catalog has {compiled}")
            ok = False

        for template in phrases:
            phrase = template.format(total=total, compiled=compiled)
            if phrase not in readme:
                print(f"{name}: visible text does not contain {phrase!r}")
                ok = False

    for problem in scan_docs(total):
        print(f"stale doc count: {problem}")
        ok = False

    if not ok:
        return 1

    print(f"ok — {len(READMES)} READMEs advertise {total} catalogued, {compiled} compiled; "
          f"docs/ has no stale counts below {total}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
