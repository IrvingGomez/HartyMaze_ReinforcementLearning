"""Sanity tests for policy_iteration.py."""

import numpy as np

from environment import ACTIONS, DEFAULT_MAZE
from policy_iteration import (
    greedy_policy,
    policy_evaluation,
    policy_iteration,
    uniform_random_policy_value,
    value_from_q,
)


TREASURE = (0, 4)
GAMMA = 0.97


def test_uniform_random_value_is_zero_at_treasure_and_nonneg_elsewhere():
    v = uniform_random_policy_value(TREASURE, GAMMA, DEFAULT_MAZE)
    assert v[TREASURE] == 0.0
    assert np.all(v >= 0.0)
    # Reachable cells should accumulate some non-zero probability mass.
    assert v.sum() > 0


def test_policy_iteration_returns_v_close_to_gamma_near_treasure():
    policy, v, _ = policy_iteration(TREASURE, GAMMA, DEFAULT_MAZE, seed=0)
    # (0,5) has code 2 (top + right walls). 'left' lands on treasure (0,4).
    # Optimal Q for that cell is gamma * reward = 0.97 * 1 = 0.97.
    assert v[0, 5] == 1  # stepping onto treasure cell yields immediate reward 1
    # Actually with our Bellman convention (terminal reward not discounted into V of neighbor),
    # V[(0,5)] under optimal policy = 1 (the immediate reward from 'left').
    assert policy[0, 5] == 'left'


def test_policy_iteration_treasure_cell_marked_blank():
    policy, _, _ = policy_iteration(TREASURE, GAMMA, DEFAULT_MAZE, seed=0)
    assert policy[TREASURE] == ''


def test_policy_iteration_converges_in_few_cycles_for_default_maze():
    _, _, cycles = policy_iteration(TREASURE, GAMMA, DEFAULT_MAZE, seed=0)
    assert cycles < 50, f'policy iteration should converge well under safety cap, took {cycles}'


def test_policy_iteration_values_decrease_with_distance_from_treasure():
    # V should be highest near the treasure under the optimal policy.
    _, v, _ = policy_iteration(TREASURE, GAMMA, DEFAULT_MAZE, seed=0)
    # Direct neighbor (0,5) lands on treasure in one step -> V = 1
    # Two steps away cells should have V <= gamma
    assert v[0, 5] >= v[5, 5]


def test_greedy_policy_picks_action_that_lands_on_treasure_when_available():
    # Build a Q-table by hand: cell (0,5) should clearly prefer 'left'.
    q = np.zeros((10, 10, len(ACTIONS)))
    q[0, 5, ACTIONS.index('left')] = 1.0
    policy = greedy_policy(q, TREASURE, DEFAULT_MAZE, rng=np.random.default_rng(0))
    assert policy[0, 5] == 'left'
    assert policy[TREASURE] == ''


def test_value_from_q_matches_q_under_chosen_action():
    q = np.zeros((10, 10, len(ACTIONS)))
    q[3, 3, ACTIONS.index('up')] = 0.5
    policy = np.empty((10, 10), dtype=object)
    policy.fill('up')
    policy[TREASURE] = ''
    v = value_from_q(q, policy, TREASURE, DEFAULT_MAZE)
    assert v[3, 3] == 0.5
    assert v[TREASURE] == 0.0


def test_policy_evaluation_converges():
    policy = np.empty((10, 10), dtype=object)
    policy.fill('up')
    policy[TREASURE] = ''
    q1 = policy_evaluation(policy, TREASURE, GAMMA, DEFAULT_MAZE, n_sweeps=200)
    q2 = policy_evaluation(policy, TREASURE, GAMMA, DEFAULT_MAZE, n_sweeps=400)
    # If converged, more sweeps shouldn't change Q materially.
    assert np.max(np.abs(q1 - q2)) < 1e-4


def test_policy_iteration_marks_holes_as_terminal():
    holes = [(5, 5)]
    policy, v, _ = policy_iteration(
        TREASURE, GAMMA, DEFAULT_MAZE, seed=0, holes=holes,
    )
    assert policy[holes[0]] == ''
    assert v[holes[0]] == 0.0


def test_policy_iteration_neighbor_of_hole_avoids_it():
    # Place a hole at (0,5). Its neighbor under no-holes would prefer 'left'
    # (lands on treasure). With the hole at (0,5) itself, (0,5) is terminal
    # so we examine a different neighbor: (1,5) has code 6 (left + bottom),
    # so it can only move up or right. Stepping onto (0,5) hole gives -1;
    # the optimal policy should prefer right (to (1,6)) over up (into hole).
    holes = [(0, 5)]
    policy, _, _ = policy_iteration(
        TREASURE, GAMMA, DEFAULT_MAZE, seed=0, holes=holes,
    )
    assert policy[(1, 5)] != 'up', 'optimal policy should not walk into the hole'


def test_policy_iteration_with_portal_shortcut_yields_higher_value():
    # Without portal: V at (9,9) is small (long way to treasure).
    # With portal pairing (9,9) <-> (0,5): stepping any direction from (9,9)
    # away from a wall takes Harty to a portal endpoint? No -- portals
    # trigger on entry. So we use a portal at (9,8) <-> (0,5). Walking from
    # (9,9) 'left' lands on (9,8) -> teleport to (0,5), then 'left' to
    # treasure -> V at (9,9) should jump.
    portals = [((9, 8), (0, 5))]
    _, v_with, _ = policy_iteration(
        TREASURE, GAMMA, DEFAULT_MAZE, seed=0, portals=portals,
    )
    _, v_without, _ = policy_iteration(
        TREASURE, GAMMA, DEFAULT_MAZE, seed=0,
    )
    assert v_with[9, 9] > v_without[9, 9]
