package {ui_package};

import android.content.Context;
import android.graphics.Canvas;
import android.graphics.Paint;
import android.graphics.RectF;
import android.graphics.Typeface;
import android.util.AttributeSet;
import android.view.View;

/**
 * The settings editor: one row per adjustable parameter, label on the LEFT and its current
 * value on the RIGHT, in a single scrolling column.
 *
 * Why this exists. The editor used to be the main screen's chip strip with the top bar
 * hidden. That strip is horizontal, so on a camera screen it showed two or three chips at a
 * time and everything else was off-screen behind a sideways scroll — which reads as "the
 * settings got smaller", even when nothing was removed. A column shows eight or nine rows at
 * once, and a row that says "反差        +2" is self-explanatory in a way a chip that stacks
 * "CON" over "+2" is not.
 *
 * Nothing is hidden here. The old rowVisible() dropped STYLE / SAT / CON / SHARP / MATRIX /
 * STRENGTH whenever the look used a Picture Effect — the GR high-contrast B&W recipes are
 * all pe=7, so opening the editor on one of them left seven rows and no strength percentage,
 * which is exactly the "百分比没了、能调的变少了" report. Those parameters really are
 * overridden by a Picture Effect on the body, so they are still not editable: they are listed
 * greyed out with a note saying why, rather than silently missing. A control that vanishes
 * looks like a bug; a control that is visibly disabled reads as information.
 *
 * Rows are pushed in by MainActivity.syncEditor() — this view holds no camera state of its
 * own, it only draws what it is handed. Colours come from catalog/ui-theme.json via
 * tools/patch_ui.py, so they live in exactly one place, like the rest of the UI.
 */
public class EditorView extends View {
    private static final int ACCENT = {editor_accent};

    /** Set by MainActivity.applyFont(); applied to the Paints below on the first draw. */
    public static Typeface FONT;

    private final Paint bg = new Paint(Paint.ANTI_ALIAS_FLAG), sel = new Paint(Paint.ANTI_ALIAS_FLAG),
            edge = new Paint(Paint.ANTI_ALIAS_FLAG), item = new Paint(Paint.ANTI_ALIAS_FLAG),
            small = new Paint(Paint.ANTI_ALIAS_FLAG), note = new Paint(Paint.ANTI_ALIAS_FLAG),
            rule = new Paint(), track = new Paint(Paint.ANTI_ALIAS_FLAG), thumb = new Paint(Paint.ANTI_ALIAS_FLAG);
    private final RectF r = new RectF();
    private final float d;
    private final Legend legend;

    // UP/DOWN walk the rows, LEFT/RIGHT dial the value — a vertical list is navigated with
    // its own axis (v0.92 hardware feedback: the v0.91 mapping read backwards). The wheel
    // and the dial are dials: MainActivity routes them to stepValue in this state.
    private static final int[] ICONS = { Legend.UPDOWN, Legend.LEFTRIGHT, Legend.ENTER, Legend.MENU };
    private static final String[] TEXT = { "param", "value", "done", "done" };
    private static final String[] TEXT_ZH = { "切换", "数值", "完成", "完成" };
    static { if (Recipes.ZH) System.arraycopy(TEXT_ZH, 0, TEXT, 0, TEXT_ZH.length); }

    private String[] names = new String[0], values = new String[0];
    private boolean[] off = null;
    private int selRow = 0;
    private boolean focused = false;
    private String title = "";
    private int lastCount = -1;
    private boolean fontApplied = false;

    public EditorView(Context c, AttributeSet a) {
        super(c, a);
        d = c.getResources().getDisplayMetrics().density;
        legend = new Legend(d);
        bg.setColor({editor_bg});
        sel.setColor(ACCENT);
        edge.setColor({editor_accent}); edge.setStyle(Paint.Style.STROKE); edge.setStrokeWidth(d);
        item.setColor({editor_ink}); item.setTextSize(13 * d);
        small.setColor({editor_dim}); small.setTextSize(11 * d);
        note.setColor({editor_dim}); note.setTextSize(9 * d);
        rule.setColor({editor_rule});
        track.setColor(0x260F1B26); thumb.setColor(0xCCF2B85C);
    }

    /** MainActivity hands over the whole editor state at once; the view keeps no logic. */
    public void setRows(String title, String[] names, String[] values, boolean[] off,
                        int selRow, boolean focused) {
        this.title = title;
        this.names = names;
        this.values = values;
        this.off = off;
        this.selRow = selRow;
        this.focused = focused;
        if (names.length != lastCount) { lastCount = names.length; requestLayout(); }
        else invalidate();
    }

    private static final float ROW_H = 26f;      // one row: label + value on one line
    private static final float HEAD_H = 26f;     // recipe name, so you know what you are editing
    private static final float FOOT_H = 24f;     // key legend

