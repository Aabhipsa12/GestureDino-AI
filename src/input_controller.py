"""
Input Abstraction Layer for GestureDino AI.

Decouples physical input hardware (Keyboard, Gestures, or Tests) from the core game engine.
The game engine only consumes high-level GameInput actions.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional
import pygame


@dataclass
class GameInput:
    """
    Unified representation of user actions for a single game tick.
    
    Attributes:
        jump_pressed: True only on the frame the jump action was initiated.
                      (Edge-triggered to prevent holding space from auto-bouncing).
        duck_held: True as long as the duck action is continuously active.
                   (Level-triggered: player remains ducked while held).
        pause_triggered: True when the player requests pause/resume toggle.
        restart_triggered: True when the player requests restarting a game over.
        quit_triggered: True when the player requests exiting the game.
    """
    jump_pressed: bool = False
    duck_held: bool = False
    pause_triggered: bool = False
    restart_triggered: bool = False
    quit_triggered: bool = False


class BaseInputController(ABC):
    """Abstract interface that all input providers (Keyboard, Gesture, Mock) must satisfy."""
    
    @abstractmethod
    def poll(self, events: Optional[List[pygame.event.Event]] = None) -> GameInput:
        """Poll the input device and return the current GameInput state."""
        pass

    def reset(self) -> None:
        """Reset internal input states (e.g. on game restart)."""
        pass


class KeyboardInputController(BaseInputController):
    """
    Translates Pygame keyboard events into unified GameInput actions.
    
    Mapping:
      - Jump: Space or Up Arrow (single press)
      - Duck: Down Arrow (held down)
      - Pause / Resume: P key
      - Restart: R key
      - Quit: Q key, Escape key, or Window close button
    """
    
    def __init__(self) -> None:
        self._jump_was_down: bool = False
    
    def poll(self, events: Optional[List[pygame.event.Event]] = None) -> GameInput:
        if events is None:
            events = pygame.event.get()
            
        jump_pressed = False
        pause_triggered = False
        restart_triggered = False
        quit_triggered = False
        
        for event in events:
            if event.type == pygame.QUIT:
                quit_triggered = True
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_SPACE, pygame.K_UP):
                    jump_pressed = True
                elif event.key == pygame.K_p:
                    pause_triggered = True
                elif event.key == pygame.K_r:
                    restart_triggered = True
                elif event.key in (pygame.K_q, pygame.K_ESCAPE):
                    quit_triggered = True

        # Check continuous hold for ducking
        keys = pygame.key.get_pressed()
        duck_held = bool(keys[pygame.K_DOWN])

        return GameInput(
            jump_pressed=jump_pressed,
            duck_held=duck_held,
            pause_triggered=pause_triggered,
            restart_triggered=restart_triggered,
            quit_triggered=quit_triggered,
        )

    def reset(self) -> None:
        self._jump_was_down = False
