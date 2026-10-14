"""
Animator example - animating a sprite sheet.

Shows: loading a sprite sheet, add_animation(), play(), play_once(),
and flipping the image to face left.
LEFT / RIGHT to walk, SPACE to jump.

The sprite sheet (assets/player_sheet.png) has 4 frames across, 3 rows:
    row 0 = idle, row 1 = walk, row 2 = jump
"""
import os
import sys
import pygame as pg

# Lets this example find the library one folder up.
# In your own game, just put PygameTkinterGUITools.py next to your game file.
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from PygameTkinterGUITools import Animator, Label

# Folder with the images and maps for the examples
ASSETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")

# ---------- Settings ----------
WIDTH, HEIGHT = 800, 600
FPS = 60
SPEED = 250                      # pixels per second


def init_pygame():
    """Set up pygame, the window, the clock and all game objects."""
    global screen, clock, animator, x, facing_left, help_text
    pg.init()
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    pg.display.set_caption("Animator example")
    clock = pg.time.Clock()

    # >>> Create objects here (after pg.init and set_mode)
    animator = Animator(os.path.join(ASSETS, "player_sheet.png"), from_sheet=True,
                        tile_width=32, tile_height=32, rows=3, cols=4,
                        frame_rate=8, scale=4)
    # (row, col) of each frame on the sheet
    animator.add_animation("idle", [(0, 0), (0, 1), (0, 2), (0, 3)])
    animator.add_animation("walk", [(1, 0), (1, 1), (1, 2), (1, 3)])
    animator.add_animation("jump", [(2, 0), (2, 1), (2, 2), (2, 3)])
    animator.play("idle")

    x = WIDTH // 2
    facing_left = False
    help_text = Label(20, 20, "LEFT / RIGHT to walk, SPACE to jump")


def handle_inputs():
    """Check every event: quitting, keys, mouse, controllers."""
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            sys.exit()

        # >>> Objects that react to events go here
        if event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
            animator.play_once("jump")       # plays once, then stops on the last frame


def update(tick):
    """Move, animate and check things."""
    global x, facing_left, image
    keys = pg.key.get_pressed()              # keys being held down
    jumping = animator.current_animation == "jump" and animator.playing

    moving = False
    if keys[pg.K_LEFT]:
        x -= SPEED * tick / 1000
        facing_left = True
        moving = True
    if keys[pg.K_RIGHT]:
        x += SPEED * tick / 1000
        facing_left = False
        moving = True

    if not jumping:
        if moving:
            animator.play("walk")            # does nothing if already walking
        else:
            animator.play("idle")

    # >>> Objects with update(tick) go here
    image = animator.update(tick, flip_x=facing_left)   # returns the frame to draw


def draw_game():
    """Draw everything, then show it."""
    screen.fill((120, 190, 240))
    pg.draw.rect(screen, (90, 170, 80), (0, 450, WIDTH, HEIGHT - 450))   # ground

    # >>> Objects with draw(screen) go here
    screen.blit(image, image.get_rect(midbottom=(x, 455)))
    help_text.draw(screen)

    pg.display.flip()


# ---------- Main program ----------
init_pygame()
while True:
    tick = clock.tick(FPS)   # tick = milliseconds since the last frame (used for animation)
    handle_inputs()
    update(tick)
    draw_game()
