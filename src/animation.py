"""Animate Harty walking through the maze.

Three pieces:
    simulate_path   -- pure logic, returns the sequence of (cell, facing) tuples
    animate_path    -- matplotlib FuncAnimation that draws Harty moving along the path
    save_animation  -- write a FuncAnimation to disk as .gif, .mp4, or .html
"""

from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

from environment import ACTIONS, apply_portal, is_terminal, next_state
from maze_renderer import draw_maze
from visualization import (
    load_harty_image,
    load_treasure_image,
    overlay_holes,
    overlay_image_at_cell,
    overlay_policy_arrows,
    overlay_portals,
    plot_value_heatmap,
)


def uniform_random_action(position, rng):
    """A policy function that picks one of the four actions uniformly at random."""
    return rng.choice(ACTIONS)


def simulate_path(policy, start, treasure, maze, max_steps=100, seed=None,
                  holes=(), portals=()):
    """Walk through the maze following `policy`.

    `policy` may be either
        - a 2D numpy array of action strings (deterministic), e.g. the output of
          policy_iteration; or
        - a callable `policy(position, rng) -> action` (stochastic).

    Returns a list of (cell, facing) tuples. The first entry uses facing='idle'
    so the initial frame shows Harty standing still. Subsequent entries use the
    action taken as the facing, so Harty turns even when bumping a wall. The
    walk stops as soon as a terminal cell (treasure or hole) is reached.
    """
    rng = np.random.default_rng(seed)
    path = [(start, 'idle')]
    pos = start

    for _ in range(max_steps):
        if is_terminal(pos, treasure, holes):
            break

        action = policy(pos, rng) if callable(policy) else policy[pos]
        if action == '':
            break

        new_pos = next_state(pos, action, maze)
        new_pos = apply_portal(new_pos, portals)
        path.append((new_pos, action))
        pos = new_pos

    return path


def _harty_extent(cell, image, padding=0.05):
    """Compute the imshow extent that preserves the image's aspect ratio inside
    a single grid cell."""
    img_h, img_w = image.shape[0], image.shape[1]
    cell_size = 1 - 2 * padding
    if img_h >= img_w:
        height = cell_size
        width = cell_size * img_w / img_h
    else:
        width = cell_size
        height = cell_size * img_h / img_w

    cx = cell[1] + 0.5
    cy = cell[0] + 0.5
    return [cx - width / 2, cx + width / 2, cy + height / 2, cy - height / 2]


def animate_path(
    path,
    treasure,
    maze,
    *,
    holes=(),
    portals=(),
    value=None,
    policy=None,
    cmap=None,
    vmin=-1.0,
    vmax=1.0,
    interval=400,
    figsize=(7, 7),
    title=None,
):
    """Build a FuncAnimation of Harty walking along `path`.

    `value` (optional) colors the cells; if None, the background stays white.
    `policy` (optional) draws the arrows underneath.
    `holes`, `portals` (optional) draw hazard and portal overlays.
    `interval` is the milliseconds-per-frame for playback.
    Returns the FuncAnimation; convert with `anim.to_jshtml()` for inline display.
    """
    fig, ax = plt.subplots(figsize=figsize)
    if value is not None:
        plot_value_heatmap(ax, value, cmap=cmap, vmin=vmin, vmax=vmax)
    draw_maze(ax, maze)
    if policy is not None:
        overlay_policy_arrows(ax, policy, treasure=treasure, holes=holes)
    overlay_holes(ax, holes)
    overlay_portals(ax, portals)
    overlay_image_at_cell(ax, load_treasure_image(), treasure)
    if title:
        ax.set_title(title)

    initial_cell, initial_facing = path[0]
    initial_image = load_harty_image(initial_facing)
    harty = ax.imshow(
        initial_image,
        extent=_harty_extent(initial_cell, initial_image),
        zorder=4,
    )

    def update(frame_idx):
        cell, facing = path[frame_idx]
        img = load_harty_image(facing)
        harty.set_data(img)
        harty.set_extent(_harty_extent(cell, img))
        return (harty,)

    anim = FuncAnimation(
        fig,
        update,
        frames=len(path),
        interval=interval,
        blit=False,
    )
    plt.close(fig)
    return anim


def save_animation(anim, path, fps=2):
    """Save a FuncAnimation to disk.

    Supported extensions:
        .gif  -- uses Pillow, no ffmpeg required.
        .mp4  -- uses ffmpeg; requires ffmpeg on PATH.
        .html -- writes the standalone jshtml document (plays in any browser).

    Parent directories are created on demand.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    ext = path.suffix.lower()

    if ext == '.gif':
        anim.save(path, writer='pillow', fps=fps)
    elif ext in ('.mp4', '.mov'):
        anim.save(path, writer='ffmpeg', fps=fps)
    elif ext == '.html':
        html = anim.to_jshtml(fps=fps)
        path.write_text(html, encoding='utf-8')
    else:
        raise ValueError(
            f'unsupported animation format: {ext!r}. '
            'Use .gif, .mp4, or .html.'
        )

    return path
