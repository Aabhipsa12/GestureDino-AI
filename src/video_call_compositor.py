"""
High-Performance Video Call UI & Compositor for GestureDino AI.
Provides:
  - Fast C-buffer camera blitting
  - Video Call UI chrome (Meeting title, live indicators, call controls bar, status pills)
  - 3-Gesture Visual Status Indicator:
      ✌️ V-SIGN: HOVER / RUN
      ✋ OPEN PALM: JUMP
      ✊ CLOSED FIST: SLIDE / DUCK
"""

from typing import Optional, Tuple
import cv2
import numpy as np
import pygame

from src.hand_tracking import HandGesture


class VideoCallCompositor:
    def __init__(self, target_width: int = 1280, target_height: int = 720) -> None:
        self.width = target_width
        self.height = target_height
        
        # State
        self.game_active: bool = False
        self.play_button_rect = pygame.Rect(self.width // 2 - 130, self.height // 2 - 45, 260, 90)
        self.end_call_rect = pygame.Rect(self.width // 2 - 55, self.height - 60, 110, 44)

        if not pygame.font.get_init():
            pygame.font.init()
        font_name = pygame.font.match_font("segoeui") or "arial"
        self.font_title = pygame.font.Font(font_name, 20)
        self.font_sub = pygame.font.Font(font_name, 16)
        self.font_large = pygame.font.Font(font_name, 32)

    def process_mouse_click(self, pos: Tuple[int, int]) -> Optional[str]:
        """Handles clicks on video call UI elements."""
        mx, my = pos
        if not self.game_active and self.play_button_rect.collidepoint(mx, my):
            self.game_active = True
            return "START_GAME"
        elif self.end_call_rect.collidepoint(mx, my):
            if self.game_active:
                self.game_active = False
                return "STOP_GAME"
            else:
                return "QUIT"
        return None

    def draw_webcam_to_screen(self, screen: pygame.Surface, webcam_bgr: np.ndarray) -> None:
        """Fast conversion and copy of webcam frame onto the Pygame screen."""
        h, w = webcam_bgr.shape[:2]
        if w != self.width or h != self.height:
            webcam_bgr = cv2.resize(webcam_bgr, (self.width, self.height), interpolation=cv2.INTER_LINEAR)
        
        rgb_frame = cv2.cvtColor(webcam_bgr, cv2.COLOR_BGR2RGB)
        cam_surf = pygame.image.frombuffer(rgb_frame.tobytes(), (self.width, self.height), "RGB")
        screen.blit(cam_surf, (0, 0))

    def draw_call_ui(self, screen: pygame.Surface, gesture: HandGesture) -> None:
        """Draws top call header, bottom controls, and real-time 3-gesture status pill."""
        # 1. Header Bar
        header_surf = pygame.Surface((self.width, 52), pygame.SRCALPHA)
        header_surf.fill((12, 16, 24, 200))
        screen.blit(header_surf, (0, 0))

        # Title & Live indicator
        pygame.draw.circle(screen, (245, 55, 55), (28, 26), 6)
        txt_title = self.font_title.render("GestureDino AI Video Conference", True, (245, 245, 250))
        screen.blit(txt_title, (46, 15))

        # 2. Status Pill (Feedback for HOVER / JUMP / SLIDE)
        gesture_text = "HAND: NOT DETECTED"
        gesture_bg = (50, 55, 70, 220)
        gesture_fg = (200, 210, 230)
        
        if gesture == HandGesture.HOVER:
            gesture_text = "GESTURE: ✌️ V-SIGN [HOVER / RUN]"
            gesture_bg = (30, 140, 210, 230)  # Bright blue
            gesture_fg = (255, 255, 255)
        elif gesture == HandGesture.OPEN_PALM:
            gesture_text = "GESTURE: ✋ OPEN PALM [JUMP ⬆]"
            gesture_bg = (35, 185, 85, 235)   # Vivid green
            gesture_fg = (255, 255, 255)
        elif gesture == HandGesture.CLOSED_FIST:
            gesture_text = "GESTURE: ✊ CLOSED FIST [SLIDE ⬇]"
            gesture_bg = (235, 115, 25, 235)  # Orange
            gesture_fg = (255, 255, 255)

        pill_surf = pygame.Surface((340, 36), pygame.SRCALPHA)
        pill_surf.fill(gesture_bg)
        pill_rect = pill_surf.get_rect(topright=(self.width - 20, 8))
        screen.blit(pill_surf, pill_rect)
        pygame.draw.rect(screen, (0, 220, 180), pill_rect, width=1, border_radius=6)
        txt_g = self.font_sub.render(gesture_text, True, gesture_fg)
        screen.blit(txt_g, (pill_rect.x + 16, pill_rect.y + 7))

        # 3. Bottom Call Control Bar
        bar_surf = pygame.Surface((self.width, 68), pygame.SRCALPHA)
        bar_surf.fill((14, 18, 26, 210))
        screen.blit(bar_surf, (0, self.height - 68))

        # End Call / Leave Button
        btn_action_color = (235, 65, 75) if self.game_active else (75, 85, 105)
        btn_label = "End Game" if self.game_active else "Exit"
        pygame.draw.rect(screen, btn_action_color, self.end_call_rect, border_radius=22)
        txt_leave = self.font_sub.render(btn_label, True, (255, 255, 255))
        screen.blit(txt_leave, txt_leave.get_rect(center=self.end_call_rect.center))

        # Controls Hint
        instr_txt = self.font_sub.render("Gestures: [✌️ V-Sign = Hover/Run]  |  [✋ Open Palm = Jump]  |  [✊ Fist = Slide]", True, (170, 195, 225))
        screen.blit(instr_txt, (30, self.height - 43))

        # 4. If game is NOT active, show large "Play Game" button in center of camera
        if not self.game_active:
            btn_surf = pygame.Surface((self.play_button_rect.width, self.play_button_rect.height), pygame.SRCALPHA)
            btn_surf.fill((18, 24, 36, 225))
            screen.blit(btn_surf, self.play_button_rect)
            pygame.draw.rect(screen, (0, 220, 180), self.play_button_rect, width=2, border_radius=16)

            btn_txt = self.font_large.render("▶ PLAY GAME", True, (0, 220, 180))
            screen.blit(btn_txt, btn_txt.get_rect(center=self.play_button_rect.center))

            hint_txt = self.font_sub.render("Click to start game over your camera feed!", True, (240, 240, 245))
            screen.blit(hint_txt, hint_txt.get_rect(center=(self.width // 2, self.height // 2 + 75)))
