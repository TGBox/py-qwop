"""Game over dialog shown upon runner collapse or finish line victory."""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from py_qwop.config import COLORS


class GameOverDialog(QWidget):
    """End-of-run summary dialog presenting results and options."""

    restart_requested = Signal()
    main_menu_requested = Signal()

    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
        self.setObjectName("GameOverDialog")
        self._build_ui()

    def _build_ui(self) -> None:
        """Construct card layout."""
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.card = QFrame()
        self.card.setFixedWidth(440)
        self.card.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS.ui_panel_bg};
                border: 2px solid {COLORS.ui_accent};
                border-radius: 14px;
                padding: 24px;
            }}
            QLabel {{
                color: {COLORS.ui_text};
                border: none;
            }}
            QPushButton {{
                background-color: {COLORS.ui_card_bg};
                color: {COLORS.ui_text};
                border: 1px solid #4a5d78;
                border-radius: 8px;
                font-size: 15px;
                font-weight: bold;
                padding: 12px 18px;
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

        card_layout = QVBoxLayout(self.card)
        card_layout.setSpacing(14)

        # Header Title
        self.lbl_title = QLabel("GESTÜRZT!")
        self.lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_title.setStyleSheet("font-size: 28px; font-weight: 900; color: #e74c3c; letter-spacing: 2px;")
        card_layout.addWidget(self.lbl_title)

        # Record Badge
        self.lbl_record = QLabel("🏆 NEUER REKORD!")
        self.lbl_record.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_record.setStyleSheet("font-size: 16px; font-weight: bold; color: #f1c40f; padding: 4px; background: rgba(241,196,15,30); border-radius: 6px;")
        self.lbl_record.setVisible(False)
        card_layout.addWidget(self.lbl_record)

        # Stats Container
        stats_box = QFrame()
        stats_box.setStyleSheet(f"background: {COLORS.ui_card_bg}; border-radius: 8px; padding: 12px;")
        stats_layout = QVBoxLayout(stats_box)
        stats_layout.setSpacing(8)

        self.lbl_distance = QLabel("Erreichte Weite: 0.0 m")
        self.lbl_distance.setStyleSheet("font-size: 18px; font-weight: bold; color: #ecf0f1;")
        self.lbl_distance.setAlignment(Qt.AlignmentFlag.AlignCenter)
        stats_layout.addWidget(self.lbl_distance)

        self.lbl_time = QLabel("Benötigte Zeit: 00:00.0")
        self.lbl_time.setStyleSheet(f"font-size: 14px; color: {COLORS.ui_text_dim};")
        self.lbl_time.setAlignment(Qt.AlignmentFlag.AlignCenter)
        stats_layout.addWidget(self.lbl_time)

        card_layout.addWidget(stats_box)

        # Action Buttons
        btn_restart = QPushButton("Erneut versuchen (R)")
        btn_restart.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS.ui_accent};
                color: #ffffff;
                border: none;
            }}
            QPushButton:hover {{
                background-color: {COLORS.ui_accent_hover};
            }}
        """)
        btn_restart.clicked.connect(self.restart_requested.emit)
        card_layout.addWidget(btn_restart)

        btn_menu = QPushButton("Hauptmenü")
        btn_menu.clicked.connect(self.main_menu_requested.emit)
        card_layout.addWidget(btn_menu)

        layout.addWidget(self.card)

    def set_results(self, is_victory: bool, distance: float, time_sec: float, is_new_record: bool) -> None:
        """Update display with run outcome."""
        mins = int(time_sec // 60)
        secs = time_sec % 60

        if is_victory:
            self.lbl_title.setText("ZIEL ERREICHT! 🥇")
            self.lbl_title.setStyleSheet("font-size: 28px; font-weight: 900; color: #2ecc71; letter-spacing: 2px;")
            self.card.setStyleSheet(self.card.styleSheet().replace(COLORS.ui_accent, "#2ecc71"))
        else:
            self.lbl_title.setText("GESTÜRZT!")
            self.lbl_title.setStyleSheet("font-size: 28px; font-weight: 900; color: #e74c3c; letter-spacing: 2px;")
            self.card.setStyleSheet(self.card.styleSheet().replace("#2ecc71", COLORS.ui_accent))

        self.lbl_distance.setText(f"Erreichte Weite: {distance:0.1f} Meter")
        self.lbl_time.setText(f"Benötigte Zeit: {mins:02d}:{secs:04.1f}")
        self.lbl_record.setVisible(is_new_record)

    def paintEvent(self, event) -> None:
        """Dim background with semi-transparent overlay."""
        from PySide6.QtGui import QColor, QPainter
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(0, 0, 0, 170))
