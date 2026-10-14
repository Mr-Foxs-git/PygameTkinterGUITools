"""
Label example - showing text.

Shows: Label(x, y, text), changing text with config(), center=True,
and draw_text() for quick one-off text.
Press SPACE to add points.
"""
import os
import sys
import pygame as pg

# Lets this example find the library one folder up.
# In your own game, just put PygameTkinterGUITools.py next to your game file.
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from PygameTkinterGUITools import Label, draw_text

# ---------- Settings ----------
WIDTH, HEIGHT = 800, 600
FPS = 60


def init_pygame():
    """Set up pygame, the window, the clock and all game objects."""
    global screen, clock, title, score_label, time_label, score, time_played
    pg.init()
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    pg.display.set_caption("Label example")
    clock = pg.time.Clock()

    # >>> Create objects here (after pg.init)
    title = Label(WIDTH // 2, 60, "Label Example", font_size=60, center=True)
    score_label = Label(20, 150, "Score: 0", fg=(255, 220, 0), font_size=40)
    time_label = Label(20, 200, "Time: 0.0", fg=(0, 0, 0), bg=(200, 200, 200))
    score = 0
    time_played = 0


def handle_inputs():
    """Check every event: quitting, keys, mouse, controllers."""
    global score
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            sys.exit()

        # >>> Objects that react to events go here
        if event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
            score += 10
            score_label.config(text=f"Score: {score}")     # change the text


def update(tick):
    """Move, animate and check things."""
    global time_played
    # >>> Objects with update(tick) go here
    time_played += tick                                     # tick is in milliseconds
    time_label.config(text=f"Time: {time_played / 1000:.1f}")


def draw_game():
    """Draw everything, then show it."""
    screen.fill((30, 30, 30))

    # >>> Objects with draw(screen) go here
    title.draw(screen)
    score_label.draw(screen)
    time_label.draw(screen)

    # draw_text() is handy for text you don't need to keep or change
    draw_text(screen, "Press SPACE to score", WIDTH // 2, HEIGHT - 40, center=True)

    pg.display.flip()


# ---------- Main program ----------
init_pygame()
while True:
    tick = clock.tick(FPS)   # tick = milliseconds since the last frame (used for animation)
    handle_inputs()
    update(tick)
    draw_game()