    /** As tall as the rows need, never more than 62% of the screen: the frame stays visible. */
    @Override
    protected void onMeasure(int w, int h) {
        int n = names.length;
        float want = (12 + 12) * d + HEAD_H * d + FOOT_H * d + n * ROW_H * d;
        int max = (int) (getResources().getDisplayMetrics().heightPixels * 0.62f);
        setMeasuredDimension(MeasureSpec.getSize(w), Math.min((int) want, max));
    }

    @Override
    protected void onDraw(Canvas c) {
        if (FONT != null && !fontApplied) {
            item.setTypeface(FONT); small.setTypeface(FONT); note.setTypeface(FONT);
            fontApplied = true;
        }
        float w = getWidth(), h = getHeight(), pad = 12 * d;
        c.drawRect(0, 0, w, h, bg);

        int n = names.length;
        float listTop = pad + HEAD_H * d;
        float listBottom = h - pad - FOOT_H * d;
        float listH = Math.max(ROW_H * d, listBottom - listTop);
        float x = pad + 6 * d, xr = w - pad - 6 * d;

        // header: which look these settings belong to
        small.setColor({editor_ink});
        small.setFakeBoldText(true);
        c.drawText(title, pad, pad + 13 * d, small);
        small.setFakeBoldText(false);
        c.drawLine(pad, listTop - 4 * d, w - pad, listTop - 4 * d, rule);

        int visible = Math.max(1, (int) (listH / (ROW_H * d)));
        int first = Math.max(0, Math.min(selRow - visible / 2, Math.max(0, n - visible)));

        // v0.92: the rows live inside [listTop, listBottom] and nowhere else. Without this
        // clip a half-scrolled row painted straight over the header title (the "选中的菜单和
        // 左上角的名字重合" report) — the loop's bounds check only skips rows that are FULLY
        // outside, so a straddling row drew across the header's baseline. Clipping also
        // keeps the selection capsule out of the legend below.
        c.save();
        c.clipRect(0, listTop, w, listBottom);

        float y = listTop - first * ROW_H * d;
        for (int i = 0; i < n; i++, y += ROW_H * d) {
            if (y + ROW_H * d < listTop || y > listBottom) continue;
            boolean on = i == selRow;
            boolean disabled = off != null && off[i];
            if (on) {
                r.set(pad, y + d, w - pad, y + ROW_H * d - d);
                c.drawRoundRect(r, 4 * d, 4 * d, sel);
                if (focused) c.drawRoundRect(r, 4 * d, 4 * d, edge);
            }
            // label on the left, value on the right, both clipped to their own half so a
            // long value can never push the label off the row (or vice versa). The value
            // draws RIGHT-aligned ending at xr — v0.91 drew it left-aligned FROM xr, which
            // put every glyph outside the value clip and off the panel edge: the "右侧什
            // 么都没有写" report.
            float mid = x + (xr - x) * 0.62f;
            c.save();
            c.clipRect(x, y, mid, y + ROW_H * d);
            item.setColor(disabled ? {editor_dim} : on ? {editor_accent_ink} : {editor_ink});
            item.setFakeBoldText(on);
            c.drawText(names[i], x, y + 17 * d, item);
            item.setFakeBoldText(false);
            c.restore();

            c.save();
            c.clipRect(mid, y, xr, y + ROW_H * d);
            item.setColor(disabled ? {editor_dim} : on ? {editor_accent_ink} : {editor_ink});
            item.setTextAlign(Paint.Align.RIGHT);
            c.drawText(values[i], xr, y + 17 * d, item);
            // A Picture Effect overrides the Creative Style parameters on the body, so they
            // are listed (they exist) but visibly not in play — the value stays readable,
            // with the why right under it.
            if (disabled) {
                note.setTextAlign(Paint.Align.RIGHT);
                c.drawText(Recipes.ZH ? "（不能改动）" : "(read-only)", xr, y + 24 * d, note);
                note.setTextAlign(Paint.Align.LEFT);
            }
            item.setTextAlign(Paint.Align.LEFT);
            c.restore();
        }
        c.restore();

        if (n > visible) {
            float sbW = 4 * d, sx = w - pad - sbW;
            r.set(sx, listTop, sx + sbW, listTop + listH);
            c.drawRoundRect(r, sbW / 2, sbW / 2, track);
            float thumbH = Math.max(12 * d, listH * visible / n);
            float thumbY = listTop + (listH - thumbH) * first / Math.max(1, n - visible);
            r.set(sx, thumbY, sx + sbW, thumbY + thumbH);
            c.drawRoundRect(r, sbW / 2, sbW / 2, thumb);
        }

        c.drawLine(pad, h - pad - FOOT_H * d + 4 * d, w - pad, h - pad - FOOT_H * d + 4 * d, rule);
        legend.draw(c, pad, h - pad - 8 * d, w - 2 * pad, ICONS, TEXT);
    }
}
