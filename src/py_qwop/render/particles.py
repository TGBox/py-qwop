"""Particle system for visual effects: dust, sand, hurdle debris, and victory confetti."""

import random

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPainter

from py_qwop.render.camera import Camera


class Particle:
    """Individual visual effect particle."""

    def __init__(
        self,
        x: float,
        y: float,
        vx: float,
        vy: float,
        color: QColor,
        size: float,
        life: float,
        gravity: float = -9.8,
        is_confetti: bool = False,
    ):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.size = size
        self.max_life = life
        self.life = life
        self.gravity = gravity
        self.is_confetti = is_confetti
        self.rotation = random.uniform(0.0, 360.0)
        self.rot_speed = random.uniform(-180.0, 180.0)

    def update(self, dt: float) -> bool:
        """Update particle position and age. Returns False when particle dies."""
        self.life -= dt
        if self.life <= 0.0:
            return False

        self.vy += self.gravity * dt
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.rotation += self.rot_speed * dt

        # Stop particles bouncing forever below ground
        if self.y < 0.0:
            self.y = 0.0
            self.vy = -self.vy * 0.2
            self.vx *= 0.7

        return True


class ParticleSystem:
    """Manages active particle pools and rendering."""

    def __init__(self):
        self.particles: list[Particle] = []
        self._confetti_colors = [
            QColor(231, 76, 60),
            QColor(52, 152, 219),
            QColor(46, 204, 113),
            QColor(241, 196, 15),
            QColor(155, 89, 182),
            QColor(230, 126, 34),
            QColor(255, 255, 255),
        ]

    def spawn_foot_dust(self, x: float, y: float, is_sand: bool = False) -> None:
        """Spawn dust or sand burst when foot strikes ground."""
        count = random.randint(5, 8)
        base_color = QColor(212, 172, 13) if is_sand else QColor(192, 57, 43, 180)

        for _ in range(count):
            vx = random.uniform(-1.2, 0.8)
            vy = random.uniform(0.5, 2.2)
            life = random.uniform(0.3, 0.6)
            size = random.uniform(2.5, 5.0)

            c = QColor(base_color)
            c.setAlpha(random.randint(120, 200))
            p = Particle(
                x=x + random.uniform(-0.05, 0.05),
                y=max(0.02, y),
                vx=vx,
                vy=vy,
                color=c,
                size=size,
                life=life,
                gravity=-12.0,
            )
            self.particles.append(p)

    def spawn_confetti(self, center_x: float, center_y: float = 3.0, count: int = 120) -> None:
        """Explosion of festive confetti at finish line."""
        for _ in range(count):
            vx = random.uniform(-3.5, 5.5)
            vy = random.uniform(2.0, 7.0)
            life = random.uniform(2.5, 4.5)
            size = random.uniform(4.0, 8.0)
            color = random.choice(self._confetti_colors)

            p = Particle(
                x=center_x + random.uniform(-1.0, 1.0),
                y=center_y + random.uniform(-0.5, 1.5),
                vx=vx,
                vy=vy,
                color=color,
                size=size,
                life=life,
                gravity=-3.5,  # Slow fluttering fall
                is_confetti=True,
            )
            self.particles.append(p)

    def update(self, dt: float) -> None:
        """Advance all active particles and remove expired ones."""
        self.particles = [p for p in self.particles if p.update(dt)]

    def render(self, painter: QPainter, camera: Camera) -> None:
        """Draw active particles transformed by camera projection."""
        painter.save()
        for p in self.particles:
            pt = camera.world_to_screen(p.x, p.y)
            alpha = int(255 * (p.life / p.max_life))
            color = QColor(p.color)
            color.setAlpha(min(color.alpha(), max(0, alpha)))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(color)

            if p.is_confetti:
                painter.save()
                painter.translate(pt.x(), pt.y())
                painter.rotate(p.rotation)
                painter.drawRect(
                    int(-p.size / 2),
                    int(-p.size / 4),
                    int(p.size),
                    int(p.size / 2),
                )
                painter.restore()
            else:
                radius = int(p.size)
                painter.drawEllipse(pt, radius, radius)

        painter.restore()

    def clear(self) -> None:
        """Clear all active particles."""
        self.particles.clear()
