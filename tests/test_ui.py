"""Unit tests for PySide6 UI widgets and fullscreen management."""

import os
import sys

import pytest
from PySide6.QtWidgets import QApplication

# Ensure offscreen platform for headless test execution
os.environ["QT_QPA_PLATFORM"] = "offscreen"


@pytest.fixture(scope="session")
def qapp():
    """Ensure single persistent QApplication instance."""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    return app


def test_main_window_and_fullscreen_toggle(qapp):
    """Verify MainWindow creation, view switching, and fullscreen toggle."""
    from py_qwop.ui.main_window import MainWindow

    window = MainWindow()
    assert window.stack.count() == 2

    # Initial view is MainMenu (index 0)
    assert window.stack.currentIndex() == 0

    # Switch to GameWidget
    window.show_game()
    assert window.stack.currentIndex() == 1

    # Switch back to MainMenu
    window.show_menu()
    assert window.stack.currentIndex() == 0

    # Test fullscreen toggle calls
    window.toggle_fullscreen()
    assert window.isFullScreen()

    window.toggle_fullscreen()
    assert not window.isFullScreen()

    window.close()


def test_settings_dialog_initialization(qapp):
    """Verify settings modal dialog initialization and controls."""
    from py_qwop.ui.settings_dialog import SettingsDialog

    dialog = SettingsDialog()
    assert "thigh_q" in dialog.bind_buttons
    assert "calf_o" in dialog.bind_buttons
    assert dialog.chk_ghost is not None
    dialog.close()


def test_game_widget_key_events_and_pause(qapp):
    """Verify game canvas responds to pause and restart."""
    from py_qwop.ui.game_widget import GameWidget

    widget = GameWidget()
    widget.show()
    assert widget.state == GameWidget.STATE_PLAYING

    # Test pause
    widget.pause_game()
    assert widget.state == GameWidget.STATE_PAUSED
    assert not widget.pause_overlay.isHidden()

    # Test resume
    widget.resume_game()
    assert widget.state == GameWidget.STATE_PLAYING
    assert widget.pause_overlay.isHidden()

    # Test restart
    widget.restart_game()
    assert widget.state == GameWidget.STATE_PLAYING

    widget.close()
