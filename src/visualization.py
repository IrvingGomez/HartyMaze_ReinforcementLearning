"""Plot the maze, value function, policy arrows, and characters.

Coordinate convention matches maze_renderer: cell (row, col) occupies the
square [col, col+1] x [row, row+1] with the y-axis inverted so row 0 is on
top. All draw helpers use the same axes, so layers compose cleanly.
"""

from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.image as mpimg

from environment import ACTION_SYMBOLS, is_terminal
from maze_renderer import draw_maze


IMAGES_DIR = Path(__file__).resolve().parent.parent / 'images'

TREASURE_IMAGE_PATH = IMAGES_DIR / 'Treasure.png'
HARTY_IMAGE_PATHS = {
    'idle':  IMAGES_DIR / 'Harty_iddle.png',
    'up':    IMAGES_DIR / 'Harty_up.png',
    'down':  IMAGES_DIR / 'Harty_down.png',
    'left':  IMAGES_DIR / 'Harty_left.png',
    'right': IMAGES_DIR / 'Harty_right.png',
}
HOLE_IMAGE_PATH = IMAGES_DIR / 'Dead.png'
PORTAL_IMAGE_PATHS = [
    IMAGES_DIR / 'Portal1.png',
    IMAGES_DIR / 'Portal2.png',
]


def make_value_colormap():
    """Build a diverging cmap: red at the bottom, white in the middle, purple at the top.

    The cmap itself spans [0, 1] (matplotlib's required input range). To make
    V = -1 render as red and V = +1 as purple, the caller sets vmin=-1, vmax=+1
    when drawing the heatmap.
    """
    low = plt.cm.RdBu(np.linspace(0.0, 0.5, 128))      # red -> white
    high = plt.cm.PuOr(np.linspace(0.5, 1.0, 128))     # white -> purple
    return mcolors.LinearSegmentedColormap.from_list(
        'value_cmap', np.vstack((low, high))
    )


def plot_value_heatmap(ax, value, cmap=None, vmin=-1.0, vmax=1.0):
    """Color the grid cells by value."""
    if cmap is None:
        cmap = make_value_colormap()
    rows, cols = value.shape
    ax.imshow(
        value,
        cmap=cmap,
        vmin=vmin,
        vmax=vmax,
        extent=[0, cols, rows, 0],
        aspect='equal',
        zorder=0,
    )


def overlay_policy_arrows(ax, policy, treasure=None, holes=(),
                          fontsize=18, color='black'):
    """Write the action arrow at the center of each cell, skipping terminals."""
    rows, cols = policy.shape
    for r in range(rows):
        for c in range(cols):
            if treasure is not None and is_terminal((r, c), treasure, holes):
                continue
            symbol = ACTION_SYMBOLS.get(policy[r, c], '')
            if symbol:
                ax.text(
                    c + 0.5, r + 0.5,
                    symbol,
                    ha='center', va='center',
                    fontsize=fontsize, color=color,
                    zorder=3,
                )


def overlay_image_at_cell(ax, image, cell, padding=0.05):
    """Place a PNG inside one grid cell, preserving its aspect ratio.

    The image is scaled so its longer side equals one grid cell (minus
    padding), and centered inside the cell. Portrait images (Harty) end up
    narrower than the cell; near-square images (treasure) almost fill it.
    """
    r, c = cell
    img_h, img_w = image.shape[0], image.shape[1]
    cell_size = 1 - 2 * padding

    if img_h >= img_w:
        height = cell_size
        width = cell_size * img_w / img_h
    else:
        width = cell_size
        height = cell_size * img_h / img_w

    center_x = c + 0.5
    center_y = r + 0.5
    left = center_x - width / 2
    right = center_x + width / 2
    top = center_y - height / 2
    bottom = center_y + height / 2

    ax.imshow(image, extent=[left, right, bottom, top], zorder=4)


def load_treasure_image():
    return mpimg.imread(TREASURE_IMAGE_PATH)


def load_harty_image(facing='idle'):
    path = HARTY_IMAGE_PATHS.get(facing, HARTY_IMAGE_PATHS['idle'])
    return mpimg.imread(path)


def load_hole_image():
    return mpimg.imread(HOLE_IMAGE_PATH)


def load_portal_image(pair_index):
    return mpimg.imread(PORTAL_IMAGE_PATHS[pair_index])


def overlay_holes(ax, holes):
    """Stamp Dead.png on every hole cell."""
    if not holes:
        return
    img = load_hole_image()
    for cell in holes:
        overlay_image_at_cell(ax, img, cell)


def overlay_portals(ax, portals):
    """Stamp Portal1.png on both cells of the first pair, Portal2.png on the second."""
    for pair_idx, (a, b) in enumerate(portals):
        img = load_portal_image(pair_idx)
        overlay_image_at_cell(ax, img, a)
        overlay_image_at_cell(ax, img, b)


def plot_policy_and_value(
    policy,
    value,
    treasure,
    harty,
    maze,
    *,
    holes=(),
    portals=(),
    harty_facing='idle',
    cmap=None,
    vmin=-1.0,
    vmax=1.0,
    figsize=(7, 7),
    title=None,
):
    """Compose the full picture: colors, walls, arrows, hazards, treasure, Harty."""
    fig, ax = plt.subplots(figsize=figsize)

    plot_value_heatmap(ax, value, cmap=cmap, vmin=vmin, vmax=vmax)
    draw_maze(ax, maze)
    overlay_policy_arrows(ax, policy, treasure=treasure, holes=holes)
    overlay_holes(ax, holes)
    overlay_portals(ax, portals)
    overlay_image_at_cell(ax, load_treasure_image(), treasure)
    overlay_image_at_cell(ax, load_harty_image(facing=harty_facing), harty)

    if title:
        ax.set_title(title)

    return fig, ax


def plot_value_only(
    value,
    treasure,
    harty,
    maze,
    *,
    holes=(),
    portals=(),
    harty_facing='idle',
    cmap=None,
    vmin=-1.0,
    vmax=1.0,
    figsize=(7, 7),
    title=None,
):
    """Same as plot_policy_and_value but without arrows. Useful for the
    'before learning' baseline picture under the uniform random policy.
    """
    fig, ax = plt.subplots(figsize=figsize)

    plot_value_heatmap(ax, value, cmap=cmap, vmin=vmin, vmax=vmax)
    draw_maze(ax, maze)
    overlay_holes(ax, holes)
    overlay_portals(ax, portals)
    overlay_image_at_cell(ax, load_treasure_image(), treasure)
    overlay_image_at_cell(ax, load_harty_image(facing=harty_facing), harty)

    if title:
        ax.set_title(title)

    return fig, ax
