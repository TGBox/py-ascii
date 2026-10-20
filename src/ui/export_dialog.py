"""Export dialog managing format selection, file paths, and background progress."""

from pathlib import Path

from PIL import Image
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QButtonGroup,
    QDialog,
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QRadioButton,
    QVBoxLayout,
    QWidget,
)

from src.core.ascii_converter import AsciiConfig, AsciiFrame
from src.core.exporter import VideoExportWorker, export_image_png, export_image_txt


class ExportDialog(QDialog):
    """Modal dialog for exporting ASCII art to various image and video formats."""

    def __init__(
        self,
        config: AsciiConfig,
        current_image: Image.Image | None = None,
        current_video_path: Path | None = None,
        current_frame: AsciiFrame | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle("ASCII Kunst exportieren")
        self.setMinimumWidth(420)

        self._config = config
        self._image = current_image
        self._video_path = current_video_path
        self._frame = current_frame
        self._worker: VideoExportWorker | None = None

        self._init_ui()

    def _init_ui(self) -> None:
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(14)

        if self._image is None and self._video_path is None:
            lbl = QLabel("Es ist aktuell kein Bild oder Video zum Exportieren geladen.")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            main_layout.addWidget(lbl)
            btn_close = QPushButton("Schließen")
            btn_close.clicked.connect(self.reject)
            main_layout.addWidget(btn_close)
            return

        is_video = self._video_path is not None

        # Format Selection
        format_group = QGroupBox("Export-Format auswählen")
        format_layout = QVBoxLayout(format_group)
        self._btn_group = QButtonGroup(self)

        if is_video:
            self._radio_mp4 = QRadioButton("MP4-Video (mit erhaltener Tonspur)")
            self._radio_mp4.setChecked(True)
            self._radio_gif = QRadioButton("Animiertes GIF")
            self._btn_group.addButton(self._radio_mp4)
            self._btn_group.addButton(self._radio_gif)
            format_layout.addWidget(self._radio_mp4)
            format_layout.addWidget(self._radio_gif)
        else:
            self._radio_png = QRadioButton("PNG-Bild (*.png)")
            self._radio_png.setChecked(True)
            self._radio_txt = QRadioButton("Reine Textdatei (*.txt)")
            self._btn_group.addButton(self._radio_png)
            self._btn_group.addButton(self._radio_txt)
            format_layout.addWidget(self._radio_png)
            format_layout.addWidget(self._radio_txt)

        main_layout.addWidget(format_group)

        # Progress Section (for videos)
        self._progress_bar = QProgressBar()
        self._progress_bar.setRange(0, 100)
        self._progress_bar.setValue(0)
        self._progress_bar.setVisible(False)
        main_layout.addWidget(self._progress_bar)

        self._status_label = QLabel("")
        self._status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._status_label.setVisible(False)
        main_layout.addWidget(self._status_label)

        # Action Buttons
        btn_layout = QHBoxLayout()
        self._btn_cancel = QPushButton("Abbrechen")
        self._btn_cancel.clicked.connect(self._on_cancel_clicked)
        btn_layout.addWidget(self._btn_cancel)

        self._btn_export = QPushButton("Speichern unter...")
        self._btn_export.setObjectName("primaryButton")
        self._btn_export.clicked.connect(self._on_export_clicked)
        btn_layout.addWidget(self._btn_export)

        main_layout.addLayout(btn_layout)

    def _on_export_clicked(self) -> None:
        if self._video_path is not None:
            self._start_video_export()
        elif self._image is not None and self._frame is not None:
            self._start_image_export()

    def _start_image_export(self) -> None:
        is_txt = self._radio_txt.isChecked()
        filter_str = "Textdatei (*.txt)" if is_txt else "PNG-Bild (*.png)"
        default_name = "ascii_art.txt" if is_txt else "ascii_art.png"

        save_path, _ = QFileDialog.getSaveFileName(
            self,
            "ASCII-Bild speichern",
            default_name,
            filter_str,
        )
        if not save_path:
            return

        dest = Path(save_path)
        try:
            if is_txt:
                export_image_txt(self._frame, dest)
            else:
                export_image_png(self._frame, dest, self._config)
            QMessageBox.information(
                self,
                "Export erfolgreich",
                f"Die Datei wurde erfolgreich gespeichert:\n{dest.name}",
            )
            self.accept()
        except Exception as exc:  # noqa: BLE001
            QMessageBox.critical(
                self,
                "Exportfehler",
                f"Beim Speichern ist ein Fehler aufgetreten:\n{exc}",
            )

    def _start_video_export(self) -> None:
        assert self._video_path is not None
        is_gif = self._radio_gif.isChecked()
        fmt = "gif" if is_gif else "mp4"
        filter_str = "Animiertes GIF (*.gif)" if is_gif else "MP4-Video (*.mp4)"
        default_name = f"ascii_{self._video_path.stem}.{fmt}"

        save_path, _ = QFileDialog.getSaveFileName(
            self,
            "ASCII-Video exportieren",
            default_name,
            filter_str,
        )
        if not save_path:
            return

        dest = Path(save_path)

        # Configure UI for active export
        self._progress_bar.setVisible(True)
        self._progress_bar.setValue(0)
        self._status_label.setVisible(True)
        self._status_label.setText("Export wird vorbereitet...")
        self._btn_export.setEnabled(False)

        self._worker = VideoExportWorker(
            input_video_path=self._video_path,
            output_path=dest,
            config=self._config,
            format_type=fmt,
            parent=self,
        )
        self._worker.progress.connect(self._on_worker_progress)
        self._worker.finished.connect(self._on_worker_finished)
        self._worker.failed.connect(self._on_worker_failed)
        self._worker.cancelled.connect(self._on_worker_cancelled)
        self._worker.start()

    def _on_worker_progress(self, ratio: float, text: str) -> None:
        self._progress_bar.setValue(int(ratio * 100))
        self._status_label.setText(text)

    def _on_worker_finished(self, out_path: Path) -> None:
        self._progress_bar.setValue(100)
        self._status_label.setText("Fertig!")
        QMessageBox.information(
            self,
            "Export abgeschlossen",
            f"Das Video wurde erfolgreich gespeichert unter:\n{out_path}",
        )
        self.accept()

    def _on_worker_failed(self, error_msg: str) -> None:
        self._btn_export.setEnabled(True)
        self._status_label.setText("Export fehlgeschlagen.")
        QMessageBox.critical(
            self,
            "Exportfehler",
            f"Beim Exportieren ist ein Fehler aufgetreten:\n{error_msg}",
        )

    def _on_worker_cancelled(self) -> None:
        self._status_label.setText("Export abgebrochen.")
        self._btn_export.setEnabled(True)
        QMessageBox.information(self, "Abgebrochen", "Der Export wurde abgebrochen.")

    def _on_cancel_clicked(self) -> None:
        if self._worker is not None and self._worker.isRunning():
            self._worker.cancel()
        else:
            self.reject()

    def closeEvent(self, event) -> None:
        if self._worker is not None and self._worker.isRunning():
            self._worker.cancel()
            self._worker.wait(1000)
        super().closeEvent(event)
