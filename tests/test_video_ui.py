"""Unit tests for PlaybackBarWidget and MainWindow video integration."""

import time
from pathlib import Path

import cv2
import numpy as np
from PySide6.QtWidgets import QApplication

from src.ui.main_window import MainWindow
from src.ui.playback_bar import PlaybackBarWidget

_APP = QApplication.instance() or QApplication([])


def _create_dummy_video(path: Path, frame_count: int = 10) -> None:
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(str(path), fourcc, 15.0, (80, 60))
    for i in range(frame_count):
        frame = np.full((60, 80, 3), (i * 25) % 255, dtype=np.uint8)
        writer.write(frame)
    writer.release()


def test_playback_bar_standalone() -> None:
    bar = PlaybackBarWidget()
    assert not bar.isEnabled()

    bar.set_video_info(100, 25.0)
    assert bar.isEnabled()
    assert bar.slider.maximum() == 99

    bar.set_playback_state(True)
    assert "Pause" in bar.btn_play.text()

    bar.set_playback_state(False)
    assert "Abspielen" in bar.btn_play.text()

    seek_values: list[int] = []
    bar.seek_requested.connect(seek_values.append)
    bar.slider.setValue(42)
    bar._on_slider_pressed()
    bar._on_slider_released()
    assert 42 in seek_values

    bar.reset()
    assert not bar.isEnabled()


def test_main_window_video_loading(tmp_path: Path) -> None:
    video_path = tmp_path / "test_clip.mp4"
    _create_dummy_video(video_path, frame_count=12)

    window = MainWindow()
    assert not window.playback_bar.isEnabled()

    window.open_media(video_path)
    # Pump Qt events to let worker emit loaded signals
    start = time.time()
    while time.time() - start < 0.5 and not window.playback_bar.isEnabled():
        _APP.processEvents()
        time.sleep(0.02)
    _APP.processEvents()

    assert window.playback_bar.isEnabled()
    assert window.canvas.get_frame() is not None
    assert window.playback_bar.slider.maximum() >= 10

    # Test toggling play via space key press simulation
    from PySide6.QtCore import Qt
    from PySide6.QtGui import QKeyEvent

    space_event = QKeyEvent(
        QKeyEvent.Type.KeyPress, Qt.Key.Key_Space, Qt.KeyboardModifier.NoModifier
    )
    window.keyPressEvent(space_event)
    _APP.processEvents()

    window.close()
