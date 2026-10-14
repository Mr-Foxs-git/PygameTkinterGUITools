"""
Progressbar example - health, energy and loading bars.

Shows: Progressbar with value / step(), changing bar_color, show_text,
a vertical bar, a picture bar (hearts) and an "indeterminate" loading bar.
H = get hurt, J = heal, hold SPACE to use energy.
"""
import os
import sys
import pygame as pg

# Lets this example find the library one folder up.
# In your own game, just put PygameTkinterGUITools.py next to your game file.
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from PygameTkinterGUITools import Progressbar, Label

# Folder with the images for the examples
ASSETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")

# ---------- Settings ----------
WIDTH, HEIGHT = 800, 600
FPS = 60


def init_pygame():
    """Set up pygame, the window, the clock and all game objects."""
    global screen, clock, health, energy, hearts, loading, help_text
    pg.init()
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    pg.display.set_caption("Progressbar example")
    clock = pg.time.Clock()

    # >>> Create objects here (after pg.init and set_mode)
    health = Progressbar(50, 80, length=300, thickness=26, maximum=100, value=100,
                         bar_color=(80, 200, 120), show_text=True, border_radius=6)
    energy = Progressbar(450, 60, length=200, thickness=24, orient="vertical",
                         maximum=100, value=100, bar_color=(250, 200, 60))
    hearts = Progressbar(50, 160, length=270, thickness=48, maximum=5, value=5,
                         bar_image=os.path.join(ASSETS, "hearts_full.png"),
                         trough_image=os.path.join(ASSETS, "hearts_empty.png"))
    loading = Progressbar(50, 480, length=500, thickness=16, mode="indeterminate")
    help_text = Label(50, 20, "H = hurt   J = heal   hold SPACE = use energy")


def handle_inputs():
    """Check every event: quitting, keys, mouse, controllers."""
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            sys.exit()

        # >>> Objects that react to events go here
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_h:
                health.step(-15)            # step() adds; negative takes away
                hearts.step(-1)
            if event.key == pg.K_j:
                health.step(15)
                hearts.step(1)


def update(tick):
    """Move, animate and check things."""
    # Energy runs down while SPACE is held, and slowly comes back
    if pg.key.get_pressed()[pg.K_SPACE]:
        energy.step(-60 * tick / 1000)
    else:
        energy.step(20 * tick / 1000)

    # Health bar changes colour when low
    if health.value < 30:
        health.config(bar_color=(230, 60, 60))
    elif health.value < 60:
        health.config(bar_color=(240, 180, 50))
    else:
        health.config(bar_color=(80, 200, 120))

    # >>> Objects with update(tick) go here
    loading.update(tick)                    # moves the "indeterminate" block


def draw_game():
    """Draw everything, then show it."""
    screen.fill((30, 30, 30))

    # >>> Objects with draw(screen) go here
    help_text.draw(screen)
    Label(50, 55, "Health").draw(screen)
    health.draw(screen)
    hearts.draw(screen)
    Label(440, 30, "Energy").draw(screen)
    energy.draw(screen)
    Label(50, 450, "Loading...").draw(screen)
    loading.draw(screen)

    pg.display.flip()


# ---------- Main program ----------
init_pygame()
while True:
    tick = clock.tick(FPS)   # tick = milliseconds since the last frame (used for animation)
    handle_inputs()
    update(tick)
    draw_game()
