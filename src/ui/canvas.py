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
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)

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

        avail_w = max(10.0, float(self.width() - 16))
        avail_h = max(10.0, float(self.height() - 16))

        # Use base monospace font metrics to calculate stable natural grid size
        metrics = QFontMetricsF(self._base_font)
        char_w = metrics.horizontalAdvance("M")
        line_h = metrics.lineSpacing()
        ascent = metrics.ascent()

        grid_w = max(1.0, cols * char_w)
        grid_h = max(1.0, rows * line_h)

        if self._fit_to_window:
            scale = min(avail_w / grid_w, avail_h / grid_h) * self._zoom_factor
        else:
            scale = self._zoom_factor

        content_w = grid_w * scale
        content_h = grid_h * scale

        start_x = max(8.0, (self.width() - content_w) / 2.0)
        start_y = max(8.0, (self.height() - content_h) / 2.0)

        painter.save()
        painter.translate(start_x, start_y)
        painter.scale(scale, scale)
        painter.setFont(self._base_font)

        # Draw rows
        if is_rgb and colors is not None:
            # RGB mode: Batch contiguous characters with same RGB color per line
            for r, line in enumerate(self._frame.chars):
                base_y = r * line_h + ascent
                row_colors = colors[r]
                line_len = len(line)

                c = 0
                while c < line_len:
                    cur_r, cur_g, cur_b = row_colors[c]
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
                    x_pos = span_start * char_w
                    painter.drawText(QPointF(x_pos, base_y), span_text)
        else:
            # Monochrome mode: Draw full line at once
            painter.setPen(self._fg_color)
            for r, line in enumerate(self._frame.chars):
                base_y = r * line_h + ascent
                painter.drawText(QPointF(0.0, base_y), line)

        painter.restore()
        painter.end()
