# cv.json – Datenformat

Eine Datei pro Lebenslauf. `fill_builder.py` schreibt sie in den Builder, `check_cv.py` prüft sie.

```json
{
  "level": "junior | mid | senior",
  "template": 5,
  "style": "e3xler",
  "lang": "de",
  "photo": false,
  "hidden": [],
  "cv": { ... }
}
```

| Feld | Bedeutung |
|---|---|
| `level` | Steuert die Längenprüfung: junior ≈ 1 Seite, mid 1 bis 2, senior 2 |
| `template` | Vorlage 1 bis 12, siehe templates.md |
| `style` | `e3xler`, `vent3x` (Kontrast), `3xlabs` (Raster), `forest`, `atelier`, `signal` |
| `lang` | `de` oder `en`, betrifft nur die Überschriften im Builder. Den Text schreibst du in der Sprache der Anzeige |
| `photo` | Foto anzeigen. Default `false` |
| `hidden` | Abschnitte ausblenden. Leere Abschnitte blendet `fill_builder.py` selbst aus |

## Objekt `cv`

| Feld | Typ | Regel |
|---|---|---|
| `name` | Text | Pflicht |
| `title` | Text | Pflicht. Die Zielrolle, möglichst wörtlich aus der Anzeige |
| `email`, `phone` | Text | Mindestens eins von beiden |
| `location` | Text | Pflicht. Stadt, Land |
| `website`, `linkedin` | Text | Ohne `https://` |
| `birth`, `nationality` | Text | Optional (AGG). Nur wenn der Nutzer es will |
| `photo` | Text | Leer lassen. Der Nutzer lädt das Foto selbst im Builder hoch |
| `summary` | Text | 2 bis 3 Sätze. Junior: Berufsziel. Mid/Senior: Profil mit Belegen |
| `experience[]` | Liste | `{role, company, location, start, end, bullets[]}`, neueste zuerst |
| `education[]` | Liste | `{degree, school, location, start, end, note}` |
| `projects[]` | Liste | `{name, desc}` |
| `skills[]` | Liste | `{label, items}`, `items` komma-getrennt, z. B. `{"label": "Werkzeuge", "items": "Jira, Figma"}` |
| `rated[]` | Liste | `{name, level}` mit Level 1 bis 5. Nur für Vorlagen mit bewerteten Kenntnissen (2, 8, 9) |
| `languages[]` | Liste | `{name, label, level}`, z. B. `{"name": "Englisch", "label": "Verhandlungssicher", "level": 4}` |
| `certs[]` | Liste | `{name, issuer, date}` |
| `interests[]` | Liste | Texte. Nur wenn sie etwas über die Person sagen |

## Datumsformat

`MM/JJJJ` für Stationen (`04/2022`), `JJJJ` bei Ausbildung ist okay, laufend = `heute` (englisch `today`).

## Platzhalter = Wahrheits-Gate

Fehlt eine Zahl, ein Datum oder ein Name, steht im Text ein Platzhalter in eckigen Klammern mit Fragezeichen:
`[ZAHL?]`, `[DATUM?]`, `[FIRMA?]`. `check_cv.py` meldet jeden davon als offen. Ausgegeben wird erst, wenn
keiner mehr da ist: Entweder der Nutzer liefert die Angabe, oder der Satz wird ohne sie umformuliert.

Vollständiges Beispiel: `examples/lena-berger.json`.
