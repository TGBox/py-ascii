"""Export engine for ASCII images, animated GIFs, and MP4 videos with preserved audio."""

import subprocess
import tempfile
from pathlib import Path

import cv2
import imageio_ffmpeg
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from PySide6.QtCore import QMutex, QMutexLocker, QThread, Signal

from src.core.ascii_converter import AsciiConfig, AsciiConverter, AsciiFrame, ColorMode


def export_image_txt(frame: AsciiFrame, output_path: Path) -> None:
    """Exports ASCII frame as UTF-8 plaintext file."""
    output_path.write_text(frame.text, encoding="utf-8")


def render_frame_to_image(
    frame: AsciiFrame,
    config: AsciiConfig,
    char_size: tuple[int, int] = (8, 14),
) -> Image.Image:
    """Renders an AsciiFrame to a PIL RGB image."""
    char_w, char_h = char_size
    img_w = max(1, frame.width * char_w)
    img_h = max(1, frame.height * char_h)

    bg_color = config.bg_color
    fg_color = config.fg_color
    is_rgb = frame.colors is not None and config.color_mode == ColorMode.RGB

    img = Image.new("RGB", (img_w, img_h), color=bg_color)
    draw = ImageDraw.Draw(img)

    # Use default PIL monospace font
    font = ImageFont.load_default()

    for r, line in enumerate(frame.chars):
        y = r * char_h
        if is_rgb and frame.colors is not None:
            row_colors = frame.colors[r]
            for c, char in enumerate(line):
                x = c * char_w
                r_val, g_val, b_val = row_colors[c]
                draw.text((x, y), char, fill=(int(r_val), int(g_val), int(b_val)), font=font)
        else:
            draw.text((0, y), line, fill=fg_color, font=font)

    return img


def export_image_png(
    frame: AsciiFrame,
    output_path: Path,
    config: AsciiConfig,
    char_size: tuple[int, int] = (8, 14),
) -> None:
    """Exports ASCII frame as rendered PNG image."""
    img = render_frame_to_image(frame, config, char_size)
    img.save(output_path, format="PNG")


