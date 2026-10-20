"""Unit tests for MainWindow and the image workflow."""

from pathlib import Path

from PIL import Image
from PySide6.QtWidgets import QApplication

from src.ui.main_window import MainWindow

_APP = QApplication.instance() or QApplication([])


def test_main_window_init() -> None:
    window = MainWindow()
    assert window.canvas is not None
    assert window.controls is not None
    assert window.statusBar is not None
    assert "py-ascii" in window.windowTitle()
    window.close()


def test_main_window_image_loading_and_recomputing(tmp_path: Path) -> None:
    # Create a temporary test image
    img_path = tmp_path / "sample.png"
    img = Image.new("RGB", (100, 60), color=(255, 0, 0))
    img.save(img_path)

    window = MainWindow()
    window.open_media(img_path)

    frame = window.canvas.get_frame()
    assert frame is not None
    assert frame.width == window.controls.get_config().width
    assert frame.height > 0
    assert frame.colors is not None

    # Change settings via controls
    window.controls._slider_width.setValue(50)
    updated_frame = window.canvas.get_frame()
    assert updated_frame is not None
    assert updated_frame.width == 50

    # Switch to monochrome
    window.controls._radio_mono.setChecked(True)
    mono_frame = window.canvas.get_frame()
    assert mono_frame is not None
    assert mono_frame.colors is None
    window.close()


def test_main_window_fullscreen_toggle() -> None:
    window = MainWindow()
    assert not window.isFullScreen()

    window.toggle_fullscreen()
    assert window.isFullScreen()

    window.toggle_fullscreen()
    assert not window.isFullScreen()
    window.close()


def test_main_window_zoom_and_shortcuts() -> None:
    window = MainWindow()
    initial_zoom = window.canvas._zoom_factor
    window._zoom_in()
    assert window.canvas._zoom_factor > initial_zoom

    window._zoom_out()
    assert abs(window.canvas._zoom_factor - initial_zoom) < 0.05

    window._zoom_reset()
    assert window.canvas._zoom_factor == 1.0
    window.close()
