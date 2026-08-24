# Dapur Run

An interactive grocery checklist — one self-contained HTML page.

Tick what you need, note the quantity and what's still in the kitchen, then print a clean A4
list or download it as a PDF. A separate **What I Bought** page records what you actually
bought and what you paid, and compares it against your estimate.

**Live:** <https://skhairulnisa.github.io/dapur-run/>

- 163 items across 15 categories, each with a real photograph
- Replace any photo with your own; add your own items to any category
- Estimated prices, with a running "about RM…" total as you tick
- Printable A4 shopping list, plus a hand-built PDF export (no libraries)
- Everything is embedded — photos, fonts, code — so it works with no internet
- Your list lives in your browser; **Backup** and **Restore** move it between devices

`index.html` is the entire app. There is no build step.

See [HANDOVER.md](HANDOVER.md) to make changes, and `tests/` for the test suite.
