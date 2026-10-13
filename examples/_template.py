"""
Game template - copy this file to start a new game.

Every example in this folder uses this same structure:
    init_pygame()   - set up pygame, the window and your objects
    handle_inputs() - check events (keys, mouse, controllers)
    update(tick)    - move and animate things
    draw_game()     - draw everything on the screen
The ">>>" comments show where each object's code goes.
"""
import os
import sys
import pygame as pg

# Lets this example find the library one folder up.
# In your own game, just put PygameTkinterGUITools.py next to your game file.
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from PygameTkinterGUITools import Button, Label

# ---------- Settings ----------
WIDTH, HEIGHT = 800, 600
FPS = 60


def say_hello():
    print("Hello!")


def init_pygame():
    """Set up pygame, the window, the clock and all game objects."""
    global screen, clock, title, hello_button
    pg.init()
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    pg.display.set_caption("My game")
    clock = pg.time.Clock()

    # >>> Create objects here (after pg.init)
    title = Label("My game", x=20, y=20, font_size=40)
    hello_button = Button(20, 80, 150, 50, "Hello", action=say_hello)


def handle_inputs():
    """Check every event: quitting, keys, mouse, controllers."""
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            sys.exit()

        # >>> Objects that react to events go here
        hello_button.handle_event(event)


def update(tick):
    """Move, animate and check things."""
    # >>> Objects with update(tick) go here (e.g. Animator, TextBox)
    pass


def draw_game():
    """Draw everything, then show it."""
    screen.fill((30, 30, 30))

    # >>> Objects with draw(screen) go here
    title.draw(screen)
    hello_button.draw(screen)

    pg.display.flip()


# ---------- Main program ----------
init_pygame()
while True:
    tick = clock.tick(FPS)   # tick = milliseconds since the last frame (used for animation)
    handle_inputs()
    update(tick)
    draw_game()
