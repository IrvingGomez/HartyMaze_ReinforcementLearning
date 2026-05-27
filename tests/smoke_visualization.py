"""Visual smoke test for visualization.py. Not a pytest test -- this is a
script that produces PNGs the user can eyeball. Run with:

    python tests/smoke_visualization.py
"""

from pathlib import Path

import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt

from environment import DEFAULT_MAZE
from policy_iteration import policy_iteration, uniform_random_policy_value
from visualization import plot_policy_and_value, plot_value_only


OUT_DIR = Path(__file__).resolve().parent / '_smoke_out'
OUT_DIR.mkdir(exist_ok=True)

TREASURE = (0, 4)
HARTY = (9, 9)
GAMMA = 0.97


def main():
    v_random = uniform_random_policy_value(TREASURE, GAMMA, DEFAULT_MAZE)
    fig, _ = plot_value_only(
        v_random, TREASURE, HARTY, DEFAULT_MAZE,
        title='Before learning (uniform random policy)',
    )
    fig.savefig(OUT_DIR / 'before_learning.png', dpi=120, bbox_inches='tight')
    plt.close(fig)

    policy, v, cycles = policy_iteration(TREASURE, GAMMA, DEFAULT_MAZE, seed=0)
    print(f'policy_iteration converged in {cycles} cycles')
    fig, _ = plot_policy_and_value(
        policy, v, TREASURE, HARTY, DEFAULT_MAZE,
        title='After learning (optimal policy)',
    )
    fig.savefig(OUT_DIR / 'after_learning.png', dpi=120, bbox_inches='tight')
    plt.close(fig)

    print(f'Wrote {OUT_DIR}/before_learning.png and after_learning.png')


if __name__ == '__main__':
    main()
