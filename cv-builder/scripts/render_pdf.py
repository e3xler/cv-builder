#!/usr/bin/env python3
"""Optional: rendert die befuellte Builder-HTML direkt als PDF und prueft, ob ein
Bewerbungssystem (ATS) den Text sauber liest. Braucht Playwright mit Chromium; fehlt es,
reicht der Knopf "PDF / Drucken" im Builder.

Aufruf:
    python3 render_pdf.py <lebenslauf.html> <lebenslauf.pdf>

ATS-Check: Text aus dem PDF ziehen (pypdf) und pruefen, ob Name und Abschnitts-Ueberschriften
als echter Text in der richtigen Reihenfolge ankommen.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

HEADINGS = {
    "de": {"summary": "Profil", "experience": "Berufserfahrung", "education": "Ausbildung", "projects": "Projekte",
           "skills": "Kompetenzen", "languages": "Sprachen", "certs": "Zertifikate"},
    "en": {"summary": "Profile", "experience": "Experience", "education": "Education", "projects": "Projects",
           "skills": "Skills", "languages": "Languages", "certs": "Certifications"},
}


def norm(s: str) -> str:
    """Nur Buchstaben und Ziffern, klein: gesperrte Versalien ("BERUF SERF AHRUNG"), Trennstriche
    und Icon-Glyphen stoeren den Vergleich nicht mehr."""
    return "".join(c for c in s.lower() if c.isalnum() and not 0xE000 <= ord(c) <= 0xF8FF)


def probe(cv: dict, key: str) -> str:
    """Erstes Inhaltsstueck eines Abschnitts, an dem sich die Lesereihenfolge pruefen laesst."""
    first = (cv.get(key) or [None])[0]
    if key == "summary":
        return " ".join(str(cv.get("summary", "")).split()[:4])
    if not isinstance(first, dict):
        return ""
    field = {"experience": "role", "education": "degree", "projects": "name", "languages": "name",
             "certs": "name", "skills": "items"}[key]
    return str(first.get(field, "")).split(",")[0]


def render(html: Path, pdf: Path) -> None:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        sys.exit("Kein Playwright: lebenslauf.html im Browser öffnen und 'PDF / Drucken' klicken.")
    with sync_playwright() as pw:
        page = pw.chromium.launch().new_page(viewport={"width": 1280, "height": 900})
        page.goto(html.resolve().as_uri(), wait_until="load")
        page.wait_for_selector("[data-scale]", timeout=30000)
        page.wait_for_timeout(1500)  # Webfonts
        page.pdf(path=str(pdf), format="A4", print_background=True, prefer_css_page_size=True)


def seed_state(html: Path) -> dict:
    """Liest den Zustand aus dem Seed-Block der befuellten HTML (Name, Sprache, Ausgeblendetes)."""
    m = re.search(r'<script id="cvb-seed" type="application/json">(.*?)</script>', html.read_text(encoding="utf-8"), re.S)
    return json.loads(m.group(1).replace("<\\/", "</"))["state"] if m else {}


def layout_text(pdf: Path) -> str | None:
    """Text mit Layout-Analyse (pdfminer): Textbloecke nach Position, so wie viele ATS-Parser lesen.
    None, wenn pdfminer fehlt."""
    try:
        from pdfminer.high_level import extract_text
    except ImportError:
        return None
    return extract_text(str(pdf))


def order_problems(flat: str, cv: dict, keys: list[str], lang: str) -> tuple[list[str], list[str]]:
    """Je Abschnitt: Ueberschrift gefunden, und ihr erstes Inhaltsstueck folgt, bevor eine andere
    Ueberschrift kommt. Gibt (getrennte, fehlende) Ueberschriften zurueck."""
    heads = {k: flat.find(norm(HEADINGS[lang][k])) for k in keys}
    split, missing = [], []
    for key, h_pos in heads.items():
        if h_pos < 0:
            missing.append(HEADINGS[lang][key])
            continue
        pr = norm(probe(cv, key))
        c_pos = flat.find(pr, h_pos) if pr else h_pos
        if c_pos < 0 or any(h_pos < p < c_pos for k, p in heads.items() if k != key):
            split.append(HEADINGS[lang][key])
    return split, missing


def ats_check(pdf: Path, state: dict) -> list[str]:
    try:
        from pypdf import PdfReader
    except ImportError:
        return ["HINWEIS pypdf fehlt, ATS-Check übersprungen"]
    reader = PdfReader(str(pdf))
    stream = "\n".join(p.extract_text() or "" for p in reader.pages)
    text = re.sub(r"\s+", " ", stream)
    cv, lang = state.get("cv", {}), state.get("lang", "de")
    hidden = set(state.get("hidden", []))
    out = [f"Seiten: {len(reader.pages)}"]
    if len(norm(stream)) < 300:
        return out + ["PROBLEM kaum Text im PDF, vermutlich als Bild gerendert"]
    name = norm(cv.get("name", ""))
    if name and name not in norm(stream):
        out.append(f"PROBLEM Name '{cv.get('name')}' nicht als Text im PDF")

    # Lesereihenfolge mit Layout-Analyse (Textbloecke nach Position), wie viele ATS-Parser lesen.
    # Die reine Malreihenfolge taugt nicht: Chromium malt die Ueberschriften mit Icons zuerst.
    keys = [k for k in HEADINGS[lang] if k not in hidden and cv.get(k)]
    layout = layout_text(pdf)
    _, missing = order_problems(norm(stream), cv, keys, lang)
    if missing:
        out.append("HINWEIS nicht im PDF (zeigt die Vorlage nicht): " + ", ".join(missing))
    if layout is None:
        out.append("HINWEIS pdfminer fehlt, Layout-Lesart übersprungen")
    else:
        split_pos, _ = order_problems(norm(layout), cv, keys, lang)
        out.append("PROBLEM mit Layout-Analyse getrennt von ihrem Inhalt: " + ", ".join(split_pos) if split_pos
                   else "Layout-Analyse: Überschriften und Inhalt in Lesereihenfolge")

    # Bindestrich-Woerter muessen woertlich ankommen, sonst findet ein ATS "A/B-Tests" nicht.
    # Nur Abschnitte, die die Vorlage zeigt; ein Zeilenumbruch nach dem Strich ist kein Fehler.
    shown = [cv.get(k) for k in keys if HEADINGS[lang][k] not in missing]
    words = json.dumps(shown, ensure_ascii=False).replace('"', " ").split()
    hyphen = {w.strip(".,;:") for w in words if "-" in w and w[0].isalpha() and not w.startswith("http")}
    joined = re.sub(r"-\s+", "-", text)
    broken = sorted(w for w in hyphen if w not in joined)
    if broken:
        out.append("PROBLEM Bindestrich-Wörter nicht wörtlich im PDF: " + ", ".join(broken[:8]))
    return out


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(__doc__)
        return 2
    html, pdf = Path(argv[0]), Path(argv[1])
    render(html, pdf)
    print(f"ok {pdf}")
    findings = ats_check(pdf, seed_state(html))
    for line in findings:
        print(line)
    return 1 if any(line.startswith("PROBLEM") for line in findings) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
