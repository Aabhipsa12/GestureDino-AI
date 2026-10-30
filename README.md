# GestureDino AI 🦖⚡

An original endless-runner game built in Python and Pygame, featuring real-time **hand gesture controls** (via Google MediaPipe) composited directly into a **live webcam video call interface**.

Play right in your video conference stream using natural hand movements:
- ✋ **Open Palm**: Jump over ground obstacles
- ✊ **Closed Fist**: Duck / Slide under flying surveillance drones

---

## Architecture & Features

1. **Video Call Interface (`src/video_call_compositor.py`)**:
   - 1280×720 HD live mirrored webcam feed.
   - Interactive on-screen "▶ PLAY GAME" card.
   - Picture-in-Picture game viewport positioned so the player's face/upper body remains fully visible on camera.
   - Live visual status pills showing recognized gestures and confidence in real time.

2. **Hand Tracking & Gesture Classification (`src/hand_tracking.py`)**:
   - Modern Google MediaPipe Tasks API (`HandLandmarker`) running in `RunningMode.VIDEO`.
   - Real-time 21-landmark hand skeleton visualization.
   - Relative finger geometry classifier:
     - 4+ extended fingers $\rightarrow$ `OPEN_PALM` (Jump)
     - Clenched fingers $\rightarrow$ `CLOSED_FIST` (Duck)

3. **Hybrid Input Controller (`src/gesture_controller.py`)**:
   - Edge-triggered jump debouncing to prevent auto-repeat loops.
   - Full keyboard fallback (Space/Up, Down, P, R, Q/Esc).

4. **Pure Game Simulation Engine (`src/game_state.py`)**:
   - Headless physics simulation ($y$, $v_y$, gravity, jump velocity, crouch hitboxes).
   - Dynamic obstacle spawner with fair-spacing guarantees and progressive speed ramping.
   - Persistent local high score saving (`data/high_score.json`).
   - 100% automated test coverage across 21 test suites.

---

## Installation & Setup

### Prerequisites
- Python 3.14.6 (64-bit)
- Working webcam

### Quick Start
```powershell
cd D:\GestureProjects\GestureDino
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python src/main.py
```

### Controls
| Control | Action |
|---|---|
| ✋ **Open Palm** or **Space / Up** | Jump |
| ✊ **Closed Fist** or **Down Arrow (Hold)** | Duck / Slide |
| **P** | Pause / Resume |
| **R** | Restart (after Game Over) |
| **Q** or **Escape** | Exit |

---

## Running Automated Tests
```powershell
.\.venv\Scripts\pytest -v tests/
```
