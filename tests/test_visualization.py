"""Smoke tests for visualization.py -- only check that plots run without errors
and produce non-empty figures. Visual correctness is checked by eye via
tests/smoke_visualization.py.
"""

import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

from environment import DEFAULT_MAZE
from policy_iteration import policy_iteration, uniform_random_policy_value
from visualization import (
    make_value_colormap,
    plot_policy_and_value,
    plot_value_only,
)


TREASURE = (0, 4)
HARTY = (9, 9)
GAMMA = 0.97


def test_value_colormap_low_is_red_high_is_purple():
    cmap = make_value_colormap()
    low = cmap(0.0)
    high = cmap(1.0)
    # low end: red dominant (R > G, R > B)
    assert low[0] > low[1] and low[0] > low[2]
    # high end: blue/purple dominant (B > R, B > G)
    assert high[2] > high[1]


def test_plot_value_only_runs_on_random_policy_baseline():
    v = uniform_random_policy_value(TREASURE, GAMMA, DEFAULT_MAZE, n_sweeps=50)
    fig, ax = plot_value_only(v, TREASURE, HARTY, DEFAULT_MAZE)
    assert ax.has_data()
    plt.close(fig)


def test_plot_policy_and_value_runs_after_iteration():
    policy, v, _ = policy_iteration(TREASURE, GAMMA, DEFAULT_MAZE, seed=0)
    fig, ax = plot_policy_and_value(policy, v, TREASURE, HARTY, DEFAULT_MAZE)
    assert ax.has_data()
    plt.close(fig)


def test_plot_handles_custom_maze_shape():
    # A 4x5 mini maze of all-open cells (code 4).
    mini = np.full((4, 5), 4, dtype=int)
    v = np.zeros((4, 5))
    v[0, 0] = 1.0
    policy = np.full((4, 5), 'right', dtype=object)
    policy[0, 0] = ''
    fig, ax = plot_policy_and_value(policy, v, (0, 0), (3, 4), mini)
    assert ax.has_data()
    plt.close(fig)


def test_plot_renders_holes_and_portals():
    holes = [(5, 5)]
    portals = [((1, 1), (8, 8))]
    policy, v, _ = policy_iteration(
        TREASURE, GAMMA, DEFAULT_MAZE, seed=0, holes=holes, portals=portals,
    )
    fig, ax = plot_policy_and_value(
        policy, v, TREASURE, HARTY, DEFAULT_MAZE,
        holes=holes, portals=portals,
    )
    assert ax.has_data()
    plt.close(fig)
