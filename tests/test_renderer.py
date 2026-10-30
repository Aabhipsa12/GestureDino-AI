"""
Automated unit tests for the GameRenderer across all game states.
Runs headlessly using the SDL dummy video driver.
"""

import os
import pytest

# Ensure headless test execution without requiring physical monitor
os.environ["SDL_VIDEODRIVER"] = "dummy"
import pygame

from src.input_controller import GameInput
from src.game_state import GameEngine, GameState
from src.renderer import GameRenderer
from src.obstacles import Obstacle, ObstacleType
from src.config import PLAYER_X, GROUND_Y, OBSTACLE_GROUND_HEIGHT, OBSTACLE_GROUND_WIDTH, OBSTACLE_AIR_Y, OBSTACLE_AIR_WIDTH, OBSTACLE_AIR_HEIGHT


@pytest.fixture(scope="module", autouse=True)
def init_pygame():
    pygame.init()
    pygame.font.init()
    yield
    pygame.quit()


def test_renderer_initialization() -> None:
    """Verify renderer initializes with target dimensions."""
    renderer = GameRenderer(1280, 720)
    assert renderer.width == 1280
    assert renderer.height == 720


def test_renderer_renders_all_game_states() -> None:
    """Verify overlay rendering executes cleanly across all game states directly onto target surface."""
    renderer = GameRenderer(1280, 720)
    target_surf = pygame.Surface((1280, 720))
    engine = GameEngine()

    # 1. Start Screen
    assert engine.state == GameState.START_SCREEN
    renderer.render_overlay(target_surf, engine, dt=0.016)

    # 2. Playing (with both ground and aerial obstacles active)
    engine.start_game()
    engine.obstacle_manager.obstacles.append(
        Obstacle(ObstacleType.GROUND, 400.0, GROUND_Y - OBSTACLE_GROUND_HEIGHT, OBSTACLE_GROUND_WIDTH, OBSTACLE_GROUND_HEIGHT)
    )
    engine.obstacle_manager.obstacles.append(
        Obstacle(ObstacleType.AIR, 600.0, OBSTACLE_AIR_Y, OBSTACLE_AIR_WIDTH, OBSTACLE_AIR_HEIGHT)
    )
    renderer.render_overlay(target_surf, engine, dt=0.016)

    # Ducking posture rendering
    engine.player.update(dt=0.016, jump_pressed=False, duck_held=True)
    renderer.render_overlay(target_surf, engine, dt=0.016)

    # Jumping posture rendering
    engine.player.update(dt=0.016, jump_pressed=True, duck_held=False)
    renderer.render_overlay(target_surf, engine, dt=0.016)

    # 3. Paused
    engine.toggle_pause()
    renderer.render_overlay(target_surf, engine, dt=0.016)

    # 4. Game Over
    engine.state = GameState.GAME_OVER
    renderer.render_overlay(target_surf, engine, dt=0.016)
