"""Play mode: Harty driven by clickable arrow buttons.

Pure logic (PlayState + handle_key) lives at the top so it can be unit-tested.
The `launch_game` function wires the logic to an ipywidgets UI: four arrow
buttons plus a reset button. The maze is rendered as an Image widget that
gets refreshed on every step, so this works in every Jupyter front end
(VS Code, classic Jupyter, JupyterLab) with no extra backend setup.
"""

from dataclasses import dataclass, field, replace
from typing import Any

import matplotlib.pyplot as plt
import ipywidgets as widgets
from IPython.display import clear_output, display

from animation import _harty_extent
from environment import ACTIONS, next_state
from maze_renderer import draw_maze
from visualization import (
    load_harty_image,
    load_treasure_image,
    overlay_image_at_cell,
)


@dataclass
class PlayState:
    """Snapshot of the game. `handle_key` returns a new instance on each step."""

    position: tuple
    facing: str
    treasure: tuple
    maze: Any = field(repr=False)
    steps_taken: int = 0
    won: bool = False


def handle_key(state, action):
    """Pure step function: given a state and an action, return the next state.

    Unknown actions and post-win key presses are no-ops. Walls block movement
    but the facing is still updated, so Harty turns even when he cannot walk.
    """
    if state.won:
        return state
    if action not in ACTIONS:
        return state

    new_position = next_state(state.position, action, state.maze)
    won = new_position == state.treasure

    return replace(
        state,
        position=new_position,
        facing=action,
        steps_taken=state.steps_taken + 1,
        won=won,
    )


def is_won(state):
    return state.position == state.treasure


def launch_game_window(maze, treasure, start, figsize=(7, 7)):
    """Open a real OS window where Harty is controlled by the arrow keys.

    Forces matplotlib to use the TkAgg backend (bundled with Python on
    Windows/Mac/Linux), opens a window, and blocks until the player closes
    it. Returns the final PlayState.

    Call from a notebook cell or a standalone script:
        state = launch_game_window(MAZE, TREASURE, HARTY)
        print(state)
    """
    import matplotlib

    matplotlib.use('TkAgg', force=True)
    import matplotlib.pyplot as plt  # re-import after backend switch

    state_ref = {
        'current': PlayState(
            position=start,
            facing='idle',
            treasure=treasure,
            maze=maze,
        )
    }

    fig, ax = plt.subplots(figsize=figsize)
    fig.canvas.manager.set_window_title('Harty Maze -- arrow keys to move, q to quit')

    draw_maze(ax, maze)
    overlay_image_at_cell(ax, load_treasure_image(), treasure)
    initial_image = load_harty_image('idle')
    harty_artist = ax.imshow(
        initial_image,
        extent=_harty_extent(start, initial_image),
        zorder=4,
    )
    ax.set_title('Steps: 0   (arrow keys to move)')

    def redraw(new_state):
        img = load_harty_image(new_state.facing)
        harty_artist.set_data(img)
        harty_artist.set_extent(_harty_extent(new_state.position, img))
        if new_state.won:
            ax.set_title(f'You found the treasure in {new_state.steps_taken} steps! (close window to exit)')
        else:
            ax.set_title(f'Steps: {new_state.steps_taken}   (arrow keys to move)')
        fig.canvas.draw_idle()

    def on_key(event):
        if event.key == 'q':
            plt.close(fig)
            return
        if event.key not in ACTIONS:
            return
        new_state = handle_key(state_ref['current'], event.key)
        state_ref['current'] = new_state
        redraw(new_state)

    fig.canvas.mpl_connect('key_press_event', on_key)

    plt.show(block=True)
    return state_ref['current']


def _draw_frame(state, figsize=(5, 5)):
    """Render the current frame and display it via IPython.display.

    `display(fig)` + `plt.close(fig)` works reliably inside a widgets.Output
    context in every front end (VS Code, Jupyter classic, JupyterLab) without
    needing a special backend.
    """
    fig, ax = plt.subplots(figsize=figsize)
    draw_maze(ax, state.maze)
    overlay_image_at_cell(ax, load_treasure_image(), state.treasure)

    harty_img = load_harty_image(state.facing)
    ax.imshow(harty_img, extent=_harty_extent(state.position, harty_img), zorder=4)

    if state.won:
        ax.set_title(f'You found the treasure in {state.steps_taken} steps!')
    else:
        ax.set_title(f'Steps: {state.steps_taken}')

    display(fig)
    plt.close(fig)


def launch_game(maze, treasure, start, figsize=(5, 5)):
    """Open a clickable arrow-button game. Returns (ui_widget, get_state).

    Display the widget by making it the last expression of the cell:
        ui, get_state = launch_game(MAZE, TREASURE, HARTY)
        ui
    """
    initial_state = PlayState(
        position=start,
        facing='idle',
        treasure=treasure,
        maze=maze,
    )
    state_ref = {'current': initial_state}

    output = widgets.Output()

    def refresh():
        with output:
            clear_output(wait=True)
            _draw_frame(state_ref['current'], figsize=figsize)

    refresh()  # initial draw

    def make_button(symbol, action):
        btn = widgets.Button(
            description=symbol,
            layout=widgets.Layout(width='50px', height='50px'),
        )

        def on_click(_b):
            state_ref['current'] = handle_key(state_ref['current'], action)
            refresh()

        btn.on_click(on_click)
        return btn

    up_btn = make_button('↑', 'up')
    down_btn = make_button('↓', 'down')
    left_btn = make_button('←', 'left')
    right_btn = make_button('→', 'right')

    reset_btn = widgets.Button(
        description='Reset',
        layout=widgets.Layout(width='80px', height='30px'),
    )

    def on_reset(_b):
        state_ref['current'] = replace(initial_state)
        refresh()

    reset_btn.on_click(on_reset)

    spacer = widgets.Label('', layout=widgets.Layout(width='50px'))
    arrow_grid = widgets.VBox([
        widgets.HBox([spacer, up_btn, spacer]),
        widgets.HBox([left_btn, down_btn, right_btn]),
    ])

    ui = widgets.VBox([
        output,
        arrow_grid,
        reset_btn,
    ])

    def get_state():
        return state_ref['current']

    return ui, get_state
