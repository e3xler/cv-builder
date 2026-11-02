#!/usr/bin/env python3
"""Prueft cv.json vor der Ausgabe. Das Wahrheits-Gate: kein offener Platzhalter, keine Luecke
in den Pflichtfeldern, Datumsformat, Laenge passend zum Level, optional Abgleich mit der
Stellenanzeige.

Aufruf:
    python3 check_cv.py <cv.json> [--job <stellenanzeige.txt>]

Exit 0 = bereit fuer die Ausgabe, 1 = offene Punkte (Liste auf stdout).
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

PLACEHOLDER = re.compile(r"\[[A-ZÄÖÜ ]+\?\]")          # [ZAHL?], [DATUM?], [FIRMA?] ...
DATE = re.compile(r"^(\d{2}/\d{4}|\d{4}|heute|today)$")
# Grobe Wortgrenzen je Level: 1 Seite Junior, bis 2 Seiten Mid, 2 Seiten Senior
MAX_WORDS = {"junior": 450, "mid": 800, "senior": 1000}
MAX_BULLETS = 5
STOP = set("""aber alle als also auch auf aus bei bin bis bist das dass dem den der des die dir doch durch
ein eine einem einen einer eines für hat hier ihr ihre im in ist jede kann mit nach nicht noch nur oder
sich sie sind so über um und uns unser unsere von vor was wie wir wird wo zu zum zur sowie bzw mehr sehr
du dein deine dich wenn werden wurde haben unseres team aufgaben profil bieten suchen stelle""".split())


def walk_text(value):
    """Alle Strings aus einem verschachtelten Objekt, fuer Platzhalter- und Wortsuche."""
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for v in value.values():
            yield from walk_text(v)
    elif isinstance(value, list):
        for v in value:
            yield from walk_text(v)


def check(doc: dict, job: str | None) -> tuple[list[str], list[str]]:
    errors, notes = [], []
    cv = doc.get("cv", {})
    level = doc.get("level", "mid")

    for field in ["name", "title", "location"]:
        if not str(cv.get(field, "")).strip():
            errors.append(f"Pflichtfeld fehlt: {field}")
    if not (cv.get("email") or cv.get("phone")):
        errors.append("Kontakt fehlt: E-Mail oder Telefon")
    if not (cv.get("experience") or cv.get("education")):
        errors.append("Weder Berufserfahrung noch Ausbildung")

    for text in walk_text(cv):
        for hit in PLACEHOLDER.findall(text):
            errors.append(f"Offen {hit}: {text[:90]}")

    for key in ["experience", "education"]:
        for i, item in enumerate(cv.get(key, [])):
            for side in ["start", "end"]:
                val = str(item.get(side, "")).strip()
                if val and not DATE.match(val):
                    errors.append(f"Datum {key}[{i}].{side} = {val!r}, erwartet MM/JJJJ, JJJJ oder heute")
    for i, item in enumerate(cv.get("experience", [])):
        bullets = [b for b in item.get("bullets", []) if b.strip()]
        if len(bullets) > MAX_BULLETS:
            notes.append(f"experience[{i}] hat {len(bullets)} Stichpunkte, mehr als {MAX_BULLETS} liest niemand")
        if i == 0 and not bullets:
            errors.append("Aktuelle Station ohne Stichpunkte")

    words = sum(len(t.split()) for t in walk_text(cv) if not t.startswith("data:"))
    limit = MAX_WORDS.get(level, 800)
    if words > limit:
        notes.append(f"{words} Wörter, für Level {level} sind etwa {limit} das Maximum: kürzen")
    if cv.get("photo") or doc.get("photo"):
        notes.append("Foto ist an: in DACH optional, international meist unüblich")
    if cv.get("birth"):
        notes.append("Geburtsdatum steht drin: optional (AGG), bewusst entscheiden")

    if job:
        cv_text = " ".join(walk_text(cv)).lower()
        # Satzzeichen am Wortende abschneiden ("E-Commerce." = "E-Commerce"); nur Substantive und
        # Tech-Begriffe zaehlen (Grossbuchstabe, Ziffer, + oder #), kleingeschriebene Verben nicht
        words = (w.rstrip(".,;:!?)") for w in re.findall(r"[A-Za-zÄÖÜäöüß0-9][\w\-+.#/]{2,}", job))
        terms = {w for w in words if len(w) > 2 and w.lower() not in STOP and re.search(r"[A-ZÄÖÜ0-9+#]", w)}
        missing = sorted({t for t in terms if t.lower() not in cv_text}, key=str.lower)
        if missing:
            notes.append("Begriffe aus der Anzeige, die im CV fehlen (nur aufnehmen, was stimmt): " + ", ".join(missing[:25]))
    return errors, notes


def main(argv: list[str]) -> int:
    if not argv:
        print(__doc__)
        return 2
    doc = json.loads(Path(argv[0]).read_text(encoding="utf-8"))
    job = Path(argv[argv.index("--job") + 1]).read_text(encoding="utf-8") if "--job" in argv else None
    errors, notes = check(doc, job)
    for e in errors:
        print("OFFEN   ", e)
    for n in notes:
        print("HINWEIS ", n)
    print("bereit" if not errors else f"{len(errors)} offene Punkte, erst klären, dann ausgeben")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
