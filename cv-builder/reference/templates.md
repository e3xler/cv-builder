# Die 12 Vorlagen

Spalten: Nr. für `template`, Layout, Foto-Platz, welche Abschnitte die Vorlage zeigt. Was eine Vorlage
nicht zeigt, landet nicht im PDF (z. B. hat Vorlage 5 keine Zertifikate).

**ATS-Messung** (2026-11-02, Musterkandidatin, Stil e3xler, PDF aus dem Builder): Alle 12 Vorlagen
liefern echten Text. Mit Layout-Analyse (pdfminer, so lesen viele Bewerbungssysteme) folgt in allen 12
jeder Abschnitt seiner Überschrift, und Bindestrich-Wörter wie „A/B-Tests“ kommen wörtlich an.
Trotzdem gilt: Seitenleisten und Zeitleisten sind bei älteren Parsern das größere Risiko. Für eine
Bewerbung über ein Online-Portal (Konzerne, Personaldienstleister, große Mittelständler) darum eine
einspaltige Vorlage nehmen.

| Nr | Level | Name | Layout | Foto | Für Portale | Abschnitte |
|---|---|---|---|---|---|---|
| 1 | Junior | Banner | einspaltig, dunkler Kopf | ja | ja | Profil, Ausbildung, Erfahrung, Projekte, Kompetenzen, Sprachen, Zertifikate |
| 2 | Junior | Moderner Lebenslauf | Seitenleiste links | ja | Risiko Seitenleiste | Profil, Erfahrung, Ausbildung, Projekte, Zertifikate; Leiste: Persönliches, Kontakt, Sprachen, bewertete Kenntnisse |
| 3 | Junior | Caption | einspaltig, Überschriften links daneben | nein | ja | Profil, Ausbildung, Erfahrung, Projekte, Kompetenzen, Sprachen, Zertifikate |
| 4 | Junior | Swiss Minimal | einspaltig, ruhig | nein | ja | Profil, Erfahrung, Kompetenzen, Projekte, Ausbildung, Sprachen |
| 5 | Mid | ATS Logistik | einspaltig, Akzentbalken | nein | ja | Profil, Erfahrung, Kompetenzen, Ausbildung, Projekte, Sprachen |
| 6 | Mid | Harbor | Seitenleiste rechts | ja | Risiko Seitenleiste | Profil, Ausbildung, Erfahrung, Projekte; Leiste: Kontakt, Kompetenzen, Sprachen, Zertifikate |
| 7 | Mid | Schweizer Raster | einspaltig, Datum links | nein | ja | Profil, Erfahrung, Ausbildung, Kompetenzen, Sprachen |
| 8 | Mid | Bewerbungsvorlage 6 | Seitenleiste links | ja | Risiko Seitenleiste | Erfahrung, Ausbildung, bewertete Kenntnisse, Sprachen, Interessen; Leiste: Persönliches, Kontakt |
| 9 | Senior | Bewerbungsvorlage 2 | Zeitleiste | ja | Risiko Zeitleiste | Profil, Erfahrung, Ausbildung, bewertete Kenntnisse, Sprachen |
| 10 | Senior | ATS Ingenieur | einspaltig | nein | ja | Profil, Erfahrung, Kompetenzen, Ausbildung, Projekte, Zertifikate |
| 11 | Senior | ATS Vertikaler Name | Seitenband mit Name | nein | ja | Profil, Erfahrung, Ausbildung, Kompetenzen, Sprachen |
| 12 | Senior | ATS Schweizer | einspaltig | nein | ja | Profil, Erfahrung, Ausbildung, Kompetenzen, Sprachen |

Vorlagen 2, 8 und 9 zeigen Kompetenzen nur als **bewertete Kenntnisse** (`rated[]`, Level 1 bis 5).
Wer eine davon nimmt, braucht `rated` befüllt, sonst fehlen die Kompetenzen im PDF.

## Auswahl in einem Satz

- **Bewerbung über ein Portal:** Junior 3, Mid 5, Senior 10 (mit Zertifikaten) oder 12.
- **Direkt per Mail an eine Person, Foto gewünscht:** Junior 1, Mid und Senior 6.
  Vorlage 9 hat derzeit einen Layout-Fehler (der Profiltext läuft in den farbigen Balken), darum nicht empfehlen.
- **Kreative Rolle, Agentur, Startup:** 2 oder 8, aber nie über ein ATS-Portal.

Wichtig für den Nutzer: Die Vorlage lässt sich im Builder jederzeit wechseln, die Daten bleiben.
Die Empfehlung ist ein Startpunkt, keine Festlegung.

## Stile

`e3xler` (Inter, Grün, Default), `vent3x` = Kontrast (Sora, Orange), `3xlabs` = Raster (Mona Sans),
`forest` (Tannengrün), `atelier` (Serif, Rost), `signal` (Archivo, Schweizer Rot). Für ein ATS ist der
Stil egal, er ändert nur Schrift und Farbe.
