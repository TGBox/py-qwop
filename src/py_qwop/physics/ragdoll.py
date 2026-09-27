"""Articulated humanoid ragdoll model with muscle motors for QWOP simulation."""

from typing import Any

import pymunk

from py_qwop.config import (
    COLLISION_GROUND,
    COLLISION_HURDLE,
    COLLISION_RUNNER_BODY,
    COLLISION_RUNNER_FEET,
)


class Ragdoll:
    """Represents the multi-part runner ragdoll controlled by Q, W, O, P keys."""

    # Motor speeds and torque limits
    HIP_MOTOR_RATE = 8.5       # rad/s
    HIP_MOTOR_TORQUE = 320.0   # N*m
    KNEE_MOTOR_RATE = 10.0     # rad/s
    KNEE_MOTOR_TORQUE = 280.0  # N*m

    def __init__(self, space: pymunk.Space, start_x: float = 0.0, start_y: float = 0.0):
        self.space = space
        self.start_x = start_x
        self.start_y = start_y

        self.bodies: list[pymunk.Body] = []
        self.shapes: list[pymunk.Shape] = []
        self.joints: list[pymunk.Constraint] = []

        # Body parts
        self.torso: pymunk.Body = None
        self.head: pymunk.Body = None
        self.thigh_r: pymunk.Body = None  # Right (front leg in side view)
        self.thigh_l: pymunk.Body = None  # Left (back leg in side view)
        self.shin_r: pymunk.Body = None
        self.shin_l: pymunk.Body = None
        self.foot_r: pymunk.Body = None
        self.foot_l: pymunk.Body = None
        self.arm_r_upper: pymunk.Body = None
        self.arm_r_lower: pymunk.Body = None
        self.arm_l_upper: pymunk.Body = None
        self.arm_l_lower: pymunk.Body = None

        # Motors for muscle control
        self.motor_hip_r: pymunk.SimpleMotor = None
        self.motor_hip_l: pymunk.SimpleMotor = None
        self.motor_knee_r: pymunk.SimpleMotor = None
        self.motor_knee_l: pymunk.SimpleMotor = None

        # Build ragdoll
        self._build_ragdoll()

    def _build_ragdoll(self) -> None:
        """Create bodies, shapes, joints, and motors."""
        # Body filter: body parts collide with ground and hurdles, but not with each other
        body_filter = pymunk.ShapeFilter(
            categories=COLLISION_RUNNER_BODY,
            mask=COLLISION_GROUND | COLLISION_HURDLE,
        )
        foot_filter = pymunk.ShapeFilter(
            categories=COLLISION_RUNNER_FEET,
            mask=COLLISION_GROUND | COLLISION_HURDLE,
        )

        sx, sy = self.start_x, self.start_y

        # 1. Torso
        torso_mass = 28.0
        torso_size = (0.24, 0.52)
        torso_moment = pymunk.moment_for_box(torso_mass, torso_size)
        self.torso = pymunk.Body(torso_mass, torso_moment)
        self.torso.position = (sx, sy + 1.15)
        self.torso.angle = -0.12  # Slight forward athletic lean
        torso_shape = pymunk.Poly.create_box(self.torso, torso_size, radius=0.03)
        torso_shape.filter = body_filter
        torso_shape.friction = 0.6
        torso_shape.collision_type = 10  # Critical body part for crash detection
        self._add(self.torso, torso_shape)

        # 2. Head
        head_mass = 4.5
        head_radius = 0.13
        head_moment = pymunk.moment_for_circle(head_mass, 0, head_radius)
        self.head = pymunk.Body(head_mass, head_moment)
        self.head.position = (sx + 0.05, sy + 1.55)
        head_shape = pymunk.Circle(self.head, head_radius)
        head_shape.filter = body_filter
        head_shape.friction = 0.5
        head_shape.collision_type = 11  # Head: critical crash part
        self._add(self.head, head_shape)

        # Neck Joint
        neck_pivot = pymunk.PivotJoint(self.torso, self.head, (0.02, 0.26), (0.0, -head_radius))
        neck_limit = pymunk.RotaryLimitJoint(self.torso, self.head, -0.35, 0.35)
        neck_spring = pymunk.DampedRotarySpring(self.torso, self.head, 0.0, 180.0, 15.0)
        self._add_joint(neck_pivot, neck_limit, neck_spring)

        # 3. Legs
        thigh_mass = 8.5
        thigh_size = (0.13, 0.44)
        thigh_moment = pymunk.moment_for_box(thigh_mass, thigh_size)

        shin_mass = 4.8
        shin_size = (0.10, 0.42)
        shin_moment = pymunk.moment_for_box(shin_mass, shin_size)

        foot_mass = 1.8
        foot_size = (0.24, 0.08)
        foot_moment = pymunk.moment_for_box(foot_mass, foot_size)

        # Helper to construct a leg
        def create_leg(is_right: bool, initial_hip_angle: float, initial_knee_angle: float):
            offset_x = 0.02 if is_right else -0.02

            # Thigh
            thigh_body = pymunk.Body(thigh_mass, thigh_moment)
            thigh_body.position = (sx + offset_x, sy + 0.72)
            thigh_body.angle = initial_hip_angle
            thigh_shape = pymunk.Poly.create_box(thigh_body, thigh_size, radius=0.03)
            thigh_shape.filter = body_filter
            thigh_shape.friction = 0.7
            thigh_shape.collision_type = 12

            # Shin (Calf)
            shin_body = pymunk.Body(shin_mass, shin_moment)
            shin_body.position = (sx + offset_x, sy + 0.32)
            shin_body.angle = initial_hip_angle + initial_knee_angle
            shin_shape = pymunk.Poly.create_box(shin_body, shin_size, radius=0.025)
            shin_shape.filter = body_filter
            shin_shape.friction = 0.7
            shin_shape.collision_type = 13  # Shin/knees can brush ground without crash

            # Foot
            foot_body = pymunk.Body(foot_mass, foot_moment)
            foot_body.position = (sx + offset_x + 0.06, sy + 0.05)
            fw, fh = foot_size
            dx = 0.04
            foot_vs = [
                (-fw / 2 + dx, -fh / 2),
                (fw / 2 + dx, -fh / 2),
                (fw / 2 + dx, fh / 2),
                (-fw / 2 + dx, fh / 2),
            ]
            foot_shape = pymunk.Poly(foot_body, foot_vs, radius=0.02)
            foot_shape.filter = foot_filter
            foot_shape.friction = 1.6  # High grip for sprinting shoes
            foot_shape.elasticity = 0.05
            foot_shape.collision_type = 14  # Feet

            self._add(thigh_body, thigh_shape)
            self._add(shin_body, shin_shape)
            self._add(foot_body, foot_shape)

            # Hip Joint
            hip_pivot = pymunk.PivotJoint(self.torso, thigh_body, (0.0, -0.24), (0.0, 0.20))
            # Limit hip swing: leg forward up to ~80 deg, backward up to ~65 deg
            hip_limit = pymunk.RotaryLimitJoint(self.torso, thigh_body, -1.15, 1.45)
            hip_motor = pymunk.SimpleMotor(self.torso, thigh_body, 0.0)
            hip_motor.max_force = 0.0  # Inactive until key pressed

            # Knee Joint
            knee_pivot = pymunk.PivotJoint(thigh_body, shin_body, (0.0, -0.20), (0.0, 0.19))
            # Human knee can only bend backwards: 0 to 140 degrees (2.44 rad)
            knee_limit = pymunk.RotaryLimitJoint(thigh_body, shin_body, 0.0, 2.45)
            knee_motor = pymunk.SimpleMotor(thigh_body, shin_body, 0.0)
            knee_motor.max_force = 0.0

            # Ankle Joint
            ankle_pivot = pymunk.PivotJoint(shin_body, foot_body, (0.0, -0.19), (-0.05, 0.02))
            ankle_limit = pymunk.RotaryLimitJoint(shin_body, foot_body, -0.65, 0.70)
            ankle_spring = pymunk.DampedRotarySpring(shin_body, foot_body, 0.0, 120.0, 8.0)

            self._add_joint(hip_pivot, hip_limit, hip_motor)
            self._add_joint(knee_pivot, knee_limit, knee_motor)
            self._add_joint(ankle_pivot, ankle_limit, ankle_spring)

            return thigh_body, shin_body, foot_body, hip_motor, knee_motor

        # Build Right Leg (Front) & Left Leg (Back)
        (
            self.thigh_r,
            self.shin_r,
            self.foot_r,
            self.motor_hip_r,
            self.motor_knee_r,
        ) = create_leg(is_right=True, initial_hip_angle=0.25, initial_knee_angle=0.35)

        (
            self.thigh_l,
            self.shin_l,
            self.foot_l,
            self.motor_hip_l,
            self.motor_knee_l,
        ) = create_leg(is_right=False, initial_hip_angle=-0.30, initial_knee_angle=0.45)

        # 4. Arms (for dynamic balancing and visual running animation)
        arm_mass_upper = 2.2
        arm_size_upper = (0.09, 0.32)
        arm_moment_upper = pymunk.moment_for_box(arm_mass_upper, arm_size_upper)

        arm_mass_lower = 1.4
        arm_size_lower = (0.075, 0.28)
        arm_moment_lower = pymunk.moment_for_box(arm_mass_lower, arm_size_lower)

        def create_arm(is_right: bool):
            upper_body = pymunk.Body(arm_mass_upper, arm_moment_upper)
            upper_body.position = (sx, sy + 1.15)
            upper_body.angle = -0.5 if is_right else 0.5
            upper_shape = pymunk.Poly.create_box(upper_body, arm_size_upper, radius=0.02)
            upper_shape.filter = body_filter
            upper_shape.friction = 0.5
            upper_shape.collision_type = 15

            lower_body = pymunk.Body(arm_mass_lower, arm_moment_lower)
            lower_body.position = (sx, sy + 0.90)
            lower_body.angle = 0.8 if is_right else -0.4
            lower_shape = pymunk.Poly.create_box(lower_body, arm_size_lower, radius=0.02)
            lower_shape.filter = body_filter
            lower_shape.friction = 0.5
            lower_shape.collision_type = 16

            self._add(upper_body, upper_shape)
            self._add(lower_body, lower_shape)

            shoulder_pos = (0.06, 0.19) if is_right else (-0.06, 0.19)
            shoulder = pymunk.PivotJoint(self.torso, upper_body, shoulder_pos, (0.0, 0.14))
            shoulder_spring = pymunk.DampedRotarySpring(self.torso, upper_body, 0.2 if is_right else -0.2, 50.0, 5.0)

            elbow = pymunk.PivotJoint(upper_body, lower_body, (0.0, -0.14), (0.0, 0.12))
            elbow_spring = pymunk.DampedRotarySpring(upper_body, lower_body, 1.2, 35.0, 3.5)

            self._add_joint(shoulder, shoulder_spring)
            self._add_joint(elbow, elbow_spring)

            return upper_body, lower_body

        self.arm_r_upper, self.arm_r_lower = create_arm(is_right=True)
        self.arm_l_upper, self.arm_l_lower = create_arm(is_right=False)

    def _add(self, body: pymunk.Body, shape: pymunk.Shape) -> None:
        self.bodies.append(body)
        self.shapes.append(shape)
        self.space.add(body, shape)

    def _add_joint(self, *joints: pymunk.Constraint) -> None:
        for joint in joints:
            self.joints.append(joint)
            self.space.add(joint)

    def apply_controls(self, q_pressed: bool, w_pressed: bool, o_pressed: bool, p_pressed: bool) -> None:
        """Update muscle motor torque and speed based on user key inputs.
        
        Q: Flex Right Hip (forward) & Extend Left Hip (backward)
        W: Flex Left Hip (forward) & Extend Right Hip (backward)
        O: Flex Right Knee (bend) & Extend Left Knee (straighten)
        P: Flex Left Knee (bend) & Extend Right Knee (straighten)
        """
        # Hips (Thighs)
        if q_pressed and not w_pressed:
            # Q: Right forward (+rate), Left backward (-rate)
            self.motor_hip_r.rate = self.HIP_MOTOR_RATE
            self.motor_hip_r.max_force = self.HIP_MOTOR_TORQUE
            self.motor_hip_l.rate = -self.HIP_MOTOR_RATE
            self.motor_hip_l.max_force = self.HIP_MOTOR_TORQUE
        elif w_pressed and not q_pressed:
            # W: Left forward (+rate), Right backward (-rate)
            self.motor_hip_l.rate = self.HIP_MOTOR_RATE
            self.motor_hip_l.max_force = self.HIP_MOTOR_TORQUE
            self.motor_hip_r.rate = -self.HIP_MOTOR_RATE
            self.motor_hip_r.max_force = self.HIP_MOTOR_TORQUE
        else:
            # Neither or both: relax hip motors
            self.motor_hip_r.max_force = 15.0  # Gentle passive resistance
            self.motor_hip_r.rate = 0.0
            self.motor_hip_l.max_force = 15.0
            self.motor_hip_l.rate = 0.0

        # Knees (Calves)
        if o_pressed and not p_pressed:
            # O: Right knee flexes (+rate), Left knee extends (-rate)
            self.motor_knee_r.rate = self.KNEE_MOTOR_RATE
            self.motor_knee_r.max_force = self.KNEE_MOTOR_TORQUE
            self.motor_knee_l.rate = -self.KNEE_MOTOR_RATE
            self.motor_knee_l.max_force = self.KNEE_MOTOR_TORQUE
        elif p_pressed and not o_pressed:
            # P: Left knee flexes (+rate), Right knee extends (-rate)
            self.motor_knee_l.rate = self.KNEE_MOTOR_RATE
            self.motor_knee_l.max_force = self.KNEE_MOTOR_TORQUE
            self.motor_knee_r.rate = -self.KNEE_MOTOR_RATE
            self.motor_knee_r.max_force = self.KNEE_MOTOR_TORQUE
        else:
            # Relax knees
            self.motor_knee_r.max_force = 10.0
            self.motor_knee_r.rate = 0.0
            self.motor_knee_l.max_force = 10.0
            self.motor_knee_l.rate = 0.0

    def get_progress_x(self) -> float:
        """Return the runner's furthest body point on the track in meters."""
        points = [
            self.torso.position.x,
            self.head.position.x,
            self.foot_r.position.x,
            self.foot_l.position.x,
            self.shin_r.position.x,
            self.shin_l.position.x,
        ]
        return max(points)

    def get_center_position(self) -> tuple[float, float]:
        """Return the runner's center of mass / torso coordinates for camera focus."""
        return (self.torso.position.x, self.torso.position.y)

    def get_velocity(self) -> tuple[float, float]:
        """Return torso linear velocity."""
        return (self.torso.velocity.x, self.torso.velocity.y)

    def capture_pose(self) -> dict[str, Any]:
        """Snapshot current body part coordinates and rotations for ghost playback."""
        def pack(body: pymunk.Body):
            return [round(body.position.x, 3), round(body.position.y, 3), round(body.angle, 3)]

        return {
            "torso": pack(self.torso),
            "head": pack(self.head),
            "thigh_r": pack(self.thigh_r),
            "thigh_l": pack(self.thigh_l),
            "shin_r": pack(self.shin_r),
            "shin_l": pack(self.shin_l),
            "foot_r": pack(self.foot_r),
            "foot_l": pack(self.foot_l),
            "arm_r_u": pack(self.arm_r_upper),
            "arm_r_l": pack(self.arm_r_lower),
            "arm_l_u": pack(self.arm_l_upper),
            "arm_l_l": pack(self.arm_l_lower),
        }

    def destroy(self) -> None:
        """Remove all ragdoll components from Pymunk space."""
        for joint in self.joints:
            if joint in self.space.constraints:
                self.space.remove(joint)
        for shape in self.shapes:
            if shape in self.space.shapes:
                self.space.remove(shape)
        for body in self.bodies:
            if body in self.space.bodies:
                self.space.remove(body)
        self.joints.clear()
        self.shapes.clear()
        self.bodies.clear()
