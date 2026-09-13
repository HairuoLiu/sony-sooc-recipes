#!/usr/bin/env python3
"""Validate catalog/filters.json against the Sony PMCA engine's real constraints.

Everything checked here is a rule the camera or the upstream engine actually enforces,
or a rule this repository needs to stay honest about provenance. Run it before every
commit, and in CI.

    python tools/validate_catalog.py            # validate the shipped catalog
    python tools/validate_catalog.py path.json  # validate a candidate catalog
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CATALOG = ROOT / "catalog" / "filters.json"

# --- constraint tables, mirrored from Recipe Lab's Recipes.java ---------------------
VALID_STYLES = {
    "STD", "VIVID", "NEUTRAL", "PORTRAIT", "LANDSCAPE", "MONO",
    "CLEAR", "DEEP", "LIGHT", "SUNSET", "NIGHT", "AUTUMN", "SEPIA",
}

# Creative Style sliders: the menu exposes -3..+3, but the camera core accepts more.
MENU_SLIDER_RANGE = (-3, 3)
CORE_SLIDER_RANGE = (-16, 16)

MATRIX_STYLES = {"VIVID", "CLEAR", "DEEP", "LIGHT", "SUNSET", "NIGHT", "AUTUMN"}

WB_MODES = {"AUTO", "K"}
KELVIN_RANGE = (2500, 9900)

AB_RANGE = (-7, 7)
GM_RANGE = (-7, 7)

PE_VALUES = set(range(0, 14))          # index into the runtime picture-effect list
PE_OFF = 0
# picture effects that expose a sub-parameter, and how many values that sub-parameter has
PE_SUB_COUNT = {5: 3, 1: 5, 6: 4, 3: 2}
PE_JPEG_ONLY = 1                       # effects disable RAW, so a PE recipe needs Quality = JPEG

EV_RANGE = (-5, 5)                     # in 1/3 EV steps
DRO_VALUES = {0, 1, 2, 3, 4, 5, 6}     # 0 off, 1..5 level, 6 auto
DRO_AUTO = 6

ENGINES = {"recipe-lab", "film-studio-matrix"}
SOURCES = {"recipe-lab", "film-studio", "authored-here"}
TONES = {"color", "mono"}

KNOWN_GROUPS = {
    "sony", "fuji-sim", "fuji-film", "kodak", "cine",
    "ricoh-gr", "leica", "hasselblad", "canon-nikon",
    "pana-olympus", "other-stocks", "ilford",
}

EXPECTED_UPSTREAM_RECIPES = 77


class Report:
    """Three severities, because not every finding is a problem.

    errors   — the catalog is broken or dishonest; the build must stop.
    warnings — worth a look before this ships.
    notes    — by-design consequences of the engine that a recipe author needs to know.
               Recipe Lab's own recipes trip these on purpose, so they are not defects.
    """

    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.notes: list[str] = []

    def error(self, where: str, msg: str) -> None:
        self.errors.append(f"{where}: {msg}")

    def warn(self, where: str, msg: str) -> None:
        self.warnings.append(f"{where}: {msg}")

    def note(self, where: str, msg: str) -> None:
        self.notes.append(f"{where}: {msg}")


def check_int(report: Report, where: str, field: str, value, lo: int, hi: int) -> None:
    if not isinstance(value, int) or isinstance(value, bool):
        report.error(where, f"{field} must be an integer, got {value!r}")
    elif not (lo <= value <= hi):
        report.error(where, f"{field}={value} is outside {lo}..{hi}")


def validate(catalog: dict) -> Report:
    report = Report()

    if catalog.get("engines", {}).get("film-studio-matrix", {}).get("license", "").startswith("MIT"):
        report.error("catalog", "film-studio-matrix must not be described as MIT")

    filters = catalog.get("filters")
    if not isinstance(filters, list) or not filters:
        report.error("catalog", "filters must be a non-empty list")
        return report

    seen_ids: dict[str, int] = {}
    # Only recipe-lab entries are compiled into one Java array, so only they must sit in
    # contiguous per-group runs. film-studio-matrix looks are catalogued beside them but
    # are emitted nowhere, so interleaving them is fine and keeps each brand in one place.
    group_order: list[str] = []

    for index, f in enumerate(filters):
        fid = f.get("id", f"<index {index}>")
        where = fid

        if not isinstance(f.get("id"), str) or not f["id"]:
            report.error(where, "missing id")
        elif f["id"] in seen_ids:
            report.error(where, f"duplicate id (first seen at index {seen_ids[f['id']]})")
        else:
            seen_ids[f["id"]] = index

        if not isinstance(f.get("name"), str) or not f["name"].strip():
            report.error(where, "missing name")

        group = f.get("group")
        if group not in KNOWN_GROUPS:
            report.error(where, f"unknown group {group!r}")
        elif f.get("engine") == "recipe-lab":
            if not group_order or group_order[-1] != group:
                if group in group_order:
                    report.error(
                        where,
                        f"group {group!r} appears again after another group — the generator "
                        "relies on recipe-lab entries being contiguous per group",
                    )
                group_order.append(group)

        engine = f.get("engine")
        if engine not in ENGINES:
            report.error(where, f"unknown engine {engine!r}")

        source = f.get("source")
        if source not in SOURCES:
            report.error(where, f"unknown source {source!r}")

        tone = f.get("tone")
        if tone not in TONES:
            report.error(where, f"unknown tone {tone!r}")

        if not isinstance(f.get("verified"), bool):
            report.error(where, "verified must be a boolean")

        # --- engine-specific payloads ---
        if engine == "recipe-lab":
            recipe = f.get("recipe")
            if not isinstance(recipe, dict):
                report.error(where, "recipe-lab filter needs a recipe object")
                continue
            validate_recipe(report, where, recipe)

        elif engine == "film-studio-matrix":
            if f.get("recipe") is not None:
                report.error(where, "film-studio-matrix filter must not carry a recipe object")
            strengths = f.get("strengths")
            if strengths != [30, 50, 70, 100]:
                report.error(where, f"strengths must be [30, 50, 70, 100], got {strengths!r}")
            if source == "film-studio" and f.get("verified") and not f.get("cross_ref"):
                report.warn(where, "verified film-studio look has no cross_ref to a recipe-lab twin")

    validate_cross_refs(report, filters, seen_ids)
    validate_provenance(report, filters)
    return report


def validate_recipe(report: Report, where: str, r: dict) -> None:
    style = r.get("style")
    if style not in VALID_STYLES:
        report.error(where, f"unknown style {style!r}")

    for field in ("sat", "con", "sharp"):
        check_int(report, where, field, r.get(field), *CORE_SLIDER_RANGE)

    sat = r.get("sat")
    if isinstance(sat, int) and not (MENU_SLIDER_RANGE[0] <= sat <= MENU_SLIDER_RANGE[1]):
        report.note(
            where,
            f"sat={sat} is outside the menu slider {MENU_SLIDER_RANGE} — legal, the camera "
            "core accepts it, but the on-camera slider will show the nearest value and "
            "touching it loses the extra punch",
        )

    matrix = r.get("matrix")
    if matrix not in (0, 1):
        report.error(where, f"matrix must be 0 or 1, got {matrix!r}")
    elif matrix == 1 and style not in MATRIX_STYLES:
        report.note(
            where,
            f"matrix=1 on style {style} — the alternate colour matrix only takes effect "
            "on the styles that use it",
        )

    wb = r.get("wb")
    if not isinstance(wb, dict):
        report.error(where, "recipe.wb must be an object")
    else:
        mode = wb.get("mode")
        if mode not in WB_MODES:
            report.error(where, f"unknown wb.mode {mode!r}")
        if mode == "AUTO":
            if wb.get("kelvin"):
                report.error(where, "wb.mode=AUTO must not carry a kelvin value")
        else:
            check_int(report, where, "wb.kelvin", wb.get("kelvin"), *KELVIN_RANGE)
        check_int(report, where, "wb.ab", wb.get("ab"), *AB_RANGE)
        check_int(report, where, "wb.gm", wb.get("gm"), *GM_RANGE)

    pe = r.get("pe")
    if pe not in PE_VALUES:
        report.error(where, f"unknown pe index {pe!r}")
    sub = r.get("sub")
    if not isinstance(sub, int) or isinstance(sub, bool):
        report.error(where, f"sub must be an integer, got {sub!r}")
    else:
        if pe == PE_OFF and sub != 0:
            report.error(where, f"pe=off but sub={sub}")
        expected = PE_SUB_COUNT.get(pe)
        if expected is not None and not (0 <= sub < expected):
            report.error(where, f"pe={pe} takes sub 0..{expected - 1}, got {sub}")
        if expected is None and pe != PE_OFF and sub != 0:
            report.warn(where, f"pe={pe} exposes no sub-parameter but sub={sub} is set")

    if pe != PE_OFF:
        edits = [k for k in ("sat", "con", "sharp") if r.get(k)]
        if edits:
            report.note(
                where,
                f"pe={pe} makes the camera ignore Creative Style, so {', '.join(edits)} "
                "are stored but have no visible effect",
            )
        if r.get("matrix") == 1:
            report.note(
                where,
                f"pe={pe} makes the camera ignore Creative Style, so matrix=1 has no effect",
            )

    check_int(report, where, "ev", r.get("ev"), *EV_RANGE)
    dro = r.get("dro")
    if dro not in DRO_VALUES:
        report.error(where, f"dro must be one of {sorted(DRO_VALUES)}, got {dro!r}")


def validate_cross_refs(report: Report, filters: list, seen_ids: dict) -> None:
    by_id = {f.get("id"): f for f in filters}
    for f in filters:
        ref = f.get("cross_ref")
        if ref is None:
            continue
        if ref not in by_id:
            report.error(f["id"], f"cross_ref points at unknown filter {ref!r}")
            continue
        other = by_id[ref]
        if f.get("tone") != other.get("tone"):
            report.warn(
                f["id"],
                f"cross_ref tone mismatch: {f.get('tone')} vs {other.get('tone')}",
            )
        if other.get("cross_ref") != f.get("id"):
            report.warn(f["id"], f"cross_ref to {ref} is not reciprocated")


def validate_provenance(report: Report, filters: list) -> None:
    """Fail loudly if anything sourced from a non-redistributable upstream carries
    compile-ready parameters. This is the guard that keeps the repository honest."""
    counts: dict[str, int] = {}
    for f in filters:
        counts[f.get("source", "?")] = counts.get(f.get("source", "?"), 0) + 1

    for f in filters:
        if f.get("source") == "film-studio" and f.get("recipe") is not None:
            report.error(
                f["id"],
                "film-studio is PolyForm Noncommercial and does not ship a base APK — "
                "its looks may be catalogued by name, but fitted parameters must not be "
                "transcribed into this repository",
            )

    if counts.get("recipe-lab", 0) != EXPECTED_UPSTREAM_RECIPES:
        report.warn(
            "catalog",
            f"expected {EXPECTED_UPSTREAM_RECIPES} recipe-lab recipes from upstream, "
            f"catalog has {counts.get('recipe-lab', 0)}",
        )


def main() -> int:
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_CATALOG
    catalog = json.loads(path.read_text(encoding="utf-8"))
    report = validate(catalog)

    recipe_lab = sum(1 for f in catalog["filters"] if f.get("engine") == "recipe-lab")
    matrix = sum(1 for f in catalog["filters"] if f.get("engine") == "film-studio-matrix")
    mono = sum(1 for f in catalog["filters"] if f.get("tone") == "mono")
    authored = sum(1 for f in catalog["filters"] if f.get("source") == "authored-here")

    print(f"catalog : {path}")
    print(
        f"filters : {len(catalog['filters'])} total | {recipe_lab} compiled "
        f"({authored} authored here) | {matrix} reference-only"
    )
    print(f"tones   : {mono} mono | {len(catalog['filters']) - mono} color")
    print(f"groups  : {len({f['group'] for f in catalog['filters']})}")
    print()

    for w in report.warnings:
        print(f"  warn   {w}")
    for e in report.errors:
        print(f"  ERROR  {e}")

    if report.errors:
        print(f"\nFAILED — {len(report.errors)} error(s), {len(report.warnings)} warning(s)")
        return 1

    print(f"OK — 0 errors, {len(report.warnings)} warning(s)")
    if report.notes:
        print(f"\n{len(report.notes)} note(s) — expected behaviour of the engine, not defects:")
        for n in report.notes:
            print(f"  note   {n}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
