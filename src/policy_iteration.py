"""Iterative Policy Improvement for the Mouse Maze.

Two nested loops:
    inner (policy_evaluation) -- sweep Q for a fixed policy until Q stops changing.
    outer (policy_iteration)  -- evaluate then improve, until the policy stops changing.

Both loops early-stop on convergence; both have a safety cap.
"""

import numpy as np

from environment import ACTIONS, step


def _random_deterministic_policy(maze, treasure, rng):
    """Return a policy array where each non-treasure cell holds a random action."""
    rows, cols = maze.shape
    policy = np.empty((rows, cols), dtype=object)
    for r in range(rows):
        for c in range(cols):
            policy[r, c] = '' if (r, c) == treasure else rng.choice(ACTIONS)
    return policy


def _action_index(action):
    return ACTIONS.index(action)


def q_update(state, action, q_table, policy, treasure, gamma, maze):
    """One Bellman backup for a (state, action) pair under a deterministic policy.

    Q(s, a) = r + gamma * Q(s', policy(s'))   when s' is not the treasure
    Q(s, a) = r                               when s' is the treasure
    """
    next_pos, r = step(state, action, treasure, maze)
    if next_pos == treasure:
        return r
    next_action = policy[next_pos]
    return r + gamma * q_table[next_pos[0], next_pos[1], _action_index(next_action)]


def policy_evaluation(policy, treasure, gamma, maze, n_sweeps=100, tol=1e-6):
    """Sweep the Q-table until it converges for a fixed deterministic policy."""
    rows, cols = maze.shape
    q = np.zeros((rows, cols, len(ACTIONS)))

    for _ in range(n_sweeps):
        q_new = np.zeros_like(q)
        for r in range(rows):
            for c in range(cols):
                if (r, c) == treasure:
                    continue
                for a in ACTIONS:
                    q_new[r, c, _action_index(a)] = q_update(
                        (r, c), a, q, policy, treasure, gamma, maze
                    )
        if np.max(np.abs(q_new - q)) < tol:
            q = q_new
            break
        q = q_new

    return q


def value_from_q(q_table, policy, treasure, maze):
    """Collapse Q to state-value V by reading Q[s, policy(s)] at each cell."""
    rows, cols = maze.shape
    v = np.zeros((rows, cols))
    for r in range(rows):
        for c in range(cols):
            if (r, c) == treasure:
                continue
            v[r, c] = q_table[r, c, _action_index(policy[r, c])]
    return v


def greedy_policy(q_table, treasure, maze, rng=None):
    """Greedy policy from Q-table. Random tie-break, blank string at treasure."""
    if rng is None:
        rng = np.random.default_rng()

    rows, cols = maze.shape
    policy = np.empty((rows, cols), dtype=object)

    for r in range(rows):
        for c in range(cols):
            if (r, c) == treasure:
                policy[r, c] = ''
                continue
            row = q_table[r, c]
            best = np.max(row)
            ties = [a for a, q in zip(ACTIONS, row) if np.isclose(q, best)]
            policy[r, c] = rng.choice(ties)

    return policy


def uniform_random_policy_value(treasure, gamma, maze, n_sweeps=200, tol=1e-6):
    """V under the uniform random policy (each action with prob 0.25).

    Used only for the pedagogical "before learning" plot.
    """
    rows, cols = maze.shape
    v = np.zeros((rows, cols))

    for _ in range(n_sweeps):
        v_new = np.zeros_like(v)
        for r in range(rows):
            for c in range(cols):
                if (r, c) == treasure:
                    continue
                total = 0.0
                for a in ACTIONS:
                    next_pos, reward = step((r, c), a, treasure, maze)
                    if next_pos == treasure:
                        total += reward
                    else:
                        total += reward + gamma * v[next_pos]
                v_new[r, c] = total / len(ACTIONS)
        if np.max(np.abs(v_new - v)) < tol:
            v = v_new
            break
        v = v_new

    return v


def policy_iteration(
    treasure,
    gamma,
    maze,
    n_eval_sweeps=100,
    max_cycles=50,
    tol=1e-6,
    seed=None,
):
    """Iterative Policy Improvement.

    Returns (policy, V, cycles_run) where cycles_run is the number of
    evaluate-improve cycles actually executed.
    """
    rng = np.random.default_rng(seed)
    policy = _random_deterministic_policy(maze, treasure, rng)

    for cycle in range(1, max_cycles + 1):
        q = policy_evaluation(policy, treasure, gamma, maze, n_eval_sweeps, tol)
        new_policy = greedy_policy(q, treasure, maze, rng)

        if np.array_equal(new_policy, policy):
            policy = new_policy
            break
        policy = new_policy

    v = value_from_q(q, policy, treasure, maze)
    return policy, v, cycle
