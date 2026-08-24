# Dapur Run — handover

Everything another person (or another Claude session) needs to change this app safely.

---

## 1. What it is

A grocery checklist that lives in **one HTML file**. No build step, no framework, no
dependencies at runtime. Photos, fonts and code are all embedded, so the page works with no
internet connection.

Three screens inside the one page:

| Screen | Purpose |
| --- | --- |
| **Checklist** | 163 catalogue items in 15 categories. Tick, set quantity, stock and an estimated price. |
| **Shopping List** | Only the ticked items, grouped by category. Printable / exportable. |
| **What I Bought** | Tick things off as you buy them, enter what you paid, compare to the estimate. |

---

## 2. Where everything lives

| Thing | Location |
| --- | --- |
| **Live site** | <https://skhairulnisa.github.io/dapur-run/> (GitHub Pages, **public**) |
| **Repo** | `github.com/skhairulnisa/dapur-run` — personal account |
| **Working copy** | `/Users/nisa/Downloads/dapur-run/` ← *edit here* |
| **The app** | `index.html` in that folder (~2.1 MB) |
| **Tests** | `tests/` in that folder |
| **Loose copy** | `/Users/nisa/Downloads/grocery-checklist.html` — the same file, for opening directly |

`index.html` and `grocery-checklist.html` should stay identical. The live site serves
`index.html` straight from `main`.

> The old `claude.ai/code/artifact/...` link is **stale** — it was published under a different
> signed-in account and can no longer be updated. Use the GitHub Pages URL.

---

## 3. Changing it with Claude (or any assistant)

Open a session **in the working copy**:

```bash
cd /Users/nisa/Downloads/dapur-run
claude
```

Then say what you want, and point at this file. A prompt that works:

> Read HANDOVER.md first. This is a single-file grocery checklist app in `index.html` —
> no build step, edit that file directly. I want to <describe the change>.
> Run `cd tests && node test.js` when you're done and tell me the result.

**If you are that assistant, the rules are:**

1. **Edit `index.html` directly.** There is no source file it is generated from any more.
   The original build scripts were lost; `index.html` *is* the source.
2. **Never reformat or rewrite the whole file.** It contains ~164 base64 images and 4 base64
   fonts. Use targeted string replacement (Edit tool, `sed`, or a small Python `str.replace`
   with an assertion that the target was found).
3. **Run the tests** (§6) before saying you are finished.
4. **Deploy** with §7 if the change should go live, and keep the loose copy in sync.

To work from the repo instead of the laptop, clone it:
`git clone https://github.com/skhairulnisa/dapur-run.git`

---

## 4. How the file is laid out

One `<style>` block, then the markup, then a **single `<script>`** holding all the logic in an
IIFE. Both are marked with comment banners — search for them to navigate:

```
CSS      /* ---------- tokens ---------- */          design tokens, light + dark
         /* ---------- category ---------- */         category header + grid
         /* ---------- item ---------- */              the item card
         /* ---------- shopping list view ---------- */ list + bought tables
         /* ---------- print ---------- */             @media print — the whole print design

JS       /* ---------- storage ---------- */          hydrate / load / save / saveNow
         /* ---------- painting the checklist ---------- */ paintItem / paintCat / paintTally
         /* ---------- selection ---------- */         setSel / toggle / wipe
         /* ---------- items you add yourself ---------- */ buildCard / registerItem / removeItem
         /* ---------- replacing an item photo ---------- */ the photo popover
         /* ---------- moving your list between devices ---------- */ Backup / Restore
         /* ---------- search ---------- */
         /* ---------- shopping list ---------- */     buildList / buildBought / makePdf
         /* ---------- boot ---------- */              runs everything on load
```

### The data

