# Konzeptionspapier: py-ascii Desktop App

## Problem Statement

Wie können wir eine performante, intuitive Desktop-Anwendung schaffen, mit der Anwender beliebige Bilder und Videos in Echtzeit in ästhetische ASCII-Kunst (monochrom oder vollfarbig) verwandeln und mitsamt Original-Tonspur exportieren können?

## Recommended Direction: Canvas-basierte Hochleistungs-Architektur

### 1. Entkopplung von Berechnung und Darstellung

- **NumPy-vektorisierte ASCII-Engine**:
  - Konvertierung von Bildern/Frames durch gezielte Matrix-Skalierung unter Berücksichtigung des typischen Monospace-Seitenverhältnisses (~1:2).
  - Vektorisierte Helligkeitsberechnung (Luminanz) und direktes Index-Mapping auf konfigurierbare Zeichensätze (Standard, Dicht, Blöcke, Custom).
  - Volle RGB-Farbmatrix-Erhaltung für den Farb-Modus.
- **Dedizierter Render-Canvas (`QPainter`) statt Text-Widget**:
  - Die Darstellung von Tausenden farbigen Zeichen in HTML/`QTextEdit` bricht bei Video-Wiedergabe drastisch in den einstelligen FPS-Bereich ein.
  - Stattdessen rendert ein eigens optimiertes `AsciiCanvasWidget` via `QPainter` direkt Zeichen und Farben. Dies garantiert flüssige 30–60 FPS und perfekte Skalierung bei Vollbild/Fensteranpassung.

### 2. Robuste Video-Pipeline

- **Wiedergabe**: OpenCV-basierter `VideoWorker` im separaten `QThread`. Er sendet konvertierte ASCII-Frames asynchron per Qt-Signal an die UI, ohne das User-Interface zu blockieren.
- **Export mit Audio**:
  - Bildexport: `.txt` (reiner Text) oder gerastertes `.png`.
  - Videoexport: Generierung des ASCII-Videostreams (`.mp4`) und automatisches Muxen der Original-Audiospur via FFmpeg (oder Bildfolge-Encoder) sowie animierter `.gif`-Export für kurze Clips.

---

## Key Assumptions to Validate

- [ ] **Echtzeit-Performance:** Erreicht die NumPy + QPainter-Pipeline auf durchschnittlicher Hardware flüssige 24–30 FPS bei einer Auflösung von 100–160 Zeichen Breite? *(Test: Benchmark-Skript für Frame-Konvertierung und Canvas-Repaint).*
- [ ] **FFmpeg-Verfügbarkeit / Audio-Muxing:** Wie stellen wir sicher, dass Video-Exporte mit Tonspur nahtlos auf Windows funktionieren (z. B. automatisches Auffinden oder Verwenden von `imageio-ffmpeg` / FFmpeg-Binary)?
- [ ] **Zeichensatz-Proportionen:** Ist die Korrektur des Seitenverhältnisses flexibel genug, damit runde Objekte im Quellvideo auch als ASCII-Art rund bleiben und nicht vertikal verzerrt werden?

---

## MVP Scope

### Enthalten (Must-Haves)

1. **Medienimport:**
   - Öffnen von Bildern (`.png`, `.jpg`, `.jpeg`, `.webp`, `.bmp`) und Videos (`.mp4`, `.avi`, `.mov`, `.mkv`).
   - Drag-and-Drop auf das App-Fenster sowie Standard-Dateidialog.
2. **ASCII-Verarbeitung & Einstellungs-Panel:**
   - Schieberegler für Zeichenauflösung (Breite in Spalten) und vertikales Seitenverhältnis.
   - Helligkeits-, Kontrast- und Invertierungs-Regler.
   - Auswahl vordefinierter Zeichensätze (Standard `.:-=+*#%@`, Dense, Minimal, Blocks) sowie Eingabefeld für eigenen Zeichensatz.
   - Umschaltung zwischen **Vollfarb-Modus (RGB)** und **Monochrom-Modus** (mit Farbauswahl für Text & Hintergrund, z. B. Matrix-Grün, Bernstein, Schwarz-Weiß).
3. **Interaktive Vorschau & Player:**
   - `AsciiCanvasWidget` mit stufenlosem Zoom, Fit-to-Window und Vollbildmodus (F11).
   - Videosteuerung: Play/Pause, Timeline-Scrubber, Zeit-/Frame-Anzeige.
4. **Export:**
   - Bildexport als `.txt` und hochauflösendes `.png`.
   - Videoexport als `.mp4` (mit Original-Tonspur) und `.gif`.
   - Fortschrittsanzeige mit Abbruch-Option bei längeren Exporten.
5. **UI & Theme:**
   - Responsive PySide6-Oberfläche gemäß Projektregeln.
   - Dark- und Light-Theme Umschaltung, persistente Fenstergröße via `QSettings`.

---

## Not Doing (and Why)

- **Audio-Wiedergabe während der interaktiven Live-Vorschau**: Würde komplexe A/V-Sync-Engines erfordern und die GUI verlangsamen; Ton wird erst beim Export wieder nahtlos eingespielt.
- **Videoschnitt & Effektketten (Trimming, Filtermasken)**: Die App soll ein fokussiertes Konvertierungswerkzeug sein, keine Videoschnitt-Software.
- **Webcam-Streaming im ersten Wurf**: Fokus liegt zunächst auf perfekten Datei-Konvertierungen und stabiler Player-Architektur.
- **HTML-Text-Rendering im Haupt-Viewer**: Wegen drastischer Performance-Verluste bei farbigen Videos zugunsten von `QPainter` verworfen.

---

## Open Questions & Lösungsansätze

1. *Audio-Handling beim Export:* Nutzen wir `imageio-ffmpeg` als gekapseltes Python-Paket, damit der Anwender kein separates FFmpeg installieren muss?  
   *Empfehlung:* Ja, `imageio-ffmpeg` über `uv add imageio-ffmpeg` einbinden, da es die FFmpeg-Binaries auf allen Plattformen transparent mitbringt.
2. *Zusätzliche Dependencies:* Benötigt werden `opencv-python` (für Video-Frames & Decoding), `numpy` (für High-Speed-Matrixoperationen), `pillow` (Bildverarbeitung/Font-Rendering) und `imageio-ffmpeg` (Audio-Muxing).
