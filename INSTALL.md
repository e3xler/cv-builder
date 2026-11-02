# Installation

## Claude.ai (Browser oder Desktop-App)

1. `cv-builder.zip` aus dem [neuesten Release](../../releases/latest) herunterladen. Nicht entpacken.
2. In den Einstellungen von Claude die Codeausführung (Dateien erstellen und bearbeiten) einschalten. Ohne sie laufen keine Skills mit Skripten.
3. In den Einstellungen unter Skills das Zip hochladen. Die Menünamen können je nach Version leicht abweichen.
4. Neuen Chat öffnen und schreiben: „Erstell mir einen Lebenslauf.“ Den alten Lebenslauf und die Stellenanzeige kannst du gleich anhängen.

Am Ende bekommst du eine Datei `lebenslauf-<name>.html`. Herunterladen, im Browser öffnen, Vorlage
wählen, „PDF / Drucken“ klicken. Beim Drucken: Ziel „Als PDF speichern“, Ränder „Keine“,
Hintergrundgrafiken an.

## Claude Code

```bash
unzip cv-builder.zip -d ~/.claude/skills/
```

Danach in Claude Code: „Erstell mir einen Lebenslauf.“ Mit Playwright rendert der Skill das PDF
direkt und prüft es:

```bash
pip install playwright pypdf pdfminer.six && playwright install chromium
```

## Probleme

- **Der Skill taucht nicht auf:** Codeausführung muss eingeschaltet sein.
- **Im Builder stehen alte Daten:** Der Builder merkt sich Änderungen im Browser. Eine neu erzeugte Datei überschreibt das beim ersten Öffnen automatisch.
- **Das PDF hat zwei Seiten statt einer:** Inhalt kürzen oder eine kompaktere Vorlage wählen, der Skill nennt dir die Länge im Gate.
