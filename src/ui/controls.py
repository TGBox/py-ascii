"""Sidebar controls widget for adjusting ASCII conversion settings and themes."""

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QButtonGroup,
    QCheckBox,
    QColorDialog,
    QComboBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QRadioButton,
    QScrollArea,
    QSlider,
    QVBoxLayout,
    QWidget,
)

from src.core.ascii_converter import DEFAULT_CHARSETS, AsciiConfig, ColorMode


class ControlsWidget(QWidget):
    """Sidebar widget containing all parameter controls, color settings, and actions."""

    config_changed = Signal(AsciiConfig)
    open_file_requested = Signal()
    export_requested = Signal()
    theme_changed = Signal(str)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._config = AsciiConfig()
        self._current_theme = "dark"
        self._updating_ui = False

        self._init_ui()
        self.set_config(self._config)

    def _init_ui(self) -> None:
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Scroll area for compact sidebar
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QScrollArea.Shape.NoFrame)

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setSpacing(12)
        layout.setContentsMargins(10, 10, 10, 10)

        # Section: Actions & Media
        action_group = QGroupBox("Aktionen")
        action_layout = QVBoxLayout(action_group)

        self._btn_open = QPushButton("📁 Datei öffnen...")
        self._btn_open.setObjectName("primaryButton")
        self._btn_open.setToolTip("Öffnet ein Bild oder Video (Strg+O)")
        self._btn_open.clicked.connect(self.open_file_requested.emit)
        action_layout.addWidget(self._btn_open)

        self._btn_export = QPushButton("💾 Exportieren...")
        self._btn_export.setToolTip(
            "Exportiert das aktuelle Ergebnis als Bild, Text oder Video (Strg+S)"
        )
        self._btn_export.clicked.connect(self.export_requested.emit)
        action_layout.addWidget(self._btn_export)

        self._btn_theme = QPushButton("🌙 Dunkelmodus")
        self._btn_theme.setToolTip("Wechselt zwischen dunklem und hellem Design")
        self._btn_theme.clicked.connect(self._toggle_theme)
        action_layout.addWidget(self._btn_theme)
        layout.addWidget(action_group)

        # Section: Dimensions & Scaling
        dim_group = QGroupBox("Auflösung & Proportionen")
        dim_layout = QFormLayout(dim_group)

        # Width slider
        self._slider_width = QSlider(Qt.Orientation.Horizontal)
        self._slider_width.setRange(20, 260)
        self._slider_width.setValue(self._config.width)
        self._slider_width.setToolTip("Anzahl der ASCII-Zeichenspalten in der Breite")
        self._label_width_val = QLabel(f"{self._config.width} Zeichen")
        self._slider_width.valueChanged.connect(self._on_slider_width_changed)
        dim_layout.addRow("Breite:", self._slider_width)
        dim_layout.addRow("", self._label_width_val)

        # Aspect ratio correction slider
        self._slider_aspect = QSlider(Qt.Orientation.Horizontal)
        self._slider_aspect.setRange(20, 100)
        self._slider_aspect.setValue(int(self._config.aspect_ratio_correction * 100))
        self._slider_aspect.setToolTip(
            "Korrekturfaktor für das typische 1:2-Höhenverhältnis von Monospace-Zeichen"
        )
        self._label_aspect_val = QLabel(f"{self._config.aspect_ratio_correction:.2f}")
        self._slider_aspect.valueChanged.connect(self._on_slider_aspect_changed)
        dim_layout.addRow("Seitenverhältnis:", self._slider_aspect)
        dim_layout.addRow("", self._label_aspect_val)

        layout.addWidget(dim_group)

        # Section: Character Set
        charset_group = QGroupBox("Zeichensatz")
        charset_layout = QVBoxLayout(charset_group)

        self._combo_charset = QComboBox()
        for name in DEFAULT_CHARSETS:
            self._combo_charset.addItem(name)
        self._combo_charset.addItem("Benutzerdefiniert")
        self._combo_charset.setToolTip("Wähle einen vorbereiteten Zeichensatz")
        self._combo_charset.currentTextChanged.connect(self._on_charset_preset_selected)
        charset_layout.addWidget(self._combo_charset)

        self._edit_charset = QLineEdit(self._config.charset)
        self._edit_charset.setToolTip("Aktive Zeichenfolge (von dunkel nach hell sortiert)")
        self._edit_charset.textChanged.connect(self._on_custom_charset_changed)
        charset_layout.addWidget(self._edit_charset)

        self._check_invert = QCheckBox("Helligkeit invertieren")
        self._check_invert.setToolTip("Kehrt die Zuordnung von dunklen und hellen Zeichen um")
        self._check_invert.toggled.connect(self._on_invert_toggled)
        charset_layout.addWidget(self._check_invert)

        layout.addWidget(charset_group)

        # Section: Lighting & Contrast
        lighting_group = QGroupBox("Helligkeit & Kontrast")
        lighting_layout = QFormLayout(lighting_group)

        # Brightness
        self._slider_brightness = QSlider(Qt.Orientation.Horizontal)
        self._slider_brightness.setRange(20, 250)
        self._slider_brightness.setValue(int(self._config.brightness * 100))
        self._slider_brightness.setToolTip(
            "Regelt die Gesamthelligkeit des Bildes vor der Rasterung"
        )
        self._label_brightness_val = QLabel(f"{self._config.brightness:.2f}x")
        self._slider_brightness.valueChanged.connect(self._on_brightness_changed)
        lighting_layout.addRow("Helligkeit:", self._slider_brightness)
        lighting_layout.addRow("", self._label_brightness_val)

        # Contrast
        self._slider_contrast = QSlider(Qt.Orientation.Horizontal)
        self._slider_contrast.setRange(20, 300)
        self._slider_contrast.setValue(int(self._config.contrast * 100))
        self._slider_contrast.setToolTip("Passt den Helligkeitskontrast an")
        self._label_contrast_val = QLabel(f"{self._config.contrast:.2f}x")
        self._slider_contrast.valueChanged.connect(self._on_contrast_changed)
        lighting_layout.addRow("Kontrast:", self._slider_contrast)
        lighting_layout.addRow("", self._label_contrast_val)

        layout.addWidget(lighting_group)

        # Section: Color Mode
        color_group = QGroupBox("Farbe & Stil")
        color_layout = QVBoxLayout(color_group)

        self._btn_group_mode = QButtonGroup(self)
        self._radio_rgb = QRadioButton("Vollfarbe (RGB)")
        self._radio_mono = QRadioButton("Retro-Monochrom")
        self._btn_group_mode.addButton(self._radio_rgb)
        self._btn_group_mode.addButton(self._radio_mono)
        self._radio_rgb.setChecked(self._config.color_mode == ColorMode.RGB)
        self._radio_mono.setChecked(self._config.color_mode == ColorMode.MONOCHROME)

        self._radio_rgb.toggled.connect(self._on_color_mode_changed)
        color_layout.addWidget(self._radio_rgb)
        color_layout.addWidget(self._radio_mono)

        # Sub-container for monochrome color pickers
        self._mono_widget = QWidget()
        mono_layout = QVBoxLayout(self._mono_widget)
        mono_layout.setContentsMargins(0, 4, 0, 0)

        # Retro Presets
        presets_layout = QHBoxLayout()
        btn_preset_matrix = QPushButton("Matrix")
        btn_preset_matrix.clicked.connect(
            lambda: self._apply_mono_preset((0, 255, 70), (10, 15, 10))
        )
        btn_preset_amber = QPushButton("Amber")
        btn_preset_amber.clicked.connect(
            lambda: self._apply_mono_preset((255, 176, 0), (20, 14, 5))
        )
        btn_preset_bw = QPushButton("S/W")
        btn_preset_bw.clicked.connect(lambda: self._apply_mono_preset((255, 255, 255), (0, 0, 0)))

        presets_layout.addWidget(btn_preset_matrix)
        presets_layout.addWidget(btn_preset_amber)
        presets_layout.addWidget(btn_preset_bw)
        mono_layout.addLayout(presets_layout)

        # Color picker buttons
        picker_layout = QHBoxLayout()
        self._btn_fg_color = QPushButton("Textfarbe")
        self._btn_fg_color.clicked.connect(self._pick_fg_color)
        self._btn_bg_color = QPushButton("Hintergrund")
        self._btn_bg_color.clicked.connect(self._pick_bg_color)
        picker_layout.addWidget(self._btn_fg_color)
        picker_layout.addWidget(self._btn_bg_color)
        mono_layout.addLayout(picker_layout)

        color_layout.addWidget(self._mono_widget)
        self._update_color_swatches()
        self._mono_widget.setVisible(self._config.color_mode == ColorMode.MONOCHROME)

        layout.addWidget(color_group)

        layout.addStretch()
        scroll_area.setWidget(container)
        main_layout.addWidget(scroll_area)

    def _toggle_theme(self) -> None:
        if self._current_theme == "dark":
            self._current_theme = "light"
            self._btn_theme.setText("☀️ Hellmodus")
        else:
            self._current_theme = "dark"
            self._btn_theme.setText("🌙 Dunkelmodus")
        self.theme_changed.emit(self._current_theme)

    def _update_color_swatches(self) -> None:
        fg = self._config.fg_color
        bg = self._config.bg_color
        self._btn_fg_color.setStyleSheet(
            f"background-color: rgb({fg[0]}, {fg[1]}, {fg[2]}); color: {'black' if (fg[0] + fg[1] + fg[2]) > 380 else 'white'};"
        )
        self._btn_bg_color.setStyleSheet(
            f"background-color: rgb({bg[0]}, {bg[1]}, {bg[2]}); color: {'black' if (bg[0] + bg[1] + bg[2]) > 380 else 'white'};"
        )

    def _apply_mono_preset(self, fg: tuple[int, int, int], bg: tuple[int, int, int]) -> None:
        self._config.fg_color = fg
        self._config.bg_color = bg
        self._update_color_swatches()
        self._notify_change()

    def _pick_fg_color(self) -> None:
        cur = QColor(*self._config.fg_color)
        color = QColorDialog.getColor(cur, self, "Textfarbe auswählen")
        if color.isValid():
            self._config.fg_color = (color.red(), color.green(), color.blue())
            self._update_color_swatches()
            self._notify_change()

    def _pick_bg_color(self) -> None:
        cur = QColor(*self._config.bg_color)
        color = QColorDialog.getColor(cur, self, "Hintergrundfarbe auswählen")
        if color.isValid():
            self._config.bg_color = (color.red(), color.green(), color.blue())
            self._update_color_swatches()
            self._notify_change()

    def _on_slider_width_changed(self, value: int) -> None:
        self._label_width_val.setText(f"{value} Zeichen")
        self._config.width = value
        self._notify_change()

    def _on_slider_aspect_changed(self, value: int) -> None:
        aspect = value / 100.0
        self._label_aspect_val.setText(f"{aspect:.2f}")
        self._config.aspect_ratio_correction = aspect
        self._notify_change()

    def _on_brightness_changed(self, value: int) -> None:
        val = value / 100.0
        self._label_brightness_val.setText(f"{val:.2f}x")
        self._config.brightness = val
        self._notify_change()

    def _on_contrast_changed(self, value: int) -> None:
        val = value / 100.0
        self._label_contrast_val.setText(f"{val:.2f}x")
        self._config.contrast = val
        self._notify_change()

    def _on_invert_toggled(self, checked: bool) -> None:
        self._config.invert = checked
        self._notify_change()

    def _on_charset_preset_selected(self, text: str) -> None:
        if self._updating_ui:
            return
        if text in DEFAULT_CHARSETS:
            self._updating_ui = True
            self._edit_charset.setText(DEFAULT_CHARSETS[text])
            self._config.charset = DEFAULT_CHARSETS[text]
            self._updating_ui = False
            self._notify_change()

    def _on_custom_charset_changed(self, text: str) -> None:
        if self._updating_ui:
            return
        self._config.charset = text
        # If text doesn't match current combo preset, switch combo to 'Benutzerdefiniert'
        matched = False
        for name, chars in DEFAULT_CHARSETS.items():
            if chars == text:
                self._combo_charset.setCurrentText(name)
                matched = True
                break
        if not matched:
            self._combo_charset.setCurrentText("Benutzerdefiniert")
        self._notify_change()

    def _on_color_mode_changed(self) -> None:
        is_rgb = self._radio_rgb.isChecked()
        self._config.color_mode = ColorMode.RGB if is_rgb else ColorMode.MONOCHROME
        self._mono_widget.setVisible(not is_rgb)
        self._notify_change()

    def _notify_change(self) -> None:
        if not self._updating_ui:
            self.config_changed.emit(self.get_config())

    def get_config(self) -> AsciiConfig:
        """Returns a copy of the current configuration."""
        return AsciiConfig(
            width=self._config.width,
            aspect_ratio_correction=self._config.aspect_ratio_correction,
            charset=self._config.charset,
            brightness=self._config.brightness,
            contrast=self._config.contrast,
            invert=self._config.invert,
            color_mode=self._config.color_mode,
            fg_color=self._config.fg_color,
            bg_color=self._config.bg_color,
        )

    def set_config(self, config: AsciiConfig) -> None:
        """Populates the UI controls from an AsciiConfig object."""
        self._updating_ui = True
        self._config = AsciiConfig(
            width=config.width,
            aspect_ratio_correction=config.aspect_ratio_correction,
            charset=config.charset,
            brightness=config.brightness,
            contrast=config.contrast,
            invert=config.invert,
            color_mode=config.color_mode,
            fg_color=config.fg_color,
            bg_color=config.bg_color,
        )

        self._slider_width.setValue(self._config.width)
        self._label_width_val.setText(f"{self._config.width} Zeichen")

        self._slider_aspect.setValue(int(self._config.aspect_ratio_correction * 100))
        self._label_aspect_val.setText(f"{self._config.aspect_ratio_correction:.2f}")

        self._slider_brightness.setValue(int(self._config.brightness * 100))
        self._label_brightness_val.setText(f"{self._config.brightness:.2f}x")

        self._slider_contrast.setValue(int(self._config.contrast * 100))
        self._label_contrast_val.setText(f"{self._config.contrast:.2f}x")

        self._check_invert.setChecked(self._config.invert)
        self._edit_charset.setText(self._config.charset)

        # Match preset
        matched = False
        for name, chars in DEFAULT_CHARSETS.items():
            if chars == self._config.charset:
                self._combo_charset.setCurrentText(name)
                matched = True
                break
        if not matched:
            self._combo_charset.setCurrentText("Benutzerdefiniert")

        if self._config.color_mode == ColorMode.RGB:
            self._radio_rgb.setChecked(True)
            self._mono_widget.setVisible(False)
        else:
            self._radio_mono.setChecked(True)
            self._mono_widget.setVisible(True)

        self._update_color_swatches()
        self._updating_ui = False
