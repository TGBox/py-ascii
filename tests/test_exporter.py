"""Unit tests for exporter module and export dialog."""

import time
from pathlib import Path

import cv2
import numpy as np
from PIL import Image
from PySide6.QtWidgets import QApplication

from src.core.ascii_converter import AsciiConfig, AsciiFrame
from src.core.exporter import (
    VideoExportWorker,
    export_image_png,
    export_image_txt,
    render_frame_to_image,
)
from src.ui.export_dialog import ExportDialog

_APP = QApplication.instance() or QApplication([])


def _create_dummy_video(path: Path, frame_count: int = 5) -> None:
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(str(path), fourcc, 10.0, (60, 40))
    for i in range(frame_count):
        frame = np.full((40, 60, 3), (i * 50) % 255, dtype=np.uint8)
        writer.write(frame)
    writer.release()


def test_export_image_txt(tmp_path: Path) -> None:
    frame = AsciiFrame(chars=["Line 1", "Line 2"], colors=None, width=6, height=2)
    out_txt = tmp_path / "art.txt"
    export_image_txt(frame, out_txt)

    assert out_txt.exists()
    content = out_txt.read_text(encoding="utf-8")
    assert content == "Line 1\nLine 2"


def test_export_image_png(tmp_path: Path) -> None:
    frame = AsciiFrame(chars=["@@@@", "####"], colors=None, width=4, height=2)
    config = AsciiConfig(width=4)
    out_png = tmp_path / "art.png"
    export_image_png(frame, out_png, config)

    assert out_png.exists()
    img = Image.open(out_png)
    assert img.size[0] > 0
    assert img.size[1] > 0


def test_render_frame_to_image_rgb() -> None:
    colors = np.zeros((2, 3, 3), dtype=np.uint8)
    colors[0, 0] = [255, 0, 0]
    frame = AsciiFrame(chars=["ABC", "DEF"], colors=colors, width=3, height=2)
    config = AsciiConfig()
    img = render_frame_to_image(frame, config)
    assert img.size[0] == 3 * 8
    assert img.size[1] == 2 * 14


def test_video_export_gif(tmp_path: Path) -> None:
    in_video = tmp_path / "in.mp4"
    out_gif = tmp_path / "out.gif"
    _create_dummy_video(in_video, frame_count=4)

    config = AsciiConfig(width=10)
    worker = VideoExportWorker(in_video, out_gif, config, format_type="gif")

    finished_paths: list[Path] = []
    worker.finished.connect(finished_paths.append)
    worker.start()

    start = time.time()
    while time.time() - start < 5.0 and len(finished_paths) == 0:
        _APP.processEvents()
        time.sleep(0.05)

    assert len(finished_paths) == 1
    assert out_gif.exists()
    assert out_gif.stat().st_size > 0


def test_video_export_mp4(tmp_path: Path) -> None:
    in_video = tmp_path / "in.mp4"
    out_mp4 = tmp_path / "out.mp4"
    _create_dummy_video(in_video, frame_count=4)

    config = AsciiConfig(width=10)
    worker = VideoExportWorker(in_video, out_mp4, config, format_type="mp4")

    finished_paths: list[Path] = []
    worker.finished.connect(finished_paths.append)
    worker.start()

    start = time.time()
    while time.time() - start < 10.0 and len(finished_paths) == 0:
        _APP.processEvents()
        time.sleep(0.05)

    assert len(finished_paths) == 1
    assert out_mp4.exists()
    assert out_mp4.stat().st_size > 0


def test_export_dialog_modes(tmp_path: Path) -> None:
    config = AsciiConfig()
    # Empty mode
    dialog_empty = ExportDialog(config=config)
    assert dialog_empty is not None

    # Image mode
    img = Image.new("RGB", (20, 20))
    frame = AsciiFrame(chars=["##"], colors=None, width=2, height=1)
    dialog_img = ExportDialog(config=config, current_image=img, current_frame=frame)
    assert dialog_img._radio_png.isChecked()

    # Video mode
    dummy_video = tmp_path / "clip.mp4"
    _create_dummy_video(dummy_video, frame_count=2)
    dialog_vid = ExportDialog(config=config, current_video_path=dummy_video)
    assert dialog_vid._radio_mp4.isChecked()
