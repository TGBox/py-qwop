"""Unit and integration tests for physics simulation, ragdoll mechanics, and track features."""

import pymunk

from py_qwop.config import FINISH_LINE_X, HURDLE_X
from py_qwop.physics.ragdoll import Ragdoll
from py_qwop.physics.track import Track
from py_qwop.physics.world import PhysicsWorld


def test_track_construction():
    """Verify ground surfaces and 50m hurdle setup in Pymunk space."""
    space = pymunk.Space()
    track = Track(space)

    assert track.hurdle_body is not None
    assert abs(track.hurdle_body.position.x - HURDLE_X) < 0.1
    assert len(track.hurdle_shapes) == 3

    # Test reset hurdle
    track.hurdle_body.position = (60.0, 1.0)
    track.reset_hurdle()
    assert abs(track.hurdle_body.position.x - HURDLE_X) < 0.01


def test_ragdoll_initialization():
    """Verify humanoid ragdoll body parts, joints, and motors."""
    space = pymunk.Space()
    ragdoll = Ragdoll(space, start_x=0.0, start_y=0.0)

    # Check key body parts
    assert ragdoll.torso is not None
    assert ragdoll.head is not None
    assert ragdoll.thigh_r is not None
    assert ragdoll.thigh_l is not None
    assert ragdoll.shin_r is not None
    assert ragdoll.shin_l is not None
    assert ragdoll.foot_r is not None
    assert ragdoll.foot_l is not None

    # Check motor joints
    assert ragdoll.motor_hip_r is not None
    assert ragdoll.motor_hip_l is not None
    assert ragdoll.motor_knee_r is not None
    assert ragdoll.motor_knee_l is not None

    # Check pose snapshot
    pose = ragdoll.capture_pose()
    assert "torso" in pose
    assert "head" in pose
    assert len(pose["torso"]) == 3  # [x, y, angle]

    # Test cleanup
    ragdoll.destroy()
    assert len(ragdoll.bodies) == 0
    assert len(ragdoll.shapes) == 0
    assert len(ragdoll.joints) == 0


def test_ragdoll_controls():
    """Test muscle contraction when Q, W, O, P keys are pressed."""
    space = pymunk.Space()
    ragdoll = Ragdoll(space, start_x=0.0, start_y=0.0)

    # 1. Press Q (Right hip forward, left hip back)
    ragdoll.apply_controls(q_pressed=True, w_pressed=False, o_pressed=False, p_pressed=False)
    assert ragdoll.motor_hip_r.rate > 0.0
    assert ragdoll.motor_hip_l.rate < 0.0
    assert ragdoll.motor_hip_r.max_force > 100.0

    # 2. Press W (Left hip forward, right hip back)
    ragdoll.apply_controls(q_pressed=False, w_pressed=True, o_pressed=False, p_pressed=False)
    assert ragdoll.motor_hip_l.rate > 0.0
    assert ragdoll.motor_hip_r.rate < 0.0

    # 3. Press O (Right knee flexes backward < 0, left knee extends forward > 0)
    ragdoll.apply_controls(q_pressed=False, w_pressed=False, o_pressed=True, p_pressed=False)
    assert ragdoll.motor_knee_r.rate < 0.0
    assert ragdoll.motor_knee_l.rate > 0.0
    assert ragdoll.motor_knee_r.max_force > 100.0

    # 4. Press P (Left knee flexes backward < 0, right knee extends forward > 0)
    ragdoll.apply_controls(q_pressed=False, w_pressed=False, o_pressed=False, p_pressed=True)
    assert ragdoll.motor_knee_l.rate < 0.0
    assert ragdoll.motor_knee_r.rate > 0.0

    # 5. Release all keys (relaxed state with holding torque)
    ragdoll.apply_controls(q_pressed=False, w_pressed=False, o_pressed=False, p_pressed=False)
    assert ragdoll.motor_hip_r.rate == 0.0
    assert ragdoll.motor_knee_r.rate == 0.0
    assert ragdoll.motor_hip_r.max_force == ragdoll.HIP_HOLD_TORQUE
    assert ragdoll.motor_knee_r.max_force == ragdoll.KNEE_HOLD_TORQUE


def test_ragdoll_idle_stability():
    """Verify runner stands stably without immediately crashing when idle."""
    world = PhysicsWorld()
    for _ in range(120):  # 2 full seconds of idle physics
        world.update(1.0 / 60.0, {})
        assert not world.is_crashed
    assert world.runner.torso.position.y > 0.8  # Still standing upright


def test_physics_world_simulation_step():
    """Test physics world time progression and stability."""
    world = PhysicsWorld()
    assert world.time_elapsed == 0.0
    assert not world.is_crashed
    assert not world.is_victory

    # Step simulation
    world.update(1.0 / 60.0, {"thigh_q": True})
    assert world.time_elapsed > 0.0

    # Verify reset
    world.reset()
    assert world.time_elapsed == 0.0
    assert not world.is_crashed


def test_physics_world_victory_condition():
    """Test reaching finish line triggers victory callback."""
    world = PhysicsWorld()
    victory_called = False

    def on_win():
        nonlocal victory_called
        victory_called = True

    world.on_victory = on_win

    # Move runner beyond finish line
    world.runner.torso.position = (FINISH_LINE_X + 2.0, 1.5)
    world.update(1.0 / 60.0, {})

    assert world.is_victory
    assert victory_called
