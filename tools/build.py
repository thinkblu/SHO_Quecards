import re, json, sys

W = sys.argv[1]
gist_lines = open(f"{W}/gist.txt", encoding="utf-8").read().split("\n")
act_lines = open(f"{W}/act.txt", encoding="utf-8").read().replace("\f", "\n").split("\n")

# ---------- gist ----------
rows = []
part = None
cur = None
for ln in gist_lines:
    m_b = re.match(r"^(Bahagian [IVX]+[A-Z]?\s*–.*)$", ln.strip())
    if m_b and not ln.startswith(" "):
        part = m_b.group(1).strip()
        cur = None
        continue
    if ln.strip() == "Jadual-Jadual":
        part = "Jadual-Jadual"; cur = None; continue
    m = re.match(r"^  (s\.\S+)\s{2,}(.*)$", ln)
    m2 = re.match(r"^  ((?:Pertama|Kedua|Ketiga|Keempat|Kelima) \(s\.\S+\))(?:\s*\[BAHARU 2024\])?\s{2,}(.*)$", ln)
    if m:
        cur = {"ref": m.group(1), "gist": m.group(2).strip(), "part": part}
        rows.append(cur); continue
    if m2:
        cur = {"ref": "Jadual " + m2.group(1).split(" ")[0], "gist": ("[BAHARU 2024] " if "BAHARU" in ln[:50] else "") + m2.group(2).strip(), "part": "Jadual-Jadual"}
        rows.append(cur); continue
    if ln.strip().startswith("Sumber"):
        cur = None; continue
    if cur and re.match(r"^\s{10,}\S", ln) and not re.search(r"Page \d+ of 28", ln) and "Intipati dalam" not in ln:
        cur["gist"] += " " + ln.strip()
for r in rows:
    r["gist"] = re.sub(r"\s+", " ", r["gist"]).replace("- ", "-").strip() if False else re.sub(r"\s+", " ", r["gist"]).strip()
    # fix hyphenated line wraps like "Jadual- Jadual"
    r["gist"] = re.sub(r"(\w)- (\w)", lambda m: m.group(1)+"-"+m.group(2), r["gist"])

# ---------- TOC titles ----------
titles = {}
toc = open(f"{W}/toc.txt", encoding="utf-8").read().replace("\f", "\n").split("\n")
last = None
for ln in toc:
    m = re.match(r"^\s{1,8}(\d+)\s?([A-Z]?)\.\s+(\S.*)$", ln)
    if m:
        last = m.group(1) + m.group(2)
        titles[last] = m.group(3).strip(); continue
    if last and re.match(r"^\s{9,}[a-z(]", ln):
        titles[last] += " " + ln.strip(); continue
    if ln.strip(): last = None
titles = {k: re.sub(r"\s+", " ", v) for k, v in titles.items()}

# ---------- body cleaning ----------
body = act_lines[530:]
clean = []
skip_caps = False
for ln in body:
    s = ln.strip()
    if not s: continue
    if s in ("Keselamatan dan Kesihatan Pekerjaan", "Undang-Undang Malaysia", "AKTA 514"): continue
    if re.fullmatch(r"\d{1,3}", s): continue
    if "CATATAN" in s: skip_caps = "note"; continue
    if skip_caps == "note":
        if re.match(r"^(Pekerjaan|\(Pindaan\)|m\.b\.p)", s): continue
        skip_caps = False
    if re.fullmatch(r"BAHAGIAN [IVX]+[A-Z]?", s): skip_caps = True; continue
    if skip_caps is True and s.upper() == s and not re.match(r"^\d", s): continue
    skip_caps = False
    if s.startswith("MAKA INILAH") or s.startswith("Seri Paduka") or s.startswith("persetujuan Dewan") or s.startswith("Parlimen, dan dengan"): continue
    clean.append(s)

