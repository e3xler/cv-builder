---
name: cv-builder
description: Erstellt einen professionellen Lebenslauf (CV) als fertige Datei, entweder aus einem hochgeladenen alten Lebenslauf (PDF, DOCX, Text, LinkedIn-Export) oder per Interview mit Fragen, optional zugeschnitten auf eine Stellenanzeige. Ausgabe ist ein Builder mit 12 Vorlagen (Junior, Mid, Senior, davon 8 ATS-tauglich), in dem der Nutzer das Layout wählt und mit einem Klick ein PDF druckt. Nutze diesen Skill bei "Lebenslauf erstellen", "CV schreiben", "mach meinen Lebenslauf neu", "Lebenslauf für diese Stelle anpassen", "resume", einem hochgeladenen Lebenslauf mit der Bitte um Überarbeitung oder einer Stellenanzeige mit der Bitte um einen passenden CV.
---

# cv-builder

Layout und Inhalt sind getrennt. Die 12 Vorlagen stecken fertig in `assets/builder.html`. Deine
Arbeit ist der Inhalt: eine `cv.json` (Format: `reference/schema.md`), die ehrlich, konkret und auf
die Zielstelle zugeschnitten ist. Die Skripte schreiben sie in den Builder.

**Die eine Regel: nichts erfinden.** Jede Zahl, jede Firma, jeder Zeitraum kommt vom Nutzer, aus
seinem alten CV oder aus seinen Antworten. Fehlt etwas, steht `[ZAHL?]` (oder `[DATUM?]`,
`[FIRMA?]`) im Entwurf, und du fragst nach. Ein ehrlicher Satz ohne Zahl schlägt eine erfundene Zahl.

## Ablauf

### 1. Eingang klären

Frag in einer Nachricht:
- Hast du einen alten Lebenslauf? (hochladen oder einfügen)
- Für welche Stelle? Anzeige einfügen, wenn vorhanden. Ohne Anzeige wird es ein guter CV, mit Anzeige ein passender.
- Deutsch oder Englisch?

### 2. Daten sammeln

- **Mit altem CV:** Alles extrahieren, was drinsteht, in die Struktur aus `reference/schema.md`.
  Danach nur fragen, was fehlt oder unklar ist, vor allem Ergebnisse mit Zahl je Station.
- **Ohne CV:** Interview nach `reference/interview.md`, höchstens drei Fragen pro Runde.

Level vorschlagen (unter 3 Jahre junior, 3 bis 8 mid, über 8 senior) und bestätigen lassen.

### 3. Schreiben

- **Stichpunkte:** Ergebnis vor Tätigkeit. „Abbruchquote von 71 % auf 58 % gesenkt“ statt „Verantwortlich für den Checkout“. Starkes Verb vorne, eine Zeile pro Punkt.
- **Menge:** 3 bis 5 Stichpunkte für die aktuelle Station, 2 bis 3 für ältere. Stationen älter als 10 bis 15 Jahre bekommen nur eine Zeile oder fallen weg.
- **Profil:** 2 bis 3 Sätze. Junior: Ziel und was du mitbringst. Mid/Senior: Schwerpunkt, Jahre, ein belegter Erfolg.
- **Anzeige vorhanden:** Die Begriffe der Anzeige übernehmen, wo sie für den Nutzer stimmen. Bewerbungssysteme vergleichen oft wörtlich. Relevante Erfahrung nach oben. Must-haves, die der Nutzer nicht hat, als Liste an ihn melden, nie in den CV schreiben.
- **Sprache:** klar, aktiv, ohne Floskeln („teamfähig“, „hochmotiviert“, „Hands-on-Mentalität“). Deutsch mit echten Umlauten.
- **DACH:** Foto und Geburtsdatum nur auf Wunsch. Umgekehrt chronologisch. Datum `MM/JJJJ`.

Vorlage nach `reference/templates.md` wählen: über ein Portal eine ATS-Vorlage (Junior 3, Mid 5, Senior 10 oder 12).

### 4. Gate

```bash
python3 scripts/check_cv.py cv.json            # mit Anzeige: --job anzeige.txt
```

Jeder Punkt `OFFEN` wird geklärt, bevor es weitergeht: nachfragen oder Satz umformulieren. Die
`HINWEIS`-Zeilen dem Nutzer kurz nennen (Länge, fehlende Begriffe aus der Anzeige, Foto).

Zeig dem Nutzer den fertigen Inhalt einmal als lesbaren Text (nicht als JSON) und hol ein Okay.

### 5. Ausgeben

```bash
python3 scripts/fill_builder.py cv.json lebenslauf-<vorname>-<nachname>.html
```

Die HTML-Datei dem Nutzer geben (auf claude.ai nach `/mnt/user-data/outputs/`). Dazu diese Anleitung:

1. Datei herunterladen und im Browser öffnen (Chrome, Edge, Safari, Firefox).
2. Links unter „Design“ eine andere Vorlage oder einen anderen Stil wählen, wenn du willst. Die Daten bleiben.
3. Unter „Inhalt“ kannst du jeden Text direkt ändern, die Vorschau zieht mit.
4. „PDF / Drucken“ klicken, als Ziel „Als PDF speichern“, Ränder „Keine“, Hintergrundgrafiken an.

Optional, nur wo Playwright verfügbar ist (z. B. Claude Code):

```bash
python3 scripts/render_pdf.py lebenslauf-<name>.html lebenslauf-<name>.pdf
```

Das rendert das PDF direkt und prüft, ob Name und Abschnitte als echter Text ankommen (ATS-Check).

### 6. Nächste Bewerbung

`cv.json` aufheben. Für die nächste Stelle nur Anzeige rein, Profil und Reihenfolge anpassen, Gate,
ausgeben. Das Layout bleibt, der Inhalt wird pro Bewerbung in Minuten zugeschnitten.

## Datenschutz

Alles bleibt lokal: Der Builder läuft ohne Server im Browser, Änderungen liegen nur im
Browser-Speicher des Nutzers. Keine Daten an Dritte schicken, keine Webdienste für die Erstellung nutzen.

---
Gebaut von Chris Eichler (@e3xler). Vorlagen gestaltet mit Claude Design.