| Constant | What it holds |
| --- | --- |
| `CATS` | The 163 catalogue items: `[{key, name, items:[{id, name}]}]`. Category order = display order. |
| `SEED` | 85 starting prices: `{itemId: {p: 4.99, t: "LOTUSS TOMATO 600G"}}`. `t` is shown under the box so a price can be checked. |
| `ORIG` | Each item's shipped photo (a data URL), captured at boot so a replaced photo can be restored. |
| `BYID` / `CATOF` / `MINE` | Lookups: item id → name, → category key, → "the user added this one". |

Item photos are **not** in `CATS` — they are `src` attributes on the `<img class="thumb">`
inside each card's markup.

---

## 5. Where to change what

| I want to… | Do this |
| --- | --- |
| **Change an item's photo** | Find its card by item id in the markup, replace the `src="data:image/jpeg;base64,…"` value. Keep it a small square JPEG. |
| **Rename an item** | Change it in **three** places for that id: the `CATS` entry, the card's `<span class="nm">`, and the card's `aria-label`s. |
| **Add a catalogue item** | Add to `CATS` **and** add a matching card in that category's `<div class="grid" id="grid-KEY">`. Easier: use the app's own "Add your own item" box, which needs no code. |
| **Change a starting price** | Edit the entry in `SEED`. Only affects people who have not used the app before — existing users keep their own `est` values. |
| **Change a category colour** | Edit the `.c-KEY{--cat:…}` rules (there are three sets: light, `prefers-color-scheme: dark`, and `[data-theme="dark"]`). Change all three. |
| **Change the print layout** | The `@media print` block only. |
| **Change the PDF** | `makePdf()` — it writes PDF bytes by hand. Coordinates are in points, origin bottom-left. |
| **Add a state field** | Add it to the `S` literal **and** to the `fresh` literal inside `hydrate()`, **and** to the key list `hydrate()` copies. Missing the `fresh` literal is a real bug that has happened — it breaks the app for anyone with a saved list. |

---

## 6. Testing

```bash
cd /Users/nisa/Downloads/dapur-run/tests
npm i jsdom          # first time only
node test.js         # 54 assertions, ~10s
```

The suite covers clearing behaviour, adding/removing your own items, backup→restore across a
clean browser, and that nothing external is loaded. It reads `../index.html`, so it always tests
the real file.

Deeper checks (each needs Google Chrome, and `python3 -m pip install --user pypdf pypdfium2`):

| Script | Checks |
| --- | --- |
| `python3 btest.py` | Real-browser clicks: photo/name/row ticking, adding an item, PDF builds |
| `python3 esttest.py` | Estimated-spend maths and estimate-vs-actual |
| `python3 backuptest.py` | Backup on one browser, restore into a clean one |
| `python3 phone.py` | Renders the page at 375 px and checks for horizontal overflow |

---

## 7. Deploying

```bash
cd /Users/nisa/Downloads/dapur-run
cp index.html /Users/nisa/Downloads/grocery-checklist.html   # keep the loose copy in sync
git add -A && git commit -m "…" && git push
```

GitHub Pages rebuilds in under a minute. Confirm it actually went out:

```bash
gh api repos/skhairulnisa/dapur-run/pages/builds/latest --jq .status   # -> "built"
curl -s https://skhairulnisa.github.io/dapur-run/ | wc -c              # should match index.html
```

---

## 8. Rules that must not break

- **Self-contained.** No `<script src>`, no `<link>` to a CDN, no remote images. Everything is a
  data URI. `tests/test.js` fails if any `http(s)://` reference appears.
- **The 163 catalogue items** keep their exact names, spelling, categories and order.
  No standalone "Snacks" or "Drinks" category. No chocolate spread / Nutella.
- **Every item keeps a real photograph**, and no two catalogue items share one.
- **Print stays readable**: black on white, table headings repeat on every page, no clipped rows.
- **Storage is defensive.** Reads are wrapped in try/catch; a corrupt or missing value must fall
  back to an empty list rather than throw.

---

## 8b. Sharp edges (verified against the code)

