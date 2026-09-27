"""Pause overlay dialog shown when player presses ESC."""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from py_qwop.config import COLORS


class PauseOverlay(QWidget):
    """Semi-transparent overlay displaying the pause menu."""

    resume_requested = Signal()
    restart_requested = Signal()
    main_menu_requested = Signal()

    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
        self.setObjectName("PauseOverlay")
        self._build_ui()

    def _build_ui(self) -> None:
        """Construct pause menu card layout."""
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Container card
        card = QFrame()
        card.setObjectName("PauseCard")
        card.setFixedWidth(380)
        card.setStyleSheet(f"""
            #PauseCard {{
                background-color: {COLORS.ui_panel_bg};
                border: 2px solid {COLORS.ui_accent};
                border-radius: 14px;
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
                border: 1px solid #4a5d78;
                border-radius: 8px;
                font-size: 15px;
                font-weight: bold;
                padding: 10px 16px;
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

        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(16)

        title = QLabel("SPIEL PAUSIERT")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 24px; font-weight: 900; color: #ecf0f1; letter-spacing: 2px;")
        card_layout.addWidget(title)

        subtitle = QLabel("Nimm kurz Atem – die Ziellinie wartet!")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet(f"font-size: 13px; color: {COLORS.ui_text_dim}; margin-bottom: 8px;")
        card_layout.addWidget(subtitle)

        # Buttons
        btn_resume = QPushButton("Fortsetzen (ESC)")
        btn_resume.clicked.connect(self.resume_requested.emit)
        card_layout.addWidget(btn_resume)

        btn_restart = QPushButton("Neu starten (R)")
        btn_restart.clicked.connect(self.restart_requested.emit)
        card_layout.addWidget(btn_restart)

        btn_menu = QPushButton("Hauptmenü")
        btn_menu.clicked.connect(self.main_menu_requested.emit)
        card_layout.addWidget(btn_menu)

        layout.addWidget(card)

    def paintEvent(self, event) -> None:
        """Dim background with dark semi-transparent tint."""
        from PySide6.QtGui import QColor, QPainter
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(0, 0, 0, 160))
