"""
Player entity model and physics for GestureDino AI.
Handles state transitions, jumping physics, crouch mechanics, and hitboxes.
"""

from enum import Enum, auto
from typing import Tuple
import pygame

from src.config import (
    GROUND_Y,
    PLAYER_X,
    PLAYER_WIDTH,
    PLAYER_HEIGHT_STAND,
    PLAYER_HEIGHT_DUCK,
    GRAVITY,
    JUMP_VELOCITY,
    TERMINAL_VELOCITY,
)


class PlayerState(Enum):
    """Lifecycle states for the player character."""
    RUNNING = auto()
    JUMPING = auto()
    DUCKING = auto()


class Player:
    """
    Core player character entity.
    
    Operates on pure coordinates and physics independent of rendering.
    """

    def __init__(self, x: float = PLAYER_X) -> None:
        self.x: float = float(x)
        self.state: PlayerState = PlayerState.RUNNING
        self.vy: float = 0.0
        
        # Dimensions and posture
        self.width: float = float(PLAYER_WIDTH)
        self.height: float = float(PLAYER_HEIGHT_STAND)
        
        # Snap directly to resting ground position
        self.y: float = float(GROUND_Y - self.height)
        
        # Animation & visual cycle
        self.anim_time: float = 0.0
        self.run_cycle_speed: float = 12.0  # Cycles per second

    @property
    def is_on_ground(self) -> bool:
        """True if the player is resting on the ground plane."""
        return abs((self.y + self.height) - GROUND_Y) < 0.001 and self.vy == 0.0

    def jump(self) -> bool:
        """
        Initiate a jump if on the ground.
        Returns True if jump was successfully initiated.
        """
        if self.is_on_ground and self.state != PlayerState.JUMPING:
            self.vy = JUMP_VELOCITY
            self.state = PlayerState.JUMPING
            self.height = float(PLAYER_HEIGHT_STAND)
            self.width = float(PLAYER_WIDTH)
            return True
        return False

    def update(self, dt: float, jump_pressed: bool, duck_held: bool) -> None:
        """
        Advance player physics and state by dt seconds.
        
        Args:
            dt: Delta time in seconds since previous frame.
            jump_pressed: Edge-triggered jump request.
            duck_held: Continuous state of the duck input.
        """
        if dt <= 0.0:
            return

        # 1. Handle Jump Trigger
        if jump_pressed:
            self.jump()

        # 2. Handle Airborne Physics vs Ground Posture
        if self.state == PlayerState.JUMPING or not self.is_on_ground:
            # Player is in the air: apply gravity
            # Fast-fall mechanic: if duck is held mid-air, boost gravity for quick descent
            effective_gravity = GRAVITY * 1.6 if duck_held else GRAVITY
            self.vy = min(self.vy + effective_gravity * dt, TERMINAL_VELOCITY)
            self.y += self.vy * dt

            # If ducking in mid-air, shrink hitbox height to slide over/under hazards
            if duck_held:
                self.height = float(PLAYER_HEIGHT_DUCK)
                self.width = float(PLAYER_WIDTH + 8)
            else:
                self.height = float(PLAYER_HEIGHT_STAND)
                self.width = float(PLAYER_WIDTH)

            # Check ground landing
            if (self.y + self.height) >= GROUND_Y:
                self.y = float(GROUND_Y - self.height)
                self.vy = 0.0
                if duck_held:
                    self.state = PlayerState.DUCKING
                    self.height = float(PLAYER_HEIGHT_DUCK)
                    self.width = float(PLAYER_WIDTH + 8)
                    self.y = float(GROUND_Y - self.height)
                else:
                    self.state = PlayerState.RUNNING
                    self.height = float(PLAYER_HEIGHT_STAND)
                    self.width = float(PLAYER_WIDTH)
                    self.y = float(GROUND_Y - self.height)

        else:
            # Player is on the ground
            if duck_held:
                self.state = PlayerState.DUCKING
                self.height = float(PLAYER_HEIGHT_DUCK)
                self.width = float(PLAYER_WIDTH + 8)
                self.y = float(GROUND_Y - self.height)
            else:
                self.state = PlayerState.RUNNING
                self.height = float(PLAYER_HEIGHT_STAND)
                self.width = float(PLAYER_WIDTH)
                self.y = float(GROUND_Y - self.height)

            # Advance animation cycle while moving on ground
            self.anim_time += dt

    def get_hitbox(self) -> pygame.Rect:
        """
        Get the collision bounding box.
        Includes a 3-pixel fair margin inset to avoid punitive edge collisions.
        """
        inset = 3
        return pygame.Rect(
            int(self.x + inset),
            int(self.y + inset),
            max(4, int(self.width - inset * 2)),
            max(4, int(self.height - inset * 2)),
        )

    def reset(self) -> None:
        """Reset player to initial running state."""
        self.state = PlayerState.RUNNING
        self.vy = 0.0
        self.width = float(PLAYER_WIDTH)
        self.height = float(PLAYER_HEIGHT_STAND)
        self.y = float(GROUND_Y - self.height)
        self.anim_time = 0.0
