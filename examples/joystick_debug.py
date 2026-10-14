"""
Joystick debug - run this first with a new controller.

Press buttons, move sticks and press the D-pad. The window shows every
button, axis and hat, and the console prints pygame's numbers.
Write down the numbers, then use them with bind_button / bind_axis / bind_hat
(see joystick_move.py).
"""
import os
import sys
import pygame as pg

# Lets this example find the library one folder up.
# In your own game, just put PygameTkinterGUITools.py next to your game file.
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from PygameTkinterGUITools import JoystickManager

# ---------- Settings ----------
WIDTH, HEIGHT = 800, 600
FPS = 60


def init_pygame():
    """Set up pygame, the window, the clock and all game objects."""
    global screen, clock, pad
    pg.init()
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    pg.display.set_caption("Joystick debug")
    clock = pg.time.Clock()

    # >>> Create objects here (after pg.init)
    pad = JoystickManager(0, debug=True)   # debug=True prints every change


def handle_inputs():
    """Check every event: quitting, keys, mouse, controllers."""
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            sys.exit()

        # >>> Objects that react to events go here
        pad.handle_event(event)            # also handles plug / unplug


def update(tick):
    """Move, animate and check things."""
    # >>> Objects with update go here
    pad.update(tick)


def draw_game():
    """Draw everything, then show it."""
    screen.fill((30, 30, 30))

    # >>> Objects with draw go here
    pad.draw_debug(screen, 20, 20)

    pg.display.flip()


# ---------- Main program ----------
init_pygame()
while True:
    tick = clock.tick(FPS)   # tick = milliseconds since the last frame (used for animation)
    handle_inputs()
    update(tick)
    draw_game()