class VideoExportWorker(QThread):
    """Worker thread that renders video frames and muxes original audio via FFmpeg."""

    progress = Signal(float, str)  # 0.0 to 1.0, status description
    finished = Signal(Path)
    failed = Signal(str)
    cancelled = Signal()

    def __init__(
        self,
        input_video_path: Path,
        output_path: Path,
        config: AsciiConfig,
        format_type: str = "mp4",
        parent=None,
    ) -> None:
        super().__init__(parent)
        self.input_video_path = input_video_path
        self.output_path = output_path
        self.config = config
        self.format_type = format_type.lower()
        self._mutex = QMutex()
        self._is_cancelled = False

    def cancel(self) -> None:
        """Requests cancellation of export."""
        with QMutexLocker(self._mutex):
            self._is_cancelled = True

    def _check_cancelled(self) -> bool:
        with QMutexLocker(self._mutex):
            return self._is_cancelled

    def run(self) -> None:
        """Executes the export pipeline."""
        try:
            if self.format_type == "gif":
                self._export_gif()
            else:
                self._export_mp4()
        except Exception as exc:  # noqa: BLE001
            self.failed.emit(str(exc))

    def _export_gif(self) -> None:
        cap = cv2.VideoCapture(str(self.input_video_path))
        if not cap.isOpened():
            self.failed.emit("Quellvideo konnte nicht geöffnet werden.")
            return

        total_frames = max(1, int(cap.get(cv2.CAP_PROP_FRAME_COUNT)))
        fps = float(cap.get(cv2.CAP_PROP_FPS))
        if fps <= 0.0 or fps > 60.0:
            fps = 15.0

        rendered_pil_frames: list[Image.Image] = []
        frame_idx = 0

        while True:
            if self._check_cancelled():
                cap.release()
                self.cancelled.emit()
                return

            ret, frame = cap.read()
            if not ret or frame is None:
                break

            ascii_frame = AsciiConverter.convert(frame, self.config)
            pil_img = render_frame_to_image(ascii_frame, self.config)
            rendered_pil_frames.append(pil_img)

            frame_idx += 1
            prog = frame_idx / total_frames
            self.progress.emit(prog * 0.9, f"Frame {frame_idx}/{total_frames} konvertiert...")

        cap.release()

        if not rendered_pil_frames:
            self.failed.emit("Keine Frames im Video gefunden.")
            return

        self.progress.emit(0.92, "GIF-Animation wird erstellt...")
        duration_ms = int(1000.0 / fps)
        rendered_pil_frames[0].save(
            self.output_path,
            save_all=True,
            append_images=rendered_pil_frames[1:],
            duration=duration_ms,
            loop=0,
            optimize=True,
        )

        self.progress.emit(1.0, "Export abgeschlossen!")
        self.finished.emit(self.output_path)

    def _export_mp4(self) -> None:
        cap = cv2.VideoCapture(str(self.input_video_path))
        if not cap.isOpened():
            self.failed.emit("Quellvideo konnte nicht geöffnet werden.")
            return

        total_frames = max(1, int(cap.get(cv2.CAP_PROP_FRAME_COUNT)))
        fps = float(cap.get(cv2.CAP_PROP_FPS))
        if fps <= 0.0 or fps > 120.0:
            fps = 30.0

        # Read first frame to determine rendered dimensions
        ret, first_cv_frame = cap.read()
        if not ret or first_cv_frame is None:
            cap.release()
            self.failed.emit("Konnte ersten Video-Frame nicht lesen.")
            return

        ascii_sample = AsciiConverter.convert(first_cv_frame, self.config)
        sample_pil = render_frame_to_image(ascii_sample, self.config)
        out_w, out_h = sample_pil.size

        # Reset video capture to start
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

        # Temporary file for raw ASCII video
        with tempfile.NamedTemporaryFile(suffix="_raw.mp4", delete=False) as tmp_file:
            temp_video_path = Path(tmp_file.name)

        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        writer = cv2.VideoWriter(str(temp_video_path), fourcc, fps, (out_w, out_h))

        frame_idx = 0
        while True:
            if self._check_cancelled():
                cap.release()
                writer.release()
                if temp_video_path.exists():
                    temp_video_path.unlink()
                self.cancelled.emit()
                return

            ret, frame = cap.read()
            if not ret or frame is None:
                break

            ascii_frame = AsciiConverter.convert(frame, self.config)
            pil_rendered = render_frame_to_image(ascii_frame, self.config)
            # Convert PIL RGB to OpenCV BGR
            cv_rendered = cv2.cvtColor(np.array(pil_rendered), cv2.COLOR_RGB2BGR)
            writer.write(cv_rendered)

            frame_idx += 1
            prog = frame_idx / total_frames
            self.progress.emit(prog * 0.85, f"Frame {frame_idx}/{total_frames} gerendert...")

        cap.release()
        writer.release()

        self.progress.emit(0.88, "Tonspur wird zusammengeführt (Audio-Muxing)...")

        # Use imageio-ffmpeg binary to mux original audio without re-encoding
        ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
        cmd = [
            ffmpeg_exe,
            "-y",
            "-i",
            str(temp_video_path),
            "-i",
            str(self.input_video_path),
            "-c:v",
            "copy",
            "-c:a",
            "copy",
            "-map",
            "0:v:0",
            "-map",
            "1:a:0?",  # Optional: preserve audio if present
            str(self.output_path),
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, check=False)

        # Cleanup temporary video
        if temp_video_path.exists():
            temp_video_path.unlink()

        if result.returncode != 0:
            self.failed.emit(f"FFmpeg-Fehler beim Muxen:\n{result.stderr}")
            return

        self.progress.emit(1.0, "Export abgeschlossen!")
        self.finished.emit(self.output_path)
