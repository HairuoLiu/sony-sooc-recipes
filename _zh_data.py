import json, os, re

R = r"D:\WorkBuddyData\WorkBuddy\2026-09-13-11-53-33\sony-sooc-recipes"
OUT = r"D:\WorkBuddyData\WorkBuddy\2026-09-13-11-53-33\_zh_data.log"
log = []

# 83 remaining name_zh translations. Convention follows the existing data:
# brand into Chinese (富士/柯达/徕卡/哈苏/宾得/伊尔福...), model + technical
# designators kept in Latin (Reala 500D, HNCS, GR, ACROS, Portra 400).
ZH = {
    # sony
    "sony-pt-portrait": "索尼 PT（人像）",
    "sony-nt-neutral": "索尼 NT（中性）",
    "sony-vv-vivid": "索尼 VV（鲜艳）",
    "sony-vv2": "索尼 VV2",
    "sony-fl-film-like": "索尼 FL（胶片感）",
    "sony-in-instant": "索尼 IN（即显）",
    "sony-sh-soft-high-key": "索尼 SH（柔和高调）",
    # fuji-sim (camera film simulations -> Fujifilm's own Chinese menu names)
    "provia": "标准 PROVIA", "velvia": "鲜艳 Velvia", "astia": "柔和 ASTIA",
    "classic-chrome": "经典正片", "classic-negative": "经典负片",
    "nostalgic-neg": "怀旧负片", "reala-ace": "REALA ACE",
    "pro-neg-std": "专业负片·标准", "pro-neg-hi": "专业负片·高色调",
    "eterna": "电影 ETERNA", "eterna-bleach-bypass": "漂白",
    "acros": "黑白 ACROS", "acros-ye": "ACROS 黄滤镜",
    "acros-r": "ACROS 红滤镜", "acros-g": "ACROS 绿滤镜", "sepia": "棕褐色",
    "fs-provia": "标准 PROVIA", "fs-velvia": "鲜艳 Velvia", "fs-astia": "柔和 ASTIA",
    "fs-classic-chrome": "经典正片", "fs-reala-ace": "REALA ACE",
    "fs-pro-neg-std": "专业负片·标准", "fs-classic-neg": "经典负片",
    "fs-eterna": "电影 ETERNA", "fs-eterna-bb": "漂白", "fs-acros": "黑白 ACROS",
    # fuji-film
    "fuji-pro-400h": "富士 Pro 400H", "fuji-fortia-50": "富士 Fortia 50",
    "fuji-superia-400": "富士 Superia 400", "fuji-c200": "富士 C200",
    "fuji-natura-1600": "富士 Natura 1600",
    # kodak
    "kodak-portra-160": "柯达 Portra 160", "kodak-portra-400": "柯达 Portra 400",
    "kodak-portra-800": "柯达 Portra 800", "kodak-gold-200": "柯达 Gold 200",
    "kodak-ultramax-400": "柯达 Ultra Max 400", "kodak-colorplus-200": "柯达 Color Plus 200",
    "kodak-ektar-100": "柯达 Ektar 100", "kodak-ektachrome-e100": "柯达 Ektachrome E100",
    "kodachrome-64": "柯达克罗姆 64",
    "kodak-vision3-500t": "柯达 Vision3 500T（日光）",
    "kodak-vision2-500t": "柯达 Vision2 500T（灯光）",
    "kodak-vision-200t-asteroid-city": "柯达 Vision 200T（小行星城）",
    "kodak-trix-400": "柯达 Tri-X 400", "kodak-tmax": "柯达 T-Max",
    "kodak-trix-1600-pushed": "柯达 Tri-X 1600（迫冲）",
    # cine
    "cinestill-50d": "Cinestill 50D（蓝丝绒）", "cinestill-800t": "Cinestill 800T",
    "classic-cinema": "经典电影", "rec709-video": "Rec709 视频（平）",
    # ricoh-gr
    "gr-bleach-bypass": "GR 漂白旁路", "gr-retro": "GR 复古",
    "gr-hard-monotone": "GR 硬调黑白", "gr-soft-monotone": "GR 柔调黑白",
    # leica
    "leica-contemporary": "徕卡 现代", "leica-classic": "徕卡 经典",
    "leica-eternal": "徕卡 永恒", "leica-monochrom": "徕卡 Monochrom",
    # hasselblad
    "hasselblad-hncs-natural": "哈苏 HNCS 自然",
    # canon / nikon
    "canon-standard": "佳能 标准", "canon-portrait": "佳能 人像",
    "canon-faithful": "佳能 可靠设置", "nikon-flat": "尼康 平面", "nikon-vivid": "尼康 鲜艳",
    # pana / olympus
    "pana-l-monochrome-d": "松下 L.单色D", "pana-l-classicneo": "松下 L.经典Neo",
    "olympus-pop-art": "奥林巴斯 波普艺术", "olympus-pale-light": "奥林巴斯 淡色亮调",
    # other stocks
    "agfa-vista-200": "爱克发 Vista 200", "agfa-ultra-100": "爱克发 Ultra 100",
    "polaroid-instax": "宝丽来 / 拍立得",
    # ilford
    "ilford-hp5": "伊尔福 HP5", "ilford-fp4": "伊尔福 FP4",
    "ilford-delta-100": "伊尔福 Delta 100", "ilford-delta-3200": "伊尔福 Delta 3200",
    "ilford-pan-f-50": "伊尔福 Pan F 50",
}

