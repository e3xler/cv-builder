#!/usr/bin/env python3
"""Schreibt die CV-Daten in eine Kopie des CV-Builders. Ergebnis ist eine einzelne HTML-Datei:
oeffnen, Layout waehlen, "PDF / Drucken" klicken. Alles laeuft lokal im Browser.

Aufruf:
    python3 fill_builder.py <cv.json> <ausgabe.html>

cv.json (Format siehe reference/schema.md):
    {"cv": {...}, "template": 5, "style": "e3xler", "lang": "de", "photo": false, "hidden": []}

Leere Abschnitte werden automatisch ausgeblendet, damit keine leeren Ueberschriften im PDF landen.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ASSET = Path(__file__).resolve().parent.parent / "assets" / "builder.html"
SEED_EMPTY = '<script id="cvb-seed" type="application/json">null</script>'
SECTIONS = ["summary", "experience", "education", "projects", "skills", "rated", "languages", "certs", "interests"]
LISTS = SECTIONS[1:]
# Abschnitts-Key im Builder (hidden) je Datenfeld; "rated" heisst dort "skillsRated"
SECTION_KEY = {"rated": "skillsRated"}


def is_empty(value) -> bool:
    """Leer heisst: kein Text, oder eine Liste ohne einen einzigen befuellten Eintrag."""
    if isinstance(value, str):
        return not value.strip()
    if isinstance(value, dict):
        return all(is_empty(v) for v in value.values() if not isinstance(v, (int, float)))
    if isinstance(value, list):
        return all(is_empty(v) for v in value)
    return value is None


def build_state(doc: dict) -> dict:
    """Baut den Builder-Zustand (cvb-state-v1) aus cv.json, ohne das Original zu veraendern."""
    cv = {k: v for k, v in doc["cv"].items()}
    for key in LISTS:
        cv.setdefault(key, [])
    cv.setdefault("photo", "")
    hidden = set(doc.get("hidden", []))
    hidden |= {SECTION_KEY.get(k, k) for k in SECTIONS if is_empty(cv.get(k, ""))}
    return {
        "cv": cv,
        "tpl": int(doc.get("template", 5)),
        "sty": doc.get("style", "e3xler"),
        "lang": doc.get("lang", "de"),
        "hidden": sorted(hidden),
        "showPhoto": bool(doc.get("photo", False)),
        "showIcons": bool(doc.get("icons", True)),
    }


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(__doc__)
        return 2
    src, out = Path(argv[0]), Path(argv[1])
    doc = json.loads(src.read_text(encoding="utf-8"))
    if not isinstance(doc.get("cv"), dict):
        print("FEHLER: cv.json braucht ein Objekt 'cv'")
        return 1
    state = build_state(doc)
    # Seed-ID aus dem Inhalt: neue Daten ueberschreiben den Browser-Speicher, Edits des Nutzers
    # an derselben Datei bleiben beim erneuten Oeffnen erhalten
    seed_id = hashlib.sha256(json.dumps(state, sort_keys=True).encode()).hexdigest()[:16]
    seed = json.dumps({"id": seed_id, "state": state}, ensure_ascii=False).replace("</", "<\\/")
    html = ASSET.read_text(encoding="utf-8")
    if SEED_EMPTY not in html:
        print("FEHLER: assets/builder.html hat keinen Seed-Hook")
        return 1
    html = html.replace(SEED_EMPTY, f'<script id="cvb-seed" type="application/json">{seed}</script>', 1)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
    print(f"ok {out} (Vorlage {state['tpl']}, Stil {state['sty']}, ausgeblendet: {', '.join(state['hidden']) or 'nichts'})")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
