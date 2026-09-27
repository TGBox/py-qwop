"""Olympic stadium environment, parallax stands, distance markings, hurdle, and finish arch."""

import math

import pymunk
from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import (
    QBrush,
    QColor,
    QFont,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QPen,
)

from py_qwop.config import (
    COLORS,
    FINISH_LINE_X,
    SAND_PIT_END_X,
    SAND_PIT_START_X,
)
from py_qwop.render.camera import Camera


class StadiumRenderer:
    """Renders the Olympic stadium background, running track, and obstacles."""

    def __init__(self):
        # Deterministic crowd color seeds
        self._crowd_rows = 4
        self._crowd_cols = 120
        self._crowd_palette = [
            QColor(COLORS.crowd_colors[i % len(COLORS.crowd_colors)])
            for i in range(20)
        ]

    def render(
        self,
        painter: QPainter,
        camera: Camera,
        hurdle_body: pymunk.Body = None,
        anim_time: float = 0.0,
    ) -> None:
        """Render all environment layers in back-to-front order."""
        ground_y = camera.get_ground_screen_y()
        w = camera.width

        # 1. Sky Gradient
        self._render_sky(painter, w, ground_y)

        # 2. Stadium Canopy and Floodlight Towers
        self._render_stadium_structure(painter, camera, ground_y)

        # 3. Parallax Grandstands & Crowd
        self._render_crowd(painter, camera, ground_y, anim_time)

        # 4. Tartan Track and Distance Markings
        self._render_track(painter, camera, ground_y)

        # 5. Long Jump Sand Pit
        self._render_sand_pit(painter, camera, ground_y)

        # 6. Physical 50m Hurdle
        if hurdle_body:
            self._render_hurdle(painter, camera, hurdle_body)

        # 7. 100m Finish Arch
        self._render_finish_arch(painter, camera)

    def _render_sky(self, painter: QPainter, w: int, ground_y: float) -> None:
        """Gradient sky background."""
        sky_grad = QLinearGradient(0, 0, 0, ground_y)
        sky_grad.setColorAt(0.0, QColor(COLORS.sky_top))
        sky_grad.setColorAt(1.0, QColor(COLORS.sky_bottom))
        painter.fillRect(0, 0, w, int(ground_y), QBrush(sky_grad))

    def _render_stadium_structure(self, painter: QPainter, camera: Camera, ground_y: float) -> None:
        """Background stadium roof curve and floodlight towers with slow parallax."""
        painter.save()
        parallax_x = -camera.pos_x * 12.0  # Slow background shift

        # Floodlight towers in far background
        tower_color = QColor(COLORS.stadium_seats_2)
        tower_color.setAlpha(160)
        painter.setBrush(tower_color)
        painter.setPen(Qt.PenStyle.NoPen)

        for i in range(-2, 10):
            base_x = (i * 350) + (parallax_x % 350)
            # Pylon
            poly = [
                QPointF(base_x - 15, ground_y - 120),
                QPointF(base_x - 6, ground_y - 320),
                QPointF(base_x + 6, ground_y - 320),
                QPointF(base_x + 15, ground_y - 120),
            ]
            painter.drawPolygon(poly)
            # Light bank
            painter.drawRect(int(base_x - 28), int(ground_y - 335), 56, 18)
            # Light glow
            glow = QColor(255, 255, 220, 35)
            painter.setBrush(glow)
            painter.drawEllipse(int(base_x - 40), int(ground_y - 350), 80, 50)
            painter.setBrush(tower_color)

        # Stadium roof canopy
        roof_grad = QLinearGradient(0, 0, 0, ground_y * 0.4)
        roof_grad.setColorAt(0.0, QColor(COLORS.stadium_roof))
        roof_grad.setColorAt(1.0, QColor(COLORS.stadium_seats_1))

        roof_path = QPainterPath()
        roof_path.moveTo(0, 0)
        roof_path.lineTo(camera.width, 0)
        roof_path.lineTo(camera.width, ground_y * 0.32)
        roof_path.quadTo(camera.width * 0.5, ground_y * 0.22, 0, ground_y * 0.32)
        roof_path.closeSubpath()

        painter.fillPath(roof_path, QBrush(roof_grad))
        painter.restore()

    def _render_crowd(self, painter: QPainter, camera: Camera, ground_y: float, anim_time: float) -> None:
        """Spectator grandstand tiers with animated crowd heads."""
        painter.save()
        stand_top = ground_y - 150
        stand_height = 150

        # Tier background
        tier_grad = QLinearGradient(0, stand_top, 0, ground_y)
        tier_grad.setColorAt(0.0, QColor(COLORS.stadium_seats_1))
        tier_grad.setColorAt(1.0, QColor(COLORS.stadium_seats_2))
        painter.fillRect(0, int(stand_top), camera.width, int(stand_height), QBrush(tier_grad))

        # Crowd dots
        parallax_offset = camera.pos_x * 35.0  # Medium parallax
        dot_spacing = 16.0
        row_height = 24.0

        painter.setPen(Qt.PenStyle.NoPen)
        for row in range(5):
            y_base = stand_top + 20 + (row * row_height)
            # Draw spectators in row
            start_col = int((parallax_offset - 20) / dot_spacing)
            end_col = start_col + int(camera.width / dot_spacing) + 4

            for col in range(start_col, end_col):
                x_pos = (col * dot_spacing) - parallax_offset
                color_idx = (col * 7 + row * 13) % len(self._crowd_palette)
                color = self._crowd_palette[color_idx]

                # Subtle cheer bounce
                bounce = math.sin(anim_time * 4.0 + col * 0.8 + row) * 2.5
                painter.setBrush(color)
                painter.drawEllipse(QPointF(x_pos, y_base + bounce), 4.5, 4.5)

        # Stadium railing / wall
        painter.setBrush(QColor("#1f2937"))
        painter.drawRect(0, int(ground_y - 12), camera.width, 12)
        painter.setBrush(QColor("#e5e7eb"))
        painter.drawRect(0, int(ground_y - 14), camera.width, 2)

        painter.restore()

    def _render_track(self, painter: QPainter, camera: Camera, ground_y: float) -> None:
        """Render the Tartan running track, lanes, and distance markings."""
        painter.save()
        track_height = camera.height - ground_y

        # Tartan surface
        track_grad = QLinearGradient(0, ground_y, 0, camera.height)
        track_grad.setColorAt(0.0, QColor(COLORS.tartan_track))
        track_grad.setColorAt(1.0, QColor(COLORS.tartan_track_dark))
        painter.fillRect(0, int(ground_y), camera.width, int(track_height), QBrush(track_grad))

        # Lane divider line
        lane_line_y = ground_y + (track_height * 0.45)
        painter.setPen(QPen(QColor(COLORS.track_lines), 3))
        painter.drawLine(0, int(lane_line_y), camera.width, int(lane_line_y))

        # White baseline at ground level
        painter.setPen(QPen(QColor(COLORS.track_lines), 4))
        painter.drawLine(0, int(ground_y), camera.width, int(ground_y))

        # Distance markings
        min_m, max_m = camera.get_visible_bounds_meters()
        start_meter = max(-5, math.floor(min_m))
        end_meter = min(120, math.ceil(max_m))

        font = QFont("Arial", 11, QFont.Weight.Bold)
        big_font = QFont("Arial", 18, QFont.Weight.Black)

        for m in range(start_meter, end_meter + 1):
            pt = camera.world_to_screen(float(m), 0.0)
            sx = pt.x()

            # Hash marks
            if m % 10 == 0:
                # Major 10m marker
                painter.setPen(QPen(QColor(COLORS.track_lines), 4))
                painter.drawLine(int(sx), int(ground_y), int(sx), int(ground_y + 40))

                # Large numeric stencil on track
                painter.setFont(big_font)
                painter.setPen(QColor(255, 255, 255, 220))
                text = f"{m} m"
                if m == 0:
                    text = "START 0m"
                elif m == 50:
                    text = "50m [HÜRDE]"
                elif m == 100:
                    text = "100m [ZIEL]"
                painter.drawText(int(sx + 8), int(ground_y + 35), text)
            elif m % 5 == 0:
                # Medium 5m marker
                painter.setPen(QPen(QColor(COLORS.track_lines), 3))
                painter.drawLine(int(sx), int(ground_y), int(sx), int(ground_y + 25))
                painter.setFont(font)
                painter.setPen(QColor(255, 255, 255, 170))
                painter.drawText(int(sx + 5), int(ground_y + 22), f"{m}m")
            else:
                # Minor 1m tick
                painter.setPen(QPen(QColor(255, 255, 255, 120), 2))
                painter.drawLine(int(sx), int(ground_y), int(sx), int(ground_y + 12))

        # Start block details at 0m
        start_pt = camera.world_to_screen(0.0, 0.0)
        # Checkered start strip
        check_w = 6
        check_h = 10
        for r in range(4):
            for c in range(2):
                color = QColor(255, 255, 255) if (r + c) % 2 == 0 else QColor(30, 30, 30)
                painter.fillRect(
                    int(start_pt.x() - 12 + c * check_w),
                    int(ground_y + r * check_h),
                    check_w,
                    check_h,
                    color,
                )

        painter.restore()

    def _render_sand_pit(self, painter: QPainter, camera: Camera, ground_y: float) -> None:
        """Render the golden long jump sand pit from 100m to 115m."""
        p_start = camera.world_to_screen(SAND_PIT_START_X, 0.0)
        p_end = camera.world_to_screen(SAND_PIT_END_X, 0.0)

        # Check if visible
        if p_end.x() < 0 or p_start.x() > camera.width:
            return

        painter.save()
        sand_width = p_end.x() - p_start.x()
        sand_height = camera.height - ground_y

        # Sand gradient
        sand_grad = QLinearGradient(0, ground_y, 0, camera.height)
        sand_grad.setColorAt(0.0, QColor(COLORS.sand_pit))
        sand_grad.setColorAt(1.0, QColor(COLORS.sand_pit_dark))
        painter.fillRect(int(p_start.x()), int(ground_y), int(sand_width), int(sand_height), QBrush(sand_grad))

        # Wooden border / takeoff board
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor("#795548"))
        painter.drawRect(int(p_start.x() - 6), int(ground_y), 6, int(sand_height))
        painter.drawRect(int(p_end.x()), int(ground_y), 6, int(sand_height))

        # Distance tape marks in sand pit
        font = QFont("Arial", 10, QFont.Weight.Bold)
        painter.setFont(font)
        painter.setPen(QColor("#5d4037"))
        for m in range(int(SAND_PIT_START_X) + 1, int(SAND_PIT_END_X)):
            m_pt = camera.world_to_screen(float(m), 0.0)
            painter.drawLine(int(m_pt.x()), int(ground_y), int(m_pt.x()), int(ground_y + 18))
            painter.drawText(int(m_pt.x() + 3), int(ground_y + 16), f"{m}m")

        painter.restore()

    def _render_hurdle(self, painter: QPainter, camera: Camera, hurdle_body: pymunk.Body) -> None:
        """Render the 50m athletic hurdle using its dynamic body transform."""
        painter.save()
        pos = camera.world_to_screen(hurdle_body.position.x, hurdle_body.position.y)
        angle_deg = math.degrees(hurdle_body.angle)

        painter.translate(pos.x(), pos.y())
        painter.rotate(-angle_deg)  # Invert for Qt coordinate system

        scale = camera.world_dist_to_screen(1.0)
        w_upright = 0.08 * scale
        h_upright = 0.92 * scale
        w_bar = 0.55 * scale
        h_bar = 0.12 * scale
        w_base = 0.60 * scale
        h_base = 0.06 * scale

        # Upright legs (metallic silver)
        painter.setPen(QPen(QColor("#2c3e50"), 2))
        painter.setBrush(QColor("#bdc3c7"))
        painter.drawRect(int(-w_upright / 2), int(-h_upright / 2), int(w_upright), int(h_upright))

        # Base support feet
        painter.drawRect(int(-w_base / 2 + 0.10 * scale), int(h_upright / 2 - h_base), int(w_base), int(h_base))

        # Top striped bar (orange & black/navy warning stripes)
        bar_top_y = -h_upright / 2 - h_bar / 2
        painter.setBrush(QColor(COLORS.hurdle_bar))
        painter.drawRect(int(-w_bar / 2), int(bar_top_y), int(w_bar), int(h_bar))

        # Stripes on bar
        stripe_w = w_bar / 5.0
        painter.setBrush(QColor(COLORS.hurdle_stripe))
        for s in [1, 3]:
            painter.drawRect(int(-w_bar / 2 + s * stripe_w), int(bar_top_y), int(stripe_w), int(h_bar))

        painter.restore()

    def _render_finish_arch(self, painter: QPainter, camera: Camera) -> None:
        """Render the grand finish arch at the 100m mark."""
        arch_pt = camera.world_to_screen(FINISH_LINE_X, 0.0)
        sx = arch_pt.x()
        ground_y = arch_pt.y()

        if sx < -100 or sx > camera.width + 100:
            return

        painter.save()
        scale = camera.world_dist_to_screen(1.0)
        arch_height = 4.0 * scale
        pole_width = 0.22 * scale

        # Left / Right support poles
        pole_color = QColor("#e74c3c")
        painter.setBrush(pole_color)
        painter.setPen(QPen(QColor("#c0392b"), 2))
        painter.drawRect(int(sx - pole_width / 2), int(ground_y - arch_height), int(pole_width), int(arch_height))

        # Overhead banner
        banner_w = 2.8 * scale
        banner_h = 0.8 * scale
        banner_y = ground_y - arch_height
        banner_rect = QRectF(sx - banner_w / 2, banner_y, banner_w, banner_h)

        painter.setBrush(QColor("#2980b9"))
        painter.setPen(QPen(QColor("#ffffff"), 3))
        painter.drawRoundedRect(banner_rect, 6, 6)

        # Banner text
        painter.setFont(QFont("Arial", 16, QFont.Weight.Black))
        painter.setPen(QColor("#ffffff"))
        painter.drawText(banner_rect, Qt.AlignmentFlag.AlignCenter, "ZIEL 100 m")

        # Checkered finish line ribbon (suspended across)
        ribbon_y = ground_y - 1.2 * scale
        ribbon_h = 0.15 * scale
        ribbon_w = 1.8 * scale
        for c in range(12):
            rw = ribbon_w / 12.0
            color = QColor("#ffffff") if c % 2 == 0 else QColor("#e74c3c")
            painter.fillRect(int(sx - ribbon_w / 2 + c * rw), int(ribbon_y), int(rw), int(ribbon_h), color)

        painter.restore()
