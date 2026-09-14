#!/usr/bin/env python3
"""Shared access to catalog/filters.json and catalog/packs.json.

This module exists to give four scripts one definition of the two numbers and one
loader they had each been copy-pasting:

  * the compilable-recipe count was written four times, and not identically —
    `check_readme_counts.py` and `check_docs.py` indexed `f["engine"]` (a KeyError on a
    malformed catalog) while `validate_catalog.py` and `check_fidelity.py` used
    `f.get("engine")`. `tests/run_all.py` runs every gate even after one fails, so the
    KeyError variant really was reachable: a filter missing `engine` produced a raw
    traceback in gate 5 instead of a gate message. `.get` is the deliberate choice here.

  * `load_pack` existed in `apply_pack.py` and `gen_recipes.py` with diverged guards —
    only the gen_recipes copy rejected a pack with no `groups`, so `apply_pack` would
    have transformed and shipped an empty pack. Both now share this one, and
    `tests/test_gates.py` pins the guard.

It is deliberately NOT a grab-bag: no ROOT constant, no argparse helpers, no icon
density table. Those stay per-script (and the gate copies of such tables stay
independent on purpose — a gate that imports the constant it checks against verifies
nothing). If you are about to add something here, ask whether it is data access or
whether it is a check that should restate its spec instead.

Every tool script is invoked as `python tools/<script>.py`, which puts `tools/` first
on sys.path, so `import cataloglib` resolves without any package machinery.
"""

from __future__ import annotations

import json
from pathlib import Path


def load_catalog(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def catalog_stats(catalog: dict) -> dict[str, int]:
    """The counts the gates and the docs advertise, computed once.

    `groups_declared` is `len(catalog["groups"])`; `groups_used` is the number of
    distinct groups actually referenced by a filter. They are equal in every catalog so
    far, but they are not the same question — the README and the diagrams advertise
    declared groups, `validate_catalog`'s summary prints used ones — so both are here
    and callers pick deliberately.
    """
    filters = catalog.get("filters", [])
    return {
        "total": len(filters),
        "compiled": sum(1 for f in filters if f.get("engine") == "recipe-lab"),
        "matrix": sum(1 for f in filters if f.get("engine") == "film-studio-matrix"),
        "mono": sum(1 for f in filters if f.get("tone") == "mono"),
        "authored": sum(1 for f in filters if f.get("source") == "authored-here"),
        "authored_compiled": sum(
            1 for f in filters
            if f.get("engine") == "recipe-lab" and f.get("source") == "authored-here"
        ),
        "groups_declared": len(catalog.get("groups", [])),
        "groups_used": len({f.get("group") for f in filters}),
    }


def load_pack(packs_file: Path, pack_id: str) -> tuple[dict, list[str]]:
    """Return (pack, all pack ids), or exit with a message naming what does exist.

    The empty-`groups` guard is the point of centralising this: a pack that lists no
    groups would otherwise sail through `apply_pack` — which rewrites a whole checkout
    for it — and only fail later, or worse, ship. Exit rather than raise, because every
    caller is a command-line tool whose user wants a sentence, not a traceback.
    """
    packs = json.loads(packs_file.read_text(encoding="utf-8"))["packs"]
    matches = [p for p in packs if p["id"] == pack_id]
    if not matches:
        raise SystemExit(f"no pack {pack_id!r} in {packs_file} "
                         f"(have: {', '.join(p['id'] for p in packs)})")
    pack = matches[0]
    if not pack.get("groups"):
        raise SystemExit(f"pack {pack_id!r} lists no groups")
    return pack, [p["id"] for p in packs]
