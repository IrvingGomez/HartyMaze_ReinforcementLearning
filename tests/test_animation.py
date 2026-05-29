"""Sanity tests for animation.simulate_path and animate_path setup."""

import matplotlib

matplotlib.use('Agg')
import numpy as np

from animation import animate_path, simulate_path, uniform_random_action
from environment import DEFAULT_MAZE
from policy_iteration import policy_iteration


TREASURE = (0, 4)
HARTY = (9, 9)
GAMMA = 0.97


def test_simulate_path_first_entry_is_start_idle():
    policy, _, _ = policy_iteration(TREASURE, GAMMA, DEFAULT_MAZE, seed=0)
    path = simulate_path(policy, HARTY, TREASURE, DEFAULT_MAZE, max_steps=200)
    assert path[0] == (HARTY, 'idle')


def test_simulate_path_with_optimal_policy_reaches_treasure():
    policy, _, _ = policy_iteration(TREASURE, GAMMA, DEFAULT_MAZE, seed=0)
    path = simulate_path(policy, HARTY, TREASURE, DEFAULT_MAZE, max_steps=200)
    end_cell, _ = path[-1]
    assert end_cell == TREASURE, f'expected to reach treasure, ended at {end_cell}'


def test_simulate_path_facings_match_actions_taken():
    # Deterministic 2-step example: build a policy that always goes 'down'.
    rows, cols = DEFAULT_MAZE.shape
    policy = np.full((rows, cols), 'down', dtype=object)
    policy[TREASURE] = ''
    path = simulate_path(policy, (0, 0), TREASURE, DEFAULT_MAZE, max_steps=5)
    # path[0] is (start, 'idle'); subsequent entries should be 'down'.
    for cell, facing in path[1:]:
        assert facing == 'down'


def test_uniform_random_action_returns_one_of_four():
    rng = np.random.default_rng(0)
    for _ in range(20):
        a = uniform_random_action((0, 0), rng)
        assert a in ('up', 'down', 'left', 'right')


def test_simulate_path_uniform_random_is_seed_reproducible():
    p1 = simulate_path(
        uniform_random_action, HARTY, TREASURE, DEFAULT_MAZE,
        max_steps=30, seed=42,
    )
    p2 = simulate_path(
        uniform_random_action, HARTY, TREASURE, DEFAULT_MAZE,
        max_steps=30, seed=42,
    )
    assert p1 == p2


def test_animate_path_builds_without_errors():
    policy, v, _ = policy_iteration(TREASURE, GAMMA, DEFAULT_MAZE, seed=0)
    path = simulate_path(policy, HARTY, TREASURE, DEFAULT_MAZE, max_steps=200)
    anim = animate_path(path, TREASURE, DEFAULT_MAZE, value=v, policy=policy)
    # anim.to_jshtml is the slow part; just check the object is valid.
    assert anim is not None
    assert anim._fig is not None


def test_animate_path_builds_without_value_or_policy():
    """Plain variant: no value heatmap, no policy arrows -- just walls + Harty."""
    policy, _, _ = policy_iteration(TREASURE, GAMMA, DEFAULT_MAZE, seed=0)
    path = simulate_path(policy, HARTY, TREASURE, DEFAULT_MAZE, max_steps=200)
    anim = animate_path(path, TREASURE, DEFAULT_MAZE)
    assert anim is not None


def test_simulate_path_stops_on_hole():
    # Force a policy that walks Harty straight into a hole.
    rows, cols = DEFAULT_MAZE.shape
    policy = np.full((rows, cols), 'down', dtype=object)
    policy[TREASURE] = ''
    holes = [(1, 0)]
    path = simulate_path(
        policy, (0, 0), TREASURE, DEFAULT_MAZE, max_steps=20, holes=holes,
    )
    end_cell, _ = path[-1]
    assert end_cell == (1, 0)


def test_animate_path_builds_with_holes_and_portals():
    holes = [(5, 5)]
    portals = [((1, 1), (8, 8))]
    policy, v, _ = policy_iteration(
        TREASURE, GAMMA, DEFAULT_MAZE, seed=0, holes=holes, portals=portals,
    )
    path = simulate_path(
        policy, HARTY, TREASURE, DEFAULT_MAZE,
        max_steps=200, holes=holes, portals=portals,
    )
    anim = animate_path(
        path, TREASURE, DEFAULT_MAZE,
        holes=holes, portals=portals, value=v, policy=policy,
    )
    assert anim is not None
