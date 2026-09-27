"""Main application window managing views and fullscreen mode."""

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import QMainWindow, QStackedWidget

from py_qwop.config import (
    WINDOW_DEFAULT_HEIGHT,
    WINDOW_DEFAULT_WIDTH,
    WINDOW_MIN_HEIGHT,
    WINDOW_MIN_WIDTH,
)
from py_qwop.ui.game_widget import GameWidget
from py_qwop.ui.main_menu import MainMenuWidget


class MainWindow(QMainWindow):
    """Top-level game window supporting fullscreen and windowed modes."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("py-qwop – 100m Ragdoll Meisterschaft")
        self.resize(WINDOW_DEFAULT_WIDTH, WINDOW_DEFAULT_HEIGHT)
        self.setMinimumSize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)

        # Central stacked container
        self.stack = QStackedWidget(self)
        self.setCentralWidget(self.stack)

        # Views
        self.main_menu = MainMenuWidget(self)
        self.game_widget = GameWidget(self)

        self.stack.addWidget(self.main_menu)   # Index 0
        self.stack.addWidget(self.game_widget) # Index 1

        # Connect view navigation signals
        self.main_menu.start_game_requested.connect(self.show_game)
        self.main_menu.toggle_fullscreen_requested.connect(self.toggle_fullscreen)
        self.main_menu.exit_requested.connect(self.close)

        self.game_widget.main_menu_requested.connect(self.show_menu)
        self.game_widget.toggle_fullscreen_requested.connect(self.toggle_fullscreen)

        # Global Fullscreen Action (F11)
        self.fs_action = QAction("Vollbild umschalten", self)
        self.fs_action.setShortcut(QKeySequence(Qt.Key.Key_F11))
        self.fs_action.triggered.connect(self.toggle_fullscreen)
        self.addAction(self.fs_action)

        self.show_menu()

    def show_menu(self) -> None:
        """Switch view to the main start menu."""
        self.main_menu.refresh_stats()
        self.main_menu.update_fullscreen_button_text(self.isFullScreen())
        self.stack.setCurrentIndex(0)

    def show_game(self) -> None:
        """Switch view to the game canvas and start running."""
        self.game_widget.is_fullscreen = self.isFullScreen()
        self.stack.setCurrentIndex(1)
        self.game_widget.start_new_game()

    def toggle_fullscreen(self) -> None:
        """Toggle between borderless fullscreen and windowed mode."""
        if self.isFullScreen():
            self.showNormal()
            self.game_widget.is_fullscreen = False
            self.main_menu.update_fullscreen_button_text(False)
        else:
            self.showFullScreen()
            self.game_widget.is_fullscreen = True
            self.main_menu.update_fullscreen_button_text(True)