These are the things that will actually bite you.

- **A catalogue item lives in TWO places.** Its `CATS` entry *and* its `<div class="item">` card in
  the markup. Adding to `CATS` alone crashes the page on load, because the boot code looks up a
  card that is not there. The safe way to add an item is the app's own "Add your own item" box.
- **Never change an item `id`.** It is the key for eight saved maps (`sel`, `qty`, `stk`, `done`,
  `photos`, `price`, `est`, `auto`) plus `SEED`. Changing it orphans every saved tick and price.
  Renaming the *display name* is safe.
- **Renaming touches ~7 spots** in one card: `.nm` text, `img.thumb[alt]`, and the `aria-label` on
  the checkbox, the photo button, the qty input and the stock input — plus the `CATS` entry.
- **"163 items" is hard-coded in three places**: the search placeholder, the `#hint` line, and the
  empty-query branch of `runSearch()`. Plus each category's `.btot` count. None are computed.
- **`#listbody` and `#boughtbody` are rebuilt with `innerHTML`** every time. Never hold a reference
  to a row or attach a listener to one — all row handling is delegated on the container.
- **Dark-mode values exist twice.** Once under `@media (prefers-color-scheme: dark)` and once under
  `:root[data-theme="dark"]`, and that includes all 15 category colour triplets. Change both.
- **`buildCard()` must mirror the shipped card markup.** It builds the card for user-added items.
  If you change the card's structure in the HTML, change `buildCard()` to match or user items will
  drift out of shape.
- **The `<form class="additem">` must stay the last child of its grid.** New cards are inserted
  before it (`grid.insertBefore(node, $(".additem", grid))`).
- **The PDF is independent of the print CSS.** `makePdf()` writes PDF operators with its own A4
  geometry. Changing `@media print` does *not* change the PDF, and vice versa. Change both or
  neither.
- **`paintItem()` will not overwrite the estimate box while it has focus.** Keep that guard, or
  typing a price gets wiped on every keystroke.
- **What survives what:**
  - Unticking an item clears its qty, stock, price and bought flag — but keeps its estimate.
  - "Reset everything" keeps five things: `photos`, `est`, `custom`, `pics`, `cur`.
- **Dead code you can ignore** (or clean up): `S.auto` is declared, hydrated and deleted but never
  assigned; `data-name` on each card is written but never read; `<p class="nomatch">` is always
  force-hidden so its message can never appear.

---

## 8c. Fixed on 24 Aug 2026

Three real bugs, found by re-reading the file rather than trusting memory:

| Bug | Effect | Fix |
| --- | --- | --- |
| `seedEstimates()` ran on every load | A price you deleted came back on the next refresh | Seeds once, then sets `S.seeded`; an existing list counts as already seeded |
| `.est` named two different things | The card's estimate label and the table's Est. cost column collided — the column rendered as a flex box, and print hid it | The card field is now `.estfield`; the column is `.est` |
| `aria-label` escaped twice | Screen readers announced "&amp;amp;" in the add-item boxes | Escaped once |

---

## 9. Known limitations

- **No sync.** State lives in that browser's `localStorage`, per device *and per address* — the
  hosted page and the downloaded file keep separate lists. Backup / Restore moves it deliberately.
- **No history.** "What I Bought" holds the current trip only. Starting a new list replaces it.
  Keeping past trips would need a new state shape.
- **Seed prices are a snapshot** taken from Lotus's on 24 Aug 2026, one store, and they drift.
  78 items were deliberately left unpriced because the automated match was not trustworthy.
- **The site is public.** Anyone with the link can open it.
- **iOS** cannot open the loose file well from the Files app; use the hosted URL there.

---

## 10. If you are picking this up cold

The fastest way to understand it: open `index.html` in a browser, tick a few things, press
**Create Shopping List**, then **What I bought**. Then read the JS section banners in §4 in that
same order — the code follows the same journey.
