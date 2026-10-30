"""
Automated unit tests for score accumulation, state transitions, and high score persistence.
"""

from pathlib import Path
import tempfile

from src.input_controller import GameInput
from src.game_state import GameEngine, GameState
from src.high_score import save_high_score, load_high_score


def test_score_accumulates_during_play() -> None:
    """Verify score increases proportionally with delta time while playing."""
    engine = GameEngine()
    engine.start_game()
    assert engine.score == 0.0

    # Advance 1.0 second
    engine.tick(dt=1.0, inputs=GameInput())
    assert engine.score > 0.0


def test_score_does_not_accumulate_while_paused() -> None:
    """Verify paused state freezes score progression."""
    engine = GameEngine()
    engine.start_game()
    engine.toggle_pause()
    assert engine.state == GameState.PAUSED

    current_score = engine.score
    engine.tick(dt=1.0, inputs=GameInput())
    assert engine.score == current_score


def test_high_score_file_persistence() -> None:
    """Verify saving and loading high score to a temporary JSON file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = Path(tmpdir) / "high_score.json"
        
        # Missing file returns 0
        assert load_high_score(test_file) == 0

        # Save and verify
        assert save_high_score(450, test_file) is True
        assert load_high_score(test_file) == 450


def test_game_over_updates_high_score_and_restart_resets_current() -> None:
    """Verify beating high score saves it, and restarting resets score to zero."""
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = Path(tmpdir) / "high_score.json"
        engine = GameEngine(high_score_file=test_file)
        engine.start_game()

        # Simulate achieving a score of 120
        engine.score = 120.0
        
        # Trigger game over via state
        engine.state = GameState.PLAYING
        # Simulate collision
        from src.config import PLAYER_X, GROUND_Y, OBSTACLE_GROUND_HEIGHT, OBSTACLE_GROUND_WIDTH
        from src.obstacles import Obstacle, ObstacleType
        engine.obstacle_manager.obstacles.append(
            Obstacle(ObstacleType.GROUND, PLAYER_X, GROUND_Y - OBSTACLE_GROUND_HEIGHT, OBSTACLE_GROUND_WIDTH, OBSTACLE_GROUND_HEIGHT)
        )
        engine.tick(dt=0.016, inputs=GameInput())
        
        assert engine.state == GameState.GAME_OVER
        assert engine.high_score == 120
        assert load_high_score(test_file) == 120

        # Restart
        engine.tick(dt=0.016, inputs=GameInput(restart_triggered=True))
        assert engine.state == GameState.PLAYING
        assert engine.score == 0.0
        assert engine.high_score == 120
