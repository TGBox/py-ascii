# Task List: py-ascii Desktop App

## Task 1: Abhängigkeiten & Projekt-Setup

**Description:** Installiere die erforderlichen Kernbibliotheken (`numpy`, `opencv-python`, `pillow`, `imageio-ffmpeg`) über `uv add` und stelle sicher, dass die Entwicklungs- und Testwerkzeuge (`pytest`, `ruff`) im Projekt einsatzbereit sind.

**Acceptance criteria:**

- [ ] `pyproject.toml` enthält `numpy`, `opencv-python`, `pillow`, `imageio-ffmpeg` unter den Abhängigkeiten.
- [ ] Die virtuelle Umgebung wird via `uv sync` aktualisiert und die Pakete lassen sich importieren.

**Verification:**

- [ ] Tests pass: `uv run python -c "import cv2, numpy, PIL, imageio_ffmpeg, PySide6; print('OK')"`
- [ ] Build succeeds: `uv run ruff check`

**Dependencies:** None

**Files likely touched:**

- `pyproject.toml`
- `uv.lock`

**Estimated scope:** Small (1-2 files)

---

## Task 2: Vektorisierte ASCII-Engine (`AsciiConverter`)

**Description:** Erstelle das Kernmodul zur Konvertierung von Bilddaten (NumPy-Arrays / PIL-Images) in ASCII-Kunst. Implementiere Datenklassen für die Konfiguration (`AsciiConfig`) und das Ergebnis (`AsciiFrame`), inklusive Zeichenzuordnung, Luminanzberechnung, Farbmatrix und Tests.

**Acceptance criteria:**

- [ ] Datenklassen `AsciiConfig` (Breite, Seitenverhältnis, Zeichensatz, Kontrast, Helligkeit, Farbmodus) und `AsciiFrame` (Zeichenmatrix, Farbdaten, Plaintext).
- [ ] Schnelle NumPy-basierte Vektorisierung für Graustufen- und Vollfarb-Umwandlung.
- [ ] Zuverlässige Berücksichtigung von Zeichen-Seitenverhältnissen (Monospace).
- [ ] Ausführliche Unit-Tests in `tests/test_ascii_converter.py`.

**Verification:**

- [ ] Tests pass: `uv run pytest tests/test_ascii_converter.py`
- [ ] Build succeeds: `uv run ruff check src/core/`

**Dependencies:** Task 1

**Files likely touched:**

- `src/core/__init__.py`
- `src/core/ascii_converter.py`
- `tests/test_ascii_converter.py`

**Estimated scope:** Medium (3 files)

---

## Checkpoint: Foundation

- [ ] `uv run pytest` läuft fehlerfrei durch.
- [ ] Die Core-Engine konvertiert Bilder zuverlässig in Millisekunden.

---

## Task 3: Performantes `AsciiCanvasWidget` (`QPainter`)

**Description:** Entwickle ein spezialisiertes Qt-Widget (`AsciiCanvasWidget`), das ein `AsciiFrame` über `QPainter` hardwarebeschleunigt auf den Bildschirm zeichnet. Unterstütze Vollfarb-RGB- und Monochrom-Modi sowie automatische Skalierung (Fit-to-Window).

**Acceptance criteria:**

- [ ] `AsciiCanvasWidget` rendert Monochrom- und RGB-Zeichen sauber mit Monospace-Schriftart.
- [ ] Hintergrund- und Textfarben im Monochrom-Modus frei konfigurierbar (z. B. Matrix-Grün).
- [ ] Automatisches Zentrieren und Skalieren bei Größenänderungen des Fensters.
- [ ] Zoom-Faktor und Ansichtsoptionen (Originalgröße / Einpassen).

**Verification:**

- [ ] Tests pass: `uv run pytest tests/test_canvas.py`
- [ ] Build succeeds: `uv run ruff check src/ui/canvas.py`

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

- [ ] Schieberegler für Auflösung (Spalten), Seitenverhältnis-Korrektur, Helligkeit und Kontrast mit Werteanzeige.
- [ ] Dropdown für Zeichensatz-Presets (Standard, Dicht, Blöcke) und Eingabefeld für eigenen Zeichensatz.
- [ ] Farbmodus-Umschalter (Vollfarb-RGB vs. Monochrom) mit Farbwahl-Dialogen.
- [ ] Dark- und Light-Theme QSS-Stylesheets gemäß Desktop-Konventionen.

**Verification:**

- [ ] Tests pass: `uv run pytest tests/test_controls.py`
- [ ] Build succeeds: `uv run ruff check src/ui/`

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

- [ ] Bilder können via Menü, Button oder Drag-and-Drop geladen werden.
- [ ] Änderungen an den Reglern im Einstellungs-Panel aktualisieren das Bild in Echtzeit.
- [ ] Vollbildmodus via Taste `F11` umschaltbar.
- [ ] Fenstergröße und -position werden beim Beenden in `QSettings` gesichert und beim Neustart wiederhergestellt.

**Verification:**

- [ ] Tests pass: `uv run pytest tests/test_main_window.py`
- [ ] Manual check: Starten via `uv run py-ascii`, Bild hineinziehen, Parameter testen.

