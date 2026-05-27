"""Sanity tests for environment.py."""

from environment import DEFAULT_MAZE, next_state, step


def test_top_left_walls_block_up_and_left():
    # Cell (0,0) has code 0 -> top + left walls
    assert next_state((0, 0), 'up', DEFAULT_MAZE) == (0, 0)
    assert next_state((0, 0), 'left', DEFAULT_MAZE) == (0, 0)


def test_top_left_corner_can_move_down_and_right():
    assert next_state((0, 0), 'down', DEFAULT_MAZE) == (1, 0)
    assert next_state((0, 0), 'right', DEFAULT_MAZE) == (0, 1)


def test_grid_edges_clamp_when_no_wall_code_blocks():
    # Bottom-right corner stays put regardless of the wall code.
    assert next_state((9, 9), 'right', DEFAULT_MAZE) == (9, 9)
    assert next_state((9, 9), 'down', DEFAULT_MAZE) == (9, 9)


def test_step_onto_treasure_gives_reward_one():
    # (0,5) has code 2; left is open and lands on treasure (0,4).
    treasure = (0, 4)
    pos, r = step((0, 5), 'left', treasure, DEFAULT_MAZE)
    assert pos == (0, 4)
    assert r == 1


def test_step_off_treasure_gives_zero_reward():
    treasure = (0, 4)
    _, r = step((5, 5), 'down', treasure, DEFAULT_MAZE)
    assert r == 0


def test_code_9_only_allows_up():
    # (1,8) has code 9 -> left + bottom + right walls.
    pos = (1, 8)
    assert int(DEFAULT_MAZE[pos]) == 9
    assert next_state(pos, 'left', DEFAULT_MAZE) == pos
    assert next_state(pos, 'right', DEFAULT_MAZE) == pos
    assert next_state(pos, 'down', DEFAULT_MAZE) == pos
    assert next_state(pos, 'up', DEFAULT_MAZE) == (0, 8)
