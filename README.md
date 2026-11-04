# SHO Quecards — Kad Cabut Akta 514

Random cue cards for studying the **Akta Keselamatan dan Kesihatan Pekerjaan 1994 (Akta 514)**, as at the reprint of 1 June 2024 (after Akta A1648).

Each card shows:

1. **Seksyen number** (e.g. `s.18A(3)(b)`), its Bahagian and section title
2. **Intipati** — the gist in plain Bahasa Melayu
3. **Teks Akta** — the verbatim text of that subsection/paragraph

264 cards cover every subsection from s.1 to s.67B, plus Jadual Pertama–Kelima.

## Use

Open `index.html` in any browser (no install, no server). To host it, enable GitHub Pages on the `main` branch.

- **Cabut kad!** (or Space) draws a random card; the deck is shuffled without repeats until every card in the filter has been seen
- **← →** or swipe to go back/forward
- Filter by Bahagian, or **2024 sahaja** for sections added/amended by Akta A1648
- **Mod kuiz** (K) hides the gist and text until tapped
- **★** (S) marks a card as memorised; **Belum hafal** shows only the rest (saved in your browser)
- **Lompat ke** jumps to a section, e.g. `18A` or `48(2)`

## Data

- `data/cards.json` — the cards (`ref`, `sec`, `title`, `p` = Bahagian, `gist`, `verbatim[]`)
- `data/parts.json` — Bahagian names
- `tools/build.py` — parser that produced `cards.json` from `pdftotext` output of the gist notes and the official BM reprint (`gist.txt` with `-layout`, `act.txt` plain, `toc.txt` = pages 3–8 with `-layout`)
- `tools/template.html` — page template; `__PARTS__` and `__CARDS__` are replaced with the JSON

The verbatim text was extracted automatically from the PDF reprint by Jabatan Peguam Negara, which itself is an updated text and not the authoritative print. Check the official Akta before quoting it in an exam or report.
