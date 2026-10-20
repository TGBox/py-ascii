"""Unit tests for AsciiCanvasWidget."""

import numpy as np
from PySide6.QtGui import QColor, QPixmap
from PySide6.QtWidgets import QApplication

from src.core.ascii_converter import AsciiFrame
from src.ui.canvas import AsciiCanvasWidget

# Ensure QApplication exists for headless test runs
_APP = QApplication.instance() or QApplication([])


def test_canvas_initialization() -> None:
    canvas = AsciiCanvasWidget()
    assert canvas.get_frame() is None
    assert canvas.minimumWidth() >= 320
    assert canvas.minimumHeight() >= 240


def test_canvas_set_frame_and_properties() -> None:
    canvas = AsciiCanvasWidget()
    frame = AsciiFrame(chars=["###", "###"], colors=None, width=3, height=2)
    canvas.set_frame(frame)
    assert canvas.get_frame() == frame

    canvas.set_colors(QColor(10, 10, 10), QColor(0, 200, 50))
    canvas.set_zoom_factor(1.5)
    canvas.set_fit_to_window(False)
    assert canvas._zoom_factor == 1.5
    assert not canvas._fit_to_window


def test_canvas_paint_empty() -> None:
    canvas = AsciiCanvasWidget()
    canvas.resize(400, 300)
    pixmap = QPixmap(400, 300)
    canvas.render(pixmap)
    assert not pixmap.isNull()


def test_canvas_paint_monochrome() -> None:
    canvas = AsciiCanvasWidget()
    canvas.resize(400, 300)
    frame = AsciiFrame(chars=["hello", "world"], colors=None, width=5, height=2)
    canvas.set_frame(frame)

    pixmap = QPixmap(400, 300)
    canvas.render(pixmap)
    assert not pixmap.isNull()


def test_canvas_paint_rgb() -> None:
    canvas = AsciiCanvasWidget()
    canvas.resize(400, 300)
    colors = np.zeros((2, 5, 3), dtype=np.uint8)
    colors[0, :, 0] = 255  # Red
    colors[1, :, 1] = 255  # Green

    frame = AsciiFrame(chars=["12345", "67890"], colors=colors, width=5, height=2)
    canvas.set_frame(frame)

    pixmap = QPixmap(400, 300)
    canvas.render(pixmap)
    assert not pixmap.isNull()