GROUP_ZH = {
    "sony": "索尼", "fuji-sim": "富士模拟", "fuji-film": "富士胶片", "kodak": "柯达",
    "cine": "电影", "ricoh-gr": "理光 GR", "leica": "徕卡", "hasselblad": "哈苏",
    "canon-nikon": "佳能/尼康", "pentax": "宾得", "pana-olympus": "松下/奥林巴斯",
    "other-stocks": "其他胶片", "ilford": "伊尔福", "app-look": "机内滤镜",
}

PACK_ZH = {
    "leica": "徕卡风格", "fujifilm": "富士模拟", "filmstocks": "富士胶片",
    "ricoh": "理光 GR 风格", "kodak": "柯达风格", "pentax": "宾得风格",
    "nichefilm": "小众胶片", "hasselblad": "哈苏风格", "sony": "索尼风格",
}

# ---------- 1. filters.json : insert name_zh per line ----------
fp = os.path.join(R, "catalog", "filters.json")
lines = open(fp, encoding="utf-8").read().split("\n")
patched = 0
for i, ln in enumerate(lines):
    m = re.search(r'"id":\s*"([^"]+)"', ln)
    if not m or m.group(1) not in ZH:
        continue
    if '"name_zh"' in ln:
        continue
    nm = re.search(r'"name":\s*"((?:[^"\\]|\\.)*)"', ln)
    if not nm:
        log.append(f"!! no name field on line for {m.group(1)}")
        continue
    zhv = ZH[m.group(1)]
    lines[i] = ln[:nm.end()] + f', "name_zh": "{zhv}"' + ln[nm.end():]
    patched += 1
open(fp, "w", encoding="utf-8", newline="").write("\n".join(lines))
log.append(f"filters.json: inserted name_zh on {patched} lines")

# ---------- 2. groups : insert label_zh ----------
patched_g = 0
for i, ln in enumerate(lines):
    m = re.search(r'"id":\s*"([^"]+)"', ln)
    if not m or m.group(1) not in GROUP_ZH:
        continue
    if '"label_zh"' in ln or '"label"' not in ln:
        continue
    lm = re.search(r'"label":\s*"((?:[^"\\]|\\.)*)"', ln)
    if not lm:
        continue
    lines[i] = ln[:lm.end()] + f', "label_zh": "{GROUP_ZH[m.group(1)]}"' + ln[lm.end():]
    patched_g += 1
open(fp, "w", encoding="utf-8", newline="").write("\n".join(lines))
log.append(f"filters.json: inserted label_zh on {patched_g} group lines")

# ---------- 3. packs.json : insert app_name_zh ----------
pp = os.path.join(R, "catalog", "packs.json")
plines = open(pp, encoding="utf-8").read().split("\n")
out, cur, patched_p = [], None, 0
for ln in plines:
    out.append(ln)
    m = re.search(r'"id":\s*"([^"]+)"', ln)
    if m:
        cur = m.group(1)
        continue
    if cur in PACK_ZH and '"app_name"' in ln and '"app_name_zh"' not in ln:
        indent = re.match(r"\s*", ln).group(0)
        out.append(f'{indent}"app_name_zh": "{PACK_ZH[cur]}",')
        patched_p += 1
open(pp, "w", encoding="utf-8", newline="").write("\n".join(out))
log.append(f"packs.json: inserted app_name_zh on {patched_p} packs")

# ---------- verify + collect charset ----------
f = json.load(open(fp, encoding="utf-8"))
items = f["filters"]
missing = [i["id"] for i in items if not str(i.get("name_zh", "")).strip()]
log.append(f"verify: {len(items)-len(missing)}/{len(items)} have name_zh; missing={missing[:5]}")
gm = [g["id"] for g in f["groups"] if not str(g.get("label_zh", "")).strip()]
log.append(f"verify: groups missing label_zh = {gm}")

chars = set()
for i in items:
    chars.update(str(i.get("name_zh", "")))
for g in f["groups"]:
    chars.update(str(g.get("label_zh", "")))
for v in PACK_ZH.values():
    chars.update(v)
# UI strings that must render in the app
UI = ["配方", "创意风格", "图片效果", "已启用", "预览中", "受保护", "索尼直出配方"]
for s in UI:
    chars.update(s)
chars = {c for c in chars if c.strip()}
open(r"D:\WorkBuddyData\WorkBuddy\2026-09-13-11-53-33\_zhchars.txt", "w", encoding="utf-8").write("".join(sorted(chars)))
log.append(f"charset: {len(chars)} distinct chars")

with open(OUT, "w", encoding="utf-8") as fh:
    fh.write("\n".join(log) + "\n")
print("WROTE", OUT)
