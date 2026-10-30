"""
GestureDino AI — Video Call Native Edition.

Architecture:
- Full-screen high-resolution camera mirroring (1280x720) with fast C-buffer blitting.
- Seamless Video Call Overlay: You and your room remain 100% visible!
- Only the Dino, ground line, obstacles, and sleek floating HUD appear on top.
- Ultra-smooth 60 FPS loop with real-time Hand Gesture tracking:
    - ✋ OPEN PALM  -> JUMP
    - ✊ CLOSED FIST -> DUCK / SLIDE
- Interactive "▶ PLAY GAME" button directly in the call.
"""

import sys
from pathlib import Path

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import cv2
import numpy as np
import pygame

from src.config import WINDOW_TITLE, SCREEN_WIDTH, SCREEN_HEIGHT, FPS
from src.gesture_controller import HybridGestureInputController
from src.hand_tracking import HandTracker, HandGesture
from src.video_call_compositor import VideoCallCompositor
from src.game_state import GameEngine, GameState
from src.renderer import GameRenderer


def open_webcam():
    """Initializes Windows camera with low-latency DirectShow and HD capture."""
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    if not cap.isOpened():
        cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    # Enable buffer size 1 to prevent frame lag buildup
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    return cap


def main() -> None:
    pygame.init()
    pygame.font.init()

    # HD Video Call Resolution
    CALL_WIDTH = SCREEN_WIDTH
    CALL_HEIGHT = SCREEN_HEIGHT

    screen = pygame.display.set_mode((CALL_WIDTH, CALL_HEIGHT))
    pygame.display.set_caption("GestureDino AI — Video Call Edition 🦖📹")
    clock = pygame.time.Clock()

    # Subsystems
    input_controller = HybridGestureInputController()
    engine = GameEngine()
    renderer = GameRenderer(CALL_WIDTH, CALL_HEIGHT)
    compositor = VideoCallCompositor(CALL_WIDTH, CALL_HEIGHT)

    # Initialize Webcam
    print("[INFO] Connecting to camera...")
    cap = open_webcam()
    has_webcam = cap.isOpened()
    if has_webcam:
        print("[SUCCESS] Camera connected.")
    else:
        print("[WARN] Camera unavailable. Running in simulator mode.")

    # Initialize Hand Tracker
    print("[INFO] Initializing MediaPipe Hand Tracker...")
    tracker = HandTracker()
    if tracker.is_initialized:
        print("[SUCCESS] Hand Tracker ready!")
    else:
        print("[WARN] Hand Tracker could not load model.")

    print("\n" + "=" * 55)
    print(" GESTUREDINO AI — VIDEO CALL & GESTURE READY")
    print(" Controls:")
    print("   ✋ OPEN PALM   : Jump")
    print("   ✊ CLOSED FIST  : Duck / Slide")
    print("   Keyboard Fallback: [Space/Up] Jump, [Down] Duck")
    print("   Click 'PLAY GAME' on screen to start playing!")
    print("=" * 55 + "\n")

    current_gesture = HandGesture.NONE

    while engine.is_running:
        dt = min(clock.tick(FPS) / 1000.0, 0.05)

        # 1. Grab camera frame
        if has_webcam:
            ret, frame = cap.read()
            if not ret or frame is None:
                frame = np.zeros((CALL_HEIGHT, CALL_WIDTH, 3), dtype=np.uint8)
            else:
                frame = cv2.flip(frame, 1)  # Natural mirror
        else:
            frame = np.zeros((CALL_HEIGHT, CALL_WIDTH, 3), dtype=np.uint8)
            cv2.putText(frame, "Webcam unavailable - Keyboard Mode", (440, 360),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (120, 150, 180), 2)

        # 2. Hand Gesture Detection
        if tracker.is_initialized:
            current_gesture, frame = tracker.process_frame(frame)
        else:
            current_gesture = HandGesture.NONE

        # 3. Fast render webcam frame onto screen
        compositor.draw_webcam_to_screen(screen, frame)

        # 4. Handle events & button clicks
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                engine.is_running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                action = compositor.process_mouse_click(event.pos)
                if action == "START_GAME":
                    engine.start_game()
                elif action == "STOP_GAME":
                    engine.state = GameState.START_SCREEN
                elif action == "QUIT":
                    engine.is_running = False

        # 5. Poll inputs (Gestures + Keyboard fallback)
        inputs = input_controller.poll(events=events, current_gesture=current_gesture)

        # 6. If playing: update game physics & render entities directly over camera!
        if compositor.game_active:
            engine.tick(dt=dt, inputs=inputs)
            renderer.render_overlay(screen, engine, dt)

        # 7. Draw Video Call Chrome (Header, status pill, control buttons)
        compositor.draw_call_ui(screen, current_gesture)

        # 8. Present frame
        pygame.display.flip()

    # Clean shutdown
    if has_webcam:
        cap.release()
    tracker.release()
    pygame.quit()
    sys.exit(0)


if __name__ == "__main__":
    main()
