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

  4. The two FAQs answer the same number of questions. Twin coverage only proves the Chinese
     file *exists*; it says nothing about the two files still covering the same ground. A
     question added to one language and not the other leaves a FAQ that reads as complete in
     both languages, which is exactly the drift nobody notices. Counting headings is a proxy
     rather than a proof of faithfulness — nothing mechanical can judge that — but for this
     pair the questions are the unit and they map one-to-one, so a split or a merge is an
     event worth being told about instead of finding out later.

  5. Every internal link resolves, anchors included. A rendered page does not show its
     heading ids, so `[Uninstall](#uninstall)` reads perfectly well after somebody renames
     the heading to "Getting rid of it" — the reader discovers it by clicking and going
     nowhere. The anchors are the invisible half of an edit, which is why restructuring
     a document is riskier than writing one.

Check 3 reads the `<text>` nodes and matches a small fixed vocabulary ("N looks",
"N groups", "N compiled") rather than trying to parse prose. Matching a stable three-word
phrase is not the same as parsing a wrapped sentence, which the README gate rightly refuses
to do. It still only sees those three phrasings: a diagram that says "155 recipes" some other
way is not caught, and that limit is deliberate rather than hidden.

    python tools/check_docs.py
"""

from __future__ import annotations

import cataloglib
import os
import re
import sys
import unicodedata
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

# Link targets inside Markdown and inside embedded HTML. Both forms are used in this
# repository, and both rot identically when a heading is renamed.
MD_LINK = re.compile(r"\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
HTML_HREF = re.compile(r'href="([^"]+)"')
CODE_SPAN = re.compile(r"`[^`]*`")
EXTERNAL = ("http://", "https://", "mailto:", "//")

# build/ is generated and .git is not published; neither is part of the document set.
SKIP_DIRS = {".git", "build", "node_modules"}

# phrase in a diagram -> which catalog count it must equal
DIAGRAM_COUNTS = {
    re.compile(r"(\d+)\s+looks?\b"): "total",
    re.compile(r"(\d+)\s+groups?\b"): "groups",
    re.compile(r"(\d+)\s+compiled\b"): "compiled",
}


def counts_from_catalog() -> dict[str, int]:
    stats = cataloglib.catalog_stats(cataloglib.load_catalog(CATALOG))
    return {
        "total": stats["total"],
        "compiled": stats["compiled"],
        "groups": stats["groups_declared"],
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


def check_faq_parity(errors: list[str]) -> int:
    """Both FAQs must answer the same number of questions. Returns the count.

    The pair is hardcoded rather than discovered: the invariant "one question, one twin
    question" is true of the FAQ because questions are the unit of that document. It is not
    true of prose documents, where a translation may legitimately restructure a section.
    Applying this sweep everywhere would produce false alarms, and a gate that cries wolf is
    worse than the drift it was meant to catch.
    """
    english = ROOT / "docs" / "FAQ.md"
    twin = ROOT / "docs" / "FAQ.zh-CN.md"
    if not english.exists() or not twin.exists():
        return 0  # check_twins already reports a missing or orphaned twin

    def questions(path: Path) -> list[str]:
        return [
            line[4:].strip()
            for line in path.read_text(encoding="utf-8").splitlines()
            if line.startswith("### ")
        ]

    en, zh = questions(english), questions(twin)
    if len(en) != len(zh):
        errors.append(
            f"docs/FAQ.md asks {len(en)} questions and docs/FAQ.zh-CN.md asks {len(zh)}. "
            f"A question answered in one language only leaves a FAQ that reads as complete "
            f"in both. Either translate it or delete it from the other side."
        )
    return len(en)


def _markdown_files() -> list[Path]:
    found: list[Path] = []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fn in filenames:
            if fn.endswith(".md"):
                found.append(Path(dirpath) / fn)
    return sorted(found)


def _linkable_text(text: str) -> str:
    """The prose of a document, without fenced blocks or inline code.

    Both are excluded on purpose. ADDING-FILTERS explains Markdown syntax inside fences,
    and a link in an example is a picture of a link rather than one anybody can follow —
    checking it would either demand that examples stay valid forever or invent failures.
    """
    out, fence = [], False
    for line in text.splitlines():
        if line.lstrip().startswith("```"):
            fence = not fence
            continue
        if fence:
            continue
        out.append(CODE_SPAN.sub(" ", line))
    return "\n".join(out)


def _headings(text: str) -> list[str]:
    out, fence = [], False
    for line in text.splitlines():
        if line.lstrip().startswith("```"):
            fence = not fence
            continue
        if fence:
            continue
        m = re.match(r"^#{1,6}\s+(.*)$", line)
        if m:
            out.append(m.group(1).strip())
    return out


def slugify(text: str) -> str:
    """A heading's id, the way GitHub derives it: lower-case, punctuation dropped, runs of
    spaces collapsed into hyphens.

    The traps here are all in one place. Markdown inside a heading is rendered before the
    id is made, so **`bold`** contributes "bold" rather than the asterisks. And the obvious
    way to keep CJK — a range covering U+FF00 — keeps full-width *punctuation* too, because
    that block holds both. The first version of this function did exactly that and reported
    every Chinese heading containing a full-width colon or comma as broken: a gate that
    cries wolf is worse than no gate. Categories, not ranges: keep letters and numbers,
    drop everything else, whatever block it lives in.
    """
    s = text.strip()
    s = CODE_SPAN.sub(lambda m: m.group(0)[1:-1], s)   # `label` -> label, no asterisks left
    s = re.sub(r"\*\*?([^*]*)\*\*?", r"\1", s)
    s = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", s)
    s = re.sub(r"<[^>]+>", "", s)
    s = s.lower()
    kept = [c for c in s if c in "-_ " or unicodedata.category(c)[0] in ("L", "N")]
    return "".join(kept).replace(" ", "-")


def check_links(errors: list[str]) -> int:
    """Internal links must resolve — file and anchor both.

    External URLs are excluded because reaching them means reaching the network, and a
    gate that fails when somebody's site is down gets ignored. Catalog entries rendered
    elsewhere are someone else's problem; this check is about the documents in this
    repository pointing at each other.
    """
    anchors_by_file: dict[Path, set[str]] = {}
    checked = 0

    def anchors_of(path: Path) -> set[str]:
        if path not in anchors_by_file:
            try:
                raw = path.read_text(encoding="utf-8")
            except (UnicodeDecodeError, OSError):
                anchors_by_file[path] = set()
            else:
                anchors_by_file[path] = {slugify(h) for h in _headings(raw)}
        return anchors_by_file[path]

    for path in _markdown_files():
        rel = path.relative_to(ROOT).as_posix()
        own = anchors_of(path)
        body = _linkable_text(path.read_text(encoding="utf-8", errors="replace"))

        targets: list[str] = []
        for pattern in (MD_LINK, HTML_HREF):
            targets.extend(m.group(1) for m in pattern.finditer(body))

        for target in targets:
            if target.startswith(EXTERNAL):
                continue
            if target.startswith("#"):
                checked += 1
                if slugify(target[1:]) not in own:
                    errors.append(
                        f"{rel}: link {target!r} has no matching heading. Either the heading "
                        f"was renamed or the link was typed by hand; a rendered page does not "
                        f"show its ids, so this one fails silently until somebody clicks it."
                    )
                continue

            file_part, _, fragment = target.partition("#")
            if not file_part:
                continue
            base = ROOT if file_part.startswith("/") else path.parent
            resolved = (base / file_part.lstrip("/")).resolve()
            if not resolved.exists():
                checked += 1
                where = file_part if file_part.startswith("/") else target
                errors.append(
                    f"{rel}: link {where!r} points at a file that does not exist. Relative "
                    f"links resolve against the file that contains them, not the repository "
                    f"root — from {rel} that means {resolved.relative_to(ROOT).as_posix()}."
                )
                continue
            if fragment and resolved.suffix == ".md":
                checked += 1
                if slugify(fragment) not in anchors_of(resolved):
                    errors.append(
                        f"{rel}: link {target!r} reaches "
                        f"{resolved.relative_to(ROOT).as_posix()} but that file has no "
                        f"heading producing {fragment!r}."
                    )
    return checked


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
    links = check_links(errors)
    faq_questions = check_faq_parity(errors)

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
        f"({counts['total']} looks, {counts['compiled']} compiled, {counts['groups']} groups), "
        f"{links} internal link(s) resolve, "
        f"both FAQs ask the same {faq_questions} questions"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
