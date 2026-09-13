#!/usr/bin/env python3
"""Check that the numbers the README advertises match catalog/filters.json.

A README that says 93 recipes when the catalog holds 91 is a documentation bug nobody
notices by eye, and it is exactly the kind of drift that accumulates in a project whose
whole point is a single source of truth.

The README carries a machine-readable marker rather than relying on the prose being
parsed: prose gets rewrapped, and a regex over a wrapped sentence breaks silently.

    <!-- counts: total=93 compiled=78 -->

This script also checks that the marker agrees with the prose a reader actually sees.

    python tools/check_readme_counts.py
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CATALOG = ROOT / "catalog" / "filters.json"
README = ROOT / "README.md"

MARKER = re.compile(r"<!--\s*counts:\s*total=(\d+)\s+compiled=(\d+)\s*-->")


def main() -> int:
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    filters = catalog["filters"]
    total = len(filters)
    compiled = sum(1 for f in filters if f["engine"] == "recipe-lab")

    readme = README.read_text(encoding="utf-8")
    m = MARKER.search(readme)
    if not m:
        print("README.md has no '<!-- counts: total=N compiled=M -->' marker")
        return 1

    stated_total, stated_compiled = int(m.group(1)), int(m.group(2))
    ok = True

    if stated_total != total:
        print(f"marker says {stated_total} recipes, catalog has {total}")
        ok = False
    if stated_compiled != compiled:
        print(f"marker says {stated_compiled} compiled, catalog has {compiled}")
        ok = False

    # the prose a reader sees must agree with the marker
    for phrase in (f"**{total} 款**", f"**{compiled} 款可直接编译进 APK**"):
        if phrase not in readme:
            print(f"visible README text does not contain {phrase!r}")
            ok = False

    if not ok:
        return 1

    print(f"ok — README advertises {total} catalogued, {compiled} compiled")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
