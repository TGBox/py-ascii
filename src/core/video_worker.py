"""Asynchronous video player and frame processor running in a dedicated QThread."""

import time
from pathlib import Path

import cv2
from PySide6.QtCore import QMutex, QMutexLocker, QThread, Signal

from src.core.ascii_converter import AsciiConfig, AsciiConverter, AsciiFrame


class VideoWorker(QThread):
    """Worker thread that reads video frames via OpenCV and emits converted AsciiFrames."""

    frame_ready = Signal(AsciiFrame)
    progress_changed = Signal(int, int)  # current_frame, total_frames
    state_changed = Signal(bool)  # is_playing
    media_loaded = Signal(int, float, int, int)  # total_frames, fps, width, height
    error_occurred = Signal(str)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._mutex = QMutex()
        self._cap: cv2.VideoCapture | None = None
        self._file_path: Path | None = None

        self._config: AsciiConfig = AsciiConfig()
        self._is_playing: bool = False
        self._is_running: bool = True
        self._loop: bool = True

        self._total_frames: int = 0
        self._fps: float = 30.0
        self._current_frame_idx: int = 0
        self._seek_requested: int | None = None

    def load_video(self, file_path: Path | str) -> bool:
        """Loads a video file and emits initial preview frame."""
        path = Path(file_path)
        if not path.exists():
            self.error_occurred.emit(f"Videodatei '{path}' existiert nicht.")
            return False

        with QMutexLocker(self._mutex):
            if self._cap is not None:
                self._cap.release()

            cap = cv2.VideoCapture(str(path))
            if not cap.isOpened():
                self.error_occurred.emit(f"Videodatei '{path.name}' konnte nicht geöffnet werden.")
                return False

            self._cap = cap
            self._file_path = path

            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = float(cap.get(cv2.CAP_PROP_FPS))
            if fps <= 0.0 or fps > 120.0:
                fps = 30.0

            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

            self._total_frames = max(1, total_frames)
            self._fps = fps
            self._current_frame_idx = 0
            self._seek_requested = None
            self._is_playing = False

            # Grab and emit the first frame as preview
            ret, frame = cap.read()
            if ret and frame is not None:
                ascii_frame = AsciiConverter.convert(frame, self._config)
                self.frame_ready.emit(ascii_frame)
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

        self.media_loaded.emit(self._total_frames, self._fps, width, height)
        self.progress_changed.emit(0, self._total_frames)
        self.state_changed.emit(False)
        return True

    def set_config(self, config: AsciiConfig) -> None:
        """Updates the conversion settings thread-safely."""
        with QMutexLocker(self._mutex):
            self._config = config

    def play(self) -> None:
        """Starts video playback."""
        with QMutexLocker(self._mutex):
            if self._cap is not None and not self._is_playing:
                self._is_playing = True
                self.state_changed.emit(True)

    def pause(self) -> None:
        """Pauses video playback."""
        with QMutexLocker(self._mutex):
            if self._is_playing:
                self._is_playing = False
                self.state_changed.emit(False)

    def toggle_play(self) -> None:
        """Toggles between play and pause."""
        with QMutexLocker(self._mutex):
            is_playing = not self._is_playing
            self._is_playing = is_playing
        self.state_changed.emit(is_playing)

    def stop(self) -> None:
        """Stops playback and resets to beginning."""
        with QMutexLocker(self._mutex):
            self._is_playing = False
            self._seek_requested = 0
        self.state_changed.emit(False)

    def seek(self, frame_idx: int) -> None:
        """Requests seeking to a specific frame index."""
        with QMutexLocker(self._mutex):
            self._seek_requested = max(0, min(self._total_frames - 1, frame_idx))

    def set_loop(self, loop: bool) -> None:
        """Enables or disables continuous loop playback."""
        with QMutexLocker(self._mutex):
            self._loop = loop

    def terminate_worker(self) -> None:
        """Signals thread to finish execution and release resources."""
        with QMutexLocker(self._mutex):
            self._is_running = False
            self._is_playing = False
        if self.isRunning():
            self.quit()
            self.wait(2000)
        with QMutexLocker(self._mutex):
            if self._cap is not None:
                self._cap.release()
                self._cap = None

    def run(self) -> None:
        """Main playback loop pacing frames according to original FPS."""
        while True:
            frame_to_process = None
            current_idx = 0
            frame_delay = 1.0 / max(1.0, self._fps)

            with QMutexLocker(self._mutex):
                if not self._is_running:
                    break

                cap = self._cap
                if cap is None:
                    should_sleep = True
                else:
                    # Check if a seek was requested
                    if self._seek_requested is not None:
                        cap.set(cv2.CAP_PROP_POS_FRAMES, self._seek_requested)
                        self._current_frame_idx = self._seek_requested
                        self._seek_requested = None
                        ret, frame = cap.read()
                        if ret and frame is not None:
                            frame_to_process = frame.copy()
                            current_idx = self._current_frame_idx
                        should_sleep = False
                    elif self._is_playing:
                        ret, frame = cap.read()
                        if ret and frame is not None:
                            frame_to_process = frame.copy()
                            self._current_frame_idx += 1
                            current_idx = self._current_frame_idx
                            should_sleep = False
                        else:
                            # End of video reached
                            if self._loop:
                                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                                self._current_frame_idx = 0
                                should_sleep = False
                            else:
                                self._is_playing = False
                                self.state_changed.emit(False)
                                should_sleep = True
                    else:
                        should_sleep = True

                active_config = self._config
                total_frames = self._total_frames

            if should_sleep:
                time.sleep(0.015)
                continue

            start_time = time.perf_counter()

            if frame_to_process is not None:
                ascii_frame = AsciiConverter.convert(frame_to_process, active_config)
                self.frame_ready.emit(ascii_frame)
                self.progress_changed.emit(current_idx, total_frames)

            # Throttle to match target FPS
            elapsed = time.perf_counter() - start_time
            sleep_duration = frame_delay - elapsed
            if sleep_duration > 0.001:
                time.sleep(sleep_duration)
