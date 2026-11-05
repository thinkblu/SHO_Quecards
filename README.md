# SHO Cue Cards

Random cue cards for the NIOSH SHO course, in two decks.

## Deck 1: Akta 514

Cards for the **Akta Keselamatan dan Kesihatan Pekerjaan 1994 (Akta 514)**, as at the reprint of 1 June 2024 (after Akta A1648).

Each card shows:

1. **Seksyen number** (e.g. `s.18A(3)(b)`), its Bahagian and section title
2. **Intipati** — the gist in plain Bahasa Melayu
3. **Teks Akta** — the verbatim text of that subsection/paragraph

264 cards cover every subsection from s.1 to s.67B, plus Jadual Pertama–Kelima.

## Deck 2: Akronim SHO

411 acronyms and abbreviations from Akta 302, 514, 835 and 872 and Modules 1–4 (from the "SHO Acronyms – A to Z" doc). Each card shows the acronym, its meaning and where it appears (e.g. `M2 2.10` = Module 2, chapter 2.10). Filter by letter group or by source (Akta, M1–M4).

## Use

Open `index.html` in any browser (no install, no server). To host it, enable GitHub Pages on the `main` branch.

- **Cabut kad!** (or Space) draws a random card; the deck is shuffled without repeats until every card in the filter has been seen
- **← →** or swipe to go back/forward
- Filter by Bahagian, or **2024 sahaja** for sections added/amended by Akta A1648
- **Mod kuiz** (K) hides the gist and text until tapped
- **★** (S) marks a card as memorised; **Belum hafal** shows only the rest (saved in your browser)
- **Lompat ke** jumps to a section (e.g. `18A`, `48(2)`) or an acronym (e.g. `HIRARC`)
- Switch decks with the buttons at the top (or D); each deck keeps its own ★ and progress

## Data

- `data/cards.json` — the cards (`ref`, `sec`, `title`, `p` = Bahagian, `gist`, `verbatim[]`)
- `data/parts.json` — Bahagian names
- `data/acronyms.json` — acronyms (`a` acronym, `m` meaning, `s` source, `g` letter group)
- `tools/assemble.py` — rebuilds `index.html` from the template and the data
- `tools/build.py` — parser that produced `cards.json` from `pdftotext` output of the gist notes and the official BM reprint (`gist.txt` with `-layout`, `act.txt` plain, `toc.txt` = pages 3–8 with `-layout`)
- `tools/template.html` — page template; `__PARTS__` and `__CARDS__` are replaced with the JSON

The verbatim text was extracted automatically from the PDF reprint by Jabatan Peguam Negara, which itself is an updated text and not the authoritative print. Check the official Akta before quoting it in an exam or report.
