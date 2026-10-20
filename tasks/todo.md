# Task List: py-ascii Desktop App

## Task 1: Abhängigkeiten & Projekt-Setup

**Description:** Installiere die erforderlichen Kernbibliotheken (`numpy`, `opencv-python`, `pillow`, `imageio-ffmpeg`) über `uv add` und stelle sicher, dass die Entwicklungs- und Testwerkzeuge (`pytest`, `ruff`) im Projekt einsatzbereit sind.

**Acceptance criteria:**

- [x] `pyproject.toml` enthält `numpy`, `opencv-python`, `pillow`, `imageio-ffmpeg` unter den Abhängigkeiten.
- [x] Die virtuelle Umgebung wird via `uv sync` aktualisiert und die Pakete lassen sich importieren.

**Verification:**

- [x] Tests pass: `uv run python -c "import cv2, numpy, PIL, imageio_ffmpeg, PySide6; print('OK')"`
- [x] Build succeeds: `uv run ruff check`

**Dependencies:** None

**Files likely touched:**

- `pyproject.toml`
- `uv.lock`

**Estimated scope:** Small (1-2 files)

---

## Task 2: Vektorisierte ASCII-Engine (`AsciiConverter`)

**Description:** Erstelle das Kernmodul zur Konvertierung von Bilddaten (NumPy-Arrays / PIL-Images) in ASCII-Kunst. Implementiere Datenklassen für die Konfiguration (`AsciiConfig`) und das Ergebnis (`AsciiFrame`), inklusive Zeichenzuordnung, Luminanzberechnung, Farbmatrix und Tests.

**Acceptance criteria:**

- [x] Datenklassen `AsciiConfig` (Breite, Seitenverhältnis, Zeichensatz, Kontrast, Helligkeit, Farbmodus) und `AsciiFrame` (Zeichenmatrix, Farbdaten, Plaintext).
- [x] Schnelle NumPy-basierte Vektorisierung für Graustufen- und Vollfarb-Umwandlung.
- [x] Zuverlässige Berücksichtigung von Zeichen-Seitenverhältnissen (Monospace).
- [x] Ausführliche Unit-Tests in `tests/test_ascii_converter.py`.

**Verification:**

- [x] Tests pass: `uv run pytest tests/test_ascii_converter.py`
- [x] Build succeeds: `uv run ruff check src/core/`

**Dependencies:** Task 1

**Files likely touched:**

- `src/core/__init__.py`
- `src/core/ascii_converter.py`
- `tests/test_ascii_converter.py`

**Estimated scope:** Medium (3 files)

---

## Checkpoint: Foundation

- [x] `uv run pytest` läuft fehlerfrei durch.
- [x] Die Core-Engine konvertiert Bilder zuverlässig in Millisekunden.

---

## Task 3: Performantes `AsciiCanvasWidget` (`QPainter`)

**Description:** Entwickle ein spezialisiertes Qt-Widget (`AsciiCanvasWidget`), das ein `AsciiFrame` über `QPainter` hardwarebeschleunigt auf den Bildschirm zeichnet. Unterstütze Vollfarb-RGB- und Monochrom-Modi sowie automatische Skalierung (Fit-to-Window).

**Acceptance criteria:**

- [x] `AsciiCanvasWidget` rendert Monochrom- und RGB-Zeichen sauber mit Monospace-Schriftart.
- [x] Hintergrund- und Textfarben im Monochrom-Modus frei konfigurierbar (z. B. Matrix-Grün).
- [x] Automatisches Zentrieren und Skalieren bei Größenänderungen des Fensters.
- [x] Zoom-Faktor und Ansichtsoptionen (Originalgröße / Einpassen).

**Verification:**

- [x] Tests pass: `uv run pytest tests/test_canvas.py`
- [x] Build succeeds: `uv run ruff check src/ui/canvas.py`

**Dependencies:** Task 2

**Files likely touched:**

- `src/ui/__init__.py`
- `src/ui/canvas.py`
- `tests/test_canvas.py`

