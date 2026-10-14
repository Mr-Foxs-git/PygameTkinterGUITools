"""
Popup example - a pop-up window.

Shows: Popup.show(), widgets inside a popup, the close (X) button,
and stopping the game while the popup is open.
Catch the moving box by clicking it.
"""
import os
import sys
import pygame as pg

# Lets this example find the library one folder up.
# In your own game, just put PygameTkinterGUITools.py next to your game file.
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from PygameTkinterGUITools import Popup, Label, Button

# ---------- Settings ----------
WIDTH, HEIGHT = 800, 600
FPS = 60


def restart():
    global target_speed
    target.topleft = (100, 100)
    target_speed = [4, 3]
    game_over.hide()


def init_pygame():
    """Set up pygame, the window, the clock and all game objects."""
    global screen, clock, target, target_speed, game_over, hint
    pg.init()
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    pg.display.set_caption("Popup example")
    clock = pg.time.Clock()

    # >>> Create objects here (after pg.init)
    target = pg.Rect(100, 100, 60, 60)
    target_speed = [4, 3]
    hint = Label(20, 20, "Click the box!")

    game_over = Popup(WIDTH // 2, HEIGHT // 2, 320, 200, "You caught it!", center=True)
    game_over.add(Label(150, 30, "Well done!", fg=(0, 0, 0), font_size=36, center=True),
                  Button(75, 80, 150, 50, "Play again", command=restart))


def handle_inputs():
    """Check every event: quitting, keys, mouse, controllers."""
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            sys.exit()

        # >>> Objects that react to events go here
        if game_over.visible:
            game_over.handle_event(event)  # only the popup reacts while it is open
        elif event.type == pg.MOUSEBUTTONDOWN and target.collidepoint(event.pos):
            game_over.show()


def update(tick):
    """Move, animate and check things."""
    # >>> Objects with update(tick) go here
    if game_over.visible:
        return                             # game is paused while the popup is open
    target.x += target_speed[0]
    target.y += target_speed[1]
    if target.left < 0 or target.right > WIDTH:
        target_speed[0] = -target_speed[0]
    if target.top < 0 or target.bottom > HEIGHT:
        target_speed[1] = -target_speed[1]


def draw_game():
    """Draw everything, then show it."""
    screen.fill((30, 30, 30))

    # >>> Objects with draw(screen) go here
    pg.draw.rect(screen, (255, 120, 50), target)
    hint.draw(screen)
    game_over.draw(screen)                 # draw popups last so they are on top

    pg.display.flip()


# ---------- Main program ----------
init_pygame()
while True:
    tick = clock.tick(FPS)   # tick = milliseconds since the last frame (used for animation)
    handle_inputs()
    update(tick)
    draw_game()
