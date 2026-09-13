#!/usr/bin/env python3
"""Check that every image a document points at actually exists.

A README whose pictures rot is worse than a README with no pictures, and the usual way
that happens is a rename nobody noticed. Images live in docs/assets/ and nowhere else —
nothing may be hotlinked from a third-party host, so a reference that is not a local path
is a finding too. The single exception is a status badge, which only means anything if it
is generated at request time.

    python tools/check_assets.py

Also enforces the sample naming convention from docs/assets/README.md: a file in
samples/ is `<recipe-id>--off.jpg` / `--on.jpg`, and the id has to exist in the catalog.
A typo there would otherwise leave an orphan picture that no document can find.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "docs" / "assets"
CATALOG = ROOT / "catalog" / "filters.json"

SCAN = sorted(
    [ROOT / "README.md", ROOT / "README.zh-CN.md", ROOT / "CHANGELOG.md"]
) + sorted((ROOT / "docs").glob("*.md")) + sorted(ASSETS.glob("*.md"))

IMG_TAG = re.compile(r"""<img[^>]+src\s*=\s*["']([^"']+)["']""", re.I)
MD_IMG = re.compile(r"!\[[^\]]*\]\(([^)\s]+)")
SAMPLE = re.compile(r"^(?P<id>.+)--(?P<state>off|on)\.(jpg|jpeg|png)$", re.I)
FENCES = re.compile(r"^(```|~~~).*?^\1", re.M | re.S)

# Status badges are the one legitimate exception to "no third-party hosts": they are
# generated per request, so vendoring them would freeze a build status that is supposed to
# move. Everything else — diagrams, screenshots, samples — has to live in docs/assets/.
BADGE_HOSTS = {"img.shields.io", "badgen.net", "flat.badgen.net", "badge.fury.io"}


def is_badge(ref: str) -> bool:
    """A CI status badge or a shields.io style badge."""
    try:
        parts = urlsplit(ref)
    except ValueError:
        return False
    host = (parts.hostname or "").lower()
    path = parts.path.lower()
    if host in BADGE_HOSTS:
        return True
    # GitHub renders its own workflow status as <owner>/<repo>/actions/workflows/x/badge.svg
    return host == "github.com" and "/actions/workflows/" in path and path.endswith("badge.svg")


def strip_code(text: str) -> str:
    """Assets/ conventions doc shows example <img> markup in a fenced block. Those are
    instructions, not references — without this they read as broken links."""
    return FENCES.sub("", text)


def main() -> int:
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    known_ids = {f["id"] for f in catalog["filters"]}

    errors: list[str] = []
    notes: list[str] = []
    checked = 0

    for doc in SCAN:
        if not doc.exists():
            continue
        text = strip_code(doc.read_text(encoding="utf-8"))
        refs = [m for m in IMG_TAG.findall(text)] + [m for m in MD_IMG.findall(text)]
        for ref in refs:
            if ref.startswith(("http://", "https://", "data:", "//")):
                if is_badge(ref):
                    notes.append(f"{doc.relative_to(ROOT)}: status badge {ref} — allowed, "
                                 "it has to be generated per request")
                else:
                    errors.append(f"{doc.relative_to(ROOT)}: external image {ref!r} — "
                                  "images must live in docs/assets/, not a third-party host")
                continue
            checked += 1
            target = (doc.parent / ref.split("#")[0]).resolve()
            if not target.exists():
                errors.append(f"{doc.relative_to(ROOT)}: missing image {ref} "
                              f"(looked for {target.relative_to(ROOT)})")

    # sample naming convention
    samples = ASSETS / "samples"
    if samples.exists():
        for f in sorted(samples.iterdir()):
            if not f.is_file():
                continue
            m = SAMPLE.match(f.name)
            if not m:
                errors.append(f"docs/assets/samples/{f.name}: expected "
                              "<recipe-id>--off.jpg or <recipe-id>--on.jpg")
                continue
            if m.group("id") not in known_ids:
                errors.append(f"docs/assets/samples/{f.name}: '{m.group('id')}' is not "
                              "a recipe id in catalog/filters.json")

    # orphan images: present on disk, referenced nowhere
    on_disk = {p.resolve() for p in ASSETS.rglob("*")
               if p.is_file() and p.suffix.lower() in {".svg", ".png", ".jpg", ".jpeg"}}
    referenced: set[Path] = set()
    for doc in SCAN:
        if not doc.exists():
            continue
        text = strip_code(doc.read_text(encoding="utf-8"))
        for ref in IMG_TAG.findall(text) + MD_IMG.findall(text):
            if not ref.startswith(("http", "data:", "//")):
                referenced.add((doc.parent / ref.split("#")[0]).resolve())
    for orphan in sorted(on_disk - referenced):
        notes.append(f"{orphan.relative_to(ROOT)} is not referenced by any document")

    print(f"assets   : {ASSETS.relative_to(ROOT)}")
    print(f"images   : {len(on_disk)} on disk | {checked} reference(s) checked")
    print(f"recipes  : {len(known_ids)} known ids for sample naming")
    print()

    for n in notes:
        print(f"  note   {n}")
    for e in errors:
        print(f"  ERROR  {e}")

    if errors:
        print(f"\nFAILED — {len(errors)} error(s)")
        return 1
    print(f"OK — every referenced image exists, no external hosts ({len(notes)} note(s))")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
