"""
Camera example - a world bigger than the screen.

Shows: Camera.follow(), camera.update(tick), drawing with
draw(screen, camera), and screen_to_world() for the mouse.
Arrow keys to move. The camera smoothly follows the player.
"""
import os
import sys
import pygame as pg

# Lets this example find the library one folder up.
# In your own game, just put PygameTkinterGUITools.py next to your game file.
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import random
from PygameTkinterGUITools import SpriteObject, Camera, Label

# Folder with the images and maps for the examples
ASSETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")

# ---------- Settings ----------
WIDTH, HEIGHT = 800, 600
WORLD_WIDTH, WORLD_HEIGHT = 2400, 1800     # the world is 3 x 3 screens
FPS = 60
SPEED = 400


def init_pygame():
    """Set up pygame, the window, the clock and all game objects."""
    global screen, clock, player, rocks, camera, info
    pg.init()
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    pg.display.set_caption("Camera example")
    clock = pg.time.Clock()

    # >>> Create objects here (after pg.init and set_mode)
    player = SpriteObject(WORLD_WIDTH // 2, WORLD_HEIGHT // 2, 40, 40, bg=(70, 160, 230))

    random.seed(1)
    rocks = [SpriteObject(random.randint(0, WORLD_WIDTH), random.randint(0, WORLD_HEIGHT),
                          random.randint(20, 80), random.randint(20, 80), bg=(120, 110, 100))
             for _ in range(80)]

    camera = Camera(WORLD_WIDTH, WORLD_HEIGHT, (WIDTH, HEIGHT), smooth=0.1)
    camera.follow(player)
    info = Label(10, 10, "", bg=(0, 0, 0))


def handle_inputs():
    """Check every event: quitting, keys, mouse, controllers."""
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            sys.exit()

        # >>> Objects that react to events go here
        # (movement uses held keys, which are checked in update)


def update(tick):
    """Move, animate and check things."""
    keys = pg.key.get_pressed()
    step = int(SPEED * tick / 1000)
    if keys[pg.K_LEFT]:
        player.move(-step, 0)
    if keys[pg.K_RIGHT]:
        player.move(step, 0)
    if keys[pg.K_UP]:
        player.move(0, -step)
    if keys[pg.K_DOWN]:
        player.move(0, step)
    player.rect.clamp_ip(pg.Rect(0, 0, WORLD_WIDTH, WORLD_HEIGHT))   # stay in the world

    # >>> Objects with update(tick) go here
    camera.update(tick)

    mouse_world = camera.screen_to_world(pg.mouse.get_pos())
    info.config(text=f"Player at {player.rect.topleft}   "
                     f"Mouse in world: ({int(mouse_world[0])}, {int(mouse_world[1])})")


def draw_game():
    """Draw everything, then show it."""
    screen.fill((60, 90, 60))

    # >>> Objects with draw(screen) go here
    # World objects are drawn through the camera
    for rock in rocks:
        rock.draw(screen, camera)
    player.draw(screen, camera)

    # Screen objects (like labels) are drawn normally, so they don't scroll
    info.draw(screen)

    pg.display.flip()


# ---------- Main program ----------
init_pygame()
while True:
    tick = clock.tick(FPS)   # tick = milliseconds since the last frame (used for animation)
    handle_inputs()
    update(tick)
    draw_game()
