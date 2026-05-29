"""Build HartyPlay.ipynb from cell contents.

Run this script once to (re)generate the play-mode notebook. The notebook
calls `launch_game_window` which pops open a real OS window where the
arrow keys move Harty.
"""

from pathlib import Path

import nbformat as nbf


NOTEBOOK_PATH = Path(__file__).parent / 'HartyPlay.ipynb'


def md(text):
    return nbf.v4.new_markdown_cell(text)


def code(text):
    return nbf.v4.new_code_cell(text)


cells = []

cells.append(md("""# Play the Maze -- you control Harty

You are Harty now. A small window will open on your screen. Use the
**arrow keys** to walk through the maze, reach the chest, and win.

How it works:
- Each arrow key press moves Harty one cell in that direction.
- If Harty bumps a wall he stays put, but he turns to look that way.
- Press **q** or close the window to quit.
- After you close the window, the next cell prints your final state.
"""))

cells.append(md("""## Set up the maze

Same variables as in `HartyMazeSolver.ipynb`. Pick where to drop the
treasure, where Harty starts, and (optionally) define your own maze.
"""))

cells.append(code("""import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd() / 'src'))

from environment import DEFAULT_MAZE
from play_mode import launch_game_window

MAZE = DEFAULT_MAZE
TREASURE = (0, 4)
HARTY = (9, 9)

HOLES = []              # e.g. [(3, 3), (5, 7)] -- stepping here ends the game
PORTALS = []            # e.g. [((1, 1), (8, 8))] -- up to 2 pairs; both endpoints teleport

rows, cols = MAZE.shape

assert MAZE.ndim == 2, 'MAZE must be 2D'
assert MAZE.min() >= 0 and MAZE.max() <= 14, 'wall codes must be in 0..14'
assert 0 <= TREASURE[0] < rows and 0 <= TREASURE[1] < cols
assert 0 <= HARTY[0] < rows and 0 <= HARTY[1] < cols
assert TREASURE != HARTY

trap_codes = {9, 10, 11, 12}
assert int(MAZE[HARTY]) not in trap_codes, 'Harty would be stuck in this cell'

assert len(PORTALS) <= 2, 'at most two portal pairs are supported'
for pair in PORTALS:
    assert len(pair) == 2, 'each portal pair must have exactly two cells'

reserved = {TREASURE, HARTY, *HOLES}
for pair in PORTALS:
    for cell in pair:
        assert 0 <= cell[0] < rows and 0 <= cell[1] < cols, f'portal cell {cell} outside grid'
        assert cell not in reserved, f'portal cell {cell} clashes with treasure/Harty/hole'
        reserved.add(cell)

for hole in HOLES:
    assert 0 <= hole[0] < rows and 0 <= hole[1] < cols, f'hole {hole} outside grid'
    assert hole != TREASURE, 'hole cannot share a cell with the treasure'
    assert hole != HARTY, 'hole cannot share a cell with Harty'

print(f'Maze: {rows}x{cols}, treasure at {TREASURE}, Harty starts at {HARTY}')
print(f'Holes: {HOLES}')
print(f'Portals: {PORTALS}')"""))

cells.append(md("""## Play!

Run the cell below. A new window will pop open on your desktop. **Click
on the window** so the keyboard focus is on it, then press the arrow
keys. Close the window (or press *q*) when you are done -- the cell will
finish and return Harty's final state.

Note: while the window is open this cell is "running"; the notebook will
look busy until you close the window. That is expected.
"""))

cells.append(code("""final_state = launch_game_window(MAZE, TREASURE, HARTY, holes=HOLES, portals=PORTALS)
final_state"""))

cells.append(md("""## Inspect your final state
"""))

cells.append(code("""print(f'Position: {final_state.position}')
print(f'Facing:   {final_state.facing}')
print(f'Steps:    {final_state.steps_taken}')
print(f'Won?      {final_state.won}')
print(f'Dead?     {final_state.dead}')"""))

cells.append(md("""## Want a new game?

Just re-run the *Play!* cell. Change `MAZE`, `TREASURE`, or `HARTY` in
the setup cell first if you want a different challenge.
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
