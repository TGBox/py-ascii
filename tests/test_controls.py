"""Unit tests for the ControlsWidget sidebar and theme functionality."""

from PySide6.QtWidgets import QApplication, QWidget

from src.core.ascii_converter import DEFAULT_CHARSETS, AsciiConfig, ColorMode
from src.ui.controls import ControlsWidget
from src.ui.theme import apply_theme

_APP = QApplication.instance() or QApplication([])


def test_theme_application() -> None:
    widget = QWidget()
    apply_theme(widget, "dark")
    assert "background-color: #1a1a20" in widget.styleSheet()

    apply_theme(widget, "light")
    assert "background-color: #f8fafc" in widget.styleSheet()
    widget.deleteLater()
    _APP.processEvents()


def test_controls_defaults_and_get_config() -> None:
    controls = ControlsWidget()
    config = controls.get_config()
    assert config.width == 120
    assert config.aspect_ratio_correction == 0.55
    assert config.charset == DEFAULT_CHARSETS["Standard"]
    assert config.color_mode == ColorMode.RGB
    controls.deleteLater()
    _APP.processEvents()


def test_controls_set_config() -> None:
    controls = ControlsWidget()
    new_cfg = AsciiConfig(
        width=160,
        aspect_ratio_correction=0.45,
        charset="01",
        brightness=1.5,
        contrast=1.2,
        invert=True,
        color_mode=ColorMode.MONOCHROME,
        fg_color=(0, 255, 0),
        bg_color=(10, 10, 10),
    )
    controls.set_config(new_cfg)
    cfg = controls.get_config()

    assert cfg.width == 160
    assert abs(cfg.aspect_ratio_correction - 0.45) < 0.01
    assert cfg.charset == "01"
    assert abs(cfg.brightness - 1.5) < 0.01
    assert abs(cfg.contrast - 1.2) < 0.01
    assert cfg.invert is True
    assert cfg.color_mode == ColorMode.MONOCHROME
    assert cfg.fg_color == (0, 255, 0)
    assert cfg.bg_color == (10, 10, 10)
    controls.deleteLater()
    _APP.processEvents()


def test_controls_signals() -> None:
    controls = ControlsWidget()

    emitted_configs: list[AsciiConfig] = []
    controls.config_changed.connect(emitted_configs.append)

    controls._slider_width.setValue(80)
    assert len(emitted_configs) > 0
    assert emitted_configs[-1].width == 80

    themes: list[str] = []
    controls.theme_changed.connect(themes.append)
    controls._toggle_theme()
    assert len(themes) == 1
    assert themes[0] == "light"
    controls.deleteLater()
    _APP.processEvents()


def test_mono_presets() -> None:
    controls = ControlsWidget()
    controls._apply_mono_preset((0, 255, 70), (10, 15, 10))
    cfg = controls.get_config()
    assert cfg.fg_color == (0, 255, 70)
    assert cfg.bg_color == (10, 15, 10)
    controls.deleteLater()
    _APP.processEvents()
