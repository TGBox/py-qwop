"""py-qwop - Python adaptation of QWOP physics running game."""

import sys

from PySide6.QtWidgets import QApplication

from py_qwop.ui.main_window import MainWindow

__version__ = "0.1.0"
__all__ = ["MainWindow", "main"]


def main() -> None:
    """Application entry point."""
    # Enable high-DPI scaling attributes if necessary
    app = QApplication(sys.argv)
    app.setApplicationName("py-qwop")
    app.setApplicationDisplayName("py-qwop – 100m Ragdoll Meisterschaft")

    window = MainWindow()
    window.show()

    sys.exit(app.exec())
