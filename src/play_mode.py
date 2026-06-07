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
    overlay_rocks,
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
    overlay_rocks(ax, maze)
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
