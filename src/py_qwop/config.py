"""Configuration constants for py-qwop game."""

from dataclasses import dataclass

from PySide6.QtCore import Qt

# Visual and screen constants
WINDOW_DEFAULT_WIDTH = 1200
WINDOW_DEFAULT_HEIGHT = 700
WINDOW_MIN_WIDTH = 800
WINDOW_MIN_HEIGHT = 500
TARGET_FPS = 60
PHYSICS_SUB_STEPS = 4  # Sub-steps per frame for higher numerical stability

# Physical scaling: 1 meter = 100 pixels in world coordinates
PIXELS_PER_METER = 100.0

# Track geometry (in meters)
TRACK_START_X = -5.0       # Track extends behind start line
TRACK_END_X = 120.0        # Total track length
FINISH_LINE_X = 100.0      # 100m mark
HURDLE_X = 50.0            # 50m hurdle
SAND_PIT_START_X = 100.0   # Long jump sand pit begins at finish line
SAND_PIT_END_X = 115.0     # Sand pit ends

# Gravity and physics parameters
GRAVITY_Y = -9.81          # Standard physics gravity in m/s^2
RUNNER_MASS_SCALE = 1.0
GROUND_FRICTION = 1.4      # High friction on tartan track for athletic shoes
GROUND_ELASTICITY = 0.05
SAND_FRICTION = 2.2        # Very high friction in sand pit

# Collision categories
COLLISION_GROUND = 0b0001
COLLISION_RUNNER_FEET = 0b0010
COLLISION_RUNNER_BODY = 0b0100
COLLISION_HURDLE = 0b1000

# Default key bindings
DEFAULT_KEY_BINDINGS: dict[str, Qt.Key] = {
    "thigh_q": Qt.Key.Key_Q,
    "thigh_w": Qt.Key.Key_W,
    "calf_o": Qt.Key.Key_O,
    "calf_p": Qt.Key.Key_P,
    "restart": Qt.Key.Key_R,
    "fullscreen": Qt.Key.Key_F11,
    "pause": Qt.Key.Key_Escape,
}


@dataclass
class ColorPalette:
    """Color themes for UI and rendering."""
    # Stadium and environment
    sky_top: str = "#3a7bd5"
    sky_bottom: str = "#86c5da"
    stadium_roof: str = "#2c3e50"
    stadium_seats_1: str = "#34495e"
    stadium_seats_2: str = "#243342"
    crowd_colors: tuple = ("#e74c3c", "#f39c12", "#f1c40f", "#2ecc71", "#3498db", "#9b59b6", "#ecf0f1")
    tartan_track: str = "#c0392b"
    tartan_track_dark: str = "#a93226"
    track_lines: str = "#ffffff"
    sand_pit: str = "#d4ac0d"
    sand_pit_dark: str = "#b7950b"
    grass: str = "#27ae60"
    hurdle_bar: str = "#f39c12"
    hurdle_stripe: str = "#2c3e50"

    # Runner styling
    skin_tone: str = "#c68642"
    skin_tone_shadow: str = "#9e6931"
    jersey_main: str = "#2980b9"
    jersey_accent: str = "#e74c3c"
    shorts_main: str = "#2c3e50"
    shorts_shadow: str = "#1a252f"
    shoe_main: str = "#f1c40f"
    shoe_sole: str = "#ffffff"
    hair_color: str = "#3e2723"
    headband: str = "#ffffff"
    ghost_tint: str = "rgba(255, 255, 255, 110)"

    # UI theme
    ui_dark_bg: str = "#181e28"
    ui_panel_bg: str = "rgba(24, 30, 40, 220)"
    ui_card_bg: str = "#232b38"
    ui_accent: str = "#3498db"
    ui_accent_hover: str = "#2980b9"
    ui_success: str = "#2ecc71"
    ui_warning: str = "#f39c12"
    ui_danger: str = "#e74c3c"
    ui_text: str = "#ecf0f1"
    ui_text_dim: str = "#95a5a6"


COLORS = ColorPalette()
