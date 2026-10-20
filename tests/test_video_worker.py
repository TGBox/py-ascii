"""Unit tests for the VideoWorker asynchronous player thread."""

import time
from pathlib import Path

import cv2
import numpy as np
from PySide6.QtWidgets import QApplication

from src.core.ascii_converter import AsciiConfig, AsciiFrame
from src.core.video_worker import VideoWorker

_APP = QApplication.instance() or QApplication([])


def _create_dummy_video(path: Path, frame_count: int = 5) -> None:
    """Helper to generate a lightweight video file for testing."""
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(str(path), fourcc, 10.0, (80, 60))
    for i in range(frame_count):
        # Vary color per frame
        frame = np.full((60, 80, 3), (i * 40) % 255, dtype=np.uint8)
        writer.write(frame)
    writer.release()


def test_video_worker_load_and_preview(tmp_path: Path) -> None:
    video_path = tmp_path / "sample.mp4"
    _create_dummy_video(video_path, frame_count=6)

    worker = VideoWorker()
    worker.set_config(AsciiConfig(width=20))

    loaded_data: list[tuple[int, float, int, int]] = []
    frames: list[AsciiFrame] = []

    worker.media_loaded.connect(lambda total, fps, w, h: loaded_data.append((total, fps, w, h)))
    worker.frame_ready.connect(frames.append)

    success = worker.load_video(video_path)
    assert success is True
    assert len(loaded_data) == 1
    total, fps, w, h = loaded_data[0]
    assert total >= 5
    assert fps == 10.0
    assert w == 80
    assert h == 60
    assert len(frames) >= 1  # Preview frame emitted
    assert frames[0].width == 20

    worker.terminate_worker()


def test_video_worker_playback_and_seek(tmp_path: Path) -> None:
    video_path = tmp_path / "sample_playback.mp4"
    _create_dummy_video(video_path, frame_count=8)

    worker = VideoWorker()
    worker.set_config(AsciiConfig(width=15))
    worker.load_video(video_path)

    worker.start()

    received_frames: list[AsciiFrame] = []
    worker.frame_ready.connect(received_frames.append)

    worker.play()
    # Let it play briefly while processing Qt event queue
    start = time.time()
    while time.time() - start < 0.5 and len(received_frames) == 0:
        _APP.processEvents()
        time.sleep(0.02)
    _APP.processEvents()
    worker.pause()

    assert len(received_frames) > 0

    # Test seek
    worker.seek(2)
    start = time.time()
    while time.time() - start < 0.2:
        _APP.processEvents()
        time.sleep(0.02)

    worker.terminate_worker()
