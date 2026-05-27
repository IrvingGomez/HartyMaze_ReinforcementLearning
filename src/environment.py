"""Grid-world environment for the Mouse Maze.

The maze is a 2D numpy array of wall-codes 0-14, the same encoding used in
the project's CLAUDE.md and in maze_renderer.py. Students can pass any maze
of any rectangular shape; nothing here is hard-coded to 10x10.
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


def next_state(position, action, maze):
    """Return the cell reached by taking `action` from `position`.

    The action is blocked (agent stays put) if the current cell's wall code
    forbids it, or if the move would leave the grid.
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


def reward(next_position, treasure):
    """Return 1 when stepping onto the treasure cell, 0 otherwise."""
    return 1 if next_position == treasure else 0


def step(position, action, treasure, maze):
    """Take one environment step. Returns (next_position, reward)."""
    new_position = next_state(position, action, maze)
    return new_position, reward(new_position, treasure)
