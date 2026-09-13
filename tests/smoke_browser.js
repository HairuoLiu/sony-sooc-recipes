#!/usr/bin/env node
/**
 * Smoke-test the filter browser without a browser.
 *
 * index.html is a single file with an inline script that builds the whole UI. A typo in
 * it would ship a blank page and no test would notice, so this extracts the script, runs
 * it against a minimal DOM stub, and asserts that the render actually produced cards.
 *
 *   node tests/smoke_browser.js
 */
"use strict";

const fs = require("fs");
const path = require("path");

const ROOT = path.resolve(__dirname, "..");
const html = fs.readFileSync(path.join(ROOT, "catalog", "index.html"), "utf8");
const catalog = JSON.parse(fs.readFileSync(path.join(ROOT, "catalog", "filters.json"), "utf8"));

// --- extract the inline script ------------------------------------------------------
const scripts = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map((m) => m[1]);
if (scripts.length !== 1) {
  console.error(`FAIL  expected exactly 1 inline <script>, found ${scripts.length}`);
  process.exit(1);
}
const code = scripts[0];

if (!/const DATA = \{/.test(code)) {
  console.error("FAIL  the catalog was not embedded into the script");
  process.exit(1);
}

// --- minimal DOM --------------------------------------------------------------------
const nodes = new Map();
function makeEl(id) {
  return {
    id,
    innerHTML: "",
    textContent: "",
    value: "",
    listeners: {},
    addEventListener(type, fn) { (this.listeners[type] ||= []).push(fn); },
    setAttribute(k, v) { (this.attrs ||= {})[k] = v; },
    getAttribute(k) { return (this.attrs || {})[k] ?? null; },
    insertAdjacentHTML(_pos, h) { this.innerHTML += h; },
    dispatch(type, ev) { for (const fn of this.listeners[type] || []) fn(ev); },
  };
}
global.document = {
  getElementById(id) {
    if (!nodes.has(id)) nodes.set(id, makeEl(id));
    return nodes.get(id);
  },
};

const failures = [];
const check = (ok, msg) => { if (!ok) failures.push(msg); };

// --- run ----------------------------------------------------------------------------
try {
  new Function(code)();
} catch (err) {
  console.error("FAIL  the inline script threw while rendering:");
  console.error("      " + err.message);
  process.exit(1);
}

const out = global.document.getElementById("out");
const stats = global.document.getElementById("stats");
const count = global.document.getElementById("count");
const groupSel = global.document.getElementById("group");

// --- assertions ---------------------------------------------------------------------
const cards = (out.innerHTML.match(/<article class="card">/g) || []).length;
check(cards === catalog.filters.length,
  `rendered ${cards} cards, catalog has ${catalog.filters.length}`);

check(/class="stat"/.test(stats.innerHTML), "stats block was not rendered");
check(/\d+ \/ \d+ 款/.test(count.textContent), `counter shows "${count.textContent}"`);

const compiled = catalog.filters.filter((f) => f.engine === "recipe-lab").length;
check(stats.innerHTML.includes(`>${catalog.filters.length}<`),
  `stats does not show the total ${catalog.filters.length}`);
check(stats.innerHTML.includes(`>${compiled}<`),
  `stats does not show the compiled count ${compiled}`);

// every declared group that has filters must get a heading
const groupsWithFilters = new Set(catalog.filters.map((f) => f.group));
for (const g of catalog.groups) {
  if (!groupsWithFilters.has(g.id)) continue;
  if (!out.innerHTML.includes(`>${g.label} <`)) {
    failures.push(`group heading missing for ${g.label}`);
  }
}

// the group <select> must offer every group that has filters
for (const g of catalog.groups) {
  if (!groupsWithFilters.has(g.id)) continue;
  if (!groupSel.innerHTML.includes(`value="${g.id}"`)) {
    failures.push(`group filter option missing for ${g.id}`);
  }
}

// the search box must actually filter
const app = {
  q: global.document.getElementById("q"),
  mono: global.document.getElementById("f-mono"),
};
app.q.dispatch("input", { target: { value: "portra" } });
const filtered = (out.innerHTML.match(/<article class="card">/g) || []).length;
const expected = catalog.filters.filter((f) =>
  (f.name + " " + (f.name_zh || "") + " " + f.id).toLowerCase().includes("portra")).length;
check(filtered === expected, `search "portra" gave ${filtered} cards, expected ${expected}`);
check(filtered > 0 && filtered < catalog.filters.length, "search did not narrow the list");

// mono-only toggle
app.q.dispatch("input", { target: { value: "" } });
app.mono.dispatch("click", { currentTarget: makeEl("f-mono") });
const monoOnly = (out.innerHTML.match(/<article class="card">/g) || []).length;
const monoCount = catalog.filters.filter((f) => f.tone === "mono").length;
check(monoOnly === monoCount, `mono toggle gave ${monoOnly} cards, expected ${monoCount}`);

// --- report -------------------------------------------------------------------------
if (failures.length) {
  console.error(`FAIL  ${failures.length} assertion(s):`);
  for (const f of failures) console.error("      " + f);
  process.exit(1);
}
console.log(`OK    ${cards} cards rendered, search + toggles behave, stats consistent`);
