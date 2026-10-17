"""
Cursor example - change the mouse pointer.

Shows: a picture crosshair over the play area, a red crosshair while aiming
at the target (Cursor.attach), a hand over buttons, an I-beam over the
text box, and the normal arrow over the side panel and the disabled button.
The buttons switch between the built-in crosshair, the picture, and a
picture drawn by Cursor.draw(). Click the target to score.
F1 = debug view (shows the hotspot - the pixel that clicks).
"""
import os
import sys
import random
import pygame as pg

# Lets this example find the library one folder up.
# In your own game, just put PygameTkinterGUITools.py next to your game file.
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from PygameTkinterGUITools import (Button, Cursor, Debug, Frame, Label, MouseInput,
                                   SpriteObject, TextBox)

# Folder with the images for the examples
ASSETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")

# ---------- Settings ----------
WIDTH, HEIGHT = 800, 600
FPS = 60
PLAY_AREA = pg.Rect(0, 0, 560, HEIGHT)


def use_system_crosshair():
    Cursor.set("crosshair")            # a built-in pointer: no picture needed
    mode_label.config(text="Built-in crosshair")


def use_picture():
    Cursor.set("aim")                  # our own picture (added in init_pygame)
    mode_label.config(text="Picture crosshair")


def use_drawn_picture():
    Cursor.set("aim_drawn")            # the same picture, drawn by Cursor.draw()
    mode_label.config(text="Drawn picture")


def init_pygame():
    """Set up pygame, the window, the clock and all game objects."""
    global screen, clock, mouse, target, panel, mode_label, score_label, score
    pg.init()
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    pg.display.set_caption("Cursor example")
    clock = pg.time.Clock()

    # >>> Create objects here (after pg.init)
    mouse = MouseInput()
    mouse.bind("shoot", "left")

    # Pictures for the pointer. The hotspot is the pixel that does the
    # clicking: the middle of a crosshair, the fingertip of the hand.
    Cursor.add("aim", os.path.join(ASSETS, "crosshair.png"), hotspot="center")
    Cursor.add("aim_red", os.path.join(ASSETS, "crosshair_red.png"), hotspot="center")
    Cursor.add("aim_drawn", os.path.join(ASSETS, "crosshair.png"), hotspot="center",
               drawn=True)
    Cursor.add("pointing_hand", os.path.join(ASSETS, "hand.png"), hotspot=(11, 1))
    Cursor.set("aim")                  # the normal pointer for this game

    # Something to aim at: the crosshair turns red while it is over it
    target = SpriteObject(250, 250, 60, 60, bg=(230, 160, 40))
    Cursor.attach(target, "aim_red")

    # The side panel shows the normal arrow (cursor="arrow").
    # Widgets inside it can choose their own pointer.
    panel = Frame(560, 0, 240, HEIGHT, bg=(45, 45, 60), cursor="arrow")
    mode_label = Label(10, 20, "Picture crosshair", font_size=26)
    score_label = Label(10, 60, "Score: 0", font_size=26)
    panel.add(mode_label, score_label,
              Button(10, 110, 200, 44, "Built-in crosshair", command=use_system_crosshair,
                     cursor="hand"),
              Button(10, 165, 200, 44, "Picture", command=use_picture, cursor="hand"),
              Button(10, 220, 200, 44, "Drawn picture", command=use_drawn_picture,
                     cursor="pointing_hand"),
              # Disabled widgets keep the panel's arrow (they can't be clicked)
              Button(10, 275, 200, 44, "Locked", state="disabled", cursor="hand"),
              Label(10, 345, "Your name:"),
              TextBox(10, 375, max_chars=12, cursor="text"),
              Label(10, 540, "F1 = show the hotspot", font_size=20))
    score = 0


def handle_inputs():
    """Check every event: quitting, keys, mouse, controllers."""
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            sys.exit()

        # >>> Objects that react to events go here
        Debug.handle_event(event)      # F1
        mouse.handle_event(event)
        panel.handle_event(event)


def update(tick):
    """Move, animate and check things."""
    global score
    # >>> Objects with update(tick) go here
    mouse.update(tick)                 # always first: works out pressed / released
    panel.update(tick)
    Cursor.update(tick)                # picks the pointer for whatever the mouse is over

    # Click the target: score, and it jumps somewhere else
    if mouse.was_pressed("shoot") and target.rect.collidepoint(mouse.pos):
        score += 1
        score_label.config(text=f"Score: {score}")
        target.rect.topleft = (random.randint(20, PLAY_AREA.width - 80),
                               random.randint(20, PLAY_AREA.height - 80))


def draw_game():
    """Draw everything, then show it."""
    screen.fill((30, 60, 40))

    # >>> Objects with draw(screen) go here
    target.draw(screen)
    panel.draw(screen)
    Cursor.draw(screen)                # LAST, so a drawn pointer is on top

    pg.display.flip()


# ---------- Main program ----------
init_pygame()
while True:
    tick = clock.tick(FPS)   # tick = milliseconds since the last frame (used for animation)
    handle_inputs()
    update(tick)
    draw_game()
