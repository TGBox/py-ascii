"""Bottom playback control bar for video media."""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSlider,
    QVBoxLayout,
    QWidget,
)


class PlaybackBarWidget(QWidget):
    """Widget containing play/pause, timeline scrubber, time label, and loop control."""

    play_toggled = Signal()
    stop_clicked = Signal()
    seek_requested = Signal(int)
    loop_toggled = Signal(bool)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._total_frames: int = 0
        self._fps: float = 30.0
        self._is_scrubbing: bool = False

        self._init_ui()
        self.setEnabled(False)

    def _init_ui(self) -> None:
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(12, 6, 12, 10)
        main_layout.setSpacing(6)

        # Scrubber slider
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(0, 0)
        self.slider.sliderPressed.connect(self._on_slider_pressed)
        self.slider.sliderReleased.connect(self._on_slider_released)
        self.slider.sliderMoved.connect(self._on_slider_moved)
        main_layout.addWidget(self.slider)

        # Controls row
        ctrl_layout = QHBoxLayout()
        ctrl_layout.setSpacing(10)

        self.btn_play = QPushButton("▶ Abspielen")
        self.btn_play.setFixedWidth(110)
        self.btn_play.clicked.connect(self.play_toggled.emit)
        ctrl_layout.addWidget(self.btn_play)

        self.btn_stop = QPushButton("⏹ Stop")
        self.btn_stop.setFixedWidth(80)
        self.btn_stop.clicked.connect(self.stop_clicked.emit)
        ctrl_layout.addWidget(self.btn_stop)

        self.check_loop = QCheckBox("Wiederholen")
        self.check_loop.setChecked(True)
        self.check_loop.toggled.connect(self.loop_toggled.emit)
        ctrl_layout.addWidget(self.check_loop)

        ctrl_layout.addStretch()

        self.label_time = QLabel("00:00 / 00:00")
        ctrl_layout.addWidget(self.label_time)

        main_layout.addLayout(ctrl_layout)

    def set_video_info(self, total_frames: int, fps: float) -> None:
        """Sets the video metadata and activates the playback bar."""
        self._total_frames = max(1, total_frames)
        self._fps = max(1.0, fps)
        self.slider.setRange(0, self._total_frames - 1)
        self.slider.setValue(0)
        self.update_progress(0, self._total_frames)
        self.setEnabled(True)

    def set_playback_state(self, is_playing: bool) -> None:
        """Updates the play/pause button text."""
        if is_playing:
            self.btn_play.setText("⏸ Pause")
        else:
            self.btn_play.setText("▶ Abspielen")

    def update_progress(self, current_frame: int, total_frames: int) -> None:
        """Updates slider position and time readout if not actively scrubbing."""
        if not self._is_scrubbing:
            self.slider.setValue(current_frame)

        cur_sec = int(current_frame / self._fps) if self._fps > 0 else 0
        tot_sec = int(total_frames / self._fps) if self._fps > 0 else 0

        cur_str = f"{cur_sec // 60:02d}:{cur_sec % 60:02d}"
        tot_str = f"{tot_sec // 60:02d}:{tot_sec % 60:02d}"
        self.label_time.setText(f"{cur_str} / {tot_str} (Frame {current_frame}/{total_frames})")

    def _on_slider_pressed(self) -> None:
        self._is_scrubbing = True

    def _on_slider_released(self) -> None:
        self._is_scrubbing = False
        self.seek_requested.emit(self.slider.value())

    def _on_slider_moved(self, value: int) -> None:
        if self._is_scrubbing:
            self.seek_requested.emit(value)

    def reset(self) -> None:
        """Resets playback bar and disables controls."""
        self.slider.setValue(0)
        self.slider.setRange(0, 0)
        self.btn_play.setText("▶ Abspielen")
        self.label_time.setText("00:00 / 00:00")
        self.setEnabled(False)
