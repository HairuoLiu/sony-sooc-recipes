package {ui_package};

import android.content.Context;
import android.graphics.Canvas;
import android.graphics.Paint;
import android.graphics.RectF;
import android.graphics.Typeface;
import android.util.AttributeSet;
import android.view.View;

/**
 * Single-column recipe browser: every recipe of this brand, grouped by category, in one
 * vertical list.
 *
 * The old browser was two columns — a left BRAND/groups rail and the recipes of the
 * highlighted group on the right — on a black panel. It is gone for two reasons:
 *
 *   1. Each APK now carries exactly one brand (see catalog/packs.json and tools/apply_pack.py),
 *      so there is nothing to branch to on the left. The rail was pure navigation overhead.
 *   2. The white frosted main screen is the look; a black panel next to it read as a bug.
 *
 * So the picker is now one scrollable column: a brand header — preceded by a full-width
 * divider — then that brand's recipes, all concatenated, with the whole list wrapped around
 * the current recipe. UP/DOWN (MainActivity.browserKey) calls nextRecipe(±1) across ALL
 * recipes, so the column scrolls end to end.
 *
 * v0.88 — the selected row carries a "设置" affordance. Before this, ENTER (and RIGHT)
 * only closed the list, so there was no on-screen answer to "how do I edit this look": the
 * row showed a name and a tag and nothing that read as a button. ENTER / RIGHT now open the
 * bottom-bar editor behind it.
 *
 * v0.89 — two defects fixed in this file:
 *
 *   TOFU. Every canvas-drawn view here painted with the SYSTEM face, because nothing ever
 *   called setTypeface on these Paints — MainActivity.applyFont() binds the bundled face to
 *   TextViews and to Legend.FONT, and this class was simply missed. On a Chinese body that
 *   is why 安布罗式湿版 / 宝丽来 Type 100 褐调 rendered as boxes while the main screen was
 *   fine: the main screen's name IS a TextView, this list is not. FONT is a static filled by
 *   applyFont(); it is applied on the first draw, because the view is inflated (and its
 *   Paints built) before applyFont() runs.
 *
 *   SCROLL LAG. onDraw used to measure the tag and settings text and rebuild every recipe's
 *   summary string for every visible row on every frame — measureText twice and one string
 *   build per row, per frame, while the dial is spinning. Both are now cached: the two tag
 *   widths and the settings width are measured once in the constructor (there are exactly
 *   three possible strings), summaries are memoised per recipe, and the group→row index table
 *   is built once instead of being re-summed on every draw.
 *
 * Colours come from catalog/ui-theme.json via tools/patch_ui.py, so this one file is the only
 * place the browser's colours live.
 */
public class PickerView extends View {
    private static final int ACCENT = {picker_accent};

    /** Set by MainActivity.applyFont(); applied to the Paints below on the first draw. */
    public static Typeface FONT;

    private final Paint bg = new Paint(Paint.ANTI_ALIAS_FLAG), edge = new Paint(Paint.ANTI_ALIAS_FLAG), sel = new Paint(Paint.ANTI_ALIAS_FLAG),
            head = new Paint(Paint.ANTI_ALIAS_FLAG), item = new Paint(Paint.ANTI_ALIAS_FLAG), small = new Paint(Paint.ANTI_ALIAS_FLAG), rule = new Paint(),
            track = new Paint(Paint.ANTI_ALIAS_FLAG), thumb = new Paint(Paint.ANTI_ALIAS_FLAG), tagBg = new Paint(Paint.ANTI_ALIAS_FLAG);
    private final RectF r = new RectF();
    private final float d;
    private final Legend legend;
    // v0.88: "pick" no longer describes what ENTER does — it opens the settings editor, so
    // the legend now says so. See MainActivity.browserKey / openEditor.
    private static final int[] ICONS = { Legend.UPDOWN, Legend.ENTER, Legend.FN };
    private static final String[] TEXT = { "move", "settings", "close" };
    private static final String[] TEXT_ZH = { "移动", "设置", "关闭" };
    static { if (Recipes.ZH) System.arraycopy(TEXT_ZH, 0, TEXT, 0, TEXT_ZH.length); }
    private int selected = 0;

    // --- v0.89 caches --------------------------------------------------------------------
    // Row geometry is a pure function of the (immutable) recipe table, so it is computed
    // once. groupFlat[g] is the row index of brand g's header, or -1 when that brand has no
    // recipes in this APK (a whitelist pack such as monochrome can leave a group empty).
    private static int totalRows = -1;
    private static int[] groupFlat = null;
    private String[] summaries = null;
    private final float tagW, tagWEffect, setW;
    private boolean fontApplied = false;