**Estimated scope:** Medium (2-3 files)

---

## Task 4: Einstellungs-Panel & Themes

**Description:** Erstelle die Seitenleiste (`ControlsWidget`) mit intuitiven Steuerelementen (Schieberegler für Zeichenbreite, Zeichensatz-Auswahl, Kontrast, Helligkeit, Farbmodus-Umschalter) sowie ein Stylesheet-System für Dark- und Light-Themes.

**Acceptance criteria:**

- [x] Schieberegler für Auflösung (Spalten), Seitenverhältnis-Korrektur, Helligkeit und Kontrast mit Werteanzeige.
- [x] Dropdown für Zeichensatz-Presets (Standard, Dicht, Blöcke) und Eingabefeld für eigenen Zeichensatz.
- [x] Farbmodus-Umschalter (Vollfarb-RGB vs. Monochrom) mit Farbwahl-Dialogen.
- [x] Dark- und Light-Theme QSS-Stylesheets gemäß Desktop-Konventionen.

**Verification:**

- [x] Tests pass: `uv run pytest tests/test_controls.py`
- [x] Build succeeds: `uv run ruff check src/ui/`

**Dependencies:** Task 3

**Files likely touched:**

- `src/ui/controls.py`
- `src/ui/theme.py`
- `tests/test_controls.py`

**Estimated scope:** Medium (3 files)

---

## Task 5: Hauptfenster & Bild-Workflow

**Description:** Baue das Hauptfenster (`MainWindow`), binde Canvas und Einstellungs-Panel zusammen, ermögliche das Laden von Bildern per Drag-and-Drop oder Dateidialog, implementiere F11-Vollbild und die Speicherung der Fensterposition mit `QSettings`.

**Acceptance criteria:**

- [x] Bilder können via Menü, Button oder Drag-and-Drop geladen werden.
- [x] Änderungen an den Reglern im Einstellungs-Panel aktualisieren das Bild in Echtzeit.
- [x] Vollbildmodus via Taste `F11` umschaltbar.
- [x] Fenstergröße und -position werden beim Beenden in `QSettings` gesichert und beim Neustart wiederhergestellt.

**Verification:**

- [x] Tests pass: `uv run pytest tests/test_main_window.py`
- [x] Manual check: Starten via `uv run py-ascii`, Bild hineinziehen, Parameter testen.

**Dependencies:** Task 4

**Files likely touched:**

- `src/ui/main_window.py`
- `src/main.py`
- `tests/test_main_window.py`

**Estimated scope:** Medium (3 files)

---

## Checkpoint: Bild-Workflow funktionsfähig

- [x] Bilder lassen sich öffnen, interaktiv in ASCII verwandeln und im Fenster / Vollbild betrachten.
- [x] Alle Tests bestehen.

---

## Task 6: Asynchroner `VideoWorker` (`QThread`)

**Description:** Implementiere einen dedizierten Video-Player-Worker in einem separaten `QThread`. Der Worker dekodiert Frames mittels OpenCV, nutzt die `AsciiConverter`-Engine und sendet die fertigen Frames asynchron via Qt-Signale an die Benutzeroberfläche.

**Acceptance criteria:**

- [x] `VideoWorker` liest Video-Dateien (`.mp4`, `.avi`, `.mov`, `.mkv`) über OpenCV ein.
- [x] Unterstützung für Play, Pause, Stop, Seek (Springen zu Frame) und Loop-Wiedergabe.
- [x] Timer-gesteuerte Frame-Ausgabe entsprechend der Original-FPS des Videos.
- [x] Qt-Signale für `frame_ready(AsciiFrame)`, `progress_changed(int, int)` und `status_changed(bool)`.

**Verification:**

- [x] Tests pass: `uv run pytest tests/test_video_worker.py`
- [x] Build succeeds: `uv run ruff check src/core/video_worker.py`

**Dependencies:** Task 2

**Files likely touched:**

- `src/core/video_worker.py`
- `tests/test_video_worker.py`