# find end of sections (transitional footnote) and schedules
end_idx = next(i for i, s in enumerate(clean) if s.startswith("Kecualian") or s.startswith("55. (1) Semua orang"))
# step back to the line '67B' block end: drop the "Kecualian" heading area
sec_lines = clean[:end_idx]
sched_start = next(i for i, s in enumerate(clean) if s == "JADUAL PERTAMA")
sched_lines = clean[sched_start:]
sched_end = next((i for i, s in enumerate(sched_lines) if s.startswith("SENARAI PINDAAN") or s == "UNDANG-UNDANG MALAYSIA"), len(sched_lines))
sched_lines = sched_lines[:sched_end]

# split sections
order = list(titles.keys())
sections = {}
cur_no = None
buf = []
expected = iter(order)
nxt = next(expected)
for s in sec_lines:
    m = re.match(r"^(\d+[A-Z]?)\.\s+(.*)$", s)
    if m and m.group(1) == nxt:
        if cur_no: sections[cur_no] = buf
        cur_no = nxt; buf = [m.group(2)]
        nxt = next(expected, None)
        continue
    if cur_no: buf.append(s)
if cur_no: sections[cur_no] = buf

def norm(x): return re.sub(r"\s+", " ", x).strip()

# strip next section's title from the tail of each section
for k, lines in sections.items():
    idx = order.index(k)
    if idx + 1 < len(order):
        t = norm(titles[order[idx+1]]).lower()
        for n in range(1, 5):
            tail = norm(" ".join(lines[-n:])).lower()
            if tail == t:
                sections[k] = lines[:-n]; break
    # drop trailing "*CATATAN" leftovers / stray caption "Kecualian"
    sections[k] = [l for l in sections[k] if not l.startswith("*CATATAN")]

def join(lines):
    out = ""
    for l in lines:
        if not out: out = l; continue
        if out.endswith("-") and not out.endswith(" -") and re.match(r"^[a-z]", l):
            out = out + l   # hyphenated word across line e.g. "dua-duanya"
        else:
            out = out + " " + l
    out = out.replace("*", "").replace("keduaduanya", "kedua-duanya")
    return norm(out)

def nxt_para(cur):
    if cur is None: return {"a"}
    if len(cur) == 1: return {chr(ord(cur)+1), cur+"a"}
    return {cur[0]+chr(ord(cur[1])+1), chr(ord(cur[0])+1)}

def segments(no, lines):
    """returns list of (sub, para, text-lines)"""
    segs = []
    sub = None; para = None
    exp_sub = 1
    curseg = [None, None, []]
    first = True
    for l in lines:
        if first:
            first = False
            m = re.match(r"^\((\d+[A-Z]?)\)\s*(.*)$", l)
            if m:
                sub = m.group(1); exp_sub = int(re.match(r"\d+", sub).group()) + 1
                curseg = [sub, None, [l]]; continue
            curseg = [None, None, [l]]; continue
        m = re.match(r"^\((\d+)([A-Z]?)\)(\s|$)", l)
        if m and (int(m.group(1)) == exp_sub or (m.group(2) and sub and int(m.group(1)) == int(re.match(r"\d+", sub).group()))):
            segs.append(curseg)
            sub = m.group(1)+m.group(2); para = None
            if not m.group(2): exp_sub = int(m.group(1)) + 1
            curseg = [sub, None, [l]]; continue
        m = re.match(r"^\(([a-z]{1,2})\)(\s|$)", l)
        if m and m.group(1) in nxt_para(para):
            segs.append(curseg)
            para = m.group(1)
            curseg = [sub, para, [l]]; continue
        curseg[2].append(l)
    segs.append(curseg)
    return segs

