"""
Automated unit tests for Player physics, state transitions, and hitbox mechanics.
Headless tests executed via pytest.
"""

import pytest
from src.config import (
    GROUND_Y,
    PLAYER_X,
    PLAYER_WIDTH,
    PLAYER_HEIGHT_STAND,
    PLAYER_HEIGHT_DUCK,
    JUMP_VELOCITY,
)
from src.player import Player, PlayerState


def test_player_initial_state() -> None:
    """Verify player starts on the ground in the running state."""
    player = Player()
    assert player.state == PlayerState.RUNNING
    assert player.is_on_ground is True
    assert player.x == PLAYER_X
    assert player.height == PLAYER_HEIGHT_STAND
    assert player.y == GROUND_Y - PLAYER_HEIGHT_STAND
    assert player.vy == 0.0


def test_player_jump_impulse() -> None:
    """Verify jump triggers initial upward velocity and state change."""
    player = Player()
    success = player.jump()
    assert success is True
    assert player.state == PlayerState.JUMPING
    assert player.vy == JUMP_VELOCITY


def test_prevent_double_jump() -> None:
    """Verify jumping while already airborne is rejected."""
    player = Player()
    player.jump()
    # Attempt second jump immediately
    second_jump = player.jump()
    assert second_jump is False
    assert player.state == PlayerState.JUMPING


def test_jump_arc_and_ground_return() -> None:
    """Simulate complete jump trajectory to verify ascent, descent, and landing."""
    player = Player()
    player.update(dt=1 / 60, jump_pressed=True, duck_held=False)
    
    # Must be in mid-air moving upward (negative vy)
    assert player.state == PlayerState.JUMPING
    assert player.vy < 0.0
    assert player.y < (GROUND_Y - PLAYER_HEIGHT_STAND)
    
    # Step forward through the entire jump (roughly 1.0 second)
    dt = 1 / 60
    for _ in range(70):
        player.update(dt=dt, jump_pressed=False, duck_held=False)

    # After complete arc, player must land smoothly on ground
    assert player.is_on_ground is True
    assert player.state == PlayerState.RUNNING
    assert player.y == GROUND_Y - PLAYER_HEIGHT_STAND
    assert player.vy == 0.0


def test_duck_and_release() -> None:
    """Verify duck reduces height/hitbox and releasing restores standard posture."""
    player = Player()
    
    # Duck active
    player.update(dt=1 / 60, jump_pressed=False, duck_held=True)
    assert player.state == PlayerState.DUCKING
    assert player.height == PLAYER_HEIGHT_DUCK
    assert player.y == GROUND_Y - PLAYER_HEIGHT_DUCK
    
    # Release duck
    player.update(dt=1 / 60, jump_pressed=False, duck_held=False)
    assert player.state == PlayerState.RUNNING
    assert player.height == PLAYER_HEIGHT_STAND
    assert player.y == GROUND_Y - PLAYER_HEIGHT_STAND


def test_hitbox_dimensions() -> None:
    """Verify hitbox dynamically reflects standing vs ducking postures."""
    player = Player()
    stand_hitbox = player.get_hitbox()
    
    player.update(dt=1 / 60, jump_pressed=False, duck_held=True)
    duck_hitbox = player.get_hitbox()
    
    assert duck_hitbox.height < stand_hitbox.height
    assert duck_hitbox.bottom == stand_hitbox.bottom