    public PickerView(Context c, AttributeSet a) {
        super(c, a);
        d = c.getResources().getDisplayMetrics().density;
        legend = new Legend(d);
        bg.setColor({picker_bg});
        edge.setColor(0x66F2B85C); edge.setStyle(Paint.Style.STROKE); edge.setStrokeWidth(d);
        sel.setColor(ACCENT);
        // 9sp / 13sp / 10sp — the sizes signed off against the preview. These were once bumped
        // to 11/15/12 and every visual defect since (text under the tag, text escaping the
        // selection bar, misaligned tag) traced back to that bump. Keep them here; get extra
        // legibility from the layout, not from a larger font.
        head.setColor({picker_dim}); head.setTextSize(9 * d); head.setFakeBoldText(true);
        item.setColor({picker_ink}); item.setTextSize(13 * d);
        small.setColor({picker_dim}); small.setTextSize(10 * d);
        rule.setColor({picker_rule});
        track.setColor(0x260F1B26); thumb.setColor(0xCCF2B85C);
        // Three strings, measured once: onDraw used to call measureText twice per visible
        // row per frame. The 52d floor keeps a short "CS"/"PE" reading as a deliberate chip.
        tagW = Math.max(head.measureText(Recipes.ZH ? "风格" : "CS") + 16 * d, 52 * d);
        tagWEffect = Math.max(head.measureText(Recipes.ZH ? "效果" : "PE") + 16 * d, 52 * d);
        setW = Math.max(head.measureText(Recipes.ZH ? "设置" : "SET") + 16 * d, 52 * d);
    }

    /** MainActivity calls setSelected(recipe, browserCol); the column argument is ignored now. */
    public void setSelected(int i, int col) { selected = i; invalidate(); }

    /** Flat row index of brand g's header, building the table on first use. */
    private static int[] groupFlat() {
        if (groupFlat != null) return groupFlat;
        int ng = Recipes.GROUPS.length;
        int[] flat = new int[ng + 1];
        int t = 0;
        for (int g = 0; g < ng; g++) {
            flat[g] = Recipes.GROUP_COUNT[g] > 0 ? t : -1;
            if (Recipes.GROUP_COUNT[g] > 0) t += 1 + Recipes.GROUP_COUNT[g];
        }
        flat[ng] = t;
        groupFlat = flat;
        totalRows = t;
        return flat;
    }

