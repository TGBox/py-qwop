"""Settings dialog for key remapping, ghost runner toggle, and record management."""

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QKeySequence
from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
)

from py_qwop.config import COLORS, DEFAULT_KEY_BINDINGS
from py_qwop.storage import STORAGE


class KeyBindButton(QPushButton):
    """Button that listens for a key press to assign a new key binding."""

    key_changed = Signal(int)

    def __init__(self, key_code: int, parent=None):
        super().__init__(parent)
        self.key_code = key_code
        self.listening = False
        self._update_text()

    def _update_text(self) -> None:
        if self.listening:
            self.setText("Drücke eine Taste...")
            self.setStyleSheet(f"background-color: {COLORS.ui_warning}; color: #000000; font-weight: bold;")
        else:
            name = QKeySequence(self.key_code).toString()
            self.setText(name if name else f"Key {self.key_code}")
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: {COLORS.ui_card_bg};
                    color: {COLORS.ui_text};
                    border: 1px solid #4a5d78;
                    border-radius: 6px;
                    padding: 6px 12px;
                    font-weight: bold;
                    min-width: 90px;
                }}
                QPushButton:hover {{
                    border-color: {COLORS.ui_accent};
                    background-color: #2c384a;
                }}
            """)

    def mousePressEvent(self, event):
        self.listening = True
        self._update_text()
        self.setFocus()

    def keyPressEvent(self, event):
        if self.listening:
            key = event.key()
            if key not in (Qt.Key.Key_Escape, Qt.Key.Key_unknown):
                self.key_code = key
                self.listening = False
                self._update_text()
                self.key_changed.emit(key)
            else:
                self.listening = False
                self._update_text()
        else:
            super().keyPressEvent(event)


class SettingsDialog(QDialog):
    """Settings modal configuration for controls, ghost runner, and highscores."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Einstellungen – py-qwop")
        self.setFixedSize(520, 500)
        self.setModal(True)

        self.data = STORAGE.load_data()
        self.key_bindings: dict[str, int] = dict(self.data.get("key_bindings", {}))
        self.bind_buttons: dict[str, KeyBindButton] = {}

        self._build_ui()

    def _build_ui(self) -> None:
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {COLORS.ui_dark_bg};
                color: {COLORS.ui_text};
            }}
            QLabel {{
                color: {COLORS.ui_text};
                font-size: 14px;
            }}
            QCheckBox {{
                color: {COLORS.ui_text};
                font-size: 14px;
                spacing: 8px;
            }}
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border-radius: 4px;
                border: 1px solid #4a5d78;
                background: {COLORS.ui_card_bg};
            }}
            QCheckBox::indicator:checked {{
                background: {COLORS.ui_accent};
                border-color: {COLORS.ui_accent};
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)

        # Title
        title = QLabel("EINSTELLUNGEN")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #ecf0f1;")
        layout.addWidget(title)

        # 1. Key Bindings Box
        kb_box = QFrame()
        kb_box.setObjectName("KBBox")
        kb_box.setStyleSheet(f"""
            #KBBox {{
                background-color: {COLORS.ui_panel_bg};
                border-radius: 10px;
            }}
            QLabel {{
                background: transparent;
                border: none;
                padding: 0px;
                color: {COLORS.ui_text};
            }}
        """)
        grid = QGridLayout(kb_box)
        grid.setContentsMargins(16, 14, 16, 14)
        grid.setSpacing(10)

        actions = [
            ("thigh_q", "Oberschenkel Vor/Rück (Original Q):"),
            ("thigh_w", "Oberschenkel Rück/Vor (Original W):"),
            ("calf_o", "Waden Beugen/Strecken (Original O):"),
            ("calf_p", "Waden Strecken/Beugen (Original P):"),
            ("restart", "Neustart (Original R):"),
        ]

        for row, (action_key, label_text) in enumerate(actions):
            lbl = QLabel(label_text)
            lbl.setStyleSheet("font-weight: 500;")
            key_code = self.key_bindings.get(action_key, int(DEFAULT_KEY_BINDINGS.get(action_key, Qt.Key.Key_Space)))
            btn = KeyBindButton(key_code)
            btn.key_changed.connect(lambda k, ak=action_key: self._on_key_rebound(ak, k))
            self.bind_buttons[action_key] = btn

            grid.addWidget(lbl, row, 0)
            grid.addWidget(btn, row, 1)

        layout.addWidget(kb_box)

        # 2. Gameplay Options
        opt_box = QFrame()
        opt_box.setObjectName("OptBox")
        opt_box.setStyleSheet(f"""
            #OptBox {{
                background-color: {COLORS.ui_panel_bg};
                border-radius: 10px;
            }}
            QCheckBox {{
                background: transparent;
            }}
        """)
        opt_layout = QVBoxLayout(opt_box)
        opt_layout.setContentsMargins(16, 14, 16, 14)
        opt_layout.setSpacing(10)

        self.chk_ghost = QCheckBox("Ghost-Runner anzeigen (Schattenläufer des besten Laufs)")
        self.chk_ghost.setChecked(self.data.get("settings", {}).get("ghost_runner_enabled", True))
        opt_layout.addWidget(self.chk_ghost)

        layout.addWidget(opt_box)

        # 3. Actions / Reset
        btn_reset_keys = QPushButton("Tasten auf Standard zurücksetzen")
        btn_reset_keys.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {COLORS.ui_text_dim};
                border: 1px solid #4a5d78;
                border-radius: 6px;
                padding: 6px 12px;
            }}
            QPushButton:hover {{
                color: {COLORS.ui_text};
                border-color: {COLORS.ui_accent};
            }}
        """)
        btn_reset_keys.clicked.connect(self._reset_default_keys)
        layout.addWidget(btn_reset_keys)

        # Dialog Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        btn_save = QPushButton("Speichern & Schließen")
        btn_save.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS.ui_accent};
                color: #ffffff;
                font-weight: bold;
                border: none;
                border-radius: 6px;
                padding: 8px 18px;
            }}
            QPushButton:hover {{
                background-color: {COLORS.ui_accent_hover};
            }}
        """)
        btn_save.clicked.connect(self._save_and_close)
        btn_layout.addWidget(btn_save)

        layout.addLayout(btn_layout)

    def _on_key_rebound(self, action: str, new_key: int) -> None:
        self.key_bindings[action] = new_key

    def _reset_default_keys(self) -> None:
        for action, default_qt_key in DEFAULT_KEY_BINDINGS.items():
            k_val = int(default_qt_key)
            self.key_bindings[action] = k_val
            if action in self.bind_buttons:
                self.bind_buttons[action].key_code = k_val
                self.bind_buttons[action]._update_text()

    def _save_and_close(self) -> None:
        self.data["key_bindings"] = self.key_bindings
        if "settings" not in self.data:
            self.data["settings"] = {}
        self.data["settings"]["ghost_runner_enabled"] = self.chk_ghost.isChecked()
        STORAGE.save_data(self.data)
        self.accept()
