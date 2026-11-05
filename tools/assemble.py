"""Build index.html (GitHub Pages) from tools/template.html and data/*.json.
Usage: python3 tools/assemble.py [fragment_out.html]"""
import json, sys, pathlib
root = pathlib.Path(__file__).resolve().parent.parent
t = (root / "tools/template.html").read_text(encoding="utf-8")
def js(name):
    data = json.loads((root / "data" / name).read_text(encoding="utf-8"))
    return json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
frag = t.replace("__PARTS__", js("parts.json")).replace("__CARDS__", js("cards.json")).replace("__ACRO__", js("acronyms.json"))
if len(sys.argv) > 1:
    pathlib.Path(sys.argv[1]).write_text(frag, encoding="utf-8")
i = frag.index("</style>") + len("</style>")
head = '<!doctype html>\n<html lang="ms">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
page = head + frag[:i] + "\n</head>\n<body>\n" + frag[i:].lstrip() + "\n</body>\n</html>\n"
page = page.replace("* { box-sizing: border-box; }", "* { box-sizing: border-box; }\n[hidden] { display: none !important; }\nhtml, body { margin: 0; }", 1)
(root / "index.html").write_text(page, encoding="utf-8")
print("index.html", len(page))
