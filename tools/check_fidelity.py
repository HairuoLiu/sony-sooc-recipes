#!/usr/bin/env python3
"""Verify that our catalog reproduces upstream's recipes exactly.

The whole point of this repository is that catalog/filters.json is the source of truth.
If a transcription slip ever changed a recipe, the generated APK would quietly shoot
different colours than the upstream project it claims to build on. This compares every
recipe against a real upstream checkout.

    curl -sSL -o build/upstream-Recipes.java \\
      https://raw.githubusercontent.com/voxivoid/recipe-lab-sony-pmca/development/src/com/voxivoid/recipelab/Recipes.java
    python tools/check_fidelity.py --upstream build/upstream-Recipes.java

The comparison is semantic, not textual. Both sides are expanded to the full 15-value
form using the constructor defaults, so upstream's occasional long-hand spelling of a
default tail compares equal to our compact output while any real value drift still fails.

Recipes this repository adds on top are reported separately — they are deliberately not
upstream's, and they are expected to be unverified.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from gen_recipes import DEFAULT_CATALOG, generate  # noqa: E402

CALL = re.compile(r"new Recipe\(\s*(.*?)\s*\)\s*,", re.S)
HEAD = re.compile(r'^\s*([A-Z][A-Z0-9_]*)\s*,\s*"([^"]*)"')

# The upstream project's constructors, as value counts after group and name are peeled off.
SHORT = 9    # style sat con sharp matrix wbMode kelvin ab gm
MEDIUM = 12  # ... pe ev dro
LONG = 13    # ... sub

# what the short forms imply, from the constructor bodies in Recipes.java
DEFAULTS_MEDIUM = ["0", "0", "6"]   # pe=0, ev=0, dro=DRO_AUTO
DEFAULTS_LONG = ["0"]               # sub=0

UNAUTHORED = "authored-here"


def canonical(arguments: str) -> tuple[str, str]:
    """Return (name, full 15-value argument string) for one `new Recipe(...)` call."""
    body = re.sub(r"//.*", "", arguments)
    m = HEAD.match(body)
    if not m:
        return "?", f"<unparsed> {body}"

    group, name = m.group(1), m.group(2)
    rest = body[m.end():]
    values = [t.strip() for t in rest.split(",") if t.strip()]

    if len(values) == SHORT:
        values = values + DEFAULTS_MEDIUM + DEFAULTS_LONG
    elif len(values) == MEDIUM:
        values = values + DEFAULTS_LONG
    elif len(values) != LONG:
        return name, f"<unparsed {len(values)} values> {body}"

    return name, f"{group},{name}," + ",".join(values)


def parse(text: str) -> tuple[Counter, dict[str, str]]:
    counter: Counter = Counter()
    labels: dict[str, str] = {}
    for m in CALL.finditer(text):
        name, key = canonical(m.group(1))
        counter[key] += 1
        labels.setdefault(key, name)
    return counter, labels


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--upstream", type=Path, required=True,
                    help="path to a real upstream Recipes.java")
    ap.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    args = ap.parse_args()

    if not args.upstream.exists():
        print(f"missing upstream file: {args.upstream}")
        print("see the docstring for the command that fetches it")
        return 2

    upstream, up_labels = parse(args.upstream.read_text(encoding="utf-8"))
    catalog = json.loads(args.catalog.read_text(encoding="utf-8"))
    ours, our_labels = parse(generate(catalog))

    matched = sum((upstream & ours).values())
    missing = upstream - ours      # upstream recipes we failed to reproduce
    added = ours - upstream        # recipes this repository contributes

    print(f"upstream recipes : {sum(upstream.values())}")
    print(f"our generated    : {sum(ours.values())}")
    print(f"matched exactly  : {matched}")
    print(f"missing          : {sum(missing.values())}")
    print(f"added            : {sum(added.values())}")
    print()

    if missing:
        print("MISSING — upstream recipes we do not reproduce correctly:")
        for key, count in sorted(missing.items()):
            print(f"  x{count}  {up_labels.get(key, '?')}")
            print(f"        upstream: {key}")
            ours_same_name = [k for k in ours if our_labels.get(k) == up_labels.get(key)]
            if ours_same_name:
                print(f"        ours    : {ours_same_name[0]}")
        print()

    if added:
        by_name = {
            re.sub(r"\s+", "", f["name"]): f for f in catalog["filters"]
        }
        print("ADDED — our own recipes, expected to be absent upstream:")
        for key, count in sorted(added.items()):
            label = our_labels.get(key, "?")
            owner = by_name.get(re.sub(r"\s+", "", label))
            source = owner.get("source") if owner else "unknown"
            note = ""
            if owner and not owner.get("verified"):
                note = "  NOT VERIFIED ON HARDWARE"
            print(f"  x{count}  {label}  [{source}]{note}")
        print()

    if missing:
        print(f"FAILED — {sum(missing.values())} upstream recipe(s) drifted")
        return 1

    expected_added = sum(
        1 for f in catalog["filters"]
        if f.get("engine") == "recipe-lab" and f.get("source") == UNAUTHORED
    )
    if sum(added.values()) != expected_added:
        print(
            f"FAILED — expected {expected_added} added recipe(s) from the catalog, "
            f"found {sum(added.values())}"
        )
        return 1

    print(f"OK — all {matched} upstream recipes reproduced value for value, "
          f"plus {sum(added.values())} added here.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
