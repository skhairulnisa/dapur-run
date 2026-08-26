# Dapur Run

An interactive grocery checklist — one self-contained HTML page.

Tick what you need, note the quantity and what's still in the kitchen, then print a clean A4
list or download it as a PDF. A separate **What I Bought** page records what you actually
bought and what you paid, and compares it against your estimate — reading the prices off your
receipt if you paste its text in. Finished trips are kept on a **Previous Groceries** page.

**Live:** <https://skhairulnisa.github.io/dapur-run/>

- 163 items across 15 categories, each with a real photograph
- Replace any photo with your own; add your own items to any category
- Estimated prices and pack sizes, with a running "about RM…" total and a weight to carry
- Printable A4 shopping list with real tick boxes, plus a hand-built PDF export (no libraries)
- **Receipt reader** — attach the receipt photo, paste the text your phone reads off it, and the
  prices land against the right items
- **Previous Groceries** — every finished trip kept with its items, prices and receipt, ready to
  replay onto a new list or print as extra PDF pages
- Everything is embedded — photos, fonts, code — so it works with no internet
- Your list lives in your browser; **Backup** and **Restore** move it between devices

`index.html` is the entire app. There is no build step.

See [HANDOVER.md](HANDOVER.md) to make changes, and `tests/` for the test suite.
