"""Iterative Policy Improvement for the Mouse Maze.

Two nested loops:
    inner (policy_evaluation) -- sweep Q for a fixed policy until Q stops changing.
    outer (policy_iteration)  -- evaluate then improve, until the policy stops changing.

Both loops early-stop on convergence; both have a safety cap.

Terminal cells (treasure + any holes) get a blank policy entry and are skipped
during sweeps. The Bellman backup uses the immediate reward only when the next
cell is terminal (no bootstrap).
"""

import numpy as np

from environment import ACTIONS, is_rock, is_terminal, step


def _is_skip(cell, treasure, holes, maze):
    """Cells with no value/policy: terminals (treasure + holes) and rocks."""
    return is_terminal(cell, treasure, holes) or is_rock(cell, maze)


def _random_deterministic_policy(maze, treasure, holes, rng):
    """Random action at every playable cell; blank at terminals and rocks."""
    rows, cols = maze.shape
    policy = np.empty((rows, cols), dtype=object)
    for r in range(rows):
        for c in range(cols):
            if _is_skip((r, c), treasure, holes, maze):
                policy[r, c] = ''
            else:
                policy[r, c] = rng.choice(ACTIONS)
    return policy


def _action_index(action):
    return ACTIONS.index(action)


def q_update(state, action, q_table, policy, treasure, gamma, maze,
             holes=(), portals=()):
    """One Bellman backup for a (state, action) pair under a deterministic policy.

    Q(s, a) = r                         when s' is terminal (treasure or hole)
    Q(s, a) = r + gamma * Q(s', pi(s')) otherwise
    """
    next_pos, r, done = step(state, action, treasure, maze, holes, portals)
    if done:
        return r
    next_action = policy[next_pos]
    return r + gamma * q_table[next_pos[0], next_pos[1], _action_index(next_action)]


def policy_evaluation(policy, treasure, gamma, maze, n_sweeps=100, tol=1e-6,
                      holes=(), portals=()):
    """Sweep the Q-table until it converges for a fixed deterministic policy."""
    rows, cols = maze.shape
    q = np.zeros((rows, cols, len(ACTIONS)))

    for _ in range(n_sweeps):
        q_new = np.zeros_like(q)
        for r in range(rows):
            for c in range(cols):
                if _is_skip((r, c), treasure, holes, maze):
                    continue
                for a in ACTIONS:
                    q_new[r, c, _action_index(a)] = q_update(
                        (r, c), a, q, policy, treasure, gamma, maze, holes, portals
                    )
        if np.max(np.abs(q_new - q)) < tol:
            q = q_new
            break
        q = q_new

    return q


def value_from_q(q_table, policy, treasure, maze, holes=()):
    """Collapse Q to state-value V by reading Q[s, policy(s)] at each cell.

    Terminal cells (treasure + holes) and rocks keep V = NaN so plots mask them.
    """
    rows, cols = maze.shape
    v = np.zeros((rows, cols))
    for r in range(rows):
        for c in range(cols):
            if is_rock((r, c), maze):
                v[r, c] = np.nan
                continue
            if is_terminal((r, c), treasure, holes):
                continue
            v[r, c] = q_table[r, c, _action_index(policy[r, c])]
    return v


def greedy_policy(q_table, treasure, maze, rng=None, holes=()):
    """Greedy policy from Q-table. Random tie-break, blank at terminals and rocks."""
    if rng is None:
        rng = np.random.default_rng()

    rows, cols = maze.shape
    policy = np.empty((rows, cols), dtype=object)

    for r in range(rows):
        for c in range(cols):
            if _is_skip((r, c), treasure, holes, maze):
                policy[r, c] = ''
                continue
            row = q_table[r, c]
            best = np.max(row)
            ties = [a for a, q in zip(ACTIONS, row) if np.isclose(q, best)]
            policy[r, c] = rng.choice(ties)

    return policy


def uniform_random_policy_value(treasure, gamma, maze, n_sweeps=200, tol=1e-6,
                                holes=(), portals=()):
    """V under the uniform random policy (each action with prob 0.25).

    Used only for the pedagogical "before learning" plot.
    """
    rows, cols = maze.shape
    v = np.zeros((rows, cols))

    for _ in range(n_sweeps):
        v_new = np.zeros_like(v)
        for r in range(rows):
            for c in range(cols):
                if _is_skip((r, c), treasure, holes, maze):
                    continue
                total = 0.0
                for a in ACTIONS:
                    next_pos, r_step, done = step(
                        (r, c), a, treasure, maze, holes, portals
                    )
                    if done:
                        total += r_step
                    else:
                        total += r_step + gamma * v[next_pos]
                v_new[r, c] = total / len(ACTIONS)
        if np.max(np.abs(v_new - v)) < tol:
            v = v_new
            break
        v = v_new

    for r in range(rows):
        for c in range(cols):
            if is_rock((r, c), maze):
                v[r, c] = np.nan

    return v


def policy_iteration(
    treasure,
    gamma,
    maze,
    n_eval_sweeps=100,
    max_cycles=50,
    tol=1e-6,
    seed=None,
    holes=(),
    portals=(),
):
    """Iterative Policy Improvement.

    Returns (policy, V, cycles_run) where cycles_run is the number of
    evaluate-improve cycles actually executed.
    """
    rng = np.random.default_rng(seed)
    policy = _random_deterministic_policy(maze, treasure, holes, rng)

    for cycle in range(1, max_cycles + 1):
        q = policy_evaluation(
            policy, treasure, gamma, maze, n_eval_sweeps, tol, holes, portals
        )
        new_policy = greedy_policy(q, treasure, maze, rng, holes)

        if np.array_equal(new_policy, policy):
            policy = new_policy
            break
        policy = new_policy

    v = value_from_q(q, policy, treasure, maze, holes)
    return policy, v, cycle
