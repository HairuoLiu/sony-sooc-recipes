#!/usr/bin/env python3
"""Check that the numbers the READMEs advertise match catalog/filters.json.

A README that says 93 recipes when the catalog holds 91 is a documentation bug nobody
notices by eye, and it is exactly the kind of drift that accumulates in a project whose
whole point is a single source of truth.

The README carries a machine-readable marker rather than relying on the prose being
parsed: prose gets rewrapped, and a regex over a wrapped sentence breaks silently.

    <!-- counts: total=93 compiled=78 -->

This script also checks that the marker agrees with the prose a reader actually sees.
Both READMEs are checked, each in its own language — the English page is the front door,
and a translated page that quietly still says the old number is worse than no
translation at all.

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

    if not ok:
        return 1

    print(f"ok — {len(READMES)} READMEs advertise {total} catalogued, {compiled} compiled")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
