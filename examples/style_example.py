"""
Style example - changing how every widget looks.

Shows: Style().theme_use() ("light", "dark", "retro"), style.configure()
for every Button, a named style ("Danger.Button"), and image skins
(pictures for a Button and a Checkbutton). Click the themes to switch.
"""
import os
import sys
import pygame as pg

# Lets this example find the library one folder up.
# In your own game, just put PygameTkinterGUITools.py next to your game file.
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from PygameTkinterGUITools import (Style, Button, Checkbutton, Radiobutton, Scale,
                                   Label, TextBox, Frame, StringVar, BooleanVar)

# Folder with the images for the examples
ASSETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")

# ---------- Settings ----------
WIDTH, HEIGHT = 800, 600
FPS = 60


def change_theme():
    style.theme_use(theme.get())     # every widget changes straight away


def init_pygame():
    """Set up pygame, the window, the clock and all game objects."""
    global screen, clock, style, theme, panel, widgets
    pg.init()
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    pg.display.set_caption("Style example")
    clock = pg.time.Clock()

    # >>> Create objects here (after pg.init and set_mode)
    style = Style()
    style.configure("Button", border_radius=10)               # every Button
    style.configure("Danger.Button", bg=(200, 50, 50),        # only Buttons with
                    hover_bg=(240, 80, 80), fg=(255, 255, 255))  # style="Danger.Button"

    theme = StringVar("light")
    panel = Frame(40, 40, 330, 520)
    panel.add(
        Label(0, 0, "Theme", font_size=36),
        Radiobutton(0, 50, "light", variable=theme, value="light", command=change_theme),
        Radiobutton(0, 85, "dark", variable=theme, value="dark", command=change_theme),
        Radiobutton(0, 120, "retro", variable=theme, value="retro", command=change_theme),
        Button(0, 180, 200, 50, "Normal button"),
        Button(0, 245, 200, 50, "Delete save", style="Danger.Button"),
        Checkbutton(0, 320, "Sound", variable=BooleanVar(True)),
        Scale(0, 360, length=280, label="Volume"),
        TextBox(0, 440, max_chars=12, label="Name:"),
    )

    # Image skins: your own pictures instead of drawn shapes (they are scaled to fit)
    widgets = [
        Label(420, 40, "Image skins", font_size=36),
        Button(420, 100, 240, 60, "Play", fg=(255, 255, 255),
               image=os.path.join(ASSETS, "button.png"),
               hover_image=os.path.join(ASSETS, "button_hover.png")),
        Checkbutton(420, 190, "Pixel tick box", variable=BooleanVar(True), box_size=32,
                    image=os.path.join(ASSETS, "check_off.png"),
                    selected_image=os.path.join(ASSETS, "check_on.png")),
    ]


def handle_inputs():
    """Check every event: quitting, keys, mouse, controllers."""
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            sys.exit()

        # >>> Objects that react to events go here
        panel.handle_event(event)
        for widget in widgets:
            widget.handle_event(event)


def update(tick):
    """Move, animate and check things."""
    # >>> Objects with update(tick) go here
    panel.update(tick)


def draw_game():
    """Draw everything, then show it."""
    screen.fill((20, 20, 25) if theme.get() != "light" else (30, 30, 30))

    # >>> Objects with draw(screen) go here
    panel.draw(screen)
    for widget in widgets:
        widget.draw(screen)

    pg.display.flip()


# ---------- Main program ----------
init_pygame()
while True:
    tick = clock.tick(FPS)   # tick = milliseconds since the last frame (used for animation)
    handle_inputs()
    update(tick)
    draw_game()
