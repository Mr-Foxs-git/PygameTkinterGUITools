"""
Checkbutton and Radiobutton example - game options.

Shows: BooleanVar / StringVar (shared values, like tkinter),
Checkbutton (tick on / off) and Radiobutton (choose one from a group).
"""
import os
import sys
import pygame as pg

# Lets this example find the library one folder up.
# In your own game, just put PygameTkinterGUITools.py next to your game file.
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from PygameTkinterGUITools import (Checkbutton, Radiobutton, Label, BooleanVar,
                                   StringVar)

# ---------- Settings ----------
WIDTH, HEIGHT = 800, 600
FPS = 60


def show_choices():
    """Runs when any option is clicked (command=)."""
    music = "on" if music_on.get() else "off"
    summary.config(text=f"Music {music}, difficulty {difficulty.get()}")


def init_pygame():
    """Set up pygame, the window, the clock and all game objects."""
    global screen, clock, music_on, show_fps, difficulty, options, summary
    pg.init()
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    pg.display.set_caption("Checkbutton and Radiobutton example")
    clock = pg.time.Clock()

    # >>> Create objects here (after pg.init)
    # Variables hold the values. Widgets that share a variable stay in sync.
    music_on = BooleanVar(True)
    show_fps = BooleanVar(False)
    difficulty = StringVar("Normal")

    options = [
        Label(50, 40, "Options", font_size=48),
        Checkbutton(50, 110, "Music", variable=music_on, command=show_choices),
        Checkbutton(50, 150, "Show FPS", variable=show_fps),

        # Radiobuttons with the SAME variable form a group: only one can be chosen
        Label(50, 220, "Difficulty"),
        Radiobutton(50, 260, "Easy", variable=difficulty, value="Easy", command=show_choices),
        Radiobutton(50, 300, "Normal", variable=difficulty, value="Normal", command=show_choices),
        Radiobutton(50, 340, "Hard", variable=difficulty, value="Hard", command=show_choices),
    ]
    summary = Label(50, 450, "", fg=(255, 220, 0))
    show_choices()


def handle_inputs():
    """Check every event: quitting, keys, mouse, controllers."""
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            sys.exit()

        # >>> Objects that react to events go here
        for widget in options:
            widget.handle_event(event)


def update(tick):
    """Move, animate and check things."""
    # >>> Objects with update(tick) go here
    pass


def draw_game():
    """Draw everything, then show it."""
    screen.fill((30, 30, 30))

    # >>> Objects with draw(screen) go here
    for widget in options:
        widget.draw(screen)
    summary.draw(screen)
    if show_fps.get():                              # read the value any time
        Label(WIDTH - 120, 10, f"FPS: {clock.get_fps():.0f}").draw(screen)

    pg.display.flip()


# ---------- Main program ----------
init_pygame()
while True:
    tick = clock.tick(FPS)   # tick = milliseconds since the last frame (used for animation)
    handle_inputs()
    update(tick)
    draw_game()
