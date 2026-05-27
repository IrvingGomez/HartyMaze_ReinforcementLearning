"""Build HartyMazeSolver.ipynb from cell contents.

Run this script once to (re)generate the notebook. The notebook itself is
intentionally a thin shell: all real logic lives in src/.
"""

from pathlib import Path

import nbformat as nbf


NOTEBOOK_PATH = Path(__file__).parent / 'HartyMazeSolver.ipynb'


def md(text):
    return nbf.v4.new_markdown_cell(text)


def code(text):
    return nbf.v4.new_code_cell(text)


cells = []

cells.append(md("""# Harty and the Treasure Maze

Welcome! Harty is a fox who wants to find a treasure hidden inside a maze.
We will teach Harty the best plan (a *policy*) for getting to the treasure
no matter which cell he starts in.

The technique is called **Iterative Policy Improvement**. The idea:

1. Start with a random plan.
2. Score it: how good is every cell under this plan?
3. Improve the plan: at each cell, pick the action that leads to the best score.
4. Repeat until the plan stops changing.

Run every cell from top to bottom (Shift + Enter).
"""))

cells.append(code("""import sys
from pathlib import Path

# Make modules in src/ importable from this notebook.
sys.path.insert(0, str(Path.cwd() / 'src'))

import numpy as np
import matplotlib.pyplot as plt

from environment import DEFAULT_MAZE
from policy_iteration import policy_iteration, uniform_random_policy_value
from visualization import plot_policy_and_value, plot_value_only
from animation import animate_path, save_animation, simulate_path, uniform_random_action
from IPython.display import HTML, Image"""))

cells.append(md("""## 1. How the maze is encoded

Every cell in the maze is given a number from **0 to 14**. The number tells
which walls that cell has. Here is the legend:

![Wall code legend](images/MouseMazeCode.png)

And here is the default maze with each cell's code drawn inside:

![Default maze with codes](images/mousemaze_withcode_v2.png)

Students who want to design their own maze just need to write a 2D array of
these numbers. Two neighbour cells should agree on shared walls (if cell A
says "right wall" then cell B on its right should say "left wall").
"""))

cells.append(md("""## 2. Choose your setup

Change the values below to play with the maze. Then rerun every cell.

- `MAZE` is a numpy array of wall codes (default supplied by the project).
- `TREASURE` is the (row, column) where the treasure sits.
- `HARTY` is the cell where Harty stands.
- `DISCOUNT_RATE` (gamma) decides how much Harty cares about future steps.
  Closer to 1 = patient; closer to 0 = short-sighted.
"""))

cells.append(code("""MAZE = DEFAULT_MAZE     # replace with your own np.array of wall codes 0-14
TREASURE = (0, 4)
HARTY = (9, 9)
DISCOUNT_RATE = 0.97

rows, cols = MAZE.shape

assert MAZE.ndim == 2, 'MAZE must be a 2D array'
assert MAZE.dtype.kind in 'iu', 'MAZE values must be integers'
assert MAZE.min() >= 0 and MAZE.max() <= 14, 'wall codes must be in 0..14'

assert 0 <= TREASURE[0] < rows and 0 <= TREASURE[1] < cols, 'TREASURE outside grid'
assert 0 <= HARTY[0] < rows and 0 <= HARTY[1] < cols, 'HARTY outside grid'
assert TREASURE != HARTY, 'TREASURE and HARTY cannot share a cell'

trap_codes = {9, 10, 11, 12}
assert int(MAZE[HARTY]) not in trap_codes, 'HARTY is in a fully-walled cell, he cannot move'

print(f'Maze: {rows} x {cols}')
print(f'Treasure at {TREASURE}, Harty at {HARTY}, gamma = {DISCOUNT_RATE}')"""))

cells.append(md("""## 3. The maze

Here is the empty maze with the treasure and Harty placed at the cells you
chose. No learning yet, just the picture.
"""))

cells.append(code("""V_empty = np.zeros_like(MAZE, dtype=float)
fig, _ = plot_value_only(
    V_empty, TREASURE, HARTY, MAZE,
    title='The maze (no value yet)',
)
plt.show()"""))

cells.append(md("""## 4. Before learning -- the random walker

To start, let us see what happens if Harty walks **randomly** at every step
(each direction with probability 1/4). The colors below show the *value* of
each cell -- how often a random walk starting there ends at the treasure.

Hot colors (purple) = high value. Cold colors (red) = low value.

You will see that random walking is bad: most cells light up only a little.
"""))

cells.append(code("""V_random = uniform_random_policy_value(TREASURE, DISCOUNT_RATE, MAZE)

fig, _ = plot_value_only(
    V_random, TREASURE, HARTY, MAZE,
    title='Before learning: value under a random policy',
)
plt.show()"""))

