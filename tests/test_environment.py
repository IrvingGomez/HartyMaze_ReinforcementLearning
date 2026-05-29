"""Sanity tests for environment.py."""

from environment import DEFAULT_MAZE, apply_portal, next_state, step


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


def test_step_onto_treasure_gives_reward_one_and_done():
    # (0,5) has code 2; left is open and lands on treasure (0,4).
    treasure = (0, 4)
    pos, r, done = step((0, 5), 'left', treasure, DEFAULT_MAZE)
    assert pos == (0, 4)
    assert r == 1
    assert done


def test_step_off_treasure_gives_zero_reward_and_not_done():
    treasure = (0, 4)
    _, r, done = step((5, 5), 'down', treasure, DEFAULT_MAZE)
    assert r == 0
    assert not done


def test_code_9_only_allows_up():
    # (1,8) has code 9 -> left + bottom + right walls.
    pos = (1, 8)
    assert int(DEFAULT_MAZE[pos]) == 9
    assert next_state(pos, 'left', DEFAULT_MAZE) == pos
    assert next_state(pos, 'right', DEFAULT_MAZE) == pos
    assert next_state(pos, 'down', DEFAULT_MAZE) == pos
    assert next_state(pos, 'up', DEFAULT_MAZE) == (0, 8)


def test_step_into_hole_is_terminal_with_negative_reward():
    treasure = (0, 4)
    holes = [(1, 0)]
    # (0,0) code 0; 'down' lands on (1,0) which is a hole.
    pos, r, done = step((0, 0), 'down', treasure, DEFAULT_MAZE, holes=holes)
    assert pos == (1, 0)
    assert r == -1
    assert done


def test_apply_portal_teleports_to_partner_in_either_direction():
    portals = [((1, 1), (8, 8))]
    assert apply_portal((1, 1), portals) == (8, 8)
    assert apply_portal((8, 8), portals) == (1, 1)
    assert apply_portal((5, 5), portals) == (5, 5)


def test_step_through_portal_lands_on_partner():
    treasure = (0, 4)
    portals = [((1, 0), (5, 5))]
    # (0,0) -> 'down' -> (1,0) which is a portal endpoint -> teleport to (5,5).
    pos, r, done = step((0, 0), 'down', treasure, DEFAULT_MAZE, portals=portals)
    assert pos == (5, 5)
    assert r == 0
    assert not done


def test_portal_does_not_chain():
    # Two portal pairs whose endpoints would otherwise chain: stepping onto
    # the first endpoint teleports once to its partner, even though the
    # partner is also a portal endpoint.
    treasure = (0, 4)
    portals = [((1, 0), (5, 5)), ((5, 5), (9, 9))]
    pos, _, _ = step((0, 0), 'down', treasure, DEFAULT_MAZE, portals=portals)
    assert pos == (5, 5)
