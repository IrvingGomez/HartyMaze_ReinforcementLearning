# PLAN — Video mode and Play mode

Two new modes for the Mouse Maze project, layered on top of the Phase-0..4
deliverables (modules in `src/`, notebook `HartyMazeSolver.ipynb`).

| Mode | What it does | Driver |
|------|--------------|--------|
| **Video mode** | Animates Harty walking from his start cell to the treasure, following the learned policy. Side-by-side layout: policy + value plot on the left, Harty moving on the right. | Automatic (policy is the controller) |
| **Play mode** | The student controls Harty with the keyboard arrow keys. No keypress = Harty stays idle. Used before or after running policy iteration so students can try the maze themselves. | Human (keyboard input) |

Both modes share the same dependency: Harty rendered in four facing directions.
We tackle the assets first, then play mode, then video mode.

---

## Phase A — Image assets

### What we have

- `images/harty.png` (252 KB) — full-size character art (probably a clean
  drawing of Harty that can be transformed).
- `images/HartyMaze_right.png` (16 KB) — maze-sized Harty facing right.
- `images/Treasure.png` — chest icon.

### What we need

Three more direction variants matching the size and style of
`HartyMaze_right.png`:

- `images/HartyMaze_left.png`
- `images/HartyMaze_up.png`
- `images/HartyMaze_down.png`

Optional (nice-to-have for idle frame in play mode):

- `images/HartyMaze_idle.png` — Harty standing still, looking forward.

### How to produce them

Three options, pick whichever fits the project's art needs:

1. **Programmatic flip for `left`.** Mirror `HartyMaze_right.png`
   horizontally with PIL (`Image.transpose(Image.FLIP_LEFT_RIGHT)`).
   Looks correct for symmetric characters. Trivial.
2. **Hand-drawn `up` and `down`.** Rotating a side-view 90 degrees looks
   wrong (character lying on its back). Best result is to draw or source
   front/back views of Harty.
3. **Fallback simplification.** Use `HartyMaze_right.png` for every
   direction. Less satisfying visually but unblocks the rest of the work
   immediately.

Recommendation: do option 1 now (left), accept option 3 for up/down as a
placeholder, and replace with hand-drawn assets later when available.

### Module support

Update `visualization.py`:

- Extend `HARTY_IMAGE_PATHS` dict with the three new keys: `'left'`,
  `'up'`, `'down'`. `load_harty_image(facing)` already takes the parameter,
  so once the paths exist no further code change is needed.
- Add a tiny helper `make_left_image_from_right(src_path, dst_path)` that
  generates `HartyMaze_left.png` once with PIL. Run it as a one-off script.

### Verification

- Plot Harty at four different cells, one per direction, in a single
  test figure. Eye check: each variant faces the right way.
- Existing pytest suite still passes (visualization tests should be
  parameterized over `facing` to make sure missing images do not crash).

---

## Phase B — Play mode

The student presses arrow keys; Harty moves through the maze respecting
the wall codes. Treasure pickup = win. No keypress = idle (Harty stays
put, facing his last direction).

### Choice of input layer

CLAUDE.md says "no UI / frontend / webpage" -- play mode needs SOME way to
read keys but does not have to be a webapp. Plain options:

| Option | Pros | Cons |
|--------|------|------|
| matplotlib `key_press_event` in a notebook with `%matplotlib widget` | Stays in the notebook; no new dependency beyond `ipympl` | Requires a backend switch; some students see backend issues |
| matplotlib in a standalone window via `%matplotlib qt` or running a `.py` script | Works without notebook setup quirks | Pops out of the notebook flow |
| `keyboard` or `pynput` library | Fine-grained keypress | Extra dependency, OS permission prompts |
| `pygame` | Best game-feel | Heavy dependency, separate window |

Recommendation: **matplotlib `key_press_event` with `%matplotlib widget`**.
Same plot family the students already see, no new dependency beyond
`ipympl` (one `pip install`).

### Module: `src/play_mode.py`

Pure logic, no UI concerns:

- `PlayState` — small dataclass: `position`, `facing`, `treasure`,
  `maze`, `steps_taken`, `won`.
