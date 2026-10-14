"""
Frame example - grouping widgets.

Shows: Frame.add(), children positioned from the frame's inside corner,
and hiding the whole menu at once. Press M (or the button) to show/hide.
"""
import os
import sys
import pygame as pg

# Lets this example find the library one folder up.
# In your own game, just put PygameTkinterGUITools.py next to your game file.
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from PygameTkinterGUITools import Frame, Label, Button

# ---------- Settings ----------
WIDTH, HEIGHT = 800, 600
FPS = 60


def toggle_menu():
    menu.toggle_visibility()           # hides / shows everything inside it


def start_game():
    status.config(text="Starting game...")


def show_options():
    status.config(text="Options clicked")


def init_pygame():
    """Set up pygame, the window, the clock and all game objects."""
    global screen, clock, menu, menu_button, status
    pg.init()
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    pg.display.set_caption("Frame example")
    clock = pg.time.Clock()

    # >>> Create objects here (after pg.init)
    menu = Frame(250, 120, 300, 300, bg=(50, 50, 80), border_color=(200, 200, 255))

    # These positions are measured from the inside corner of the frame
    menu.add(Label(140, 20, "Main Menu", font_size=40, center=True),
             Button(40, 70, 200, 50, "Start", command=start_game),
             Button(40, 140, 200, 50, "Options", command=show_options),
             Button(40, 210, 200, 50, "Close menu", command=toggle_menu))

    menu_button = Button(20, 20, 160, 40, "Menu (M)", command=toggle_menu)
    status = Label(20, HEIGHT - 50, "")


def handle_inputs():
    """Check every event: quitting, keys, mouse, controllers."""
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            sys.exit()

        # >>> Objects that react to events go here
        if event.type == pg.KEYDOWN and event.key == pg.K_m:
            toggle_menu()
        menu.handle_event(event)       # passes the event to everything inside
        menu_button.handle_event(event)


def update(tick):
    """Move, animate and check things."""
    # >>> Objects with update(tick) go here
    menu.update(tick)                  # updates everything inside


def draw_game():
    """Draw everything, then show it."""
    screen.fill((30, 30, 30))

    # >>> Objects with draw(screen) go here
    menu_button.draw(screen)
    status.draw(screen)
    menu.draw(screen)                  # draws the frame and everything inside

    pg.display.flip()


# ---------- Main program ----------
init_pygame()
while True:
    tick = clock.tick(FPS)   # tick = milliseconds since the last frame (used for animation)
    handle_inputs()
    update(tick)
    draw_game()
