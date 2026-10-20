"""Main application window coordinating canvas, controls, and video playback workflows."""

from pathlib import Path

from PIL import Image, UnidentifiedImageError
from PySide6.QtCore import QByteArray, QSettings, Qt
from PySide6.QtGui import (
    QAction,
    QCloseEvent,
    QColor,
    QDragEnterEvent,
    QDropEvent,
    QKeySequence,
)
from PySide6.QtWidgets import (
    QFileDialog,
    QMainWindow,
    QMessageBox,
    QSplitter,
    QStatusBar,
    QVBoxLayout,
    QWidget,
)

from src.core.ascii_converter import AsciiConverter, ColorMode
from src.core.video_worker import VideoWorker
from src.ui.canvas import AsciiCanvasWidget
from src.ui.controls import ControlsWidget
from src.ui.export_dialog import ExportDialog
from src.ui.playback_bar import PlaybackBarWidget
from src.ui.theme import apply_theme

SUPPORTED_IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".gif"}
SUPPORTED_VIDEO_EXTS = {".mp4", ".avi", ".mov", ".mkv"}


class MainWindow(QMainWindow):
    """Main application window for py-ascii."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("py-ascii — Bild & Video zu ASCII Kunst")
        self.setAcceptDrops(True)

        self._current_theme = "dark"
        self._current_file_path: Path | None = None
        self._loaded_image: Image.Image | None = None

        # Asynchronous video player thread (started on demand)
        self.video_worker = VideoWorker(self)

        self._init_ui()
        self._init_menu()
        self._init_video_signals()
        self._restore_settings()

    def _init_ui(self) -> None:
        self.statusBar = QStatusBar(self)
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("Bereit. Ziehe eine Bild- oder Videodatei in das Fenster.")

        # Splitter dividing canvas/player and sidebar
        splitter = QSplitter(Qt.Orientation.Horizontal, self)

        # Center canvas container with bottom playback bar
        canvas_container = QWidget(self)
        canvas_layout = QVBoxLayout(canvas_container)
        canvas_layout.setContentsMargins(0, 0, 0, 0)
        canvas_layout.setSpacing(0)

        self.canvas = AsciiCanvasWidget(canvas_container)
        canvas_layout.addWidget(self.canvas, 1)

        self.playback_bar = PlaybackBarWidget(canvas_container)
        canvas_layout.addWidget(self.playback_bar, 0)

        splitter.addWidget(canvas_container)

        # Right controls sidebar
        self.controls = ControlsWidget(self)
        self.controls.setFixedWidth(310)
        splitter.addWidget(self.controls)

        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 0)
        self.setCentralWidget(splitter)

        # Connect controls signals
        self.controls.config_changed.connect(self._on_config_changed)
        self.controls.open_file_requested.connect(self.prompt_open_file)
        self.controls.export_requested.connect(self.prompt_export)
        self.controls.theme_changed.connect(self.set_theme)

    def _init_menu(self) -> None:
        menubar = self.menuBar()

        # File menu
        menu_file = menubar.addMenu("Datei")

        action_open = QAction("Datei öffnen...", self)
        action_open.setShortcut(QKeySequence.StandardKey.Open)
        action_open.triggered.connect(self.prompt_open_file)
        menu_file.addAction(action_open)

        action_export = QAction("Exportieren...", self)
        action_export.setShortcut(QKeySequence.StandardKey.Save)
        action_export.triggered.connect(self.prompt_export)
        menu_file.addAction(action_export)

        menu_file.addSeparator()

        action_exit = QAction("Beenden", self)
        action_exit.setShortcut(QKeySequence.StandardKey.Quit)
        action_exit.triggered.connect(self.close)
        menu_file.addAction(action_exit)

        # View menu
        menu_view = menubar.addMenu("Ansicht")

        self.action_fullscreen = QAction("Vollbild", self)
        self.action_fullscreen.setShortcut(Qt.Key.Key_F11)
        self.action_fullscreen.triggered.connect(self.toggle_fullscreen)
        menu_view.addAction(self.action_fullscreen)

        action_fit = QAction("Auf Fenster einpassen", self)
        action_fit.setCheckable(True)
        action_fit.setChecked(True)
        action_fit.triggered.connect(self.canvas.set_fit_to_window)
        menu_view.addAction(action_fit)

        menu_view.addSeparator()

        action_zoom_in = QAction("Zoom vergrößern", self)
        action_zoom_in.setShortcut(QKeySequence.StandardKey.ZoomIn)
        action_zoom_in.triggered.connect(self._zoom_in)
        menu_view.addAction(action_zoom_in)

        action_zoom_out = QAction("Zoom verkleinern", self)
        action_zoom_out.setShortcut(QKeySequence.StandardKey.ZoomOut)
        action_zoom_out.triggered.connect(self._zoom_out)
        menu_view.addAction(action_zoom_out)

        action_zoom_reset = QAction("Zoom zurücksetzen", self)
        action_zoom_reset.setShortcut("Ctrl+0")
        action_zoom_reset.triggered.connect(self._zoom_reset)
        menu_view.addAction(action_zoom_reset)

        # Help menu
        menu_help = menubar.addMenu("Hilfe")
        action_about = QAction("Über py-ascii", self)
        action_about.triggered.connect(self._show_about_dialog)
        menu_help.addAction(action_about)

    def _zoom_in(self) -> None:
        self.canvas.set_zoom_factor(self.canvas._zoom_factor * 1.15)

    def _zoom_out(self) -> None:
        self.canvas.set_zoom_factor(self.canvas._zoom_factor / 1.15)

    def _zoom_reset(self) -> None:
        self.canvas.set_zoom_factor(1.0)

    def _init_video_signals(self) -> None:
        """Connects VideoWorker signals to canvas and playback bar."""
        self.video_worker.frame_ready.connect(self.canvas.set_frame)
        self.video_worker.progress_changed.connect(self.playback_bar.update_progress)
        self.video_worker.state_changed.connect(self.playback_bar.set_playback_state)
        self.video_worker.media_loaded.connect(self._on_video_loaded)
        self.video_worker.error_occurred.connect(self._on_video_error)

        self.playback_bar.play_toggled.connect(self.video_worker.toggle_play)
        self.playback_bar.stop_clicked.connect(self.video_worker.stop)
        self.playback_bar.seek_requested.connect(self.video_worker.seek)
        self.playback_bar.loop_toggled.connect(self.video_worker.set_loop)

    def _on_video_loaded(self, total_frames: int, fps: float, w: int, h: int) -> None:
        """Handles video loaded event."""
        self.playback_bar.set_video_info(total_frames, fps)
        filename = self._current_file_path.name if self._current_file_path else "Video"
        self.statusBar.showMessage(
            f"Video geladen: {filename} ({w}x{h}px, {total_frames} Frames, {fps:.1f} FPS)"
        )

    def _on_video_error(self, message: str) -> None:
        """Displays error when video loading/playback fails."""
        QMessageBox.warning(self, "Videofehler", message)

    def set_theme(self, theme: str) -> None:
        """Applies theme stylesheet to the window and updates colors."""
        self._current_theme = theme
        apply_theme(self, theme)

    def toggle_fullscreen(self) -> None:
        """Toggles between fullscreen and normal window state."""
        if self.isFullScreen():
            self.showNormal()
            self.action_fullscreen.setText("Vollbild")
        else:
            self.showFullScreen()
            self.action_fullscreen.setText("Fenstermodus")

    def prompt_open_file(self) -> None:
        """Opens a file dialog to select image or video files."""
        file_filter = (
            "Alle unterstützten Medien (*.png *.jpg *.jpeg *.webp *.bmp *.mp4 *.avi *.mov *.mkv);;"
            "Bilder (*.png *.jpg *.jpeg *.webp *.bmp);;"
            "Videos (*.mp4 *.avi *.mov *.mkv);;"
            "Alle Dateien (*.*)"
        )
        selected_file, _ = QFileDialog.getOpenFileName(
            self,
            "Bild- oder Videodatei öffnen",
            "",
            file_filter,
        )
        if selected_file:
            self.open_media(Path(selected_file))

    def prompt_export(self) -> None:
        """Opens the export dialog for the current media."""
        video_path = None
        if (
            self._current_file_path
            and self._current_file_path.suffix.lower() in SUPPORTED_VIDEO_EXTS
        ):
            video_path = self._current_file_path

        dialog = ExportDialog(
            config=self.controls.get_config(),
            current_image=self._loaded_image,
            current_video_path=video_path,
            current_frame=self.canvas.get_frame(),
            parent=self,
        )
        dialog.exec()

    def open_media(self, file_path: Path) -> None:
        """Loads and processes the given media file path."""
        if not file_path.exists():
            QMessageBox.warning(
                self, "Datei nicht gefunden", f"Die Datei '{file_path}' existiert nicht."
            )
            return

        ext = file_path.suffix.lower()
        if ext in SUPPORTED_IMAGE_EXTS:
            self._load_image(file_path)
        elif ext in SUPPORTED_VIDEO_EXTS:
            self._load_video(file_path)
        else:
            QMessageBox.warning(
                self,
                "Nicht unterstütztes Format",
                f"Das Dateiformat '{ext}' wird nicht unterstützt.",
            )

    def _load_image(self, file_path: Path) -> None:
        """Loads a static image and renders its ASCII representation."""
        # Pause video if active
        self.video_worker.pause()
        self.playback_bar.reset()

        try:
            img = Image.open(file_path)
            img.load()
            self._loaded_image = img
            self._current_file_path = file_path
            self._recompute_ascii()

            orig_w, orig_h = img.size
            self.statusBar.showMessage(f"Bild geladen: {file_path.name} ({orig_w}x{orig_h}px)")
        except (UnidentifiedImageError, OSError) as exc:
            QMessageBox.critical(
                self,
                "Fehler beim Laden",
                f"Das Bild konnte nicht geladen werden:\n{exc}",
            )

    def _load_video(self, file_path: Path) -> None:
        """Loads video file into worker thread and activates player controls."""
        self._loaded_image = None
        self._current_file_path = file_path

        # Synchronize canvas colors
        config = self.controls.get_config()
        self.canvas.set_colors(QColor(*config.bg_color), QColor(*config.fg_color))
        self.video_worker.set_config(config)

        if not self.video_worker.isRunning():
            self.video_worker.start()
        self.video_worker.load_video(file_path)

    def _on_config_changed(self) -> None:
        """Triggered when parameters in the controls sidebar change."""
        self._recompute_ascii()

    def _recompute_ascii(self) -> None:
        """Applies configuration changes to the current static image or video."""
        config = self.controls.get_config()

        bg_col = QColor(*config.bg_color)
        fg_col = QColor(*config.fg_color)
        self.canvas.set_colors(bg_col, fg_col)

        if self._loaded_image is not None:
            frame = AsciiConverter.convert(self._loaded_image, config)
            self.canvas.set_frame(frame)
            mode_str = "RGB" if config.color_mode == ColorMode.RGB else "Monochrom"
            self.statusBar.showMessage(
                f"Bild: {self._current_file_path.name if self._current_file_path else ''} | "
                f"ASCII: {frame.width}x{frame.height} Zeichen ({mode_str})"
            )
        elif self._current_file_path is not None:
            # Video mode: update worker settings and refresh current frame
            self.video_worker.set_config(config)
            if not self.video_worker._is_playing and self.playback_bar.isEnabled():
                self.video_worker.seek(self.playback_bar.slider.value())

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        """Accepts drag events containing supported media files."""
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if urls:
                path = Path(urls[0].toLocalFile())
                ext = path.suffix.lower()
                if ext in SUPPORTED_IMAGE_EXTS or ext in SUPPORTED_VIDEO_EXTS:
                    event.acceptProposedAction()
                    return
        event.ignore()

    def dropEvent(self, event: QDropEvent) -> None:
        """Handles dropped media file."""
        urls = event.mimeData().urls()
        if urls:
            file_path = Path(urls[0].toLocalFile())
            self.open_media(file_path)
            event.acceptProposedAction()

    def keyPressEvent(self, event) -> None:
        """Handles global keyboard shortcuts."""
        if event.key() == Qt.Key.Key_F11:
            self.toggle_fullscreen()
            event.accept()
        elif event.key() == Qt.Key.Key_Space and self.playback_bar.isEnabled():
            self.video_worker.toggle_play()
            event.accept()
        elif event.key() == Qt.Key.Key_Left and self.playback_bar.isEnabled():
            cur = self.playback_bar.slider.value()
            self.video_worker.seek(max(0, cur - 10))
            event.accept()
        elif event.key() == Qt.Key.Key_Right and self.playback_bar.isEnabled():
            cur = self.playback_bar.slider.value()
            self.video_worker.seek(cur + 10)
            event.accept()
        else:
            super().keyPressEvent(event)

    def _restore_settings(self) -> None:
        """Restores window size and position from persistent settings."""
        settings = QSettings("py-ascii", "py-ascii")
        geom = settings.value("geometry")
        if isinstance(geom, QByteArray) and not geom.isEmpty():
            self.restoreGeometry(geom)
        else:
            self.resize(1024, 700)

        saved_theme = settings.value("theme", "dark")
        self.set_theme(str(saved_theme))

    def closeEvent(self, event: QCloseEvent) -> None:
        """Persists window geometry and state on application exit and cleans up threads."""
        if self.video_worker.isRunning():
            self.video_worker.terminate_worker()

        settings = QSettings("py-ascii", "py-ascii")
        settings.setValue("geometry", self.saveGeometry())
        settings.setValue("windowState", self.saveState())
        settings.setValue("theme", self._current_theme)
        super().closeEvent(event)

    def _show_about_dialog(self) -> None:
        """Displays dialog with application info."""
        QMessageBox.about(
            self,
            "Über py-ascii",
            "<h3>py-ascii v0.2.0</h3>"
            "<p>Ein modernes Werkzeug zur Umwandlung von Bildern und Videos in ASCII-Kunst.</p>"
            "<p>Erstellt mit PySide6, OpenCV und NumPy.</p>",
        )
