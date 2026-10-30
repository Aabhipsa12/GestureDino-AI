"""
Automated unit tests for the Obstacle and ObstacleManager systems.
"""

from src.config import (
    INITIAL_GAME_SPEED,
    MAX_GAME_SPEED,
    SCREEN_WIDTH,
    OBSTACLE_AIR_Y,
    GROUND_Y,
)
from src.obstacles import Obstacle, ObstacleManager, ObstacleType


def test_obstacle_movement() -> None:
    """Verify obstacle moves left based on delta time and speed."""
    obs = Obstacle(ObstacleType.GROUND, x=500.0, y=300.0, width=30.0, height=50.0)
    dt = 0.5
    speed = 300.0
    obs.update(dt, speed)
    assert obs.x == 500.0 - (300.0 * 0.5)
    assert obs.is_off_screen is False


def test_obstacle_off_screen_detection() -> None:
    """Verify obstacle reports is_off_screen correctly."""
    obs = Obstacle(ObstacleType.GROUND, x=-60.0, y=300.0, width=30.0, height=50.0)
    assert obs.is_off_screen is True


def test_obstacle_manager_spawns_and_cleans() -> None:
    """Verify manager spawns obstacles and removes off-screen ones over time."""
    manager = ObstacleManager()
    assert len(manager.obstacles) == 0

    # Advance time past spawn delay
    manager.update(dt=3.0, current_score=0.0)
    assert len(manager.obstacles) >= 1
    
    first_obs = manager.obstacles[0]
    assert first_obs.x >= SCREEN_WIDTH

    # Advance substantial time so first obstacle moves completely off screen
    # At 340 px/s, 4 seconds moves ~1360px which clears the screen
    for _ in range(40):
        manager.update(dt=0.1, current_score=50.0)

    # First obstacle must have been cleaned up
    assert first_obs not in manager.obstacles


def test_obstacle_manager_minimum_gap() -> None:
    """Verify consecutive obstacles respect the minimum gap."""
    manager = ObstacleManager()
    # Force two rapid spawns
    manager.next_spawn_delay = 0.0
    manager.update(dt=0.01, current_score=0.0)
    
    # Attempt another immediate spawn
    manager.next_spawn_delay = 0.0
    manager.update(dt=0.01, current_score=0.0)

    # Should only have 1 obstacle because safe gap was not yet cleared
    assert len(manager.obstacles) == 1


def test_speed_scaling_capped() -> None:
    """Verify game speed ramps with score but never exceeds max speed."""
    manager = ObstacleManager()
    assert manager.speed == INITIAL_GAME_SPEED

    # High score
    manager.update(dt=0.1, current_score=5000.0)
    assert manager.speed > INITIAL_GAME_SPEED
    assert manager.speed <= MAX_GAME_SPEED
