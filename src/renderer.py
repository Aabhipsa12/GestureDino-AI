"""
Visual Rendering Engine for GestureDino AI.
Renders directly over the camera feed (Transparent backdrop).
Only draws:
  - Sleek modern ground track with glowing neon edge
  - Procedural animated Cyber-Dino (Standing/Running, Jumping, Ducking)
  - Obstacles (Ground spikes requiring jump, Flying drones requiring duck)
  - Clean floating HUD (Score, High Score) and State Overlays
No opaque wallpaper or backdrop is drawn, keeping you fully visible in the call!
"""

import math
from typing import Tuple, List
import pygame

from src.config import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    GROUND_Y,
    COLOR_GROUND,
    COLOR_GROUND_LINE,
    COLOR_PLAYER,
    COLOR_PLAYER_EYE,
    COLOR_OBSTACLE_GROUND,
    COLOR_OBSTACLE_AIR,
    COLOR_TEXT,
    COLOR_TEXT_MUTED,
    COLOR_ACCENT,
)
from src.player import Player, PlayerState
from src.obstacles import Obstacle, ObstacleType
from src.game_state import GameEngine, GameState


class GameRenderer:
    def __init__(self, width: int = SCREEN_WIDTH, height: int = SCREEN_HEIGHT) -> None:
        self.width = width
        self.height = height
        
        # Ground scroll animation offset
        self.ground_scroll: float = 0.0

        if not pygame.font.get_init():
            pygame.font.init()
            
        font_name = pygame.font.match_font("consolas") or pygame.font.match_font("segoeui") or "arial"
        self.font_large = pygame.font.Font(font_name, 38)
        self.font_med = pygame.font.Font(font_name, 22)
        self.font_small = pygame.font.Font(font_name, 16)

    def render_overlay(self, surface: pygame.Surface, engine: GameEngine, dt: float) -> None:
        """
        Draws the game elements directly on top of the target surface (e.g. the live camera frame).
        """
        # 1. Update ground scroll while playing
        if engine.state == GameState.PLAYING:
            self.ground_scroll = (self.ground_scroll + engine.obstacle_manager.speed * dt) % 50.0

        # 2. Draw ground track & scrolling markings
        self._draw_ground(surface)

        # 3. Draw obstacles
        for obs in engine.obstacle_manager.obstacles:
            self._draw_obstacle(surface, obs)

        # 4. Draw Player Dino
        self._draw_player(surface, engine.player)

        # 5. Draw HUD (Current Score & High Score)
        self._draw_hud(surface, engine)

        # 6. Draw State Overlays (Paused, Game Over)
        if engine.state == GameState.PAUSED:
            self._draw_pause_screen(surface)
        elif engine.state == GameState.GAME_OVER:
            self._draw_game_over_screen(surface, engine)

    def _draw_ground(self, surface: pygame.Surface) -> None:
        """Draws subtle translucent ground foundation and glowing top runner line."""
        ground_h = self.height - GROUND_Y
        
        # Translucent ground track so camera feed subtly shows through
        ground_rect = pygame.Rect(0, GROUND_Y, self.width, ground_h)
        ground_surf = pygame.Surface((self.width, ground_h), pygame.SRCALPHA)
        ground_surf.fill((16, 20, 30, 210))  # Semi-transparent dark slate
        surface.blit(ground_surf, (0, GROUND_Y))

        # Vibrant neon runner line
        pygame.draw.line(surface, COLOR_GROUND_LINE, (0, GROUND_Y), (self.width, GROUND_Y), width=3)

        # Scrolling neon track dash markers
        dash_spacing = 50
        for x in range(-dash_spacing, self.width + dash_spacing, dash_spacing):
            draw_x = x - int(self.ground_scroll)
            pygame.draw.line(surface, (0, 180, 140), (draw_x, GROUND_Y + 12), (draw_x + 22, GROUND_Y + 12), width=3)

    def _draw_player(self, surface: pygame.Surface, player: Player) -> None:
        """Draws vibrant animated Dino character with clear running, jumping, and ducking postures."""
        px = int(player.x)
        py = int(player.y)
        pw = int(player.width)
        ph = int(player.height)

        if player.state == PlayerState.DUCKING:
            # Low aerodynamic crouch body
            body_rect = pygame.Rect(px, py + 8, pw, ph - 8)
            pygame.draw.rect(surface, COLOR_PLAYER, body_rect, border_radius=8)
            
            # Head reaching forward
            head_rect = pygame.Rect(px + pw - 16, py + 4, 22, 18)
            pygame.draw.rect(surface, COLOR_PLAYER, head_rect, border_radius=5)
            
            # Glowing Visor / Eye
            pygame.draw.rect(surface, COLOR_ACCENT, pygame.Rect(px + pw + 2, py + 8, 5, 8))

            # Crouched tail
            tail_pts = [(px, py + 14), (px - 14, py + 22), (px, py + ph - 2)]
            pygame.draw.polygon(surface, COLOR_PLAYER, tail_pts)

        else:
            # Standing or Jumping posture
            # Torso
            torso_rect = pygame.Rect(px + 4, py + 16, pw - 8, ph - 28)
            pygame.draw.rect(surface, COLOR_PLAYER, torso_rect, border_radius=6)

            # Head & snout
            head_rect = pygame.Rect(px + 16, py, 30, 24)
            pygame.draw.rect(surface, COLOR_PLAYER, head_rect, border_radius=5)

            # Glowing cyber visor
            pygame.draw.rect(surface, COLOR_ACCENT, pygame.Rect(px + 36, py + 5, 8, 9))

            # Tail
            tail_pts = [(px + 6, py + 26), (px - 14, py + 32), (px + 6, py + 44)]
            pygame.draw.polygon(surface, COLOR_PLAYER, tail_pts)

            # Small mechanical arms
            pygame.draw.rect(surface, (40, 210, 100), pygame.Rect(px + 30, py + 28, 10, 5))

            # Running legs animation
            if player.state == PlayerState.JUMPING:
                # Tucked legs in flight
                pygame.draw.line(surface, COLOR_PLAYER, (px + 12, py + ph - 14), (px + 6, py + ph - 4), width=4)
                pygame.draw.line(surface, COLOR_PLAYER, (px + 28, py + ph - 14), (px + 22, py + ph - 4), width=4)
            else:
                # Alternating leg swing
                phase = player.anim_time * player.run_cycle_speed
                leg1_offset = math.sin(phase) * 12
                leg2_offset = math.sin(phase + math.pi) * 12

                # Back leg
                pygame.draw.line(surface, (35, 180, 80), (px + 14, py + ph - 14), (px + 14 + leg2_offset, py + ph), width=5)
                # Front leg
                pygame.draw.line(surface, COLOR_PLAYER, (px + 28, py + ph - 14), (px + 28 + leg1_offset, py + ph), width=5)

    def _draw_obstacle(self, surface: pygame.Surface, obs: Obstacle) -> None:
        """Render ground spikes (jump) or aerial surveillance drones (duck)."""
        ox = int(obs.x)
        oy = int(obs.y)
        ow = int(obs.width)
        oh = int(obs.height)

        if obs.obstacle_type == ObstacleType.GROUND:
            # Neon crystal hazard / barrier
            pts = [
                (ox + ow // 2, oy),
                (ox + ow, oy + oh),
                (ox, oy + oh),
            ]
            pygame.draw.polygon(surface, COLOR_OBSTACLE_GROUND, pts)
            # Glowing core spine
            pygame.draw.line(surface, COLOR_ACCENT, (ox + ow // 2, oy + 6), (ox + ow // 2, oy + oh), width=3)

        else:
            # Aerial drone / hovering hazard
            body_rect = pygame.Rect(ox + 8, oy + 6, ow - 16, oh - 10)
            pygame.draw.rect(surface, COLOR_OBSTACLE_AIR, body_rect, border_radius=5)

            # Flapping wings
            wing_pulse = math.sin(obs.anim_time * 18.0) * 5
            left_wing = [(ox + 8, oy + 10), (ox - 2, oy + 4 + int(wing_pulse)), (ox + 8, oy + 20)]
            right_wing = [(ox + ow - 8, oy + 10), (ox + ow + 2, oy + 4 - int(wing_pulse)), (ox + ow - 8, oy + 20)]
            pygame.draw.polygon(surface, (220, 40, 180), left_wing)
            pygame.draw.polygon(surface, (220, 40, 180), right_wing)

            # Red sensor beacon
            pygame.draw.circle(surface, (255, 30, 30), (ox + ow // 2, oy + oh // 2), 4)

    def _draw_hud(self, surface: pygame.Surface, engine: GameEngine) -> None:
        """Render clean floating scoreboard at the upper-right corner of the call."""
        score_val = int(engine.score)
        score_str = f"SCORE {score_val:05d}"
        hi_str = f"HI {engine.high_score:05d}"

        # Pill background for HUD
        hud_box = pygame.Surface((310, 42), pygame.SRCALPHA)
        hud_box.fill((15, 20, 32, 190))
        surface.blit(hud_box, (self.width - 330, 70))
        pygame.draw.rect(surface, (0, 220, 180), pygame.Rect(self.width - 330, 70, 310, 42), width=1, border_radius=6)

        hi_surf = self.font_med.render(hi_str, True, COLOR_TEXT_MUTED)
        score_surf = self.font_med.render(score_str, True, COLOR_TEXT)

        surface.blit(hi_surf, (self.width - 315, 80))
        surface.blit(score_surf, (self.width - 165, 80))

    def _draw_pause_screen(self, surface: pygame.Surface) -> None:
        """Subtle pause banner."""
        banner = pygame.Surface((360, 90), pygame.SRCALPHA)
        banner.fill((15, 20, 30, 220))
        b_rect = banner.get_rect(center=(self.width // 2, 280))
        surface.blit(banner, b_rect)
        pygame.draw.rect(surface, COLOR_ACCENT, b_rect, width=2, border_radius=10)

        p_txt = self.font_large.render("PAUSED", True, COLOR_ACCENT)
        r_txt = self.font_med.render("Press P to Resume", True, COLOR_TEXT)
        surface.blit(p_txt, p_txt.get_rect(center=(self.width // 2, 260)))
        surface.blit(r_txt, r_txt.get_rect(center=(self.width // 2, 305)))

    def _draw_game_over_screen(self, surface: pygame.Surface, engine: GameEngine) -> None:
        """Clean game-over notification card."""
        banner = pygame.Surface((440, 130), pygame.SRCALPHA)
        banner.fill((25, 12, 18, 230))
        b_rect = banner.get_rect(center=(self.width // 2, 280))
        surface.blit(banner, b_rect)
        pygame.draw.rect(surface, (255, 70, 70), b_rect, width=2, border_radius=12)

        go_txt = self.font_large.render("GAME OVER", True, (255, 80, 80))
        sc_txt = self.font_med.render(f"Score: {int(engine.score)}", True, COLOR_TEXT)
        re_txt = self.font_med.render("Press R or Open Palm to Retry", True, COLOR_ACCENT)

        surface.blit(go_txt, go_txt.get_rect(center=(self.width // 2, 245)))
        surface.blit(sc_txt, sc_txt.get_rect(center=(self.width // 2, 285)))
        surface.blit(re_txt, re_txt.get_rect(center=(self.width // 2, 325)))
