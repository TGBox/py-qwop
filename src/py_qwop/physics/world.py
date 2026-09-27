"""Physics simulation world manager coordinating Pymunk space, track, runner, and collisions."""

import math
from collections.abc import Callable

import pymunk

from py_qwop.config import (
    FINISH_LINE_X,
    GRAVITY_Y,
    PHYSICS_SUB_STEPS,
)
from py_qwop.physics.ragdoll import Ragdoll
from py_qwop.physics.track import Track


class PhysicsWorld:
    """Encapsulates the Pymunk simulation space, track, runner ragdoll, and game rules."""

    def __init__(self):
        self.space = pymunk.Space()
        self.space.gravity = (0.0, GRAVITY_Y)
        self.space.iterations = 25  # High solver iterations for constraint stiffness

        self.track = Track(self.space)
        self.runner = Ragdoll(self.space, start_x=0.0, start_y=0.0)

        # Callbacks
        self.on_crash: Callable[[], None] | None = None
        self.on_victory: Callable[[], None] | None = None
        self.on_footstep: Callable[[float, float, bool], None] | None = None

        self.is_crashed: bool = False
        self.is_victory: bool = False
        self.time_elapsed: float = 0.0

        # Register collision callbacks
        self._setup_collision_handlers()

    def _setup_collision_handlers(self) -> None:
        """Register collision event hooks for game over and particle effects."""
        # 1. Head / Chest (type 11) hitting ground (types 1, 2)
        def handle_head_crash(arbiter, space, data):
            if not self.is_crashed and not self.is_victory and self.time_elapsed > 0.15:
                self.is_crashed = True
                if self.on_crash:
                    self.on_crash()
            return True

        for ground_type in [1, 2]:  # Track, Sand
            self.space.on_collision(11, ground_type, begin=handle_head_crash)

        # 2. Footstep events (Foot type 14 hitting ground type 1 or sand type 2)
        def handle_footstep(arbiter, space, data):
            if self.on_footstep and len(arbiter.contact_point_set.points) > 0:
                point = arbiter.contact_point_set.points[0].point_a
                is_sand = arbiter.shapes[1].collision_type == 2
                self.on_footstep(point.x, point.y, is_sand)
            return True

        for ground_type in [1, 2]:
            self.space.on_collision(14, ground_type, begin=handle_footstep)

    def update(self, dt: float, keys: dict[str, bool]) -> None:
        """Advance the physics simulation by dt seconds using sub-stepping."""
        if not self.is_crashed:
            # Apply control torques to runner
            self.runner.apply_controls(
                q_pressed=keys.get("thigh_q", False),
                w_pressed=keys.get("thigh_w", False),
                o_pressed=keys.get("calf_o", False),
                p_pressed=keys.get("calf_p", False),
            )
            self.time_elapsed += dt

            # Check flat-on-ground fall condition
            if self.time_elapsed > 0.4:
                torso_y = self.runner.torso.position.y
                head_y = self.runner.head.position.y
                torso_angle = self.runner.torso.angle
                if torso_y < 0.25 and head_y < 0.28 and abs(math.sin(torso_angle)) > 0.85:
                    self.is_crashed = True
                    if self.on_crash:
                        self.on_crash()

            # Check victory condition
            if not self.is_victory and self.runner.get_progress_x() >= FINISH_LINE_X:
                self.is_victory = True
                if self.on_victory:
                    self.on_victory()

        # Step the physics engine in smaller increments for constraint stability
        sub_dt = dt / PHYSICS_SUB_STEPS
        for _ in range(PHYSICS_SUB_STEPS):
            self.space.step(sub_dt)

    def reset(self) -> None:
        """Reset world to fresh start."""
        self.is_crashed = False
        self.is_victory = False
        self.time_elapsed = 0.0

        self.runner.destroy()
        self.runner = Ragdoll(self.space, start_x=0.0, start_y=0.0)
        self.track.reset_hurdle()
