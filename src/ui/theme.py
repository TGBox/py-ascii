"""Modern dark and light themes for py-ascii using Qt Style Sheets (QSS)."""

from PySide6.QtWidgets import QApplication, QWidget

DARK_THEME_QSS = """
QWidget {
    background-color: #1a1a20;
    color: #e6e6ec;
    font-family: "Segoe UI", -apple-system, BlinkMacSystemFont, "Roboto", sans-serif;
    font-size: 13px;
}

QGroupBox {
    border: 1px solid #30303c;
    border-radius: 6px;
    margin-top: 14px;
    padding-top: 12px;
    font-weight: bold;
    color: #a0a0c0;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 10px;
    padding: 0 4px;
    background-color: #1a1a20;
}

QPushButton {
    background-color: #2a2a36;
    color: #ffffff;
    border: 1px solid #3d3d4e;
    border-radius: 5px;
    padding: 6px 14px;
    font-weight: 500;
}

QPushButton:hover {
    background-color: #38384a;
    border-color: #52526c;
}

QPushButton:pressed {
    background-color: #1e1e28;
}

QPushButton:disabled {
    background-color: #1e1e24;
    color: #5a5a6a;
    border-color: #282834;
}

QPushButton#primaryButton {
    background-color: #2563eb;
    border-color: #3b82f6;
    font-weight: bold;
}

QPushButton#primaryButton:hover {
    background-color: #1d4ed8;
}

QSlider::groove:horizontal {
    height: 6px;
    background: #2a2a36;
    border-radius: 3px;
}

QSlider::sub-page:horizontal {
    background: #3b82f6;
    border-radius: 3px;
}

QSlider::handle:horizontal {
    background: #e6e6ec;
    border: 1px solid #3b82f6;
    width: 14px;
    margin-top: -5px;
    margin-bottom: -5px;
    border-radius: 7px;
}

QSlider::handle:horizontal:hover {
    background: #ffffff;
}

QComboBox, QLineEdit {
    background-color: #242430;
    color: #ffffff;
    border: 1px solid #3d3d4e;
    border-radius: 5px;
    padding: 5px 10px;
}

QComboBox:focus, QLineEdit:focus {
    border: 1px solid #3b82f6;
}

QComboBox::drop-down {
    border: none;
    width: 20px;
}

QComboBox QAbstractItemView {
    background-color: #242430;
    color: #ffffff;
    selection-background-color: #3b82f6;
    selection-color: #ffffff;
    border: 1px solid #3d3d4e;
}

QRadioButton, QCheckBox {
    spacing: 8px;
    color: #e6e6ec;
}

QRadioButton::indicator, QCheckBox::indicator {
    width: 16px;
    height: 16px;
}

QScrollBar:vertical {
    background: #1a1a20;
    width: 10px;
    margin: 0px;
}

QScrollBar::handle:vertical {
    background: #2f2f3e;
    min-height: 20px;
    border-radius: 5px;
}

QScrollBar::handle:vertical:hover {
    background: #424256;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}
"""

LIGHT_THEME_QSS = """
QWidget {
    background-color: #f8fafc;
    color: #1e293b;
    font-family: "Segoe UI", -apple-system, BlinkMacSystemFont, "Roboto", sans-serif;
    font-size: 13px;
}

QGroupBox {
    border: 1px solid #cbd5e1;
    border-radius: 6px;
    margin-top: 14px;
    padding-top: 12px;
    font-weight: bold;
    color: #475569;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 10px;
    padding: 0 4px;
    background-color: #f8fafc;
}

QPushButton {
    background-color: #ffffff;
    color: #0f172a;
    border: 1px solid #cbd5e1;
    border-radius: 5px;
    padding: 6px 14px;
    font-weight: 500;
}

QPushButton:hover {
    background-color: #f1f5f9;
    border-color: #94a3b8;
}

QPushButton:pressed {
    background-color: #e2e8f0;
}

QPushButton:disabled {
    background-color: #f1f5f9;
    color: #94a3b8;
    border-color: #e2e8f0;
}

QPushButton#primaryButton {
    background-color: #2563eb;
    color: #ffffff;
    border-color: #1d4ed8;
    font-weight: bold;
}

QPushButton#primaryButton:hover {
    background-color: #1d4ed8;
}

QSlider::groove:horizontal {
    height: 6px;
    background: #e2e8f0;
    border-radius: 3px;
}

QSlider::sub-page:horizontal {
    background: #2563eb;
    border-radius: 3px;
}

QSlider::handle:horizontal {
    background: #ffffff;
    border: 1px solid #2563eb;
    width: 14px;
    margin-top: -5px;
    margin-bottom: -5px;
    border-radius: 7px;
}

QSlider::handle:horizontal:hover {
    background: #f8fafc;
}

QComboBox, QLineEdit {
    background-color: #ffffff;
    color: #0f172a;
    border: 1px solid #cbd5e1;
    border-radius: 5px;
    padding: 5px 10px;
}

QComboBox:focus, QLineEdit:focus {
    border: 1px solid #2563eb;
}

QComboBox::drop-down {
    border: none;
    width: 20px;
}

QComboBox QAbstractItemView {
    background-color: #ffffff;
    color: #0f172a;
    selection-background-color: #2563eb;
    selection-color: #ffffff;
    border: 1px solid #cbd5e1;
}

QRadioButton, QCheckBox {
    spacing: 8px;
    color: #1e293b;
}

QRadioButton::indicator, QCheckBox::indicator {
    width: 16px;
    height: 16px;
}

QScrollBar:vertical {
    background: #f8fafc;
    width: 10px;
    margin: 0px;
}

QScrollBar::handle:vertical {
    background: #cbd5e1;
    min-height: 20px;
    border-radius: 5px;
}

QScrollBar::handle:vertical:hover {
    background: #94a3b8;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}
"""


def apply_theme(target: QApplication | QWidget, theme_name: str = "dark") -> None:
    """Applies either the dark or light theme stylesheet to a QApplication or QWidget."""
    if theme_name.lower() == "light":
        target.setStyleSheet(LIGHT_THEME_QSS)
    else:
        target.setStyleSheet(DARK_THEME_QSS)