cells.append(md("""### Watch Harty wander randomly

Each step Harty picks a direction at random with equal chance. You will
see him bump into walls, backtrack, and rarely reach the chest in time.
"""))

cells.append(code("""random_path = simulate_path(
    uniform_random_action, HARTY, TREASURE, MAZE,
    max_steps=80, seed=0,
)
anim_random = animate_path(
    random_path, TREASURE, MAZE,
    value=V_random,
    title='Harty wandering with the random policy',
)
HTML(anim_random.to_jshtml())"""))

cells.append(md("""### Save the random-policy video as a GIF

Run this cell to write the animation to `outputs/harty_random.gif`. The GIF
is shown inline below; right-click it to save, or open the `outputs/` folder
in the file explorer to grab the file.
"""))

cells.append(code("""saved = save_animation(anim_random, 'outputs/harty_random.gif', fps=2)
print(f'Saved: {saved.resolve()}')
Image(filename=str(saved))"""))

cells.append(md("""### Plain version -- just the maze and Harty

Same random walk, but without the value colors or any arrows. Useful for
introducing the maze without giving away the policy.
"""))

cells.append(code("""anim_random_plain = animate_path(
    random_path, TREASURE, MAZE,
    title='Harty wandering (plain)',
)
HTML(anim_random_plain.to_jshtml())"""))

cells.append(md("""Save the plain random-policy video:"""))

cells.append(code("""saved = save_animation(anim_random_plain, 'outputs/harty_random_plain.gif', fps=2)
print(f'Saved: {saved.resolve()}')
Image(filename=str(saved))"""))

cells.append(md("""## 5. After learning -- the best policy

Now we run **Iterative Policy Improvement**. Each cell gets an arrow telling
Harty the best direction to go from there. The colors show how good each
cell is under this learned plan.

If you follow the arrows starting from Harty's cell, you should reach the
treasure.
"""))

cells.append(code("""policy, V, cycles = policy_iteration(
    TREASURE, DISCOUNT_RATE, MAZE, seed=0,
)
print(f'Policy iteration converged in {cycles} cycles.')

fig, _ = plot_policy_and_value(
    policy, V, TREASURE, HARTY, MAZE,
    title='After learning: best policy and value',
)
plt.show()"""))

cells.append(md("""### Watch Harty follow the best policy

Now Harty obeys the arrows at every cell. He should walk straight to the
treasure with no backtracking.
"""))

cells.append(code("""best_path = simulate_path(
    policy, HARTY, TREASURE, MAZE, max_steps=80,
)
anim_best = animate_path(
    best_path, TREASURE, MAZE,
    value=V,
    policy=policy,
    title='Harty following the best policy',
)
HTML(anim_best.to_jshtml())"""))

cells.append(md("""### Save the best-policy video as a GIF

Run this cell to write the animation to `outputs/harty_best.gif`. The GIF
is shown inline below; right-click it to save, or open the `outputs/` folder
in the file explorer to grab the file.
"""))

cells.append(code("""saved = save_animation(anim_best, 'outputs/harty_best.gif', fps=2)
print(f'Saved: {saved.resolve()}')
Image(filename=str(saved))"""))

cells.append(md("""### Plain version -- just the maze and Harty

Same optimal walk, but without value colors or arrows. Pure focus on the
path Harty takes to reach the treasure.
"""))

cells.append(code("""anim_best_plain = animate_path(
    best_path, TREASURE, MAZE,
    title='Harty following the best policy (plain)',
)
HTML(anim_best_plain.to_jshtml())"""))

cells.append(md("""Save the plain best-policy video:"""))

cells.append(code("""saved = save_animation(anim_best_plain, 'outputs/harty_best_plain.gif', fps=2)
print(f'Saved: {saved.resolve()}')
Image(filename=str(saved))"""))

cells.append(md("""## 6. Read the result

The matrix below shows the value of every cell, rounded to two decimals.
Cells next to the treasure should be close to 1 (one step away from a
reward of 1). Cells deep in the maze are smaller.
"""))

cells.append(code("""print(np.round(V, 2))"""))

cells.append(md("""## What to try next

- Move the treasure to a different cell (for example `(5, 5)`).
- Move Harty.
- Change `DISCOUNT_RATE` to `0.5` (impatient) or `0.99` (very patient).
- Build your own maze with the wall codes from section 1.

Rerun the notebook each time. The plan and the colors will update.
"""))


nb = nbf.v4.new_notebook()
nb['cells'] = cells
nb['metadata'] = {
    'kernelspec': {
        'display_name': 'Python 3',
        'language': 'python',
        'name': 'python3',
    },
    'language_info': {'name': 'python'},
}

with NOTEBOOK_PATH.open('w', encoding='utf-8') as f:
    nbf.write(nb, f)

print(f'Wrote {NOTEBOOK_PATH}')
