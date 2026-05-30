"""Grid-world environment for the Mouse Maze.

The maze is a 2D numpy array of wall-codes 0-14, the same encoding used in
the project's CLAUDE.md and in maze_renderer.py. Students can pass any maze
of any rectangular shape; nothing here is hard-coded to 10x10.

Two optional hazards extend the basic maze:
    holes   -- iterable of (row, col). Stepping onto a hole ends the episode
               with reward -1.
    portals -- list of pairs ((cellA, cellB), ...). Stepping onto either
               endpoint teleports the agent to its partner. The teleport
               happens once per step, so a portal whose partner is another
               portal does not chain.
"""

import numpy as np

from maze_renderer import WALL_CODES


ACTIONS = ['up', 'down', 'left', 'right']

ACTION_SYMBOLS = {
    'up': '↑',
    'down': '↓',
    'left': '←',
    'right': '→',
    '': '',
}

MOVES = {
    'up':    (-1, 0),
    'down':  (1, 0),
    'left':  (0, -1),
    'right': (0, 1),
}

WALL_TO_ACTION = {
    'top': 'up',
    'bottom': 'down',
    'left': 'left',
    'right': 'right',
}

BLOCKED_ACTIONS_BY_CODE = {
    code: {WALL_TO_ACTION[wall] for wall in walls}
    for code, walls in WALL_CODES.items()
}


DEFAULT_MAZE = np.array([
    [0, 13, 2, 12, 11, 2, 11, 2, 0, 2],
    [14, 11, 8, 6, 2, 6, 13, 5, 9, 14],
    [6, 13, 1, 1, 5, 0, 13, 8, 0, 8],
    [12, 0, 8, 14, 9, 6, 13, 13, 5, 12],
    [6, 8, 0, 7, 2, 11, 13, 2, 6, 5],
    [0, 2, 6, 2, 6, 2, 0, 8, 12, 14],
    [14, 6, 13, 8, 12, 6, 8, 0, 7, 8],
    [6, 2, 0, 13, 8, 11, 2, 6, 13, 2],
    [0, 8, 3, 10, 0, 2, 3, 1, 10, 14],
    [6, 13, 7, 13, 8, 6, 8, 6, 13, 8],
])

BIG_MAZE = np.array([
    [11,13,13,2,0,13,13,13,1,13,13,13,1,1,10,11,13,2],
    [0,13,2,14,14,11,13,2,14,0,13,2,14,3,13,2,11,5],
    [6,2,6,8,3,13,10,14,14,6,2,6,8,6,10,3,2,14],
    [12,3,13,13,7,13,2,14,6,10,6,13,13,13,2,14,14,14],
    [14,3,13,13,13,2,14,6,2,12,0,13,13,2,14,9,14,14],
    [14,9,0,13,13,8,9,0,8,14,9,0,1,8,9,0,8,14],
    [3,13,8,12,0,13,13,7,2,3,13,8,14,0,13,7,2,14],
    [9,0,13,5,6,13,13,2,14,14,0,13,8,6,13,2,14,14],
    [0,7,2,14,0,13,13,8,6,8,6,2,12,0,13,8,9,14],
    [14,0,8,6,7,2,0,13,13,13,1,8,6,5,0,13,13,8],
    [14,14,0,13,13,5,14,0,13,2,14,0,10,14,14,0,13,2],
    [9,14,14,11,13,8,6,8,0,8,14,14,11,8,6,8,0,8],
    [0,8,14,0,13,13,13,13,8,0,8,14,0,13,13,13,8,12],
    [14,0,8,14,0,13,13,13,2,14,0,8,14,0,13,13,2,14],
    [14,6,2,9,6,1,1,2,9,14,6,2,9,6,2,12,9,14],
    [14,0,7,13,2,14,14,6,13,5,0,7,13,2,14,6,13,5],
    [14,14,0,13,8,14,3,13,2,14,14,0,13,8,3,13,2,14],
    [6,8,6,13,2,14,14,0,8,6,8,6,13,2,14,0,8,14],
    [11,13,13,13,7,7,8,6,13,13,13,13,13,7,8,6,13,8],
])

def apply_portal(position, portals):
    """If `position` matches one endpoint of any portal pair, return its partner.

    `portals` is an iterable of ((rA, cA), (rB, cB)) pairs. Lookup is by exact
    tuple equality, so the caller is expected to pass tuples (not numpy ints).
    """
    for a, b in portals:
        if position == a:
            return b
        if position == b:
            return a
    return position


def next_state(position, action, maze):
    """Return the cell reached by taking `action` from `position`.

    The action is blocked (agent stays put) if the current cell's wall code
    forbids it, or if the move would leave the grid. Portals and hazards are
    NOT applied here; see `step` for the full transition.
    """
    code = int(maze[position])
    if action in BLOCKED_ACTIONS_BY_CODE[code]:
        return position

    dr, dc = MOVES[action]
    next_row = position[0] + dr
    next_col = position[1] + dc

    rows, cols = maze.shape
    if not (0 <= next_row < rows and 0 <= next_col < cols):
        return position

    return (next_row, next_col)


def reward(next_position, treasure, holes=()):
    """+1 on the treasure, -1 on a hole, 0 elsewhere."""
    if next_position == treasure:
        return 1
    if next_position in tuple(holes):
        return -1
    return 0


def is_terminal(cell, treasure, holes=()):
    return cell == treasure or cell in tuple(holes)


def step(position, action, treasure, maze, holes=(), portals=()):
    """Take one environment step. Returns (next_position, reward, done).

    Order of operations:
        1. Move per the action (walls + grid bounds).
        2. Teleport once if the new cell is a portal endpoint.
        3. Compute reward and done from the final cell.
    """
    new_position = next_state(position, action, maze)
    new_position = apply_portal(new_position, portals)
    r = reward(new_position, treasure, holes)
    done = is_terminal(new_position, treasure, holes)
    return new_position, r, done
