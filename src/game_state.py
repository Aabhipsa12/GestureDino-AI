"""
Core Game Engine and State Machine for GestureDino AI.

Manages all game simulation logic, collision detection, scoring,
and game state transitions headlessly.
"""

from enum import Enum, auto
from typing import Optional
from pathlib import Path

from src.config import SCORE_PER_SECOND, INITIAL_GAME_SPEED
from src.input_controller import GameInput
from src.player import Player, PlayerState
from src.obstacles import ObstacleManager, ObstacleType
from src.high_score import load_high_score, save_high_score, DEFAULT_HIGH_SCORE_FILE


class GameState(Enum):
    """Overall gameplay lifecycle states."""
    START_SCREEN = auto()
    PLAYING = auto()
    PAUSED = auto()
    GAME_OVER = auto()


class GameEngine:
    """
    Pure simulation engine for GestureDino AI.
    
    Contains NO window or audio calls, allowing for 100% headless testing.
    """

    def __init__(self, high_score_file: Optional[Path] = None) -> None:
        self.high_score_file: Path = high_score_file or DEFAULT_HIGH_SCORE_FILE
        self.state: GameState = GameState.START_SCREEN
        
        self.player: Player = Player()
        self.obstacle_manager: ObstacleManager = ObstacleManager()
        
        self.score: float = 0.0
        self.high_score: int = load_high_score(self.high_score_file)
        self.is_running: bool = True  # Application exit flag

    def start_game(self) -> None:
        """Begin active gameplay from start screen or reset."""
        self.state = GameState.PLAYING
        self.score = 0.0
        self.player.reset()
        self.obstacle_manager.reset()

    def restart(self) -> None:
        """Restart after game over."""
        self.start_game()

    def toggle_pause(self) -> None:
        """Toggle between PLAYING and PAUSED states."""
        if self.state == GameState.PLAYING:
            self.state = GameState.PAUSED
        elif self.state == GameState.PAUSED:
            self.state = GameState.PLAYING

    def check_collisions(self) -> bool:
        """
        Check if player hitbox intersects any active obstacle hitbox.
        Returns True if a collision occurred.
        """
        player_rect = self.player.get_hitbox()
        for obstacle in self.obstacle_manager.obstacles:
            if player_rect.colliderect(obstacle.get_hitbox()):
                return True
        return False

    def tick(self, dt: float, inputs: GameInput) -> None:
        """
        Advance the game simulation by dt seconds with the provided inputs.
        
        Args:
            dt: Elapsed time in seconds.
            inputs: High-level GameInput actions for this tick.
        """
        # Handle universal quit
        if inputs.quit_triggered:
            self.is_running = False
            return

        if self.state == GameState.START_SCREEN:
            # Pressing jump or restart starts the game
            if inputs.jump_pressed or inputs.restart_triggered:
                self.start_game()

        elif self.state == GameState.PLAYING:
            if inputs.pause_triggered:
                self.toggle_pause()
                return

            # 1. Update Player
            self.player.update(
                dt=dt,
                jump_pressed=inputs.jump_pressed,
                duck_held=inputs.duck_held,
            )

            # 2. Accumulate Score
            # Faster speeds reward slightly higher score rates
            speed_ratio = self.obstacle_manager.speed / INITIAL_GAME_SPEED
            self.score += dt * SCORE_PER_SECOND * speed_ratio

            # 3. Update Obstacles with current score for speed scaling
            self.obstacle_manager.update(dt=dt, current_score=self.score)

            # 4. Check Collisions
            if self.check_collisions():
                self.state = GameState.GAME_OVER
                current_int_score = int(self.score)
                if current_int_score > self.high_score:
                    self.high_score = current_int_score
                    save_high_score(self.high_score, self.high_score_file)

        elif self.state == GameState.PAUSED:
            if inputs.pause_triggered:
                self.toggle_pause()

        elif self.state == GameState.GAME_OVER:
            if inputs.restart_triggered or inputs.jump_pressed:
                self.restart()
