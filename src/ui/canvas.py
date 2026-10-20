"""Hardware-accelerated ASCII canvas widget using QPainter."""

from PySide6.QtCore import QPointF, Qt
from PySide6.QtGui import (
    QColor,
    QFont,
    QFontDatabase,
    QFontMetricsF,
    QPainter,
    QPaintEvent,
)
from PySide6.QtWidgets import QWidget

from src.core.ascii_converter import AsciiFrame


class AsciiCanvasWidget(QWidget):
    """Custom widget rendering AsciiFrames with fast QPainter drawing."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_OpaquePaintEvent, True)

        self._frame: AsciiFrame | None = None
        self._bg_color: QColor = QColor(15, 15, 18)
        self._fg_color: QColor = QColor(0, 255, 100)  # Classic terminal green
        self._fit_to_window: bool = True
        self._zoom_factor: float = 1.0

        # Monospace font configuration
        self._base_font: QFont = QFontDatabase.systemFont(QFontDatabase.SystemFont.FixedFont)
        self._base_font.setStyleHint(QFont.StyleHint.Monospace)
        self._base_font.setPointSize(10)

        self.setMinimumSize(320, 240)

    def set_frame(self, frame: AsciiFrame | None) -> None:
        """Sets the current ASCII frame and requests a repaint."""
        self._frame = frame
        self.update()

    def get_frame(self) -> AsciiFrame | None:
        """Returns the currently active ASCII frame."""
        return self._frame

    def set_colors(self, bg_color: QColor, fg_color: QColor) -> None:
        """Updates background and monochrome foreground colors."""
        self._bg_color = bg_color
        self._fg_color = fg_color
        self.update()

    def set_fit_to_window(self, fit: bool) -> None:
        """Enables or disables auto-fitting to widget bounds."""
        self._fit_to_window = fit
        self.update()

    def set_zoom_factor(self, zoom: float) -> None:
        """Sets the zoom multiplier (1.0 = 100%)."""
        self._zoom_factor = max(0.2, min(5.0, zoom))
        self.update()

    def _draw_placeholder(self, painter: QPainter) -> None:
        """Renders placeholder message when no frame is loaded."""
        painter.fillRect(self.rect(), self._bg_color)
        painter.setPen(QColor(140, 140, 160))
        font = QFont(self.font().family(), 12)
        painter.setFont(font)

        text = (
            "Kein Medium geladen\n\n"
            "Ziehe ein Bild oder Video hierher oder klicke auf 'Datei öffnen'"
        )
        painter.drawText(
            self.rect(),
            Qt.AlignmentFlag.AlignCenter | Qt.TextFlag.TextWordWrap,
            text,
        )

    def paintEvent(self, event: QPaintEvent) -> None:
        """Paints the ASCII frame or placeholder."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing, True)

        if not self._frame or self._frame.width == 0 or self._frame.height == 0:
            self._draw_placeholder(painter)
            painter.end()
            return

        cols = self._frame.width
        rows = self._frame.height
        colors = self._frame.colors
        is_rgb = colors is not None

        # Fill canvas background
        painter.fillRect(self.rect(), self._bg_color)

        avail_w = max(10, self.width() - 16)
        avail_h = max(10, self.height() - 16)

        # Estimate font pixel size to fit dimensions
        font = QFont(self._base_font)
        if self._fit_to_window:
            # Typical monospace aspect ratio: width is ~0.6 of height
            est_h = avail_h / rows
            est_w = avail_w / (cols * 0.6)
            pixel_size = max(4, int(min(est_h, est_w) * self._zoom_factor))
        else:
            pixel_size = max(4, int(12 * self._zoom_factor))

        font.setPixelSize(pixel_size)
        metrics = QFontMetricsF(font)
        char_w = metrics.horizontalAdvance("M")
        line_h = metrics.lineSpacing()
        ascent = metrics.ascent()

        # Fine-tune pixel size if character width or height exceeds available bounds
        if self._fit_to_window:
            total_w = cols * char_w
            total_h = rows * line_h
            if total_w > avail_w or total_h > avail_h:
                scale_down = min(avail_w / max(1.0, total_w), avail_h / max(1.0, total_h))
                pixel_size = max(4, int(pixel_size * scale_down))
                font.setPixelSize(pixel_size)
                metrics = QFontMetricsF(font)
                char_w = metrics.horizontalAdvance("M")
                line_h = metrics.lineSpacing()
                ascent = metrics.ascent()

        painter.setFont(font)

        # Center the rendered ASCII grid
        content_w = cols * char_w
        content_h = rows * line_h
        start_x = max(8.0, (self.width() - content_w) / 2.0)
        start_y = max(8.0, (self.height() - content_h) / 2.0)

        # Draw rows
        if is_rgb and colors is not None:
            # RGB mode: Batch contiguous characters with same RGB color per line
            for r, line in enumerate(self._frame.chars):
                base_y = start_y + r * line_h + ascent
                row_colors = colors[r]
                line_len = len(line)

                c = 0
                while c < line_len:
                    cur_r, cur_g, cur_b = row_colors[c]
                    # Find span of characters sharing the exact same color
                    span_start = c
                    while (
                        c < line_len
                        and row_colors[c][0] == cur_r
                        and row_colors[c][1] == cur_g
                        and row_colors[c][2] == cur_b
                    ):
                        c += 1

                    span_text = line[span_start:c]
                    painter.setPen(QColor(int(cur_r), int(cur_g), int(cur_b)))
                    x_pos = start_x + span_start * char_w
                    painter.drawText(QPointF(x_pos, base_y), span_text)
        else:
            # Monochrome mode: Draw full line at once
            painter.setPen(self._fg_color)
            for r, line in enumerate(self._frame.chars):
                base_y = start_y + r * line_h + ascent
                painter.drawText(QPointF(start_x, base_y), line)

        painter.end()