- `handle_key(state, key)` — pure function. Takes the current state and a
  key name (`'up'|'down'|'left'|'right'`); returns a new state.
  Movement obeys `environment.next_state` (wall codes + grid bounds).
  Updates `facing` even if the move was blocked, so Harty turns to look
  but does not walk into a wall.
- `is_won(state)` — true when Harty is on the treasure cell.

### Notebook: `HartyPlay.ipynb` (or new sections in main notebook)

Cells:

1. Intro markdown: "Use the arrow keys. Reach the chest!"
2. Backend swap: `%matplotlib widget`.
3. Config cell: same `MAZE`, `TREASURE`, `HARTY`, `DISCOUNT_RATE`
   variables -- so a student can switch between play mode and learning
   mode without rewriting config.
4. Code cell that:
   - Builds the figure with maze walls + treasure + Harty.
   - Registers a key handler that calls `handle_key`, updates the
     figure in place (new Harty cell + facing image), redraws.
   - On treasure-reach: print "You won in N steps!" and freeze input.
5. Optional: a button or printable cell that resets the game.

### Verification

- Move Harty manually across the default maze; arrow keys move him in the
  expected directions; walls block him; he wins on reaching the treasure.
- `handle_key` covered by unit tests in `tests/test_play_mode.py`:
  - Pressing 'right' from a cell with no right wall moves Harty right
    and sets `facing='right'`.
  - Pressing 'right' from a cell with a right wall keeps Harty put but
    still sets `facing='right'`.
  - Reaching the treasure sets `won=True`.

---

## Phase C — Video mode (animated policy execution)

After the student has learned the optimal policy via `policy_iteration`,
they can watch Harty walk the maze automatically.

### Module: `src/play_mode.py` or new `src/animation.py`

- `simulate_path(policy, start, treasure, maze, max_steps=200)` —
  generator yielding the sequence of cells Harty visits. Already
  listed as a Phase 6 stub in `docs/PLAN.md`; promote it to real code
  here. Each yield includes `(cell, facing)` so the renderer can pick
  the right Harty image.
- `animate_policy(policy, V, start, treasure, maze, ...)` — uses
  matplotlib `FuncAnimation`:
  - Left panel: static `plot_policy_and_value(...)` minus the moving
    Harty.
  - Right panel: same maze, but Harty's position updates each frame.
  - Returns the `FuncAnimation` object so the caller can `.save('out.gif')`
    or display it in a notebook with `HTML(anim.to_jshtml())`.

### Notebook integration

Add a final section to `HartyMazeSolver.ipynb`:

- "Watch Harty solve the maze" — runs `animate_policy` after the
  policy iteration cell. Saves a small mp4 or gif to `outputs/` (create
  the directory on demand) and displays it inline.

### Verification

- After learning, the animation visibly traces a path from Harty's start
  to the treasure.
- Number of frames matches the path length (plus a few idle frames at
  start and end for clarity).
- Wall-respecting: Harty never crosses a black wall line.

---

## Order of work

1. **Phase A.1**: PIL flip script -> generate `HartyMaze_left.png`. Decide
   policy for up/down (fallback to right.png in `HARTY_IMAGE_PATHS` for
   now).
2. **Phase A.2**: Update `visualization.py` to register the new paths;
   parameterize a visualization test over the four directions.
3. **Phase B**: Build `play_mode.py` (pure logic + tests) then the
   interactive notebook cells (`%matplotlib widget` + key handler).
4. **Phase C**: Implement `simulate_path` and `animate_policy`; add the
   final animation cell to `HartyMazeSolver.ipynb`.

---

## Open questions

1. **Up/down Harty art**: hand-drawn later, or fallback to the right-facing
   image for all upward/downward steps until art is ready?
2. **Play-mode notebook**: separate `HartyPlay.ipynb`, or new tab inside
   `HartyMazeSolver.ipynb`? Recommend separate so the learning narrative
   stays linear.
3. **Animation output format**: inline jshtml (renders in any Jupyter, no
   ffmpeg needed) or save as `.gif`/`.mp4` to disk?
4. **`%matplotlib widget` acceptable** under the "no UI / frontend"
   limitation? It stays inside the notebook, no webpage, no deployment --
   but it is interactive matplotlib. Confirm before committing.
