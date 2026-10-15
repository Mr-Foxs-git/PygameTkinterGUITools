"""
Button example - clickable buttons.

Shows: command= (the function to run), hover colour, border, rounded
corners, shadow, and changing a button with config().
"""
import os
import sys
import pygame as pg

# Lets this example find the library one folder up.
# In your own game, just put PygameTkinterGUITools.py next to your game file.
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from PygameTkinterGUITools import *


from PygameTkinterGUITools import Button, Label

# ---------- Settings ----------
WIDTH, HEIGHT = 800, 600
FPS = 60
BACKGROUNDS = [(30, 30, 30), (30, 60, 90), (80, 40, 60)]


# Functions for the buttons to run (no brackets when you give them to command=)
def add_click():
    global clicks
    clicks += 1
    message.config(text=f"Clicked {clicks} times")


def change_background():
    global background_index
    background_index = (background_index + 1) % len(BACKGROUNDS)


def toggle_sound():
    global sound_on
    sound_on = not sound_on
    sound_button.config(text="Sound: ON" if sound_on else "Sound: OFF",
                        bg=(80, 200, 120) if sound_on else (200, 80, 80))


def init_pygame():
    """Set up pygame, the window, the clock and all game objects."""
    global screen, clock, clicks, background_index, sound_on
    global click_button, colour_button, sound_button, message
    pg.init()
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    pg.display.set_caption("Button example")
    clock = pg.time.Clock()

    # >>> Create objects here (after pg.init)
    clicks = 0
    background_index = 0
    sound_on = True

    # A plain button
    click_button = Button(50, 100, 200, 60, "Click me", command=add_click)

    # Rounded corners, border and shadow
    colour_button = Button(300, 100, 220, 60, "Background", command=change_background,
                           bg=(250, 200, 60), hover_bg=(255, 230, 120),
                           border_radius=15, border_color=(0, 0, 0), border_width=3,
                           shadow=True)

    # A button that changes itself when clicked
    sound_button = Button(WIDTH // 2, 300, 220, 60, "Sound: ON", command=toggle_sound,
                          bg=(80, 200, 120), hover_bg=(150, 230, 170), center=True)

    message = Label(50, 450, "Clicked 0 times", font_size=36)


def handle_inputs():
    """Check every event: quitting, keys, mouse, controllers."""
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            sys.exit()

        # >>> Objects that react to events go here
        click_button.handle_event(event)
        colour_button.handle_event(event)
        sound_button.handle_event(event)


def update(tick):
    """Move, animate and check things."""
    # >>> Objects with update(tick) go here (buttons don't need updating)
    pass


def draw_game():
    """Draw everything, then show it."""
    screen.fill(BACKGROUNDS[background_index])

    # >>> Objects with draw(screen) go here
    click_button.draw(screen)
    colour_button.draw(screen)
    sound_button.draw(screen)
    message.draw(screen)

    pg.display.flip()


# ---------- Main program ----------
init_pygame()
while True:
    tick = clock.tick(FPS)   # tick = milliseconds since the last frame (used for animation)
    handle_inputs()
    update(tick)
    draw_game()
