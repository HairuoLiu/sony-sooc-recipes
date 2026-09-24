#!/usr/bin/env python3
"""Write the Chinese twin of the launcher label: res/values-zh/strings.xml.

This mirrors tools/gen_recipes.py on purpose: --pack selects the brand pack, no --pack
means the all-in-one. Taking the pack as an argument rather than reading it back out of
the checkout is what makes the result deterministic — the all-in-one build never runs
apply_pack.py at all, so its package name is still upstream's at this point and cannot
tell us which app we are building.

Android picks res/values-zh/ on its own from the body's locale, so no app-side code is
involved. values-zh (not values-zh-rCN) is deliberate: it matches every Chinese locale
the firmware might report, and the catalog is Simplified either way.

The Chinese text is data, not code — it comes from catalog/packs.json (app_name_zh),
with the all-in-one label as the only literal here because the all-in-one has no entry.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_FORK = ROOT / "build" / "recipe-lab-sony-pmca"
DEFAULT_PACKS = ROOT / "catalog" / "packs.json"

# The all-in-one app has no entry in packs.json — every pack is a subset of it.
ALL_IN_ONE_ZH = "索尼直出配方"

REL = Path("res") / "values-zh" / "strings.xml"


def app_name_zh(pack: str | None, packs_path: Path) -> str:
    if not pack:
        return ALL_IN_ONE_ZH
    packs = json.loads(packs_path.read_text(encoding="utf-8"))
    for p in packs["packs"]:
        if p["id"] == pack:
            return p.get("app_name_zh") or p["app_name"]
    raise SystemExit(f"packs.json has no pack {pack!r}")


def render(pack: str | None, packs_path: Path) -> str:
    return ('<?xml version="1.0" encoding="utf-8"?>\n'
            '<resources>\n'
            f'    <string name="app_name">{app_name_zh(pack, packs_path)}</string>\n'
            '</resources>\n')


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--pack", metavar="ID",
                    help="emit this pack's label; with no --pack, the all-in-one's")
    ap.add_argument("--packs", type=Path, default=DEFAULT_PACKS)
    ap.add_argument("--fork", type=Path, default=DEFAULT_FORK,
                    help="path to the upstream checkout to patch")
    ap.add_argument("--check", action="store_true",
                    help="exit non-zero if the file on disk differs from the generated one")
    args = ap.parse_args()

    fork: Path = args.fork
    if not fork.is_dir():
        raise SystemExit(f"no checkout at {fork}")

    wanted = render(args.pack, args.packs)
    target = fork / REL

    if args.check:
        if not target.is_file():
            print(f"MISSING {REL}")
            return 1
        if target.read_text(encoding="utf-8") != wanted:
            print(f"STALE   {REL} — rerun tools/patch_i18n.py for this pack")
            return 1
        print(f"ok      {REL}")
        return 0

    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(wanted, encoding="utf-8", newline="")
    print(f"wrote {target}  ({app_name_zh(args.pack, args.packs)})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
