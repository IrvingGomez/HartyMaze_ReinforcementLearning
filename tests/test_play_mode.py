"""Tests for the pure logic in play_mode (PlayState + handle_key)."""

from environment import DEFAULT_MAZE
from play_mode import PlayState, handle_key, is_won


TREASURE = (0, 4)


def fresh_state(position=(9, 9), holes=(), portals=()):
    return PlayState(
        position=position,
        facing='idle',
        treasure=TREASURE,
        maze=DEFAULT_MAZE,
        holes=tuple(holes),
        portals=tuple(portals),
    )


def test_move_right_when_open_updates_position_and_facing():
    # (9, 0) has code 6 (left + bottom) -- right is open.
    state = fresh_state((9, 0))
    next_state_ = handle_key(state, 'right')
    assert next_state_.position == (9, 1)
    assert next_state_.facing == 'right'
    assert next_state_.steps_taken == 1
    assert not next_state_.won


def test_move_into_wall_keeps_position_but_updates_facing():
    # (0, 0) has code 0 (top + left walls) -- 'left' is blocked.
    state = fresh_state((0, 0))
    next_state_ = handle_key(state, 'left')
    assert next_state_.position == (0, 0)
    assert next_state_.facing == 'left'
    assert next_state_.steps_taken == 1


def test_step_onto_treasure_sets_won():
    # (0, 5) has code 2 -- 'left' goes onto treasure (0, 4).
    state = fresh_state((0, 5))
    next_state_ = handle_key(state, 'left')
    assert next_state_.position == TREASURE
    assert next_state_.won


def test_no_op_after_won():
    state = fresh_state((0, 5))
    won_state = handle_key(state, 'left')
    assert won_state.won

    # Further key presses do not change anything.
    after = handle_key(won_state, 'right')
    assert after == won_state


def test_unknown_action_is_no_op():
    state = fresh_state()
    after = handle_key(state, 'jump')
    assert after == state


def test_is_won_reflects_position():
    state = fresh_state(TREASURE)
    assert is_won(state)
    assert not is_won(fresh_state((5, 5)))


def test_step_onto_hole_sets_dead():
    # (0,0) code 0 allows 'down' to (1,0). Mark (1,0) as a hole.
    state = fresh_state((0, 0), holes=[(1, 0)])
    after = handle_key(state, 'down')
    assert after.position == (1, 0)
    assert after.dead
    assert not after.won


def test_no_op_after_dead():
    state = fresh_state((0, 0), holes=[(1, 0)])
    dead_state = handle_key(state, 'down')
    assert dead_state.dead
    again = handle_key(dead_state, 'right')
    assert again == dead_state


def test_portal_teleports_on_entry():
    # (0,0) -> 'down' lands on (1,0). Portal pair (1,0) <-> (5,5) teleports
    # Harty to (5,5).
    portals = [((1, 0), (5, 5))]
    state = fresh_state((0, 0), portals=portals)
    after = handle_key(state, 'down')
    assert after.position == (5, 5)
    assert after.facing == 'down'
    assert not after.won
    assert not after.dead
