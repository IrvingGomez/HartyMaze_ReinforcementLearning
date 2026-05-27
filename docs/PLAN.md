# PLAN — GridWorld Mouse Maze (Harty edition)

Goal: Refactor `04_GridWorldMouseMaze_V4.ipynb` into a simple, modular, high-school-friendly Iterative Policy Improvement project. Add Harty character, user-chosen treasure/Harty positions, user-chosen discount rate, and per-cell value coloring (orange-to-purple gradient, V4 style).

Do NOT modify `04_GridWorldMouseMaze_V4.ipynb`.

---

## Locked decisions

1. **Output**: `.py` modules + one thin pedagogical notebook that imports them. Notebook = narrative (markdown + small calls + plots). Modules = logic.
2. **Maze image**: render walls programmatically from the Maze code matrix. Lives in its own non-RL module.
3. **Policy**: deterministic-only policy iteration core. Initial baseline = uniform-stochastic policy (one helper function, used only for the "before" plot). After that, iteration is deterministic.
4. **Rewards**: `tired=0, treasure=1` (same as V4).

---

## File layout

```
GridWorldClaude/
  04_GridWorldMouseMaze_V4.ipynb        # untouched reference
  docs/PLAN.md
  images/                               # Treasure.png, HartyMaze_right.png, ...
  src/
    maze_renderer.py                    # Phase 0 — walls from matrix, no RL
    environment.py                      # Phase 1 — Maze constant, next_state, reward
    policy_iteration.py                 # Phase 2 — eval + improvement (deterministic)
    visualization.py                    # Phase 3 — colormap, value heatmap, arrows, character overlays
  HartyMazeSolver.ipynb                 # thin notebook: user knobs + narrative + calls
```

---

## Phase 0 — `maze_renderer.py` (walls from matrix)

Pure rendering, no RL imports.

- `WALL_CODES` mapping cell code 0-14 -> set of walls present (`{'top','left','right','bottom'}`).
- `draw_maze(ax, maze)` — for each cell, draw the walls indicated by its code as black line segments on `ax`. Sets axes equal, hides ticks.
- `cell_to_xy(cell, maze)` — converts `(row, col)` to plot coordinates (top-left grid origin, row grows downward to match V4 heatmap orientation).

Verification: standalone test cell -> render empty 10x10 maze; eyeball compare to `images/MouseMaze.png` walls.

---

## Phase 1 — `environment.py`

- `DEFAULT_MAZE` (10x10 numpy array, same wall codes as V4). Students can pass their own maze; functions accept it as an argument.
- `ACTIONS = ['up','down','left','right']`.
- `ACTION_SYMBOLS = {'up':'↑','down':'↓','left':'←','right':'→','':''}`.
- `MOVES = {'up':(-1,0),'down':(1,0),'left':(0,-1),'right':(0,1)}`.
- `BLOCKED_ACTIONS_BY_CODE` — dict `code -> set of blocked actions` (replaces V4's giant if/elif chain).
- `next_state(position, action, maze)` — applies move, then clamps to current cell if action is blocked by current cell's wall code, AND clamps to grid bounds (so custom mazes without outer walls don't escape).
- `reward(next_position, treasure)` — 1 if `next_position == treasure` else 0.
- `step(position, action, treasure, maze)` — returns `(next_position, reward)`.

Verification: small assert block — wall codes block expected actions; step into treasure yields reward 1; step into wall stays put.

---

## Phase 2 — `policy_iteration.py` (deterministic core)

Break V4's monolith into named small functions:

- `uniform_random_policy_value(treasure, gamma, maze, n_sweeps=100, tol=1e-6)` — iterative eval where each cell picks each of 4 actions with prob 0.25. Returns V matrix. Used ONLY for initial baseline plot. Early-stops when V change < tol.
- `q_update(s, a, q_table, policy, treasure, gamma, maze)` — single Bellman update for one (s,a).
- `policy_evaluation(policy, treasure, gamma, maze, n_sweeps=100, tol=1e-6)` — sweeps Q-table for a deterministic `policy`. Returns Q. Inner loop early-stops when `max|Q_new - Q_old| < tol`.
- `value_from_q(q_table, policy, maze)` — collapses Q to V.
- `greedy_policy(q_table, treasure, maze)` — argmax, random tie-break, blank string at treasure cell.
- `policy_iteration(treasure, gamma, maze, n_eval_sweeps=100, max_cycles=50, tol=1e-6, seed=None)` — outer loop:
  1. start with random deterministic policy.
  2. evaluate -> Q-table (inner early-stop on Q convergence).
  3. improve -> new greedy policy.
  4. break when policy unchanged from previous cycle (outer early-stop). Hard cap = `max_cycles`.
  Returns `(policy, V)`.

