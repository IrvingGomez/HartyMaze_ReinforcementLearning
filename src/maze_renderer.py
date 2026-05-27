"""Render maze walls from a code matrix. No RL logic here.

Each cell holds a code 0-14 describing which of its four walls exist.
The mapping below mirrors the convention used in the project's CLAUDE.md.
"""

import numpy as np
import matplotlib.pyplot as plt


WALL_CODES = {
    0:  {'top', 'left'},
    1:  {'top'},
    2:  {'top', 'right'},
    3:  {'left'},
    4:  set(),
    5:  {'right'},
    6:  {'left', 'bottom'},
    7:  {'bottom'},
    8:  {'right', 'bottom'},
    9:  {'left', 'right', 'bottom'},
    10: {'top', 'right', 'bottom'},
    11: {'top', 'left', 'bottom'},
    12: {'top', 'left', 'right'},
    13: {'top', 'bottom'},
    14: {'left', 'right'},
}


def cell_to_xy(cell):
    """Return (x, y) center of a grid cell for plotting.

    Uses (col, row) plot coordinates with the y-axis later inverted so
    row 0 sits at the top, matching seaborn heatmap orientation.
    """
    row, col = cell
    return col + 0.5, row + 0.5


def _wall_segment(row, col, side):
    """Return ((x0, y0), (x1, y1)) endpoints for one wall of a cell."""
    if side == 'top':
        return (col, row), (col + 1, row)
    if side == 'bottom':
        return (col, row + 1), (col + 1, row + 1)
    if side == 'left':
        return (col, row), (col, row + 1)
    if side == 'right':
        return (col + 1, row), (col + 1, row + 1)


def draw_maze(ax, maze, linewidth=2.5, color='black'):
    """Draw maze walls onto an axes from the code matrix.

    Args:
        ax: matplotlib axes to draw on.
        maze: 2D numpy array of wall codes (0-14).
        linewidth: thickness of wall lines.
        color: wall color.
    """
    rows, cols = maze.shape

    for r in range(rows):
        for c in range(cols):
            for side in WALL_CODES[int(maze[r, c])]:
                (x0, y0), (x1, y1) = _wall_segment(r, c, side)
                ax.plot([x0, x1], [y0, y1], color=color, linewidth=linewidth)

    ax.set_xlim(0, cols)
    ax.set_ylim(0, rows)
    ax.invert_yaxis()
    ax.set_aspect('equal')
    ax.set_xticks([])
    ax.set_yticks([])


if __name__ == '__main__':
    MAZE = np.array([
        [0, 13, 2, 12, 11, 2, 11, 2, 0, 2],
        [14, 11, 8, 6, 2, 6, 13, 5, 9, 14],
        [6, 13, 11, 1, 5, 0, 13, 8, 0, 8],
        [12, 0, 8, 14, 9, 6, 13, 13, 5, 12],
        [6, 8, 0, 7, 2, 11, 13, 2, 6, 5],
        [0, 2, 6, 2, 6, 2, 0, 8, 12, 14],
        [14, 6, 13, 8, 12, 6, 8, 0, 7, 8],
        [6, 2, 0, 13, 8, 11, 2, 6, 13, 2],
        [0, 8, 3, 10, 0, 2, 3, 1, 10, 14],
        [6, 13, 7, 13, 8, 6, 8, 6, 13, 8],
    ])

    fig, ax = plt.subplots(figsize=(6, 6))
    draw_maze(ax, MAZE)
    ax.set_title('Maze rendered from wall codes')
    plt.tight_layout()
    plt.savefig('maze_render_test.png', dpi=120)
    print('Saved maze_render_test.png')
