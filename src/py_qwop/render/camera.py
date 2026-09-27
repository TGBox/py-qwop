"""2D Tracking camera transforming physics meters into screen pixels."""


from PySide6.QtCore import QPointF

from py_qwop.config import PIXELS_PER_METER


class Camera:
    """Manages viewport positioning, smooth tracking of the runner, and coordinate mapping."""

    def __init__(self, viewport_width: int = 1200, viewport_height: int = 700):
        self.width = viewport_width
        self.height = viewport_height

        # Camera center in physics meters
        self.pos_x: float = 0.0
        self.pos_y: float = 1.0

        # Viewport ratios
        self.ground_ratio_y: float = 0.72  # Ground line is placed at 72% of window height
        self.focus_ratio_x: float = 0.35   # Runner is placed at 35% of window width (looking forward)

        self.zoom: float = 1.0
        self.target_lead_x: float = 0.0

    def resize(self, width: int, height: int) -> None:
        """Update viewport dimensions on window resize."""
        self.width = max(width, 100)
        self.height = max(height, 100)
        # Dynamically adapt zoom for various aspect ratios / resolutions
        base_h = 700.0
        self.zoom = min(1.2, max(0.75, self.height / base_h))

    def update(self, target_x: float, target_y: float, vel_x: float, dt: float) -> None:
        """Smoothly track the runner target with velocity look-ahead."""
        # Look ahead based on forward velocity
        look_ahead = min(3.0, max(-0.5, vel_x * 0.4))
        target_cam_x = target_x + look_ahead
        target_cam_y = max(0.8, min(2.5, target_y))

        # Exponential smoothing
        blend = 1.0 - (0.01 ** dt)
        self.pos_x += (target_cam_x - self.pos_x) * blend
        self.pos_y += (target_cam_y - self.pos_y) * blend

    def reset(self, target_x: float = 0.0, target_y: float = 1.0) -> None:
        """Snap camera directly to start position."""
        self.pos_x = target_x
        self.pos_y = target_y

    def world_to_screen(self, wx: float, wy: float) -> QPointF:
        """Convert physics world coordinate (meters) to screen pixel coordinate."""
        scale = PIXELS_PER_METER * self.zoom

        screen_origin_x = self.width * self.focus_ratio_x
        screen_origin_y = self.height * self.ground_ratio_y

        sx = screen_origin_x + (wx - self.pos_x) * scale
        sy = screen_origin_y - (wy - 0.0) * scale  # wy=0.0 is the ground line

        return QPointF(sx, sy)

    def world_dist_to_screen(self, meters: float) -> float:
        """Convert a length in meters to screen pixels."""
        return meters * PIXELS_PER_METER * self.zoom

    def get_ground_screen_y(self) -> float:
        """Return the Y coordinate of the track ground in screen space."""
        return self.height * self.ground_ratio_y

    def get_visible_bounds_meters(self) -> tuple[float, float]:
        """Return (min_x, max_x) visible in the viewport in world meters."""
        scale = PIXELS_PER_METER * self.zoom
        left_meters = (self.width * self.focus_ratio_x) / scale
        right_meters = (self.width * (1.0 - self.focus_ratio_x)) / scale
        return (self.pos_x - left_meters - 2.0, self.pos_x + right_meters + 2.0)