Verification:
- `uniform_random_policy_value` -> V mostly small, near zero far from treasure.
- After `policy_iteration` with treasure at (0,4), gamma=0.97: arrows on reachable cells point toward treasure; V monotonically decreases with maze distance; V[adjacent to treasure] ≈ `gamma * 1`.

---

## Phase 3 — `visualization.py`

- `make_value_colormap()` — V4's gradient: concat `plt.cm.RdBu(linspace(0, 0.5, 128))` with `plt.cm.PuOr(linspace(0.5, 1, 128))` via `LinearSegmentedColormap.from_list`. Low V -> blue/white, high V -> orange/purple.
- `plot_value_heatmap(ax, V, cmap, vmin=-1, vmax=1)` — seaborn heatmap on `ax`, no cbar, square.
- `overlay_policy_arrows(ax, policy, treasure)` — write action symbols at cell centers, skip treasure.
- `overlay_image_at_cell(ax, image, cell)` — place PNG (Treasure or Harty) at given grid cell.
- `plot_policy_and_value(policy, V, treasure, harty, maze=MAZE, treasure_img, harty_img)` — composes: heatmap colors -> maze walls (via `maze_renderer.draw_maze`) -> arrows -> treasure image -> Harty image. One figure, one call.

Verification: render result for known-good config matches V4's converged figure (arrows, gradient direction, treasure placement).

---

## Phase 4 — `HartyMazeSolver.ipynb` (thin notebook)

Narrative sections (markdown + small code cells):

1. **What we're solving** — short intro: maze, Harty, treasure, find best plan.
2. **How the maze is encoded** — markdown cell before the config cell. Embed `images/MouseMazeCode.png` (the 15-state legend showing what each code 0-14 means) and `images/mousemaze_withcode.png` (the default maze with codes labeled per cell). Short text: each cell is a number 0-14 saying which walls it has.
3. **Choose your setup** — single config cell with four plain assignments:
   ```python
   from environment import DEFAULT_MAZE
   MAZE = DEFAULT_MAZE        # students can replace with their own np.array of wall codes 0-14
   TREASURE = (0, 4)
   HARTY = (9, 9)
   DISCOUNT_RATE = 0.97
   ```
   Plus minimal asserts: maze is 2D int array with codes in 0-14, in-bounds positions, not a fully-walled trap (codes 9/10/11/12), treasure != Harty.
4. **The maze** — render empty maze + Harty + treasure (visualization only, no policy yet).
5. **Before learning** — show `uniform_random_policy_value` colored heatmap. Discuss: random walking, low values.
6. **After learning** — run `policy_iteration`, plot policy arrows on colored value heatmap with Harty + treasure overlaid.
7. **Read the result** — print V rounded to 2 decimals; mention how arrows form a path from Harty to treasure.

No widgets, no `input()`. Students edit the config cell and rerun.

Verification: change `TREASURE` to (5,5), rerun all cells; arrows + colors recompute and point to new goal.

---

## Phase 5 — End-to-end checks

- Run notebook top-to-bottom with default config; output matches expected V4 result.
- Change treasure to two different cells; policy + colors update sensibly.
- Change `DISCOUNT_RATE` to 0.5 then 0.99; arrows still point home; values differ in magnitude as expected.
- Place Harty in several spots; it draws at the right cell with no policy change.

---

## Phase 6 — Future hooks (stubs only)

Reserve interfaces for the upcoming video feature without building it:

- `harty_facing` parameter on `overlay_image_at_cell` (values `'right'|'left'|'up'|'down'`; today only `'right'` asset exists — others fall back to right + TODO note).
- `simulate_path(policy, start, treasure, max_steps)` — generator of cells visited following the policy. Lives in `policy_iteration.py`.
- Notebook end note: animation needs left/up/down Harty PNG variants; future layout = policy/value plot left, Harty walking right.

---

## Out of scope (current iteration)

- No UI / frontend / web app / deployment.
- No animation/video yet.
- No changes to `04_GridWorldMouseMaze_V4.ipynb`.
- No slippery / stochastic-environment branch.
- No defensive programming beyond the three student-facing asserts in the config cell.
