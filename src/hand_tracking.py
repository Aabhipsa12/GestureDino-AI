"""
Hand Tracking & Gesture Classification Engine for GestureDino AI.
Supports 3 distinct hand poses:
  - ✌️ PEACE / V-SIGN (Index + Middle extended, others curled): HOVER / RUN (Neutral state)
  - ✋ OPEN PALM (All fingers extended): JUMP (Edge-triggered)
  - ✊ CLOSED FIST (All fingers curled): SLIDE / DUCK (Continuous hold)
"""

import os
import time
from enum import Enum, auto
from typing import Optional, Tuple
from pathlib import Path

import cv2
import numpy as np
import mediapipe as mp
from mediapipe.tasks.python import BaseOptions
from mediapipe.tasks.python.vision import (
    HandLandmarker,
    HandLandmarkerOptions,
    RunningMode,
    HandLandmarksConnections,
    drawing_utils,
)

DEFAULT_MODEL_PATH = Path(__file__).resolve().parent.parent / "models" / "hand_landmarker.task"


class HandGesture(Enum):
    NONE = auto()        # No hand detected
    HOVER = auto()       # ✌️ V-sign (Index + Middle): Safe hovering / running
    OPEN_PALM = auto()   # ✋ Open Palm (All extended): Jump
    CLOSED_FIST = auto() # ✊ Closed Fist (All curled): Duck / Slide


class HandTracker:
    def __init__(self, model_path: Optional[str] = None) -> None:
        if model_path is None:
            model_path = str(DEFAULT_MODEL_PATH)
        self.model_path = model_path
        self.landmarker: Optional[HandLandmarker] = None
        self.last_timestamp_ms: int = 0
        self.is_initialized: bool = False
        self._init_detector()

    def _init_detector(self) -> None:
        if not os.path.isfile(self.model_path):
            print(f"[WARN] Hand tracking model not found at {self.model_path}")
            return
        try:
            options = HandLandmarkerOptions(
                base_options=BaseOptions(model_asset_path=self.model_path),
                running_mode=RunningMode.VIDEO,
                num_hands=1,
                min_hand_detection_confidence=0.55,
                min_hand_presence_confidence=0.55,
                min_tracking_confidence=0.55,
            )
            self.landmarker = HandLandmarker.create_from_options(options)
            self.is_initialized = True
        except Exception as e:
            print(f"[ERROR] Failed to load HandLandmarker: {e}")
            self.is_initialized = False

    def process_frame(self, bgr_frame: np.ndarray) -> Tuple[HandGesture, np.ndarray]:
        """Processes frame and returns detected gesture and skeleton drawing."""
        if not self.is_initialized or self.landmarker is None:
            return HandGesture.NONE, bgr_frame

        rgb_frame = cv2.cvtColor(bgr_frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)

        current_timestamp_ms = int(time.time() * 1000)
        if current_timestamp_ms <= self.last_timestamp_ms:
            current_timestamp_ms = self.last_timestamp_ms + 1
        self.last_timestamp_ms = current_timestamp_ms

        gesture = HandGesture.NONE

        try:
            detection_result = self.landmarker.detect_for_video(mp_image, current_timestamp_ms)
            if detection_result.hand_landmarks:
                first_hand = detection_result.hand_landmarks[0]
                
                # Draw hand landmarks
                drawing_utils.draw_landmarks(
                    bgr_frame,
                    first_hand,
                    HandLandmarksConnections.HAND_CONNECTIONS,
                )
                
                gesture = self.classify_gesture(first_hand)
        except Exception:
            pass

        return gesture, bgr_frame

    @staticmethod
    def classify_gesture(landmarks) -> HandGesture:
        """
        Classifies gestures based on individual finger extension relative to wrist.
        Landmark indices:
          Wrist: 0
          Thumb: 4 (tip), 2 (mcp)
          Index: 8 (tip), 6 (pip)
          Middle: 12 (tip), 10 (pip)
          Ring: 16 (tip), 14 (pip)
          Pinky: 20 (tip), 18 (pip)
        """
        wrist = landmarks[0]

        def is_finger_extended(tip_idx: int, pip_idx: int) -> bool:
            tip = landmarks[tip_idx]
            pip = landmarks[pip_idx]
            dist_tip = (tip.x - wrist.x) ** 2 + (tip.y - wrist.y) ** 2
            dist_pip = (pip.x - wrist.x) ** 2 + (pip.y - wrist.y) ** 2
            return dist_tip > (dist_pip * 1.15)

        index_ext = is_finger_extended(8, 6)
        middle_ext = is_finger_extended(12, 10)
        ring_ext = is_finger_extended(16, 14)
        pinky_ext = is_finger_extended(20, 18)

        # Thumb extension
        thumb_tip = landmarks[4]
        thumb_mcp = landmarks[2]
        thumb_dist_tip = (thumb_tip.x - wrist.x) ** 2 + (thumb_tip.y - wrist.y) ** 2
        thumb_dist_mcp = (thumb_mcp.x - wrist.x) ** 2 + (thumb_mcp.y - wrist.y) ** 2
        thumb_ext = thumb_dist_tip > (thumb_dist_mcp * 1.10)

        extended_count = sum([index_ext, middle_ext, ring_ext, pinky_ext, thumb_ext])

        # 1. V-SIGN / PEACE (Hover/Run): Index + Middle are OPEN, Ring + Pinky are CURLED
        if index_ext and middle_ext and (not ring_ext) and (not pinky_ext):
            return HandGesture.HOVER

        # 2. OPEN PALM (Jump): 4 or 5 fingers extended
        if extended_count >= 4:
            return HandGesture.OPEN_PALM

        # 3. CLOSED FIST (Slide/Duck): 0 or 1 finger extended
        if extended_count <= 1:
            return HandGesture.CLOSED_FIST

        # Any transition or ambiguous state defaults to safe HOVER if hand is present
        return HandGesture.HOVER

    def release(self) -> None:
        if self.landmarker:
            self.landmarker.close()
            self.landmarker = None
            self.is_initialized = False
