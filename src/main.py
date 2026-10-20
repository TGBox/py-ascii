"""Application entrypoint for py-ascii."""

import sys

from PySide6.QtWidgets import QApplication

from src.ui.main_window import MainWindow


def main() -> None:
    """Initializes Qt application and launches the main window."""
    app = QApplication(sys.argv)
    app.setApplicationName("py-ascii")
    app.setOrganizationName("py-ascii")

    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
