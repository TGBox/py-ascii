# Statement of Intent: py-ascii Desktop App

## Outcome

Eine moderne PySide6-Desktop-App zur interaktiven Konvertierung von Bildern und Videos in ASCII-Art mit Live-Vorschau (sowohl Vollfarb-RGB als auch Retro-Monochrom) und vielseitigen Exportfunktionen.

## User

Der Entwickler/Anwender selbst, um schnell, visuell ansprechend und intuitiv Bilder und Videoclips in ASCII-Kunst umzuwandeln, zu experimentieren und Ergebnisse für Social Media oder Retro-Projekte zu teilen.

## Why Now

Ein visuelles Desktop-Tool mit sofortigem Schieberegler-Feedback (Auflösung, Zeichensatz, Kontrast, Farbfilter) und integriertem Videoplayer bietet ein Vielfaches an Bedienkomfort und Experimentierfreude gegenüber starren CLI-Skripten oder langsamen Web-Tools.

## Success Criteria

- Bilder und Videos können komfortabel via Dateidialog oder Drag-and-Drop geladen werden.
- Flüssige Live-Vorschau/Wiedergabe mit anpassbaren Parametern (Auflösung, Zeichenbreite/Höhenverhältnis, Zeichenmenge, Helligkeit/Kontrast).
- Zwei Haupt-Rendering-Modi:
  - **Vollfarb-RGB**: Zeichen übernehmen die Original-Farben der Pixel.
  - **Retro-Monochrom**: Klassischer Schwarz-Weiß- oder Terminal-Look (Matrix-Grün, Amber, frei wählbare Text- und Hintergrundfarben).
- Zuverlässiger Export:
  - Bilder als reine Textdatei (`.txt`) oder gerendertes Bild (`.png`).
  - Videos als `.mp4` (unter Beibehaltung der Original-Audiospur) sowie animiertes `.gif`.

## Constraints

- **Performance**: Flüssige Frame-Berechnung bei Videowiedergabe ohne Blockieren der GUI (Nutzung von `QThread`/Workern, NumPy-Vektorisierung und OpenCV).
- **Projekt-Richtlinien**:
  - Python 3.12+ mit `uv` als Paketmanager.
  - Deutsche Benutzeroberfläche (Texte, Dialoge, Fehlermeldungen) bei englischem Quellcode.
  - Responsive Fenster- und Vollbildunterstützung (F11), Fenstergeometrie-Persistenz via `QSettings`.
  - Konsistentes modernes Styling mit Hell- und Dunkelmodus (Dark / Light Theme).

## Out of Scope

- Echtzeit-Audiosynchronisation während der Live-Vorschau in der GUI (visueller Fokus; Audio wird erst beim finalen Video-Export eingebunden).
- Umfangreiche Videoschnitt-Funktionen (Timeline-Trimming, Multi-Track, Filterketten).
- Webcam-Live-Stream für den ersten Wurf (Architektur modular halten, damit dies später nachrüstbar ist).
