# cv-builder

Ein Claude-Skill, der dir einen professionellen Lebenslauf baut. Kostenlos, ohne Abo, ohne Generator.

Du lädst deinen alten Lebenslauf hoch oder beantwortest ein paar Fragen. Wenn du willst, gibst du die
Stellenanzeige dazu. Der Skill schreibt den Inhalt, prüft ihn und liefert dir eine HTML-Datei mit
12 fertigen Vorlagen. Im Browser wählst du das Layout und klickst auf „PDF / Drucken“. Fertig.

## Warum das funktioniert

Layout und Inhalt sind getrennt. Die Vorlagen sind einmal gestaltet (mit Claude Design), der Skill
kümmert sich nur um den Inhalt. Für jede neue Bewerbung passt du den Inhalt an, das Layout bleibt.

## Was der Skill kann

- **Zwei Eingänge:** alter Lebenslauf (PDF, DOCX, Text, LinkedIn-Export) oder Interview mit Fragen in kurzen Runden.
- **Zuschnitt auf die Stelle:** Begriffe aus der Anzeige abgleichen, relevante Erfahrung nach oben, fehlende Must-haves als Liste an dich.
- **Wahrheits-Gate:** Der Skill erfindet keine Zahlen. Fehlt eine Angabe, steht `[ZAHL?]` im Entwurf, und er fragt nach. Ausgegeben wird erst, wenn nichts mehr offen ist.
- **12 Vorlagen** für Junior, Mid und Senior, 6 Farbstile. Die einspaltigen Vorlagen sind für Bewerbungsportale gedacht.
- **ATS-geprüft:** Alle 12 Vorlagen liefern echten Text in Lesereihenfolge (geprüft mit pdfminer), Bindestrich-Wörter wie „A/B-Tests“ kommen wörtlich an.
- **Lokal:** Der Builder läuft ohne Server im Browser. Deine Daten gehen nirgendwo hin.

## Installation

Lade `cv-builder.zip` aus dem [neuesten Release](../../releases/latest) herunter und folge [INSTALL.md](INSTALL.md).

## Aufbau

```
cv-builder/
├── SKILL.md              Ablauf, Regeln, Gate
├── reference/            Datenformat, die 12 Vorlagen, Interview-Fragen
├── scripts/
│   ├── check_cv.py       Gate: Platzhalter, Pflichtfelder, Datum, Länge, Abgleich mit der Anzeige
│   ├── fill_builder.py   schreibt deine Daten in den Builder
│   └── render_pdf.py     optional: PDF direkt rendern plus ATS-Check (braucht Playwright)
├── assets/builder.html   der Builder mit allen Vorlagen
└── examples/             Musterkandidatin (erfunden)
```

## Tests

```bash
pip install pytest pypdf pdfminer.six playwright && playwright install chromium
python3 -m pytest -q                 # alles, rund eine Minute
python3 -m pytest -q -m "not slow"   # ohne PDF-Rendering
```

## Lizenzen

- Code und Texte des Skills: MIT, siehe [LICENSE](LICENSE).
- Die im Builder eingebetteten Schriften stehen unter der SIL Open Font License.
- Icons: [Uicons by Flaticon](https://www.flaticon.com/uicons).

---

Gebaut von Chris Eichler, [@e3xler](https://www.instagram.com/e3xler).
