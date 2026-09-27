"""Unit tests for 2D tracking camera and coordinate transformations."""

from py_qwop.render.camera import Camera


def test_camera_world_to_screen():
    """Verify conversion from world meters to viewport screen coordinates."""
    cam = Camera(viewport_width=1200, viewport_height=700)
    cam.reset(target_x=0.0, target_y=1.0)

    # Ground line at x=0, y=0
    pt_ground = cam.world_to_screen(0.0, 0.0)
    assert abs(pt_ground.x() - (1200 * cam.focus_ratio_x)) < 1.0
    assert abs(pt_ground.y() - (700 * cam.ground_ratio_y)) < 1.0

    # Point 1 meter above ground
    pt_above = cam.world_to_screen(0.0, 1.0)
    assert pt_above.y() < pt_ground.y()  # Higher in world = smaller Y on screen

    # Length scaling
    dist_px = cam.world_dist_to_screen(2.0)
    assert dist_px > 0


def test_camera_tracking_and_bounds():
    """Test camera target tracking with velocity lookahead and visible bounds."""
    cam = Camera(viewport_width=1000, viewport_height=600)
    cam.reset(0.0, 1.0)

    # Update tracking runner moving forward at 5 m/s
    cam.update(target_x=10.0, target_y=1.2, vel_x=5.0, dt=0.05)
    assert cam.pos_x > 0.0  # Camera moving towards target

    min_x, max_x = cam.get_visible_bounds_meters()
    assert min_x < cam.pos_x < max_x