    @Override
    protected void onDraw(Canvas c) {
        if (FONT != null && !fontApplied) {
            head.setTypeface(FONT); item.setTypeface(FONT); small.setTypeface(FONT);
            fontApplied = true;
        }
        float w = getWidth(), h = getHeight(), pad = 12 * d;
        c.drawRect(0, 0, w, h, bg);

        // top reserves the header band: the divider sits at top-5d and the list starts at
        // top. pad+16d left the divider almost touching the "RECIPES · N" descriptors (the
        // baseline is at pad+7d), so raise the reserve to give the header real breathing room.
        float top = pad + 20 * d, bottom = h - pad - 24 * d;     // header / footer reserved
        float listTop = top, listH = bottom - listTop;
        float rowH = 30 * d;
        float x = pad, xr = w - pad;

        // One visual row per brand header plus per recipe, all concatenated. Total lets us
        // window the list around the selected recipe the same way the scrollbar is drawn.
        int ng = Recipes.GROUPS.length;
        int[] flat0 = groupFlat();
        int total = totalRows;
        int visible = Math.max(1, (int) (listH / rowH));

        // Flat index of the selected recipe (every header before it counts as a row too).
        int gsel = Recipes.ALL[selected].group;
        int flat = flat0[gsel] + 1 + (selected - Recipes.GROUP_START[gsel]);
        int first = Math.max(0, Math.min(flat - visible / 2, total - visible));
        if (summaries == null) summaries = new String[Recipes.ALL.length];

        // top header
        head.setColor({picker_ink});
        c.drawText((Recipes.ZH ? "配方  ·  " : "RECIPES  ·  ") + Recipes.ALL.length, pad, pad + 7 * d, head);
        c.drawLine(pad, top - 5 * d, w - pad, top - 5 * d, rule);

        // list
        // Anchor row `first` at the top of the viewport, so the window scrolls with the
        // selection. The naive version (y = listTop + drawFlat*rowH) draws every row at its
        // absolute offset, which pushes the selected recipe far below `bottom` the moment
        // you scroll past the first screenful — the panel renders blank.
        float y = listTop - first * rowH;
        int drawFlat = 0;
        for (int gg = 0; gg < ng; gg++) {
            int start = Recipes.GROUP_START[gg], count = Recipes.GROUP_COUNT[gg];
            if (count == 0) continue;                       // this APK carries none of them
            boolean headerVisible = drawFlat >= first && y < bottom;
            if (headerVisible) {
                // v0.89: a full-width divider marks where a new brand starts, so scrolling
                // past a boundary is visible instead of something you have to read. It is
                // skipped only when the header is the first thing in the viewport, where a
                // line with nothing above it reads as a stray artefact.
                if (y > listTop + d) c.drawLine(pad, y + d, w - pad, y + d, rule);
                // v0.91: the brand name is as big as the recipe names below it (item 13sp,
                // not head 9sp), and the count moved to the far right of the row — it is
                // metadata (how many are in this group), not a label.
                item.setColor({picker_ink});
                item.setFakeBoldText(true);
                c.drawText(Recipes.GROUPS[gg].toUpperCase(), x, y + 17 * d, item);
                item.setFakeBoldText(false);
                small.setColor({picker_dim});
                String cnt = String.valueOf(count);
                c.drawText(cnt, xr - small.measureText(cnt), y + 17 * d, small);
            }
            drawFlat++; y += rowH;
            for (int k = 0; k < count; k++, drawFlat++) {
                if (drawFlat >= first && y < bottom) {
                    int idx = start + k; Recipes.Recipe rc = Recipes.ALL[idx];
                    boolean on = idx == selected;
                    if (on) {
                        // Top edge keeps a fixed ~2.75d strip above the name glyphs. The glyph
                        // top moves with the font (13d here, 15d during the +2 bump), so this
                        // must be re-tuned whenever setTextSize changes.
                        r.set(x - 6 * d, y + d / 2, xr + 6 * d, y + rowH - 2 * d);
                        c.drawRoundRect(r, 4 * d, 4 * d, sel);
                    }
                    // The tag lives in a fixed column on the right. Reserve that column and
                    // clip the recipe name + sub-text to it, so a long name (the +2 font made
                    // this visible) cannot run under the tag. The tag is centred between the
                    // name line (baseline y+13d) and the sub-text line (baseline y+24d).
                    String tag = Recipes.ZH ? (rc.isEffect() ? "效果" : "风格") : (rc.isEffect() ? "PE" : "CS");
                    float tw = rc.isEffect() ? tagWEffect : tagW, tx = xr - tw;
                    // v0.88 — the settings affordance, drawn on the SELECTED row only and
                    // sitting immediately left of the tag pill. ENTER / RIGHT open the
                    // bottom-bar editor for this row (MainActivity.openEditor). Measured
                    // before the clip so a long recipe name stops before the chip instead
                    // of running underneath it.
                    String set = Recipes.ZH ? "设置" : "SET";
                    float sw = on ? setW : 0f;
                    float sx = tx - 8 * d - sw;
                    c.save();
                    c.clipRect(x - 4 * d, y, on ? sx - 6 * d : tx - 6 * d, y + rowH);
                    item.setColor(on ? {picker_accent_ink} : {picker_ink});
                    item.setFakeBoldText(on);
                    c.drawText(rc.name, x, y + 13 * d, item);
                    String sum = summaries[idx];
                    if (sum == null) { sum = rc.summary(); summaries[idx] = sum; }
                    small.setColor(on ? {picker_accent_ink} : {picker_dim});
                    c.drawText(sum, x, y + 24 * d, small);
                    c.restore();
                    item.setFakeBoldText(false);

                    if (on) {
                        r.set(sx, y + 12 * d, sx + sw, y + 24 * d);
                        tagBg.setColor(0x40FFFFFF);
                        c.drawRoundRect(r, 2 * d, 2 * d, tagBg);
                        head.setColor({picker_accent_ink});
                        c.drawText(set, sx + 8 * d, y + 21 * d, head);
                    }

                    r.set(tx, y + 12 * d, tx + tw, y + 24 * d);
                    tagBg.setColor(on ? 0x331A1208
                                     : (rc.isEffect() ? 0x55B8741A : {picker_rule}));
                    c.drawRoundRect(r, 2 * d, 2 * d, tagBg);
                    head.setColor(on ? {picker_accent_ink} : {picker_dim});
                    c.drawText(tag, tx + 4 * d, y + 21 * d, head);
                }
                y += rowH;
                if (y > bottom && drawFlat >= first + visible) break;
            }
            if (y > bottom && drawFlat >= first + visible) break;
        }

        // scrollbar
        if (total > visible) {
            float sbW = 4 * d, sx = w - pad - sbW;
            r.set(sx, listTop, sx + sbW, listTop + listH);
            c.drawRoundRect(r, sbW / 2, sbW / 2, track);
            float thumbH = Math.max(12 * d, listH * visible / total);
            float thumbY = listTop + (listH - thumbH) * first / Math.max(1, total - visible);
            r.set(sx, thumbY, sx + sbW, thumbY + thumbH);
            c.drawRoundRect(r, sbW / 2, sbW / 2, thumb);
        }

        // footer: key legend
        c.drawLine(pad, h - pad - 20 * d, w - pad, h - pad - 20 * d, rule);
        legend.draw(c, pad, h - pad - 10 * d, w - 2 * pad, ICONS, TEXT);
    }
}
