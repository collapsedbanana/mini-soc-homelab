"""Génère rapport-mini-soc.pdf à partir de detections/README.md et des parties fixes ci-dessous.
Usage : python3 build.py   (nécessite : pip install markdown playwright pypdf)
"""
import re, pathlib, markdown
from PIL import Image
from playwright.sync_api import sync_playwright
from pypdf import PdfReader, PdfWriter

ROOT = pathlib.Path(__file__).parent
README = (ROOT / "../detections/README.md").read_text(encoding="utf-8")
CSS = (ROOT / "style.css").read_text(encoding="utf-8")

# ---------- 1. Corps : les fiches de test viennent du README ----------
start = README.index("## Mise en place côté Windows")
end = README.index("## Leçons générales")
body_md = README[start:end].replace("\n---\n", "\n")
body = markdown.markdown(body_md, extensions=["tables"])

fig = {"n": 0}
# images groupées dans un même paragraphe
def multi(m):
    imgs = re.findall(r'<img alt="([^"]*)" src="([^"]*)" />', m.group(0))
    out = ""
    for alt, src in imgs:
        fig["n"] += 1
        px = Image.open((ROOT / src).resolve()).size[0]
        out += f'<figure><img src="{src}" style="width:{max(px * 0.45, 220):.0f}px"><figcaption><b>Figure {fig["n"]}</b> : {alt}</figcaption></figure>'
    return out
body = re.sub(r'<p>(?:<img [^>]+/>\s*)+</p>', multi, body)

# encadrés
for label, cls in [("Verdict", "key"), ("Leçon", "key"), ("Piège rencontré", "warn"), ("Problème", "warn"),
                   ("Limites restantes", "warn"), ("Choix assumé", "info"),
                   ("Pourquoi ne pas simplement monter la 92032 ?", "info")]:
    body = re.sub(rf'<p><strong>{re.escape(label)}</strong>\s*:?\s*(.*?)</p>',
                  lambda m: f'<div class="box {cls}"><div class="ttl">{label}</div><p>{m.group(1)[:1].upper() + m.group(1)[1:]}</p></div>', body, flags=re.S)

badges = {
    "1. T1136": '<span class="v ok">Détecté</span>',
    "2. T1053": '<span class="v fix">Corrigé : règle 100100</span>',
    "3. T1547": '<span class="v ok">Détecté</span>',
    "4. T1003": '<span class="v fix">Corrigé : collecte Defender</span>',
    "5. T1070": '<span class="v ok">Détecté</span>',
    "L1. T1110": '<span class="v ok">Détecté</span>',
    "L2. FIM": '<span class="v ok">Détecté</span>',
    "Bonus": '<span class="v mid">Faux positif qualifié</span>',
}
def h2(m):
    t = m.group(1)
    b = next((v for k, v in badges.items() if t.startswith(k)), "")
    return f'<h2>{t} {b}</h2>'
body = re.sub(r'<h2>(.*?)</h2>', h2, body)
body = re.sub(r'<h3>(.*?)</h3>', lambda m: h2(m).replace("h2", "h3"), body)
body = body.replace("<table>", '<table class="t">')

# ---------- 2. Parties fixes ----------
FRONT = (ROOT / "parties/avant.html").read_text(encoding="utf-8")
BACK = (ROOT / "parties/apres.html").read_text(encoding="utf-8")
COVER = (ROOT / "parties/couverture.html").read_text(encoding="utf-8")

def page(inner):
    return f'<!doctype html><html lang="fr"><head><meta charset="utf-8"><style>{CSS}</style></head><body>{inner}</body></html>'

CSS += "\n.results h2 { page-break-before: always; margin-top: 0; }\n.results h2:first-child { page-break-before: avoid; }\n"
main_html = page(FRONT + '<h1 class="section"><span class="num">5</span>Résultats détaillés, test par test</h1>'
                 + (ROOT / "parties/intro-resultats.html").read_text(encoding="utf-8") + '<div class="results">' + body + '</div>' + BACK)
(ROOT / "rapport-mini-soc.html").write_text(main_html, encoding="utf-8")
(ROOT / "_cover.html").write_text(page(COVER), encoding="utf-8")

FOOT = ('<div style="font-family:Liberation Sans,sans-serif;font-size:7.5pt;color:#5b6676;width:100%;'
        'padding:0 18mm;display:flex;justify-content:space-between">'
        '<span>Mini-SOC maison : rapport de tests de détection</span>'
        '<span>Page <span class="pageNumber"></span> / <span class="totalPages"></span></span></div>')

with sync_playwright() as p:
    br = p.chromium.launch(executable_path="/opt/pw-browsers/chromium-1194/chrome-linux/chrome")
    pg = br.new_page()
    pg.goto((ROOT / "_cover.html").resolve().as_uri()); pg.wait_for_load_state("networkidle")
    pg.pdf(path=str(ROOT / "_cover.pdf"), format="A4", print_background=True, prefer_css_page_size=True)
    pg.goto((ROOT / "rapport-mini-soc.html").resolve().as_uri()); pg.wait_for_load_state("networkidle")
    pg.pdf(path=str(ROOT / "_main.pdf"), format="A4", print_background=True, display_header_footer=True,
           header_template="<span></span>", footer_template=FOOT,
           margin={"top": "18mm", "bottom": "20mm", "left": "18mm", "right": "18mm"})
    br.close()

w = PdfWriter()
for f in ["_cover.pdf", "_main.pdf"]:
    for pg_ in PdfReader(str(ROOT / f)).pages:
        w.add_page(pg_)
w.add_metadata({"/Title": "Mini-SOC maison : rapport de tests de détection", "/Author": "collapsedbanana"})
with open(ROOT / "rapport-mini-soc.pdf", "wb") as fh:
    w.write(fh)
for f in ["_cover.pdf", "_main.pdf", "_cover.html"]:
    (ROOT / f).unlink()
print("figures:", fig["n"], "pages:", len(PdfReader(str(ROOT / "rapport-mini-soc.pdf")).pages))
