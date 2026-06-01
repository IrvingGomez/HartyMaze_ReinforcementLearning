"""Play mode: Harty driven by the arrow keys in a popup window.

Pure logic (PlayState + handle_key) lives at the top so it can be unit-tested.
`launch_game_window` forces the TkAgg matplotlib backend, opens a real OS
window, and registers a key_press_event handler. It blocks until the player
closes the window and returns the final PlayState.

Holes and portals are optional; both default to empty. Stepping on a hole
sets `dead`; stepping on the treasure sets `won`. Portals teleport once per
move.
"""

from dataclasses import dataclass, field, replace
from typing import Any

from animation import _harty_extent
from environment import ACTIONS, apply_portal, next_state
from maze_renderer import draw_maze
from visualization import (
    load_harty_image,
    load_treasure_image,
    overlay_holes,
    overlay_image_at_cell,
    overlay_portals,
)


@dataclass
class PlayState:
    """Snapshot of the game. `handle_key` returns a new instance on each step."""

    position: tuple
    facing: str
    treasure: tuple
    maze: Any = field(repr=False)
    holes: tuple = ()
    portals: tuple = ()
    steps_taken: int = 0
    won: bool = False
    dead: bool = False


def handle_key(state, action):
    """Pure step function: given a state and an action, return the next state.

    Unknown actions and post-terminal key presses are no-ops. Walls block
    movement but the facing still updates, so Harty turns even when he cannot
    walk. Portals teleport once per step. Stepping onto a hole sets `dead`;
    stepping onto the treasure sets `won`.
    """
    if state.won or state.dead:
        return state
    if action not in ACTIONS:
        return state

    new_position = next_state(state.position, action, state.maze)
    new_position = apply_portal(new_position, state.portals)
    won = new_position == state.treasure
    dead = new_position in tuple(state.holes)

    return replace(
        state,
        position=new_position,
        facing=action,
        steps_taken=state.steps_taken + 1,
        won=won,
        dead=dead,
    )


def is_won(state):
    return state.position == state.treasure


def launch_game_window(maze, treasure, start, holes=(), portals=(), figsize=(7, 7)):
    """Open a real OS window where Harty is controlled by the arrow keys.

    Forces matplotlib to use the TkAgg backend (bundled with Python on
    Windows/Mac/Linux), opens a window, and blocks until the player closes
    it. Returns the final PlayState.

    Call from a notebook cell or a standalone script:
        state = launch_game_window(MAZE, TREASURE, HARTY, holes=HOLES, portals=PORTALS)
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
            holes=tuple(holes),
            portals=tuple(portals),
        )
    }

    fig, ax = plt.subplots(figsize=figsize)
    fig.canvas.manager.set_window_title('Harty Maze -- arrow keys to move, q to quit')

    draw_maze(ax, maze)
    overlay_holes(ax, holes)
    overlay_portals(ax, portals)
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
        elif new_state.dead:
            ax.set_title(f'Game over -- fell in a hole after {new_state.steps_taken} steps. (close window to exit)')
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


def launch_game_widget(maze, treasure, start, holes=(), portals=(), figsize=(7, 7)):
    """In-notebook play mode using ipywidgets buttons. Works in Colab and Jupyter.

    Renders the maze inside an Output widget and exposes Up/Down/Left/Right
    plus Reset buttons. Each click advances the game one step. Returns the
    `state_ref` dict; read `state_ref['current']` for the live PlayState.
    """
    import ipywidgets as widgets
    from IPython.display import display
    import matplotlib.pyplot as plt

    def fresh_state():
        return PlayState(
            position=start,
            facing='idle',
            treasure=treasure,
            maze=maze,
            holes=tuple(holes),
            portals=tuple(portals),
        )

    state_ref = {'current': fresh_state()}
    out = widgets.Output()

    def render():
        with out:
            out.clear_output(wait=True)
            fig, ax = plt.subplots(figsize=figsize)
            draw_maze(ax, maze)
            overlay_holes(ax, holes)
            overlay_portals(ax, portals)
            overlay_image_at_cell(ax, load_treasure_image(), treasure)
            s = state_ref['current']
            img = load_harty_image(s.facing)
            ax.imshow(img, extent=_harty_extent(s.position, img), zorder=4)
            if s.won:
                ax.set_title(f'You found the treasure in {s.steps_taken} steps!')
            elif s.dead:
                ax.set_title(f'Game over -- fell in a hole after {s.steps_taken} steps.')
            else:
                ax.set_title(f'Steps: {s.steps_taken}   (click buttons to move)')
            plt.show()

    def step(action):
        state_ref['current'] = handle_key(state_ref['current'], action)
        render()

    def reset(_):
        state_ref['current'] = fresh_state()
        render()

    btn_up = widgets.Button(description='Up', layout=widgets.Layout(width='80px'))
    btn_down = widgets.Button(description='Down', layout=widgets.Layout(width='80px'))
    btn_left = widgets.Button(description='Left', layout=widgets.Layout(width='80px'))
    btn_right = widgets.Button(description='Right', layout=widgets.Layout(width='80px'))
    btn_reset = widgets.Button(description='Reset', button_style='warning',
                               layout=widgets.Layout(width='80px'))

    btn_up.on_click(lambda _: step('up'))
    btn_down.on_click(lambda _: step('down'))
    btn_left.on_click(lambda _: step('left'))
    btn_right.on_click(lambda _: step('right'))
    btn_reset.on_click(reset)

    spacer = widgets.Label(value='', layout=widgets.Layout(width='80px'))
    row1 = widgets.HBox([spacer, btn_up, spacer])
    row2 = widgets.HBox([btn_left, btn_down, btn_right])
    row3 = widgets.HBox([spacer, btn_reset, spacer])
    controls = widgets.VBox([row1, row2, row3])

    display(widgets.HBox([out, controls]))
    render()
    return state_ref