def lookup(ref):
    m = re.match(r"^s\.(\d+[A-Z]?)(.*)$", ref)
    no, rest = m.group(1), m.group(2)
    lines = sections.get(no)
    if not lines: return None, no
    segs = segments(no, lines)
    parts = re.findall(r"\(([0-9]+[A-Z]?|[a-z]{1,2})\)", rest)
    rng = re.match(r"^\((\d+)\)–\((\d+)\)$", rest)
    subs, para = [], None
    if rng:
        subs = [str(x) for x in range(int(rng.group(1)), int(rng.group(2))+1)]
    else:
        for p in parts:
            if p[0].isdigit(): subs = [p]
            else: para = p
    if not subs and not para:
        return [join(s[2]) for s in segs], no
    out = []
    if subs and para:
        out = [join(s[2]) for s in segs if s[0] == subs[0] and s[1] is None] + [join(s[2]) for s in segs if s[0] == subs[0] and s[1] == para]
    elif subs:
        out = [join(s[2]) for s in segs if s[0] in subs]
    else:
        out = [join(s[2]) for s in segs if s[0] is None and s[1] is None] + [join(s[2]) for s in segs if s[1] == para]
    return out, no

# schedules
sched = {}
names = ["PERTAMA", "KEDUA", "KETIGA", "KEEMPAT", "KELIMA"]
curk = None
for s in sched_lines:
    m = re.match(r"^JADUAL (PERTAMA|KEDUA|KETIGA|KEEMPAT|KELIMA)$", s)
    if m: curk = m.group(1); sched[curk] = []; continue
    if curk: sched[curk].append(s)

def sched_items(lines):
    out = []; head = []
    for l in lines:
        if re.match(r"^\d+[A-Z]?\.\s", l): out.append([l])
        elif out: out[-1].append(l)
        else: head.append(l)
    return [join(h) for h in [head] if h] + [join(o) for o in out]

cards = []
miss = []
for r in rows:
    if r["ref"].startswith("Jadual"):
        key = {"Pertama":"PERTAMA","Kedua":"KEDUA","Ketiga":"KETIGA","Keempat":"KEEMPAT","Kelima":"KELIMA"}[r["ref"].split()[1]]
        v = sched_items(sched[key])
        cards.append({"ref": r["ref"], "title": "Jadual " + key.title(), "part": r["part"], "gist": r["gist"], "verbatim": v})
        continue
    v, no = lookup(r["ref"])
    if not v or not any(x.strip() for x in v):
        miss.append(r["ref"])
    cards.append({"ref": r["ref"], "sec": no, "title": titles.get(no, ""), "part": r["part"], "gist": r["gist"], "verbatim": v or []})

PARTS = [("I","Permulaan","1"),("II","Pelantikan Pegawai, Badan Pemeriksa Bebas & Orang Berlesen","5"),("III","Majlis Negara KKP","8"),("IV","Kewajipan Am Majikan, Orang Bekerja Sendiri & Prinsipal","15"),("V","Kewajipan Am Pereka Bentuk, Pengilang & Pembekal","20"),("VI","Kewajipan Am & Hak Pekerja","24"),("VIA","Notis Tempat Kerja, Pemasangan & Pemeriksaan Loji","27A"),("VII","Organisasi Keselamatan & Kesihatan","28"),("VIIA","Orang Kompeten & Penyedia Latihan Berdaftar","31B"),("VIII","Pemberitahuan Kemalangan & Siasatan","32"),("IX","Larangan Penggunaan Loji atau Bahan","35"),("X","Tataamalan Industri","37"),("XI","Penguatkuasaan & Penyiasatan","39"),("XII","Liabiliti bagi Kesalahan","51"),("XIII","Rayuan","63"),("XIV","Peraturan-Peraturan","66"),("XV","Pelbagai","67")]
starts = [(order.index(p[2]), p) for p in PARTS]
for c in cards:
    if c["ref"].startswith("Jadual"):
        c["p"] = "J"; continue
    oi = order.index(c["sec"])
    c["p"] = [p for (i, p) in starts if i <= oi][-1][0]
    del c["part"]
for c in cards: c.pop("part", None)
open(f"{W}/parts.json","w").write(json.dumps([[a,b] for a,b,_ in PARTS]+[["J","Jadual-Jadual"]], ensure_ascii=False))
json.dump(cards, open(f"{W}/cards.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(len(rows), "cards; missing:", miss)
print(len(sections), "sections; titles", len(titles))
