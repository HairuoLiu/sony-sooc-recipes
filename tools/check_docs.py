#!/usr/bin/env python3
"""Check the bilingual document set: twin coverage, shared diagrams, numbers in diagrams.

English is the front door of this repository and zh-CN is a mirror of it. A mirror that
silently drifts is worse than no mirror at all: a reader following a stale Chinese page has
no way to know it describes an older version of the project. Nothing mechanical can judge
whether a translation is *faithful* — so this gate does not pretend to. It enforces the
three parts that are actually checkable:

  1. Twin coverage. Every English document is either twinned (`X.zh-CN.md` next to `X.md`)
     or declared English-only in `ENGLISH_ONLY` below, with a reason. An undeclared gap is
     an error. The point is not that everything must be translated — it is that the
     decision is recorded rather than being an accident. Declared files print as notes.

  2. Diagrams are shared. `docs/assets/*.svg` must contain no CJK text. The diagrams are
     used by both languages; a per-language copy would be the same duplication this project
     rejects everywhere else (one catalog, one recipe engine, one icon set).

  3. Counts drawn inside a diagram. A number a reader can *see* in a diagram has to match
     `catalog/filters.json`. This is the blind spot that let `architecture.svg` keep
     advertising "99 looks, 13 groups" long after the catalog had passed 150 — the README
     has a counts gate, the diagrams had nothing.

Check 3 reads the `<text>` nodes and matches a small fixed vocabulary ("N looks",
"N groups", "N compiled") rather than trying to parse prose. Matching a stable three-word
phrase is not the same as parsing a wrapped sentence, which the README gate rightly refuses
to do. It still only sees those three phrasings: a diagram that says "155 recipes" some other
way is not caught, and that limit is deliberate rather than hidden.

    python tools/check_docs.py
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CATALOG = ROOT / "catalog" / "filters.json"
ASSETS = ROOT / "docs" / "assets"

# English-only documents, with the reason. Anything not listed here and not twinned is an
# error — add the twin, or add a row here saying why there isn't one.
ENGLISH_ONLY = {
    "docs/CHANNEL-COMPARISON.md":
        "reference table about a competing distribution channel, not about using this one",
    "docs/MAPPING-RECIPES.md":
        "24 KB table of upstream recipe ids, which are English in the upstream source anyway",
}

# Documents that must exist in both languages, beyond the docs/ sweep.
ROOT_TWINS = ["README.md", "CHANGELOG.md"]

CJK = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]")
TEXT_NODE = re.compile(r"<text[^>]*>(.*?)</text>", re.S)
TAGS = re.compile(r"<[^>]+>")

# phrase in a diagram -> which catalog count it must equal
DIAGRAM_COUNTS = {
    re.compile(r"(\d+)\s+looks?\b"): "total",
    re.compile(r"(\d+)\s+groups?\b"): "groups",
    re.compile(r"(\d+)\s+compiled\b"): "compiled",
}


def counts_from_catalog() -> dict[str, int]:
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    filters = catalog["filters"]
    return {
        "total": len(filters),
        "compiled": sum(1 for f in filters if f["engine"] == "recipe-lab"),
        "groups": len(catalog["groups"]),
    }


def check_twins(errors: list[str], notes: list[str]) -> None:
    # English original -> the twin it must have. Both the repository root and docs/.
    pairs: list[tuple[str, str]] = [(r, r[:-3] + ".zh-CN.md") for r in ROOT_TWINS]
    for path in sorted((ROOT / "docs").glob("*.md")):
        rel = path.relative_to(ROOT).as_posix()
        if rel.endswith(".zh-CN.md"):
            continue
        pairs.append((rel, rel[:-3] + ".zh-CN.md"))

    for english, twin in pairs:
        if not (ROOT / english).exists():
            errors.append(
                f"{english}: missing. It is the source of truth for {twin}, so a twin on its "
                f"own describes a document that no longer exists."
            )
            continue
        if (ROOT / twin).exists():
            continue
        if english in ENGLISH_ONLY:
            notes.append(f"{english}: English-only by declaration — {ENGLISH_ONLY[english]}")
        else:
            errors.append(
                f"{english}: no {twin}, and no row in ENGLISH_ONLY saying why. "
                f"Either translate it or declare it."
            )

    # A twin whose English original is gone is leftover, not a translation. This has to
    # sweep the repository root as well as docs/ — a root-level twin was exactly what the
    # first version of this check missed.
    orphans = list((ROOT / "docs").glob("*.zh-CN.md")) + list(ROOT.glob("*.zh-CN.md"))
    for path in sorted(orphans):
        rel = path.relative_to(ROOT).as_posix()
        if not (ROOT / rel.replace(".zh-CN.md", ".md")).exists():
            errors.append(f"{rel}: translation with no English original")

    for d in sorted(ENGLISH_ONLY):
        if not (ROOT / d).exists():
            errors.append(f"{d}: listed in ENGLISH_ONLY but the file does not exist")


def check_diagrams(counts: dict[str, int], errors: list[str]) -> int:
    svgs = sorted(ASSETS.glob("*.svg"))
    if not svgs:
        errors.append("docs/assets: no .svg diagrams found")
        return 0

    checked = 0
    for svg in svgs:
        rel = svg.relative_to(ROOT).as_posix()
        raw = svg.read_text(encoding="utf-8")

        if CJK.search(raw):
            found = sorted(set(CJK.findall(raw)))[:8]
            errors.append(
                f"{rel}: contains CJK text {''.join(found)!r}. The diagrams are shared by "
                f"both languages — keep them language-neutral."
            )

        visible = " ".join(TAGS.sub(" ", t) for t in TEXT_NODE.findall(raw))
        for pattern, key in DIAGRAM_COUNTS.items():
            for value in pattern.findall(visible):
                checked += 1
                if int(value) != counts[key]:
                    errors.append(
                        f"{rel}: says {value} {key}, catalog has {counts[key]}"
                    )
    return checked


def main() -> int:
    errors: list[str] = []
    notes: list[str] = []

    counts = counts_from_catalog()
    check_twins(errors, notes)
    checked = check_diagrams(counts, errors)

    for n in notes:
        print(f"note: {n}")
    if notes:
        print()

    for e in errors:
        print(e)

    if errors:
        print(f"\n{len(errors)} problem(s) in the document set")
        return 1

    print(
        f"ok — twins accounted for, diagrams language-neutral, "
        f"{checked} diagram counts match the catalog "
        f"({counts['total']} looks, {counts['compiled']} compiled, {counts['groups']} groups)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
