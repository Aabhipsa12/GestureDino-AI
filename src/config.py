"""
Configuration and constants for GestureDino AI.
Centralizes display settings, physics constants, gameplay rules, and colors.
"""

from typing import Tuple

# Display Settings (Full HD Video Call format)
WINDOW_TITLE: str = "GestureDino AI 🦖📹"
SCREEN_WIDTH: int = 1280
SCREEN_HEIGHT: int = 720
FPS: int = 60

# World & Ground Settings
# Ground positioned near the bottom of the video call frame so your face and torso are completely clear!
GROUND_Y: int = 600

# Player Physics & Dimensions
PLAYER_X: int = 120  # Fixed horizontal position on screen
PLAYER_WIDTH: int = 50
PLAYER_HEIGHT_STAND: int = 64
PLAYER_HEIGHT_DUCK: int = 32  # 50% height when ducking

# Physics tuning
GRAVITY: float = 2100.0         # px / s^2
JUMP_VELOCITY: float = -780.0   # Initial upward impulse (px / s)
TERMINAL_VELOCITY: float = 1400.0

# Gameplay Speed & Progression
INITIAL_GAME_SPEED: float = 380.0   # Horizontal obstacle speed in px / s
MAX_GAME_SPEED: float = 850.0       # Top speed cap
SPEED_INCREASE_RATE: float = 2.5    # Speed added per 100 points
SCORE_PER_SECOND: float = 10.0      # Score points accumulated per second of survival

# Obstacle Dimensions & Spawning Rules
OBSTACLE_GROUND_WIDTH: int = 36
OBSTACLE_GROUND_HEIGHT: int = 58

OBSTACLE_AIR_WIDTH: int = 54
OBSTACLE_AIR_HEIGHT: int = 30
OBSTACLE_AIR_Y: int = 525  # Positioned at standing head-height: must duck!

MIN_SPAWN_INTERVAL: float = 1.3     # Minimum seconds between obstacles
MAX_SPAWN_INTERVAL: float = 2.5     # Maximum seconds between obstacles

# Aesthetic Palette (Vibrant Neon to contrast cleanly over your camera feed)
COLOR_GROUND: Tuple[int, int, int] = (25, 30, 45)
COLOR_GROUND_LINE: Tuple[int, int, int] = (0, 240, 180)
COLOR_PLAYER: Tuple[int, int, int] = (60, 255, 120)
COLOR_PLAYER_EYE: Tuple[int, int, int] = (20, 30, 40)
COLOR_OBSTACLE_GROUND: Tuple[int, int, int] = (255, 90, 50)
COLOR_OBSTACLE_AIR: Tuple[int, int, int] = (245, 60, 190)
COLOR_TEXT: Tuple[int, int, int] = (250, 250, 255)
COLOR_TEXT_MUTED: Tuple[int, int, int] = (160, 175, 200)
COLOR_ACCENT: Tuple[int, int, int] = (255, 220, 50)
