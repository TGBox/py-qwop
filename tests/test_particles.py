"""Unit tests for particle system spawning and updates."""

from py_qwop.render.particles import ParticleSystem


def test_particles_dust_and_confetti():
    """Verify particle creation, update decay, and clearing."""
    ps = ParticleSystem()
    assert len(ps.particles) == 0

    # Spawn dust
    ps.spawn_foot_dust(0.0, 0.0, is_sand=False)
    assert len(ps.particles) > 0
    initial_count = len(ps.particles)

    # Spawn confetti
    ps.spawn_confetti(100.0, 3.0, count=50)
    assert len(ps.particles) == initial_count + 50

    # Advance time to age particles
    ps.update(1.0)
    # Clear all particles
    ps.clear()
    assert len(ps.particles) == 0
