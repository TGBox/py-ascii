# Implementation Plan: py-ascii Desktop App

## Overview

Entwicklung einer modernen, performanten Desktop-Anwendung auf Basis von PySide6, NumPy, OpenCV und Pillow, die Bilder und Videos in Echtzeit in ASCII-Kunst (Vollfarb-RGB und Retro-Monochrom) umwandelt, eine flüssige Live-Vorschau bietet und Exporte als Bild (`.png`, `.txt`) sowie Video (`.mp4` mit erhaltener Tonspur, `.gif`) ermöglicht.

## Architecture Decisions

- **Berechnungs-Engine mit NumPy**: Bildrasterung und Helligkeits-Mapping erfolgen vektorisiert über NumPy-Matrizen, um Frameraten von 30–60 FPS selbst bei hochauflösenden Videoquellen zu gewährleisten.
- **Custom `QPainter`-Canvas (`AsciiCanvasWidget`)**: Anstelle von HTML/RichText (welches bei Tausenden Farb-Spans pro Frame drastisch einbricht) wird ein hardwarebeschleunigtes `QWidget` mit `QPainter` eingesetzt, das Zeichen und Farben direkt rastert.
- **Asynchrone Video-Architektur (`QThread`)**: Video-Dekodierung und Frame-Generierung laufen in einem dedizierten Worker-Thread, um die GUI zu jeder Zeit reaktionsfähig zu halten.
- **Audio-Muxing via `imageio-ffmpeg`**: Für den Videoexport (`.mp4`) wird die Original-Tonspur extrahiert und mit dem gerenderten ASCII-Videostream über die in `imageio-ffmpeg` gebündelten Binaries ohne Audio-Re-Encoding gemuxt.
- **Design & UX gemäß Workspace-Richtlinien**: Deutsche Nutzeroberfläche, englischer Code, persistente Fenstergröße via `QSettings`, Vollbildunterstützung (F11), Dark- und Light-Theme.

---

## Task List

### Phase 1: Foundation & Core Engine

- [ ] **Task 1: Abhängigkeiten & Projekt-Setup**: Installation von `numpy`, `opencv-python`, `pillow`, `imageio-ffmpeg` via `uv` und Konfiguration der Testumgebung.
- [ ] **Task 2: Vektorisierte ASCII-Engine**: Implementierung von `AsciiConfig`, `AsciiFrame` und `AsciiConverter` mit NumPy-Vektorisierung und Unit-Tests.

### Checkpoint: Foundation

- [ ] Alle Unit-Tests für die ASCII-Konvertierung bestehen (`uv run pytest`).
- [ ] Konvertierungs-Performance < 5ms pro Frame bei Standard-Terminalgröße.

### Phase 2: Canvas & Bild-Workflow

- [ ] **Task 3: Performantes `AsciiCanvasWidget`**: `QPainter`-basierter Zeichenbereich mit Font-Caching, Vollfarb- und Monochrom-Modus sowie Auto-Fit.
- [ ] **Task 4: Einstellungs-Panel & Themes**: Sidebar mit Schiebereglern (Auflösung, Seitenverhältnis, Kontrast, Helligkeit), Zeichensatz-Auswahl, Farbwähler und Dark/Light-Theme.
- [ ] **Task 5: Hauptfenster & Bild-Pipeline**: Integration von Drag-and-Drop, Dateidialog, Menüleiste, F11-Vollbild und `QSettings`-Persistenz für Einzelbilder.

### Checkpoint: Bild-Workflow funktionsfähig

- [ ] Bilder können geöffnet, angepasst und verzögerungsfrei in der GUI dargestellt werden.
- [ ] Dark- und Light-Theme funktionieren nahtlos.

### Phase 3: Video-Pipeline & Player

- [ ] **Task 6: Asynchroner `VideoWorker`**: `QThread`-basierter Frame-Grabber mit OpenCV für Play, Pause, Seek und Frame-Rate-Steuerung.
- [ ] **Task 7: Video-Player-Steuerung & Timeline**: Scrubber-Slider, Play/Pause-Buttons, Zeitanzeige und synchrone Frame-Aktualisierung im Canvas.

### Checkpoint: Video-Wiedergabe flüssig

- [ ] Videos lassen sich flüssig abspielen und vor-/zurückspulen, ohne dass die GUI blockiert.

### Phase 4: Export-System & Polish

- [ ] **Task 8: Export-Engine & Dialoge**: Bildexport (`.txt`, `.png`), Videoexport (`.mp4` mit Audio via `imageio-ffmpeg`, `.gif`) und Fortschrittsdialog.
- [ ] **Task 9: Fehlerbehandlung, Shortcuts & Feinschliff**: Deutsche Lokalisierung, Tastaturkürzel (F11, Leertaste für Play/Pause), Edge-Case-Absicherung und End-to-End-Tests.

### Checkpoint: Vollständige Anwendung

- [ ] Alle Tests (`pytest`, `ruff`) bestehen grün.
- [ ] End-to-End-Flow für Bilder und Videos inklusive Export erfolgreich verifiziert.

---

## Risks and Mitigations

| Risk | Impact | Mitigation |
| ------ | -------- | ------------ |
| Render-Verzögerung bei extrem vielen Zeichen im Vollfarbmodus | Hoch | Zeichen-Batching im `QPainter`, dynamische Anpassung der Schriftgröße oder Vorab-Rasterung in eine `QPixmap`. |
| Fehlende FFmpeg-Systembibliothek auf Windows | Hoch | Nutzung von `imageio-ffmpeg`, welches vorkompilierte, plattformunabhängige FFmpeg-Binaries mitbringt. |
| Speicherüberlauf bei langen Videos im Export | Mittel | Streaming-weiser Export (Frame-by-Frame schreiben statt kompletter Pufferung im RAM). |
