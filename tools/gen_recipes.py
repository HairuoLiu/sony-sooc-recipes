#!/usr/bin/env python3
"""Generate the app's Recipes.java from catalog/filters.json.

The camera app needs its recipes as a compiled Java array. Rather than hand-editing
Recipes.java in the upstream fork — which is how recipes get lost — this generator is
the only thing that writes it. Add a filter to catalog/filters.json, run this, rebuild.

    python tools/gen_recipes.py                   # write into the fork at --fork
    python tools/gen_recipes.py --stdout          # print to stdout, write nothing
    python tools/gen_recipes.py --check           # fail if the file on disk is stale

Layout it expects in the fork:

    <fork>/src/com/hairuoliu/sonysoocrecipes/Recipes.java
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CATALOG = ROOT / "catalog" / "filters.json"
RELATIVE_TARGET = Path("src/com/hairuoliu/sonysoocrecipes/Recipes.java")

# group id -> the Java constant name the generated static block refers to.
# Order here is irrelevant; order comes from the catalog's `groups` array.
GROUP_JAVA = {
    "sony": "SONY",
    "fuji-sim": "FSIM",
    "fuji-film": "FFILM",
    "kodak": "KODAK",
    "cine": "CINE",
    "ricoh-gr": "RICOH",
    "leica": "LEICA",
    "hasselblad": "HASSEL",
    "canon-nikon": "CANIK",
    "pentax": "PENTAX",
    "pana-olympus": "PANOLY",
    "other-stocks": "OTHER",
    "ilford": "ILFORD",
    "app-look": "APPLOOK",
}

# default values baked into the base app's 10-argument constructor; we drop back to the
# short form whenever a recipe matches them, so the generated file reads like upstream's.
DEFAULT_PE = 0
DEFAULT_EV = 0
DEFAULT_DRO = 6
DRO_AUTO = 6

HEADER = '''package com.hairuoliu.sonysoocrecipes;

/**
 * GENERATED FILE — do not edit by hand.
 *
 * Source of truth: catalog/filters.json in the sony-sooc-recipes repository.
 * Regenerate with:  python tools/gen_recipes.py
 *
 * Film-look approximations built ONLY from settings this camera can store persistently.
 * {count} recipes across {group_count} groups.
 *
 * The recipe engine, the settings-store map and the original 77 recipes are the work of
 * Andre Domingues (voxivoid), MIT licensed, https://github.com/voxivoid/recipe-lab-sony-pmca
 *
 * style   : Creative Style (stored enum verified: 1 standard, 2 vivid, 3 neutral, 6 mono)
 * sat/con/sharp : Creative Style adjustments (menu range -3..+3; beyond = experimental, camera core accepts sat +-16)
 * matrix  : 1 = PP3 alternate colour matrix (~+45% chroma, blue/green cross-talk)
 * wbMode  : 0 = leave WB as is - 1 = auto - 14 = colour temperature (kelvin)
 * ab / gm : WB fine tune  amber(+)/blue(-)  green(+)/magenta(-)  (-7..+7)
 * pe      : Picture Effect (persistent; when on, Creative Style is ignored by the camera and RAW is disabled)
 * ev      : exposure bias in 1/3 EV steps (persistent)
 * dro     : DRO 0 off, 1..5, 6 auto (persistent)
 * sub     : effect sub-parameter (Soft High-key tint, Toy tone, Partial hue, Posterization mode)
 */
public class Recipes {{
    public static class Recipe {{
        public final int group; public final String name; public final int style, sat, con, sharp, matrix, wbMode, kelvin, ab, gm, pe, ev, dro, sub;
        Recipe(int group, String name, int style, int sat, int con, int sharp, int matrix, int wbMode, int kelvin, int ab, int gm) {{
            this(group, name, style, sat, con, sharp, matrix, wbMode, kelvin, ab, gm, 0, 0, DRO_AUTO);
        }}
        Recipe(int group, String name, int style, int sat, int con, int sharp, int matrix, int wbMode, int kelvin, int ab, int gm, int pe, int ev, int dro) {{
            this(group, name, style, sat, con, sharp, matrix, wbMode, kelvin, ab, gm, pe, ev, dro, 0);
        }}
        Recipe(int group, String name, int style, int sat, int con, int sharp, int matrix, int wbMode, int kelvin, int ab, int gm, int pe, int ev, int dro, int sub) {{
            this.sub = sub;
            this.group = group; this.name = name; this.style = style; this.sat = sat; this.con = con; this.sharp = sharp; this.matrix = matrix;
            this.wbMode = wbMode; this.kelvin = kelvin; this.ab = ab; this.gm = gm; this.pe = pe; this.ev = ev; this.dro = dro;
        }}
        public boolean isEffect() {{ return pe != 0; }}
        /** one-line summary for lists: "Neutral  -4/-1  A1" */
        public String summary() {{
            StringBuilder s = new StringBuilder();
            if (pe != 0) {{ s.append(PE_LABEL[pe]); String sl = subLabel(pe, sub); if (sl != null) s.append(' ').append(sl); }} else s.append(STYLE_LABEL[style]).append("  ").append(sat > 0 ? "+" : "").append(sat).append('/').append(con > 0 ? "+" : "").append(con);
            if (matrix == 1 && pe == 0) s.append("  MTX");
            if (ev != 0) s.append("  ").append(evLabel(ev));
            if (dro != DRO_AUTO) s.append("  DRO ").append(droLabel(dro));
            if (wbMode == 14) s.append("  ").append(kelvin).append('K');
            if (ab != 0) s.append("  ").append(ab > 0 ? "A" + ab : "B" + (-ab));
            if (gm != 0) s.append("  ").append(gm > 0 ? "G" + gm : "M" + (-gm));
            return s.toString();
        }}
    }}

    public static final int STD = 1, VIVID = 2, NEUTRAL = 3, PORTRAIT = 4, LANDSCAPE = 5, MONO = 6, CLEAR = 7, DEEP = 8, LIGHT = 9, SUNSET = 10, NIGHT = 11, AUTUMN = 12, SEPIA = 13;
    /** index = stored enum; value = runtime color-mode name (API) */
    public static final String[] STYLE_NAMES = {{ "?", "standard", "vivid", "neutral", "portrait", "landscape", "mono", "clear", "deep", "light", "sunset", "night", "red-leaves", "sepia" }};
    public static final String[] STYLE_LABEL = {{ "?", "Standard", "Vivid", "Neutral", "Portrait", "Landscape", "B&W", "Clear", "Deep", "Light", "Sunset", "Night", "Autumn", "Sepia" }};

    private static final int AUTO = 1, K = 14;

    /** Picture Effect: stored byte = index in the runtime list (verified) */
    public static final String[] PE_KEYS = {{ "off", "toy-camera", "pop-color", "posterization", "retro-photo", "soft-high-key", "part-color", "rough-mono", "soft-focus", "hdr-art", "richtone-mono", "miniature", "illust", "watercolor" }};
    public static final String[] PE_LABEL = {{ "off", "Toy", "Pop", "Poster", "Retro", "High-key", "Part col", "HC mono", "Soft foc", "HDR art", "Rich mono", "Miniature", "Illust", "Watercol" }};
    public static final int PE_OFF = 0, PE_TOY = 1, PE_POP = 2, PE_RETRO = 4, PE_HIGHKEY = 5, PE_HCMONO = 7;
    /** effect sub-parameter (tint / tone / hue / mode): runtime key, stored slot, value names - index = stored byte */
    public static String subKey(int pe) {{ switch (pe) {{ case 5: return "pe-soft-high-key-effect"; case 1: return "pe-toy-camera-effect"; case 6: return "pe-part-color-effect"; case 3: return "pe-posterization-effect"; default: return null; }} }}
    public static int subId(int pe) {{ switch (pe) {{ case 5: return 0x010709d8; case 1: return 0x010706f3; case 6: return 0x010706ee; case 3: return 0x010706ef; default: return 0; }} }}
    public static String[] subValues(int pe) {{
        switch (pe) {{
            case 5: return new String[] {{ "blue", "pink", "green" }};
            case 1: return new String[] {{ "normal", "cool", "warm", "green", "magenta" }};
            case 6: return new String[] {{ "red", "green", "blue", "yellow" }};
            case 3: return new String[] {{ "posterization-color", "posterization-bw" }};
            default: return null;
        }}
    }}
    public static String subLabel(int pe, int sub) {{ String[] v = subValues(pe); return v == null ? null : (sub >= 0 && sub < v.length ? v[sub].replace("posterization-", "") : "?" + sub); }}
    /** DRO: 0 off, 1..5 level, 6 auto */
    public static final int DRO_OFF = 0, DRO_AUTO = 6;
    public static String droLabel(int v) {{ return v == DRO_AUTO ? "auto" : v == 0 ? "off" : "Lv" + v; }}
    /** exposure bias in 1/3 EV steps -> "+0.7" */
    public static String evLabel(int ev) {{
        if (ev == 0) return "0";
        int a = Math.abs(ev); String frac = a % 3 == 0 ? ".0" : a % 3 == 1 ? ".3" : ".7";
        return (ev > 0 ? "+" : "-") + (a / 3) + frac;
    }}
'''


def emit_recipe(f: dict, group_const: str) -> str:
    """One `new Recipe(...)` line, using the shortest upstream constructor that fits."""
    r = f["recipe"]
    name = f["name"].replace('"', '\\"')

    wb = r["wb"]
    wb_const = "AUTO" if wb["mode"] == "AUTO" else "K"
    head = (
        f'{group_const}, "{name}", {r["style"]}, {r["sat"]}, {r["con"]}, {r["sharp"]}, '
        f'{r["matrix"]}, {wb_const}, {wb["kelvin"]}, {wb["ab"]}, {wb["gm"]}'
    )

    pe, ev, dro, sub = r["pe"], r["ev"], r["dro"], r["sub"]

    if sub != 0:
        return f"new Recipe({head}, {pe}, {ev}, {dro}, {sub}),"
    if (pe, ev, dro) != (DEFAULT_PE, DEFAULT_EV, DEFAULT_DRO):
        return f"new Recipe({head}, {pe}, {ev}, {dro}),"
    return f"new Recipe({head}),"


def generate(catalog: dict) -> str:
    groups = [g for g in catalog["groups"] if g["id"] in GROUP_JAVA]
    missing = [g["id"] for g in catalog["groups"] if g["id"] not in GROUP_JAVA]
    if missing:
        raise SystemExit(f"groups with no Java constant: {', '.join(missing)}")

    recipes = [f for f in catalog["filters"] if f.get("engine") == "recipe-lab"]
    if not recipes:
        raise SystemExit("catalog holds no recipe-lab filters")

    # verify contiguity — the GROUP_START static block below depends on it
    order: list[str] = []
    for f in recipes:
        if not order or order[-1] != f["group"]:
            if f["group"] in order:
                raise SystemExit(
                    f"group {f['group']!r} is not contiguous; reorder the catalog so every "
                    "group's recipes sit together"
                )
            order.append(f["group"])
    if order != [g["id"] for g in groups if any(f["group"] == g["id"] for f in recipes)]:
        raise SystemExit("catalog recipes do not follow the declared group order")

    out = [HEADER.format(count=len(recipes), group_count=len(groups))]
    out.append(f'    // ---- groups (brands) - recipes below MUST be listed in group order')
    out.append(
        "    public static final String[] GROUPS = { "
        + ", ".join(f'"{g["label"]}"' for g in groups)
        + " };"
    )
    out.append(
        "    private static final int "
        + ", ".join(f'{GROUP_JAVA[g["id"]]} = {i}' for i, g in enumerate(groups))
        + ";"
    )
    out.append("")
    out.append("    public static final Recipe[] ALL = {")

    for g in groups:
        gid = g["id"]
        members = [f for f in recipes if f["group"] == gid]
        if not members:
            continue
        out.append(f"        // ---- {g['label']}")
        width = max(len(f["name"]) for f in members)
        for f in members:
            line = emit_recipe(f, GROUP_JAVA[gid])
            if not f.get("verified", True):
                line += "   // NOT VERIFIED ON HARDWARE"
            out.append("        " + line)
        out.append("")

    if out[-1] == "":
        out.pop()
    out.append("    };")
    out.append("")
    out.append("    /** first recipe index of each group */")
    out.append("    public static final int[] GROUP_START = new int[GROUPS.length];")
    out.append("    public static final int[] GROUP_COUNT = new int[GROUPS.length];")
    out.append("    static {")
    out.append("        for (int g = 0; g < GROUPS.length; g++) GROUP_START[g] = -1;")
    out.append("        for (int i = 0; i < ALL.length; i++) {")
    out.append("            int g = ALL[i].group;")
    out.append("            if (GROUP_START[g] < 0) GROUP_START[g] = i;")
    out.append("            GROUP_COUNT[g]++;")
    out.append("        }")
    out.append("    }")
    out.append("}")
    return "\n".join(out) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    ap.add_argument("--fork", type=Path, default=ROOT / "build" / "recipe-lab-sony-pmca",
                    help="path to the upstream checkout to generate into")
    ap.add_argument("--stdout", action="store_true", help="print instead of writing")
    ap.add_argument("--check", action="store_true",
                    help="exit non-zero if the file on disk differs from the generated one")
    args = ap.parse_args()

    source = generate(json.loads(args.catalog.read_text(encoding="utf-8")))

    if args.stdout:
        sys.stdout.write(source)
        return 0

    target = args.fork / RELATIVE_TARGET

    if args.check:
        if not target.exists():
            print(f"STALE — {target} does not exist; run python tools/gen_recipes.py")
            return 1
        if target.read_text(encoding="utf-8") != source:
            print(f"STALE — {target} differs from the catalog; run python tools/gen_recipes.py")
            return 1
        print(f"OK — {target} matches {args.catalog}")
        return 0

    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(source, encoding="utf-8", newline="\n")
    count = source.count("new Recipe(")
    print(f"wrote {target}  ({count} recipes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
