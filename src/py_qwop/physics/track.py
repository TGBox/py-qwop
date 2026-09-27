"""Track, obstacles (50m hurdle), and boundary collision setup for Pymunk."""

import pymunk

from py_qwop.config import (
    COLLISION_GROUND,
    COLLISION_HURDLE,
    COLLISION_RUNNER_BODY,
    COLLISION_RUNNER_FEET,
    GROUND_ELASTICITY,
    GROUND_FRICTION,
    HURDLE_X,
    SAND_FRICTION,
    SAND_PIT_END_X,
    SAND_PIT_START_X,
    TRACK_END_X,
    TRACK_START_X,
)


class Track:
    """Manages static ground surfaces, the 50m hurdle, and track features."""

    def __init__(self, space: pymunk.Space):
        self.space = space
        self.hurdle_body: pymunk.Body = None
        self.hurdle_shapes: list[pymunk.Shape] = []
        self._build_ground()
        self._build_hurdle()

    def _build_ground(self) -> None:
        """Create tartan track segments and sand pit."""
        # Main tartan track (from start to sand pit)
        ground_body = self.space.static_body

        # Pre-track and track up to 100m
        track_shape = pymunk.Segment(
            ground_body,
            (TRACK_START_X, 0.0),
            (SAND_PIT_START_X, 0.0),
            radius=0.04,
        )
        track_shape.friction = GROUND_FRICTION
        track_shape.elasticity = GROUND_ELASTICITY
        track_shape.filter = pymunk.ShapeFilter(
            categories=COLLISION_GROUND,
            mask=COLLISION_RUNNER_FEET | COLLISION_RUNNER_BODY | COLLISION_HURDLE,
        )
        track_shape.collision_type = 1  # Standard ground
        self.space.add(track_shape)

        # Sand pit (from 100m to 115m) with higher friction and low bounce
        sand_shape = pymunk.Segment(
            ground_body,
            (SAND_PIT_START_X, 0.0),
            (SAND_PIT_END_X, 0.0),
            radius=0.04,
        )
        sand_shape.friction = SAND_FRICTION
        sand_shape.elasticity = 0.0
        sand_shape.filter = pymunk.ShapeFilter(
            categories=COLLISION_GROUND,
            mask=COLLISION_RUNNER_FEET | COLLISION_RUNNER_BODY | COLLISION_HURDLE,
        )
        sand_shape.collision_type = 2  # Sand pit
        self.space.add(sand_shape)

        # Post-sand barrier / extended floor
        end_shape = pymunk.Segment(
            ground_body,
            (SAND_PIT_END_X, 0.0),
            (TRACK_END_X, 0.0),
            radius=0.04,
        )
        end_shape.friction = GROUND_FRICTION
        end_shape.filter = pymunk.ShapeFilter(
            categories=COLLISION_GROUND,
            mask=COLLISION_RUNNER_FEET | COLLISION_RUNNER_BODY | COLLISION_HURDLE,
        )
        end_shape.collision_type = 1
        self.space.add(end_shape)

    def _build_hurdle(self) -> None:
        """Construct the physical hurdle obstacle at 50 meters."""
        mass = 3.5  # Lightweight athletic hurdle, easily toppled
        moment = pymunk.moment_for_box(mass, (0.6, 0.95))
        self.hurdle_body = pymunk.Body(mass, moment, body_type=pymunk.Body.DYNAMIC)
        self.hurdle_body.position = (HURDLE_X, 0.48)

        # Upright frame shape
        upright = pymunk.Poly.create_box(self.hurdle_body, size=(0.08, 0.92))
        upright.friction = 0.8
        upright.elasticity = 0.1
        upright.filter = pymunk.ShapeFilter(
            categories=COLLISION_HURDLE,
            mask=COLLISION_GROUND | COLLISION_RUNNER_BODY | COLLISION_RUNNER_FEET,
        )
        upright.collision_type = 3  # Hurdle

        # Top bar
        tb_w, tb_h = 0.55, 0.12
        tb_y = 0.42
        top_bar_vs = [
            (-tb_w / 2, tb_y - tb_h / 2),
            (tb_w / 2, tb_y - tb_h / 2),
            (tb_w / 2, tb_y + tb_h / 2),
            (-tb_w / 2, tb_y + tb_h / 2),
        ]
        top_bar = pymunk.Poly(self.hurdle_body, top_bar_vs)
        top_bar.friction = 0.6
        top_bar.filter = upright.filter
        top_bar.collision_type = 3

        # Base feet (L-shaped base)
        bf_w, bf_h = 0.60, 0.06
        bf_x, bf_y = 0.10, -0.44
        base_foot_vs = [
            (bf_x - bf_w / 2, bf_y - bf_h / 2),
            (bf_x + bf_w / 2, bf_y - bf_h / 2),
            (bf_x + bf_w / 2, bf_y + bf_h / 2),
            (bf_x - bf_w / 2, bf_y + bf_h / 2),
        ]
        base_foot = pymunk.Poly(self.hurdle_body, base_foot_vs)
        base_foot.friction = 1.0
        base_foot.filter = upright.filter
        base_foot.collision_type = 3

        self.hurdle_shapes = [upright, top_bar, base_foot]
        self.space.add(self.hurdle_body, *self.hurdle_shapes)

    def reset_hurdle(self) -> None:
        """Reset hurdle to initial upright state at 50m."""
        if self.hurdle_body:
            self.hurdle_body.position = (HURDLE_X, 0.48)
            self.hurdle_body.angle = 0.0
            self.hurdle_body.velocity = (0.0, 0.0)
            self.hurdle_body.angular_velocity = 0.0
