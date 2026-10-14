"""
Scale and Spinbox example - choosing numbers.

Shows: Scale (slider) and Spinbox (arrows) sharing IntVars with Labels.
The circle's size and number of copies come from the widgets.
"""
import os
import sys
import pygame as pg

# Lets this example find the library one folder up.
# In your own game, just put PygameTkinterGUITools.py next to your game file.
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from PygameTkinterGUITools import Scale, Spinbox, Label, IntVar, StringVar

# ---------- Settings ----------
WIDTH, HEIGHT = 800, 600
FPS = 60
COLOURS = {"Red": (230, 70, 70), "Green": (70, 200, 100), "Blue": (80, 140, 255)}


def init_pygame():
    """Set up pygame, the window, the clock and all game objects."""
    global screen, clock, size, copies, colour, widgets
    pg.init()
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    pg.display.set_caption("Scale and Spinbox example")
    clock = pg.time.Clock()

    # >>> Create objects here (after pg.init)
    size = IntVar(40)
    copies = IntVar(3)
    colour = StringVar("Blue")

    widgets = [
        Scale(50, 50, from_=10, to=100, length=300, variable=size, label="Size"),
        Scale(420, 50, from_=1, to=8, length=150, orient="vertical", variable=copies,
              label="Copies"),
        Label(50, 140, "Copies:"),
        Spinbox(150, 135, from_=1, to=8, variable=copies),     # same variable as the slider
        Label(50, 190, "Colour:"),
        Spinbox(150, 185, values=["Red", "Green", "Blue"], variable=colour, wrap=True),
        Label(50, 240, "Size is", fg=(180, 180, 180)),
        Label(140, 240, textvariable=size, fg=(255, 220, 0)),  # shows the variable
    ]


def handle_inputs():
    """Check every event: quitting, keys, mouse, controllers."""
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            sys.exit()

        # >>> Objects that react to events go here
        for widget in widgets:
            widget.handle_event(event)


def update(tick):
    """Move, animate and check things."""
    # >>> Objects with update(tick) go here
    pass


def draw_game():
    """Draw everything, then show it."""
    screen.fill((30, 30, 30))

    # >>> Objects with draw(screen) go here
    for widget in widgets:
        widget.draw(screen)

    # Use the values
    for i in range(copies.get()):
        x = 80 + i * (WIDTH - 160) // max(1, copies.get() - 1) if copies.get() > 1 else WIDTH // 2
        pg.draw.circle(screen, COLOURS[colour.get()], (x, 430), size.get() // 2)

    pg.display.flip()


# ---------- Main program ----------
init_pygame()
while True:
    tick = clock.tick(FPS)   # tick = milliseconds since the last frame (used for animation)
    handle_inputs()
    update(tick)
    draw_game()
