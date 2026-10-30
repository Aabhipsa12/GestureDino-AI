"""
Gesture and Hybrid Input Controller for GestureDino AI.
Supports:
  - ✌️ V-SIGN (Index + Middle extended): HOVER / NEUTRAL RUN
  - ✋ OPEN PALM: JUMP (Edge-triggered when opening hand from V-sign/Fist)
  - ✊ CLOSED FIST: SLIDE / DUCK (Active while fist is held)
"""

from typing import Optional, List
import pygame

from src.input_controller import BaseInputController, GameInput
from src.hand_tracking import HandGesture


class HybridGestureInputController(BaseInputController):
    def __init__(self) -> None:
        self.last_gesture: HandGesture = HandGesture.NONE
        self.gesture_jump_debounced: bool = False

    def poll(
        self,
        events: Optional[List[pygame.event.Event]] = None,
        current_gesture: HandGesture = HandGesture.NONE,
    ) -> GameInput:
        if events is None:
            events = pygame.event.get()

        jump_pressed = False
        pause_triggered = False
        restart_triggered = False
        quit_triggered = False

        # 1. Keyboard & Window events
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

        keys = pygame.key.get_pressed()
        kbd_duck_held = bool(keys[pygame.K_DOWN])

        # 2. Hand Gesture Processing
        # Open Palm -> Jump
        if current_gesture == HandGesture.OPEN_PALM:
            if not self.gesture_jump_debounced:
                jump_pressed = True
                self.gesture_jump_debounced = True
        else:
            # When hand transitions back to V-sign (Hover) or Fist, rearm the jump trigger
            self.gesture_jump_debounced = False

        # Closed Fist -> Duck / Slide (Held active as long as fist is clenched)
        gesture_duck_held = (current_gesture == HandGesture.CLOSED_FIST)

        duck_held = kbd_duck_held or gesture_duck_held
        self.last_gesture = current_gesture

        return GameInput(
            jump_pressed=jump_pressed,
            duck_held=duck_held,
            pause_triggered=pause_triggered,
            restart_triggered=restart_triggered,
            quit_triggered=quit_triggered,
        )

    def reset(self) -> None:
        self.last_gesture = HandGesture.NONE
        self.gesture_jump_debounced = False
