#!/usr/bin/env python3
"""Derive the release build matrix from catalog/packs.json.

    python tools/build_matrix.py            # the matrix, as JSON, one line
    python tools/build_matrix.py --ids      # just the pack ids, one per line
    python tools/build_matrix.py --apk-for ID  # the expected APK filename for one target

Consumed by .github/workflows/release.yml and tools/build_apk.sh.

This is a script in the repository rather than an inline `python -c` in the workflow for a
concrete reason, not a stylistic one: inside a YAML `run: |` block the code has to be
indented to sit under the block scalar, and when that code is passed through `python -c`
inside a shell substitution the indentation is part of the string. Python then dies on the
first statement with `IndentationError: unexpected indent` — the workflow fails before it
builds anything, and nothing local catches it. A file has no such ambiguity.

The matrix is *derived*. The pack list lives in catalog/packs.json and nowhere else; a
literal copy here or in the workflow would drift the first time someone adds a pack. The
entry list is the all-in-one app plus one entry per pack, and the APK filename comes from
apply_pack.apk_name() so there is exactly one definition of what a pack's build produces.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_PACKS = ROOT / "catalog" / "packs.json"

# The all-in-one app: the same matrix shape as a pack but with no pack id, so the workflow
# can run one pipeline for both and branch on `pack == ''`.
ALL_IN_ONE = {"id": "all", "pack": "", "apk": "SonySOOCRecipes.apk",
              "label": "the all-in-one app"}

sys.path.insert(0, str(ROOT / "tools"))


def entries(packs_file: Path) -> list[dict]:
    from apply_pack import apk_name  # noqa: PLC0415 — same-directory sibling script

    data = json.loads(packs_file.read_text(encoding="utf-8"))
    packs = data["packs"]
    seen: set[str] = set()
    out = [dict(ALL_IN_ONE)]
    for p in packs:
        if p["id"] in seen:
            raise SystemExit(f"duplicate pack id {p['id']!r} in {packs_file}")
        seen.add(p["id"])
        if p["id"] == "all":
            raise SystemExit('"all" is reserved for the all-in-one app; rename that pack')
        out.append({
            "id": p["id"],
            "pack": p["id"],
            "apk": apk_name(p),
            "label": f"{p['app_name']} ({len(p['groups'])} group(s))",
        })
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--ids", action="store_true", help="pack ids only, one per line")
    g.add_argument("--apk-for", metavar="ID", help="the APK filename for one target id "
                                                  "('all' for the all-in-one app)")
    args = ap.parse_args()

    rows = entries(DEFAULT_PACKS)
    if args.apk_for:
        for r in rows:
            if r["id"] == args.apk_for:
                print(r["apk"])
                return 0
        raise SystemExit(f"no build target {args.apk_for!r} "
                         f"(have: {', '.join(r['id'] for r in rows)})")
    if args.ids:
        # Pack ids only — the all-in-one is deliberately excluded, because its entry has an
        # empty pack id and a caller that loops over this list (tools/build_apk.sh
        # --all-packs) builds the all-in-one separately and would otherwise pick up an empty
        # id and build the same thing twice.
        for r in rows:
            if r["pack"]:
                print(r["pack"])
    else:
        # Single-line JSON: $GITHUB_OUTPUT takes one line per key, so a pretty-printed
        # matrix would be silently truncated at the first newline.
        print(json.dumps(rows, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
