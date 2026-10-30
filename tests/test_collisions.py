"""
Automated unit tests for precise collision detection logic.
"""

from src.config import (
    GROUND_Y,
    PLAYER_X,
    OBSTACLE_AIR_Y,
    OBSTACLE_GROUND_WIDTH,
    OBSTACLE_GROUND_HEIGHT,
    OBSTACLE_AIR_WIDTH,
    OBSTACLE_AIR_HEIGHT,
)
from src.input_controller import GameInput
from src.player import Player
from src.obstacles import Obstacle, ObstacleType
from src.game_state import GameEngine, GameState


def test_standing_into_ground_obstacle_collides() -> None:
    """A standing player at player_x collides with a ground obstacle at player_x."""
    engine = GameEngine()
    engine.start_game()
    
    # Place ground obstacle directly overlapping player x
    obs = Obstacle(
        obstacle_type=ObstacleType.GROUND,
        x=PLAYER_X,
        y=GROUND_Y - OBSTACLE_GROUND_HEIGHT,
        width=OBSTACLE_GROUND_WIDTH,
        height=OBSTACLE_GROUND_HEIGHT,
    )
    engine.obstacle_manager.obstacles.append(obs)
    
    assert engine.check_collisions() is True
    engine.tick(dt=0.016, inputs=GameInput())
    assert engine.state == GameState.GAME_OVER


def test_jumping_over_ground_obstacle_avoids_collision() -> None:
    """When the player has jumped high above the ground obstacle, no collision occurs."""
    engine = GameEngine()
    engine.start_game()
    
    # Place ground obstacle at player_x
    obs = Obstacle(
        obstacle_type=ObstacleType.GROUND,
        x=PLAYER_X,
        y=GROUND_Y - OBSTACLE_GROUND_HEIGHT,
        width=OBSTACLE_GROUND_WIDTH,
        height=OBSTACLE_GROUND_HEIGHT,
    )
    engine.obstacle_manager.obstacles.append(obs)

    # Move player up into jump apex
    engine.player.y = GROUND_Y - 180.0
    engine.player.vy = 0.0

    assert engine.check_collisions() is False


def test_standing_into_aerial_obstacle_collides() -> None:
    """A standing player collides with an aerial drone at head height."""
    engine = GameEngine()
    engine.start_game()

    # Place aerial obstacle directly overlapping player x
    obs = Obstacle(
        obstacle_type=ObstacleType.AIR,
        x=PLAYER_X,
        y=OBSTACLE_AIR_Y,
        width=OBSTACLE_AIR_WIDTH,
        height=OBSTACLE_AIR_HEIGHT,
    )
    engine.obstacle_manager.obstacles.append(obs)

    assert engine.check_collisions() is True


def test_ducking_under_aerial_obstacle_avoids_collision() -> None:
    """A ducking player ducks low enough that the head-height aerial drone passes harmlessly overhead."""
    engine = GameEngine()
    engine.start_game()

    # Place aerial obstacle at player x
    obs = Obstacle(
        obstacle_type=ObstacleType.AIR,
        x=PLAYER_X,
        y=OBSTACLE_AIR_Y,
        width=OBSTACLE_AIR_WIDTH,
        height=OBSTACLE_AIR_HEIGHT,
    )
    engine.obstacle_manager.obstacles.append(obs)

    # Player ducks
    engine.player.update(dt=0.016, jump_pressed=False, duck_held=True)
    
    # Verify player top is safely below the bottom of the aerial obstacle
    player_box = engine.player.get_hitbox()
    obs_box = obs.get_hitbox()
    assert not player_box.colliderect(obs_box)
    assert engine.check_collisions() is False
