"""Main menu screen with start game, records display, settings, and instructions."""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)
from py_qwop.config import COLORS
from py_qwop.storage import STORAGE
from py_qwop.ui.settings_dialog import SettingsDialog


class MainMenuWidget(QWidget):
    """Start menu screen for py-qwop."""

    start_game_requested = Signal()
    toggle_fullscreen_requested = Signal()
    exit_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("MainMenuWidget")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self._build_ui()
        self.refresh_stats()

    def _build_ui(self) -> None:
        self.setStyleSheet(f"""
            QWidget#MainMenuWidget {{
                background-color: {COLORS.ui_dark_bg};
            }}
            #MenuCard {{
                background-color: {COLORS.ui_panel_bg};
                border: 2px solid #2f3e52;
                border-radius: 18px;
            }}
            #ScoresBox {{
                background-color: {COLORS.ui_card_bg};
                border: 1px solid #3d4d63;
                border-radius: 10px;
            }}
            QLabel {{
                background: transparent;
                border: none;
                padding: 0px;
                color: {COLORS.ui_text};
            }}
            QPushButton {{
                background-color: {COLORS.ui_card_bg};
                color: {COLORS.ui_text};
                border: 1px solid #3d4d63;
                border-radius: 10px;
                font-size: 16px;
                font-weight: bold;
                padding: 12px 20px;
                min-width: 240px;
                min-height: 24px;
            }}
            QPushButton:hover {{
                background-color: {COLORS.ui_accent};
                color: #ffffff;
                border-color: {COLORS.ui_accent_hover};
            }}
            QPushButton:pressed {{
                background-color: {COLORS.ui_accent_hover};
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setContentsMargins(40, 30, 40, 30)

        # Center Card
        card = QFrame()
        card.setObjectName("MenuCard")
        card.setFixedWidth(560)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(36, 32, 36, 32)
        card_layout.setSpacing(18)
        card_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Logo Title
        title_box = QVBoxLayout()
        title_box.setSpacing(6)

        lbl_title = QLabel("PY-QWOP")
        lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_title.setStyleSheet("font-size: 44px; font-weight: 900; color: #3498db; letter-spacing: 4px;")
        title_box.addWidget(lbl_title)

        lbl_sub = QLabel("100m Ragdoll-Physik Meisterschaft")
        lbl_sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_sub.setStyleSheet(f"font-size: 14px; font-weight: bold; color: {COLORS.ui_text_dim};")
        title_box.addWidget(lbl_sub)
        card_layout.addLayout(title_box)

        # Highscores Panel
        self.scores_box = QFrame()
        self.scores_box.setObjectName("ScoresBox")
        scores_layout = QVBoxLayout(self.scores_box)
        scores_layout.setContentsMargins(18, 14, 18, 14)
        scores_layout.setSpacing(6)

        lbl_record_header = QLabel("🏆 PERSÖNLICHE REKORDE")
        lbl_record_header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_record_header.setStyleSheet("font-size: 13px; font-weight: bold; color: #f1c40f;")
        scores_layout.addWidget(lbl_record_header)

        self.lbl_best_dist = QLabel("Weiteste Distanz: 0.0 m")
        self.lbl_best_dist.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_best_dist.setStyleSheet("font-size: 15px; font-weight: bold; color: #ecf0f1;")
        scores_layout.addWidget(self.lbl_best_dist)

        self.lbl_best_time = QLabel("Bestzeit (100m): Noch kein Zieleinlauf")
        self.lbl_best_time.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_best_time.setStyleSheet(f"font-size: 13px; color: {COLORS.ui_text_dim};")
        scores_layout.addWidget(self.lbl_best_time)

        card_layout.addWidget(self.scores_box)

        # Action Buttons
        btn_start = QPushButton("Lauf starten")
        btn_start.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS.ui_accent};
                color: #ffffff;
                font-size: 18px;
                padding: 14px 24px;
                border: none;
            }}
            QPushButton:hover {{
                background-color: {COLORS.ui_accent_hover};
            }}
        """)
        btn_start.clicked.connect(self.start_game_requested.emit)
        card_layout.addWidget(btn_start)

        btn_settings = QPushButton("Steuerung && Einstellungen")
        btn_settings.clicked.connect(self._open_settings)
        card_layout.addWidget(btn_settings)

        self.btn_fullscreen = QPushButton("Vollbildmodus (F11)")
        self.btn_fullscreen.clicked.connect(self.toggle_fullscreen_requested.emit)
        card_layout.addWidget(self.btn_fullscreen)

        btn_exit = QPushButton("Beenden")
        btn_exit.clicked.connect(self.exit_requested.emit)
        card_layout.addWidget(btn_exit)

        # Quick Instructions
        instructions = QLabel(
            "<b>Steuerung:</b> Q & W steuern die Oberschenkel, O & P steuern die Knie/Waden.<br>"
            "Ziel: Erreiche die 100m-Ziellinie, ohne mit Kopf oder Oberkörper zu stürzen!"
        )
        instructions.setAlignment(Qt.AlignmentFlag.AlignCenter)
        instructions.setStyleSheet(f"font-size: 12px; color: {COLORS.ui_text_dim}; margin-top: 10px; line-height: 1.4;")
        card_layout.addWidget(instructions)

        layout.addWidget(card)

    def refresh_stats(self) -> None:
        """Reload and display current records from storage."""
        data = STORAGE.load_data()
        highscores = data.get("highscores", {})
        dist = highscores.get("max_distance", 0.0)
        time_100 = highscores.get("best_time_100m")

        self.lbl_best_dist.setText(f"Weiteste Distanz: {dist:0.1f} Meter")
        if time_100 is not None:
            mins = int(time_100 // 60)
            secs = time_100 % 60
            self.lbl_best_time.setText(f"Bestzeit (100m): {mins:02d}:{secs:04.1f} Min.")
        else:
            self.lbl_best_time.setText("Bestzeit (100m): Noch kein Zieleinlauf")

    def update_fullscreen_button_text(self, is_fullscreen: bool) -> None:
        """Update button label depending on current window state."""
        if is_fullscreen:
            self.btn_fullscreen.setText("Fenstermodus (F11)")
        else:
            self.btn_fullscreen.setText("Vollbildmodus (F11)")

    def _open_settings(self) -> None:
        """Display settings modal dialog."""
        dialog = SettingsDialog(self)
        dialog.exec()
        self.refresh_stats()
