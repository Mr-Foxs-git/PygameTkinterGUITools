"""
TextBox example - typing text.

Shows: TextBox with a label, on_enter= (runs when Enter is pressed),
get() and clear(). Click the box, type your name, press Enter.
"""
import os
import sys
import pygame as pg

# Lets this example find the library one folder up.
# In your own game, just put PygameTkinterGUITools.py next to your game file.
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from PygameTkinterGUITools import TextBox, Button, Label

# ---------- Settings ----------
WIDTH, HEIGHT = 800, 600
FPS = 60


def say_hello():
    name = name_box.get()              # get the typed text
    if name:
        greeting.config(text=f"Hello, {name}!")
    name_box.clear()                   # empty the box ready for the next name


def init_pygame():
    """Set up pygame, the window, the clock and all game objects."""
    global screen, clock, name_box, age_box, ok_button, greeting
    pg.init()
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    pg.display.set_caption("TextBox example")
    clock = pg.time.Clock()

    # >>> Create objects here (after pg.init)
    name_box = TextBox(50, 100, max_chars=15, label="Name:", on_enter=say_hello)
    age_box = TextBox(50, 180, max_chars=3, label="Age (label on top):",
                      label_position="top")
    ok_button = Button(400, 95, 100, 40, "OK", command=say_hello)
    greeting = Label(50, 300, "Type your name and press Enter", font_size=36)


def handle_inputs():
    """Check every event: quitting, keys, mouse, controllers."""
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            sys.exit()

        # >>> Objects that react to events go here
        name_box.handle_event(event)
        age_box.handle_event(event)
        ok_button.handle_event(event)


def update(tick):
    """Move, animate and check things."""
    # >>> Objects with update(tick) go here
    name_box.update(tick)              # makes the cursor blink
    age_box.update(tick)


def draw_game():
    """Draw everything, then show it."""
    screen.fill((30, 30, 30))

    # >>> Objects with draw(screen) go here
    name_box.draw(screen)
    age_box.draw(screen)
    ok_button.draw(screen)
    greeting.draw(screen)

    pg.display.flip()


# ---------- Main program ----------
init_pygame()
while True:
    tick = clock.tick(FPS)   # tick = milliseconds since the last frame (used for animation)
    handle_inputs()
    update(tick)
    draw_game()
