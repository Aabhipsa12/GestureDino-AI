"""
Obstacle entities and spawning system for GestureDino AI.

Includes ground obstacles (requiring jump) and aerial obstacles (requiring duck),
with fair-spacing spawn algorithms and speed scaling.
"""

from enum import Enum, auto
from typing import List, Tuple
import random
import pygame

from src.config import (
    GROUND_Y,
    SCREEN_WIDTH,
    OBSTACLE_GROUND_WIDTH,
    OBSTACLE_GROUND_HEIGHT,
    OBSTACLE_AIR_WIDTH,
    OBSTACLE_AIR_HEIGHT,
    OBSTACLE_AIR_Y,
    MIN_SPAWN_INTERVAL,
    MAX_SPAWN_INTERVAL,
    INITIAL_GAME_SPEED,
    MAX_GAME_SPEED,
    SPEED_INCREASE_RATE,
)


class ObstacleType(Enum):
    """Categories of obstacles determining dodge technique."""
    GROUND = auto()  # Low hazard — player must JUMP
    AIR = auto()     # Flying hazard at head-height — player must DUCK


class Obstacle:
    """An individual moving hazard on the field."""

    def __init__(
        self,
        obstacle_type: ObstacleType,
        x: float,
        y: float,
        width: float,
        height: float,
        variant: int = 0,
    ) -> None:
        self.obstacle_type = obstacle_type
        self.x: float = float(x)
        self.y: float = float(y)
        self.width: float = float(width)
        self.height: float = float(height)
        self.variant: int = variant
        self.anim_time: float = 0.0

    def update(self, dt: float, current_speed: float) -> None:
        """Advance obstacle position to the left according to game speed."""
        self.x -= current_speed * dt
        self.anim_time += dt

    @property
    def is_off_screen(self) -> bool:
        """True when the obstacle has completely exited the left side of the screen."""
        return (self.x + self.width) < -20.0

    def get_hitbox(self) -> pygame.Rect:
        """
        Get collision bounding box with a 2px fair margin inset.
        Prevents frustration from microscopic edge clipping.
        """
        inset = 2
        return pygame.Rect(
            int(self.x + inset),
            int(self.y + inset),
            max(4, int(self.width - inset * 2)),
            max(4, int(self.height - inset * 2)),
        )


class ObstacleManager:
    """
    Manages obstacle spawning intervals, movement, speed ramping, and despawning.
    Guarantees that impossible obstacle clusters are never spawned.
    """

    def __init__(self) -> None:
        self.obstacles: List[Obstacle] = []
        self.speed: float = INITIAL_GAME_SPEED
        self.spawn_timer: float = 0.0
        self.next_spawn_delay: float = random.uniform(MIN_SPAWN_INTERVAL, MAX_SPAWN_INTERVAL)
        self.min_gap: float = 240.0  # Minimum safe horizontal pixels between obstacles

    def reset(self) -> None:
        """Clear all active obstacles and reset speed to initial baseline."""
        self.obstacles.clear()
        self.speed = INITIAL_GAME_SPEED
        self.spawn_timer = 0.0
        self.next_spawn_delay = random.uniform(MIN_SPAWN_INTERVAL, MAX_SPAWN_INTERVAL)

    def update(self, dt: float, current_score: float) -> None:
        """
        Update all active obstacles and determine if a new obstacle should spawn.
        
        Args:
            dt: Delta time in seconds.
            current_score: Current game score, used to scale difficulty.
        """
        # 1. Gradually ramp game speed based on score (capped at MAX_GAME_SPEED)
        speed_boost = (current_score / 100.0) * SPEED_INCREASE_RATE * 8.0
        self.speed = min(INITIAL_GAME_SPEED + speed_boost, MAX_GAME_SPEED)

        # 2. Update existing obstacles
        for obstacle in self.obstacles:
            obstacle.update(dt, self.speed)

        # 3. Clean up off-screen obstacles
        self.obstacles = [obs for obs in self.obstacles if not obs.is_off_screen]

        # 4. Spawner countdown logic
        self.spawn_timer += dt
        if self.spawn_timer >= self.next_spawn_delay:
            # Check safe distance from the rightmost existing obstacle
            can_spawn = True
            if self.obstacles:
                rightmost_x = max(obs.x for obs in self.obstacles)
                if (SCREEN_WIDTH - rightmost_x) < self.min_gap:
                    can_spawn = False

            if can_spawn:
                self._spawn_random_obstacle()
                self.spawn_timer = 0.0
                # Spawn delays tighten slightly as speed increases
                speed_factor = INITIAL_GAME_SPEED / self.speed
                min_delay = max(0.9, MIN_SPAWN_INTERVAL * speed_factor)
                max_delay = max(1.6, MAX_SPAWN_INTERVAL * speed_factor)
                self.next_spawn_delay = random.uniform(min_delay, max_delay)

    def _spawn_random_obstacle(self) -> None:
        """Spawn either a ground obstacle (jump) or aerial obstacle (duck)."""
        spawn_x = SCREEN_WIDTH + 20

        # Aerial obstacles appear slightly less frequently (35% chance)
        is_air = random.random() < 0.35

        if is_air:
            # Aerial drone / hovering hazard requiring duck
            self.obstacles.append(
                Obstacle(
                    obstacle_type=ObstacleType.AIR,
                    x=spawn_x,
                    y=OBSTACLE_AIR_Y,
                    width=OBSTACLE_AIR_WIDTH,
                    height=OBSTACLE_AIR_HEIGHT,
                    variant=random.randint(0, 1),
                )
            )
        else:
            # Ground hazard requiring jump
            variant = random.randint(0, 2)
            if variant == 0:
                # Standard spike / crystal
                w, h = OBSTACLE_GROUND_WIDTH, OBSTACLE_GROUND_HEIGHT
            elif variant == 1:
                # Short wide hazard
                w, h = OBSTACLE_GROUND_WIDTH + 14, OBSTACLE_GROUND_HEIGHT - 12
            else:
                # Tall spire
                w, h = OBSTACLE_GROUND_WIDTH - 6, OBSTACLE_GROUND_HEIGHT + 6

            self.obstacles.append(
                Obstacle(
                    obstacle_type=ObstacleType.GROUND,
                    x=spawn_x,
                    y=GROUND_Y - h,
                    width=w,
                    height=h,
                    variant=variant,
                )
            )