**Estimated scope:** Medium (2 files)

---

## Task 7: Video-Player-Steuerung & Timeline

**Description:** Erweitere die Benutzeroberfläche um eine Timeline-Leiste mit Play/Pause-Button, Zeitanzeige, Frame-Scrubber und Schleifen-Umschaltung für geladene Videos.

**Acceptance criteria:**

- [x] Steuerungsleiste erscheint/aktiviert sich automatisch beim Laden einer Videodatei.
- [x] Schieberegler erlaubt ruckelfreies Vor- und Zurückspulen (Scrubben).
- [x] Play/Pause-Button mit Zustandssynchronisation und Leertasten-Shortcut.
- [x] Nahtlose Anpassung der ASCII-Einstellungen während der laufenden Videowiedergabe.

**Verification:**

- [x] Tests pass: `uv run pytest tests/test_video_ui.py`
- [x] Manual check: Videodatei laden, abspielen und durch die Timeline navigieren.

**Dependencies:** Task 5, Task 6

**Files likely touched:**

- `src/ui/playback_bar.py`
- `src/ui/main_window.py`
- `tests/test_video_ui.py`

**Estimated scope:** Medium (3 files)

---

## Checkpoint: Video-Wiedergabe flüssig

- [x] Geladene Videos laufen flüssig im ASCII-Canvas.
- [x] GUI friert beim Abspielen und Scrubben zu keinem Zeitpunkt ein.

---

## Task 8: Export-Engine & Dialoge

**Description:** Implementiere die Export-Funktionen für Bilder (`.txt`, `.png`) und Videos (`.mp4` mit Original-Tonspur via `imageio-ffmpeg`, `.gif`). Erstelle einen Fortschrittsdialog mit Abbruchoption.

**Acceptance criteria:**

- [x] Bildexport: Speichern als Plain-Text `.txt` oder als gerastertes `.png` mit wählbaren Farben.
- [x] Videoexport: Rendern der ASCII-Frames in ein `.mp4`-Video und Muxen der Original-Audiospur via `imageio-ffmpeg`.
- [x] GIF-Export für animierte Clips.
- [x] Modaler Fortschrittsdialog mit Prozentanzeige und "Abbrechen"-Schaltfläche.

**Verification:**

- [x] Tests pass: `uv run pytest tests/test_exporter.py`
- [x] Build succeeds: `uv run ruff check src/core/exporter.py`

**Dependencies:** Task 7

**Files likely touched:**

- `src/core/exporter.py`
- `src/ui/export_dialog.py`
- `tests/test_exporter.py`

**Estimated scope:** Medium to Large (3-4 files)

---

## Task 9: Fehlerbehandlung, Shortcuts & Feinschliff

**Description:** Vollständige Überprüfung aller deutschen UI-Texte, Implementierung globaler Shortcuts (Leertaste, O für Öffnen, S für Speichern, F11 für Vollbild), Abfangen fehlerhafter Mediendateien mit benutzerfreundlichen Dialogen und Durchführung der finalen Test-Suite.

**Acceptance criteria:**

- [x] Aussagekräftige deutsche Fehlermeldungen bei ungültigen Dateien oder Ladefehlern.
- [x] Tastaturkürzel intuitiv benutzbar und in Tooltips/Menüs dokumentiert.
- [x] Keine Ruff-Linter- oder Formatierungsfehler im gesamten Projekt.
- [x] Alle Pytest-Tests laufen erfolgreich durch.

**Verification:**

- [x] Tests pass: `uv run pytest`
- [x] Lint pass: `uv run ruff check .`
- [x] Format pass: `uv run ruff format --check .`

**Dependencies:** Task 8

**Files likely touched:**

- `src/ui/main_window.py`
- `src/main.py`
- `tests/`

**Estimated scope:** Small to Medium (2-3 files)

---

## Checkpoint: Vollständige Anwendung

- [x] Gesamte Testsuite ist grün.
- [x] Vollständiger End-to-End Test für Bild- und Video-Workflow erfolgreich.