**Dependencies:** Task 4

**Files likely touched:**

- `src/ui/main_window.py`
- `src/main.py`
- `tests/test_main_window.py`

**Estimated scope:** Medium (3 files)

---

## Checkpoint: Bild-Workflow funktionsfähig

- [ ] Bilder lassen sich öffnen, interaktiv in ASCII verwandeln und im Fenster / Vollbild betrachten.
- [ ] Alle Tests bestehen.

---

## Task 6: Asynchroner `VideoWorker` (`QThread`)

**Description:** Implementiere einen dedizierten Video-Player-Worker in einem separaten `QThread`. Der Worker dekodiert Frames mittels OpenCV, nutzt die `AsciiConverter`-Engine und sendet die fertigen Frames asynchron via Qt-Signale an die Benutzeroberfläche.

**Acceptance criteria:**

- [ ] `VideoWorker` liest Video-Dateien (`.mp4`, `.avi`, `.mov`, `.mkv`) über OpenCV ein.
- [ ] Unterstützung für Play, Pause, Stop, Seek (Springen zu Frame) und Loop-Wiedergabe.
- [ ] Timer-gesteuerte Frame-Ausgabe entsprechend der Original-FPS des Videos.
- [ ] Qt-Signale für `frame_ready(AsciiFrame)`, `progress_changed(int, int)` und `status_changed(bool)`.

**Verification:**

- [ ] Tests pass: `uv run pytest tests/test_video_worker.py`
- [ ] Build succeeds: `uv run ruff check src/core/video_worker.py`

**Dependencies:** Task 2

**Files likely touched:**

- `src/core/video_worker.py`
- `tests/test_video_worker.py`

**Estimated scope:** Medium (2 files)

---

## Task 7: Video-Player-Steuerung & Timeline

**Description:** Erweitere die Benutzeroberfläche um eine Timeline-Leiste mit Play/Pause-Button, Zeitanzeige, Frame-Scrubber und Schleifen-Umschaltung für geladene Videos.

**Acceptance criteria:**

- [ ] Steuerungsleiste erscheint/aktiviert sich automatisch beim Laden einer Videodatei.
- [ ] Schieberegler erlaubt ruckelfreies Vor- und Zurückspulen (Scrubben).
- [ ] Play/Pause-Button mit Zustandssynchronisation und Leertasten-Shortcut.
- [ ] Nahtlose Anpassung der ASCII-Einstellungen während der laufenden Videowiedergabe.

**Verification:**

- [ ] Tests pass: `uv run pytest tests/test_video_ui.py`
- [ ] Manual check: Videodatei laden, abspielen und durch die Timeline navigieren.

**Dependencies:** Task 5, Task 6

**Files likely touched:**

- `src/ui/playback_bar.py`
- `src/ui/main_window.py`
- `tests/test_video_ui.py`

**Estimated scope:** Medium (3 files)

---

## Checkpoint: Video-Wiedergabe flüssig

- [ ] Geladene Videos laufen flüssig im ASCII-Canvas.
- [ ] GUI friert beim Abspielen und Scrubben zu keinem Zeitpunkt ein.

---

## Task 8: Export-Engine & Dialoge

**Description:** Implementiere die Export-Funktionen für Bilder (`.txt`, `.png`) und Videos (`.mp4` mit Original-Tonspur via `imageio-ffmpeg`, `.gif`). Erstelle einen Fortschrittsdialog mit Abbruchoption.

**Acceptance criteria:**

- [ ] Bildexport: Speichern als Plain-Text `.txt` oder als gerastertes `.png` mit wählbaren Farben.
- [ ] Videoexport: Rendern der ASCII-Frames in ein `.mp4`-Video und Muxen der Original-Audiospur via `imageio-ffmpeg`.
- [ ] GIF-Export für animierte Clips.
- [ ] Modaler Fortschrittsdialog mit Prozentanzeige und "Abbrechen"-Schaltfläche.

**Verification:**

- [ ] Tests pass: `uv run pytest tests/test_exporter.py`
- [ ] Build succeeds: `uv run ruff check src/core/exporter.py`

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

- [ ] Aussagekräftige deutsche Fehlermeldungen bei ungültigen Dateien oder Ladefehlern.
- [ ] Tastaturkürzel intuitiv benutzbar und in Tooltips/Menüs dokumentiert.
- [ ] Keine Ruff-Linter- oder Formatierungsfehler im gesamten Projekt.
- [ ] Alle Pytest-Tests laufen erfolgreich durch.

**Verification:**

- [ ] Tests pass: `uv run pytest`
- [ ] Lint pass: `uv run ruff check .`
- [ ] Format pass: `uv run ruff format --check .`

**Dependencies:** Task 8

**Files likely touched:**

- `src/ui/main_window.py`
- `src/main.py`
- `tests/`

**Estimated scope:** Small to Medium (2-3 files)

---

## Checkpoint: Vollständige Anwendung

- [ ] Gesamte Testsuite ist grün.
- [ ] Vollständiger End-to-End Test für Bild- und Video-Workflow erfolgreich.
