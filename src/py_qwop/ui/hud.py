"""In-game heads-up display rendering distance scoreboard, timer, speed, and key status."""

from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import (
    QColor,
    QFont,
    QPainter,
    QPen,
)

from py_qwop.config import COLORS


class InGameHUD:
    """Renders digital scoreboard, live metrics, and visual keypress indicators."""

    def __init__(self):
        self.font_big = QFont("Arial", 28, QFont.Weight.Black)
        self.font_mid = QFont("Arial", 14, QFont.Weight.Bold)
        self.font_small = QFont("Arial", 10, QFont.Weight.Bold)

    def render(
        self,
        painter: QPainter,
        width: int,
        height: int,
        distance: float,
        time_elapsed: float,
        speed_kmh: float,
        keys_pressed: dict[str, bool],
        key_names: dict[str, str],
        is_fullscreen: bool,
    ) -> None:
        """Render HUD elements over the game scene."""
        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        # 1. Top Distance Scoreboard
        self._render_distance_board(painter, width, distance)

        # 2. Top-Left Metrics (Time and Speed)
        self._render_metrics(painter, time_elapsed, speed_kmh)

        # 3. Top-Right Controls Helper
        self._render_controls_helper(painter, width, is_fullscreen)

        # 4. Bottom Key Visualizer (Q, W, O, P)
        self._render_key_indicators(painter, width, height, keys_pressed, key_names)

        painter.restore()

    def _render_distance_board(self, painter: QPainter, width: int, distance: float) -> None:
        """Central digital stadium scoreboard showing current meter distance."""
        board_w = 260
        board_h = 65
        x = (width - board_w) / 2
        y = 16

        # Scoreboard panel with dark glass effect
        panel_rect = QRectF(x, y, board_w, board_h)
        painter.setPen(QPen(QColor(COLORS.ui_accent), 2))
        painter.setBrush(QColor(18, 24, 34, 235))
        painter.drawRoundedRect(panel_rect, 10, 10)

        # Subtitle
        painter.setFont(self.font_small)
        painter.setPen(QColor(COLORS.ui_text_dim))
        painter.drawText(
            QRectF(x, y + 6, board_w, 18),
            Qt.AlignmentFlag.AlignCenter,
            "DISTANZ",
        )

        # Main Distance Number
        dist_sign = "+" if distance >= 0 else ""
        dist_str = f"{dist_sign}{distance:0.1f} m"

        painter.setFont(self.font_big)
        # Highlight green if moving forward, yellow if past 50m, gold if over 100m
        if distance >= 100.0:
            num_color = QColor("#f1c40f")
        elif distance >= 50.0:
            num_color = QColor("#2ecc71")
        elif distance > 0.0:
            num_color = QColor("#ecf0f1")
        else:
            num_color = QColor("#e74c3c")

        painter.setPen(num_color)
        painter.drawText(
            QRectF(x, y + 20, board_w, 40),
            Qt.AlignmentFlag.AlignCenter,
            dist_str,
        )

    def _render_metrics(self, painter: QPainter, time_sec: float, speed_kmh: float) -> None:
        """Top-left panel displaying elapsed running time and current speed."""
        panel_w = 175
        panel_h = 65
        x = 20
        y = 16

        rect = QRectF(x, y, panel_w, panel_h)
        painter.setPen(QPen(QColor(255, 255, 255, 40), 1.5))
        painter.setBrush(QColor(18, 24, 34, 210))
        painter.drawRoundedRect(rect, 8, 8)

        # Time formatting: mm:ss.d
        mins = int(time_sec // 60)
        secs = time_sec % 60
        time_str = f"Zeit: {mins:02d}:{secs:04.1f}"
        speed_str = f"Tempo: {max(0.0, speed_kmh):0.1f} km/h"

        painter.setFont(self.font_mid)
        painter.setPen(QColor(COLORS.ui_text))
        painter.drawText(QRectF(x + 12, y + 10, panel_w - 24, 22), Qt.AlignmentFlag.AlignLeft, time_str)

        painter.setFont(self.font_small)
        painter.setPen(QColor(COLORS.ui_text_dim))
        painter.drawText(QRectF(x + 12, y + 36, panel_w - 24, 20), Qt.AlignmentFlag.AlignLeft, speed_str)

    def _render_controls_helper(self, painter: QPainter, width: int, is_fullscreen: bool) -> None:
        """Top-right helper bar showing keyboard shortcuts."""
        panel_w = 210
        panel_h = 65
        x = width - panel_w - 20
        y = 16

        rect = QRectF(x, y, panel_w, panel_h)
        painter.setPen(QPen(QColor(255, 255, 255, 40), 1.5))
        painter.setBrush(QColor(18, 24, 34, 210))
        painter.drawRoundedRect(rect, 8, 8)

        painter.setFont(self.font_small)
        painter.setPen(QColor(COLORS.ui_text_dim))
        fs_label = "Fenster" if is_fullscreen else "Vollbild"
        painter.drawText(QRectF(x + 12, y + 10, panel_w - 24, 18), Qt.AlignmentFlag.AlignLeft, "R: Neustart")
        painter.drawText(QRectF(x + 12, y + 26, panel_w - 24, 18), Qt.AlignmentFlag.AlignLeft, "ESC: Pause")
        painter.drawText(QRectF(x + 12, y + 42, panel_w - 24, 18), Qt.AlignmentFlag.AlignLeft, f"F11: {fs_label}")

    def _render_key_indicators(
        self,
        painter: QPainter,
        width: int,
        height: int,
        keys_pressed: dict[str, bool],
        key_names: dict[str, str],
    ) -> None:
        """Bottom interactive keyboard visualizer showing Q, W, O, P muscle contraction."""
        container_w = 420
        container_h = 70
        cx = (width - container_w) / 2
        cy = height - container_h - 20

        # Background dock
        dock_rect = QRectF(cx, cy, container_w, container_h)
        painter.setPen(QPen(QColor(255, 255, 255, 30), 1.5))
        painter.setBrush(QColor(18, 24, 34, 215))
        painter.drawRoundedRect(dock_rect, 12, 12)

        key_btn_size = 44

        # Group 1: Thighs (Q, W)
        q_pressed = keys_pressed.get("thigh_q", False)
        w_pressed = keys_pressed.get("thigh_w", False)
        self._draw_key_button(
            painter,
            cx + 25,
            cy + 13,
            key_btn_size,
            key_names.get("thigh_q", "Q"),
            q_pressed,
        )
        self._draw_key_button(
            painter,
            cx + 78,
            cy + 13,
            key_btn_size,
            key_names.get("thigh_w", "W"),
            w_pressed,
        )

        painter.setFont(self.font_small)
        painter.setPen(QColor(COLORS.ui_text_dim))
        painter.drawText(
            QRectF(cx + 15, cy + container_h - 18, 115, 14),
            Qt.AlignmentFlag.AlignCenter,
            "Oberschenkel",
        )

        # Center Divider
        painter.setPen(QPen(QColor(255, 255, 255, 40), 1))
        painter.drawLine(int(cx + container_w / 2), int(cy + 10), int(cx + container_w / 2), int(cy + container_h - 10))

        # Group 2: Calves (O, P)
        o_pressed = keys_pressed.get("calf_o", False)
        p_pressed = keys_pressed.get("calf_p", False)
        self._draw_key_button(
            painter,
            cx + container_w - 122,
            cy + 13,
            key_btn_size,
            key_names.get("calf_o", "O"),
            o_pressed,
        )
        self._draw_key_button(
            painter,
            cx + container_w - 69,
            cy + 13,
            key_btn_size,
            key_names.get("calf_p", "P"),
            p_pressed,
        )

        painter.drawText(
            QRectF(cx + container_w - 130, cy + container_h - 18, 115, 14),
            Qt.AlignmentFlag.AlignCenter,
            "Waden / Knie",
        )

    def _draw_key_button(
        self,
        painter: QPainter,
        x: float,
        y: float,
        size: float,
        label: str,
        is_pressed: bool,
    ) -> None:
        """Draw an illuminated arcade keycap with pressed state."""
        offset_y = 3.0 if is_pressed else 0.0
        rect = QRectF(x, y + offset_y, size, size)

        # Key styling
        if is_pressed:
            fill_color = QColor(COLORS.ui_accent)
            border_color = QColor("#5dade2")
            text_color = QColor("#ffffff")
        else:
            fill_color = QColor(38, 48, 64)
            border_color = QColor(60, 75, 98)
            text_color = QColor(COLORS.ui_text)

        painter.setBrush(fill_color)
        painter.setPen(QPen(border_color, 2))
        painter.drawRoundedRect(rect, 8, 8)

        # Key label
        painter.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        painter.setPen(text_color)
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, label)
