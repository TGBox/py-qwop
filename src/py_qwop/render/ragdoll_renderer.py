"""Visual rendering of the articulated runner ragdoll and ghost runner."""

import math
from typing import Any

import pymunk
from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import (
    QBrush,
    QColor,
    QFont,
    QPainter,
    QPainterPath,
    QPen,
)

from py_qwop.config import COLORS
from py_qwop.physics.ragdoll import Ragdoll
from py_qwop.render.camera import Camera


class RagdollRenderer:
    """Draws stylized athlete ragdoll with clothing, muscle contours, and ghost runner."""

    def __init__(self):
        self.c_skin_front = QColor(COLORS.skin_tone)
        self.c_skin_back = QColor(COLORS.skin_tone_shadow)
        self.c_jersey = QColor(COLORS.jersey_main)
        self.c_jersey_accent = QColor(COLORS.jersey_accent)
        self.c_shorts = QColor(COLORS.shorts_main)
        self.c_shorts_back = QColor(COLORS.shorts_shadow)
        self.c_shoe = QColor(COLORS.shoe_main)
        self.c_shoe_sole = QColor(COLORS.shoe_sole)
        self.c_hair = QColor(COLORS.hair_color)
        self.c_headband = QColor(COLORS.headband)

    def render(
        self,
        painter: QPainter,
        camera: Camera,
        runner: Ragdoll,
        ghost_frame: dict[str, Any] | None = None,
    ) -> None:
        """Render runner (and optional ghost runner) to the scene."""
        # 1. Draw ghost runner if active
        if ghost_frame:
            self._render_ghost(painter, camera, ghost_frame)

        # 2. Draw active player runner
        self._render_runner(painter, camera, runner)

    def _render_runner(self, painter: QPainter, camera: Camera, r: Ragdoll) -> None:
        """Render active runner with layered Z-ordering."""
        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        scale = camera.world_dist_to_screen(1.0)

        # Layer 1: Back Arm (Left)
        self._draw_arm(painter, camera, r.arm_l_upper, r.arm_l_lower, scale, is_front=False)

        # Layer 2: Back Leg (Left)
        self._draw_leg(painter, camera, r.thigh_l, r.shin_l, r.foot_l, scale, is_front=False)

        # Layer 3: Torso & Shorts
        self._draw_torso(painter, camera, r.torso, scale)

        # Layer 4: Head & Face
        self._draw_head(painter, camera, r.head, scale)

        # Layer 5: Front Leg (Right)
        self._draw_leg(painter, camera, r.thigh_r, r.shin_r, r.foot_r, scale, is_front=True)

        # Layer 6: Front Arm (Right)
        self._draw_arm(painter, camera, r.arm_r_upper, r.arm_r_lower, scale, is_front=True)

        painter.restore()

    def _draw_capsule(
        self,
        painter: QPainter,
        camera: Camera,
        body: pymunk.Body,
        length: float,
        width: float,
        brush: QBrush,
        pen: QPen,
    ) -> None:
        """Draw an oriented rounded box/capsule representing a limb segment."""
        pt = camera.world_to_screen(body.position.x, body.position.y)
        angle_deg = math.degrees(body.angle)

        painter.save()
        painter.translate(pt.x(), pt.y())
        painter.rotate(-angle_deg)  # Invert rotation for Qt coordinates

        scale = camera.world_dist_to_screen(1.0)
        w = width * scale
        h = length * scale
        radius = w * 0.45

        rect = QRectF(-w / 2, -h / 2, w, h)
        painter.setBrush(brush)
        painter.setPen(pen)
        painter.drawRoundedRect(rect, radius, radius)
        painter.restore()

    def _draw_torso(self, painter: QPainter, camera: Camera, torso: pymunk.Body, scale: float) -> None:
        """Draw athletic torso with jersey, race bib, and running shorts."""
        pt = camera.world_to_screen(torso.position.x, torso.position.y)
        angle_deg = math.degrees(torso.angle)

        painter.save()
        painter.translate(pt.x(), pt.y())
        painter.rotate(-angle_deg)

        w = 0.24 * scale
        h = 0.52 * scale

        # Base body outline
        torso_rect = QRectF(-w / 2, -h / 2, w, h)
        painter.setPen(QPen(QColor("#1a252f"), 2))
        painter.setBrush(self.c_jersey)
        painter.drawRoundedRect(torso_rect, 6, 6)

        # Shorts (bottom third of torso)
        shorts_h = h * 0.36
        shorts_rect = QRectF(-w / 2, h / 2 - shorts_h, w, shorts_h)
        painter.setBrush(self.c_shorts)
        painter.drawRoundedRect(shorts_rect, 4, 4)

        # Side stripes on shorts
        painter.setPen(QPen(QColor("#ffffff"), 2))
        painter.drawLine(
            QPointF(-w / 2 + 3, h / 2 - shorts_h + 2),
            QPointF(-w / 2 + 3, h / 2 - 2),
        )

        # Race Bib ("QWOP" / #42)
        bib_w = w * 0.72
        bib_h = h * 0.30
        bib_rect = QRectF(-bib_w / 2, -h * 0.22, bib_w, bib_h)
        painter.setBrush(QColor("#ffffff"))
        painter.setPen(QPen(QColor("#2c3e50"), 1))
        painter.drawRect(bib_rect)

        # Bib text
        painter.setFont(QFont("Arial", 8, QFont.Weight.Bold))
        painter.setPen(QColor("#c0392b"))
        painter.drawText(bib_rect, Qt.AlignmentFlag.AlignCenter, "QWOP")

        painter.restore()

    def _draw_head(self, painter: QPainter, camera: Camera, head: pymunk.Body, scale: float) -> None:
        """Draw runner head with hair, headband, and face profile."""
        pt = camera.world_to_screen(head.position.x, head.position.y)
        angle_deg = math.degrees(head.angle)

        painter.save()
        painter.translate(pt.x(), pt.y())
        painter.rotate(-angle_deg)

        r = 0.13 * scale

        # Head skin circle
        painter.setPen(QPen(QColor("#7d4b1a"), 2))
        painter.setBrush(self.c_skin_front)
        painter.drawEllipse(QPointF(0, 0), r, r)

        # Athletic Hair (top and back)
        hair_path = QPainterPath()
        hair_path.moveTo(-r * 0.8, -r * 0.3)
        hair_path.quadTo(-r * 0.9, -r * 1.1, 0, -r * 1.05)
        hair_path.quadTo(r * 0.8, -r * 0.9, r * 0.7, -r * 0.2)
        hair_path.quadTo(r * 0.2, -r * 0.5, -r * 0.8, -r * 0.3)
        painter.setBrush(self.c_hair)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawPath(hair_path)

        # Headband (around forehead)
        hb_rect = QRectF(-r * 0.85, -r * 0.45, r * 1.7, r * 0.32)
        painter.setBrush(self.c_headband)
        painter.setPen(QPen(QColor("#e74c3c"), 1.5))
        painter.drawRoundedRect(hb_rect, 2, 2)

        # Eye & nose facing forward (to the right)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor("#2c3e50"))
        painter.drawEllipse(QPointF(r * 0.45, -r * 0.1), 2.2, 2.2)

        # Nose tip
        painter.setPen(QPen(QColor("#7d4b1a"), 1.5))
        painter.drawLine(QPointF(r * 0.75, -r * 0.05), QPointF(r * 0.95, 0.0))
        painter.drawLine(QPointF(r * 0.95, 0.0), QPointF(r * 0.70, 0.12))

        painter.restore()

    def _draw_leg(
        self,
        painter: QPainter,
        camera: Camera,
        thigh: pymunk.Body,
        shin: pymunk.Body,
        foot: pymunk.Body,
        scale: float,
        is_front: bool,
    ) -> None:
        """Draw complete articulated leg (thigh, calf, sprint shoe)."""
        skin = self.c_skin_front if is_front else self.c_skin_back
        outline = QColor("#1a252f" if is_front else "#0d1319")
        pen = QPen(outline, 2)

        # 1. Thigh
        self._draw_capsule(painter, camera, thigh, 0.44, 0.13, QBrush(skin), pen)

        # 2. Shin / Calf
        self._draw_capsule(painter, camera, shin, 0.42, 0.10, QBrush(skin), pen)

        # 3. Running Shoe
        foot_pt = camera.world_to_screen(foot.position.x, foot.position.y)
        angle_deg = math.degrees(foot.angle)

        painter.save()
        painter.translate(foot_pt.x(), foot_pt.y())
        painter.rotate(-angle_deg)

        fw = 0.24 * scale
        fh = 0.08 * scale

        # Shoe body
        shoe_color = self.c_shoe if is_front else QColor("#d4ac0d")
        shoe_rect = QRectF(-fw / 2 + 0.04 * scale, -fh / 2, fw, fh)
        painter.setBrush(shoe_color)
        painter.setPen(pen)
        painter.drawRoundedRect(shoe_rect, 4, 4)

        # Shoe sole (white with spikes)
        sole_h = fh * 0.28
        sole_rect = QRectF(-fw / 2 + 0.04 * scale, fh / 2 - sole_h, fw, sole_h)
        painter.setBrush(self.c_shoe_sole)
        painter.drawRect(sole_rect)

        # Ankle joint circle
        painter.setBrush(skin)
        painter.drawEllipse(QPointF(-fw / 2 + 0.08 * scale, -fh / 2), 4, 4)

        painter.restore()

    def _draw_arm(
        self,
        painter: QPainter,
        camera: Camera,
        upper_arm: pymunk.Body,
        lower_arm: pymunk.Body,
        scale: float,
        is_front: bool,
    ) -> None:
        """Draw complete articulated arm (upper arm, forearm, hand)."""
        skin = self.c_skin_front if is_front else self.c_skin_back
        outline = QColor("#1a252f" if is_front else "#0d1319")
        pen = QPen(outline, 1.8)

        # Upper arm
        self._draw_capsule(painter, camera, upper_arm, 0.32, 0.09, QBrush(skin), pen)

        # Lower arm & hand
        self._draw_capsule(painter, camera, lower_arm, 0.28, 0.075, QBrush(skin), pen)

    def _render_ghost(self, painter: QPainter, camera: Camera, frame: dict[str, Any]) -> None:
        """Render semi-transparent ghost silhouette from recorded trajectory."""
        painter.save()
        ghost_color = QColor(255, 255, 255, 75)
        ghost_pen = QPen(QColor(255, 255, 255, 120), 1.5)
        painter.setBrush(ghost_color)
        painter.setPen(ghost_pen)

        scale = camera.world_dist_to_screen(1.0)

        def draw_ghost_box(coords: list[float], length: float, width: float):
            if not coords or len(coords) < 3:
                return
            x, y, angle = coords[0], coords[1], coords[2]
            pt = camera.world_to_screen(x, y)
            painter.save()
            painter.translate(pt.x(), pt.y())
            painter.rotate(-math.degrees(angle))
            w = width * scale
            h = length * scale
            painter.drawRoundedRect(QRectF(-w / 2, -h / 2, w, h), w * 0.4, w * 0.4)
            painter.restore()

        # Ghost parts
        draw_ghost_box(frame.get("thigh_l"), 0.44, 0.13)
        draw_ghost_box(frame.get("shin_l"), 0.42, 0.10)
        draw_ghost_box(frame.get("torso"), 0.52, 0.24)
        if "head" in frame:
            hx, hy, _ = frame["head"]
            h_pt = camera.world_to_screen(hx, hy)
            painter.drawEllipse(h_pt, 0.13 * scale, 0.13 * scale)
        draw_ghost_box(frame.get("thigh_r"), 0.44, 0.13)
        draw_ghost_box(frame.get("shin_r"), 0.42, 0.10)

        painter.restore()
