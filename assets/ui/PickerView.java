package {ui_package};

import android.content.Context;
import android.graphics.Canvas;
import android.graphics.Paint;
import android.graphics.RectF;
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
 * So the picker is now one scrollable column: a dim category header per group, then that
 * group's recipes, all concatenated, with the whole list wrapped around the current recipe.
 * UP/DOWN (MainActivity.browserKey) calls nextRecipe(±1) across ALL recipes, so the column
 * scrolls end to end; ENTER picks, FN closes. Colours come from catalog/ui-theme.json via
 * tools/patch_ui.py, so this one file is the only place the browser's colours live.
 */
public class PickerView extends View {
    private static final int ACCENT = {picker_accent};

    private final Paint bg = new Paint(Paint.ANTI_ALIAS_FLAG), edge = new Paint(Paint.ANTI_ALIAS_FLAG), sel = new Paint(Paint.ANTI_ALIAS_FLAG),
            head = new Paint(Paint.ANTI_ALIAS_FLAG), item = new Paint(Paint.ANTI_ALIAS_FLAG), small = new Paint(Paint.ANTI_ALIAS_FLAG), rule = new Paint(),
            track = new Paint(Paint.ANTI_ALIAS_FLAG), thumb = new Paint(Paint.ANTI_ALIAS_FLAG), tagBg = new Paint(Paint.ANTI_ALIAS_FLAG);
    private final RectF r = new RectF();
    private final float d;
    private final Legend legend;
    private static final int[] ICONS = { Legend.UPDOWN, Legend.ENTER, Legend.FN };
    private static final String[] TEXT = { "move", "pick", "close" };
    private int selected = 0;

    public PickerView(Context c, AttributeSet a) {
        super(c, a);
        d = c.getResources().getDisplayMetrics().density;
        legend = new Legend(d);
        bg.setColor({picker_bg});
        edge.setColor(0x66F2B85C); edge.setStyle(Paint.Style.STROKE); edge.setStrokeWidth(d);
        sel.setColor(ACCENT);
        head.setColor({picker_dim}); head.setTextSize(11 * d); head.setFakeBoldText(true);
        item.setColor({picker_ink}); item.setTextSize(15 * d);
        small.setColor({picker_dim}); small.setTextSize(12 * d);
        rule.setColor({picker_rule});
        track.setColor(0x260F1B26); thumb.setColor(0xCCF2B85C);
    }

    /** MainActivity calls setSelected(recipe, browserCol); the column argument is ignored now. */
    public void setSelected(int i, int col) { selected = i; invalidate(); }

    @Override
    protected void onDraw(Canvas c) {
        float w = getWidth(), h = getHeight(), pad = 12 * d;
        c.drawRect(0, 0, w, h, bg);

        // top reserves the header band: the divider sits at top-5d and the list starts at
        // top. pad+16d left the divider almost touching the "RECIPES · N" descriptors (the
        // baseline is at pad+7d), so raise the reserve to give the header real breathing room.
        float top = pad + 20 * d, bottom = h - pad - 24 * d;     // header / footer reserved
        float listTop = top, listH = bottom - listTop;
        float rowH = 30 * d;
        float x = pad, xr = w - pad;

        // One visual row per group header plus per recipe, all concatenated. Total lets us
        // window the list around the selected recipe the same way the scrollbar is drawn.
        int ng = Recipes.GROUPS.length;
        int total = 0;
        for (int g = 0; g < ng; g++) total += 1 + Recipes.GROUP_COUNT[g];
        int visible = Math.max(1, (int) (listH / rowH));

        // Flat index of the selected recipe (every header before it counts as a row too).
        int gsel = Recipes.ALL[selected].group;
        int flat = 0;
        for (int gg = 0; gg < gsel; gg++) flat += 1 + Recipes.GROUP_COUNT[gg];
        flat += 1 + (selected - Recipes.GROUP_START[gsel]);
        int first = Math.max(0, Math.min(flat - visible / 2, total - visible));

        // top header
        head.setColor({picker_ink});
        c.drawText("RECIPES  ·  " + Recipes.ALL.length, pad, pad + 7 * d, head);
        c.drawLine(pad, top - 5 * d, w - pad, top - 5 * d, rule);

        // list
        // Anchor row `first` at the top of the viewport, so the window scrolls with the
        // selection. The naive version (y = listTop + drawFlat*rowH) draws every row at its
        // absolute offset, which pushes the selected recipe far below `bottom` the moment
        // you scroll past the first screenful — the panel renders blank.
        float y = listTop - first * rowH;
        int drawFlat = 0;
        for (int gg = 0; gg < ng; gg++) {
            if (drawFlat >= first && y < bottom) {
                head.setColor({picker_dim});
                c.drawText(Recipes.GROUPS[gg].toUpperCase() + "  ·  " + Recipes.GROUP_COUNT[gg],
                           x, y + 11 * d, head);
            }
            drawFlat++; y += rowH;
            int start = Recipes.GROUP_START[gg], count = Recipes.GROUP_COUNT[gg];
            for (int k = 0; k < count; k++, drawFlat++) {
                if (drawFlat >= first && y < bottom) {
                    int idx = start + k; Recipes.Recipe rc = Recipes.ALL[idx];
                    boolean on = idx == selected;
                    if (on) {
                        // The bar must reach the sub-text descenders (~y+27d) without sheeting
                        // empty gold above the name: the name's glyph top sits at ~y+2d, so a
                        // top edge of y-1d leaves a snug strip and nothing more.
                        r.set(x - 6 * d, y - 1 * d, xr + 6 * d, y + rowH - 2 * d);
                        c.drawRoundRect(r, 4 * d, 4 * d, sel);
                    }
                    // The tag lives in a fixed column on the right. Reserve that column and
                    // clip the recipe name + sub-text to it, so a long name (the +2 font made
                    // this visible) cannot run under the tag. The tag is centred between the
                    // name line (baseline y+13d) and the sub-text line (baseline y+24d).
                    String tag = rc.isEffect() ? "PE" : "CS";
                    // Wider pill: generous padding around the 2-char label, with a floor so a
                    // short "PE"/"CS" still reads as a deliberate chip rather than a tight box.
                    float tw = Math.max(head.measureText(tag) + 16 * d, 52 * d), tx = xr - tw;
                    c.save();
                    c.clipRect(x - 4 * d, y, tx - 6 * d, y + rowH);
                    item.setColor(on ? {picker_accent_ink} : {picker_ink});
                    item.setFakeBoldText(on);
                    c.drawText(rc.name, x, y + 13 * d, item);
                    small.setColor(on ? {picker_accent_ink} : {picker_dim});
                    c.drawText(rc.summary(), x, y + 24 * d, small);
                    c.restore();
                    item.setFakeBoldText(false);

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
