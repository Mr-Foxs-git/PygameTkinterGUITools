"""
SpriteObject example - a player collecting coins.

Shows: SpriteObject with an Animator, move(), collides_with(),
and keeping score with a Label. Arrow keys to move.
"""
import os
import sys
import pygame as pg

# Lets this example find the library one folder up.
# In your own game, just put PygameTkinterGUITools.py next to your game file.
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import random
from PygameTkinterGUITools import SpriteObject, Animator, Label

# Folder with the images and maps for the examples
ASSETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")

# ---------- Settings ----------
WIDTH, HEIGHT = 800, 600
FPS = 60
SPEED = 300                      # pixels per second
NUMBER_OF_COINS = 5


def make_coin():
    """Make a spinning coin somewhere random."""
    spin = Animator(os.path.join(ASSETS, "coin_sheet.png"), from_sheet=True,
                    tile_width=16, tile_height=16, rows=1, cols=4, frame_rate=8, scale=2)
    return SpriteObject(random.randint(0, WIDTH - 32), random.randint(60, HEIGHT - 32),
                        animator=spin)


def init_pygame():
    """Set up pygame, the window, the clock and all game objects."""
    global screen, clock, player, coins, score, score_label
    pg.init()
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    pg.display.set_caption("SpriteObject example")
    clock = pg.time.Clock()

    # >>> Create objects here (after pg.init and set_mode)
    walk = Animator(os.path.join(ASSETS, "player_sheet.png"), from_sheet=True,
                    tile_width=32, tile_height=32, rows=3, cols=4, scale=2)
    walk.add_animation("walk", [(1, 0), (1, 1), (1, 2), (1, 3)])
    walk.play("walk")
    player = SpriteObject(WIDTH // 2, HEIGHT // 2, animator=walk)

    coins = [make_coin() for _ in range(NUMBER_OF_COINS)]
    score = 0
    score_label = Label(20, 20, "Coins: 0", fg=(255, 220, 0), font_size=36)


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
    global score
    # Move the player with the arrow keys
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
    player.rect.clamp_ip(screen.get_rect())       # stay on screen

    # >>> Objects with update(tick) go here
    player.update(tick)
    for coin in coins:
        coin.update(tick)

    # Collect coins (loop over a copy because we change the list)
    for coin in coins[:]:
        if player.collides_with(coin):
            coins.remove(coin)
            coins.append(make_coin())
            score += 1
            score_label.config(text=f"Coins: {score}")


def draw_game():
    """Draw everything, then show it."""
    screen.fill((40, 60, 40))

    # >>> Objects with draw(screen) go here
    for coin in coins:
        coin.draw(screen)
    player.draw(screen)
    score_label.draw(screen)

    pg.display.flip()


# ---------- Main program ----------
init_pygame()
while True:
    tick = clock.tick(FPS)   # tick = milliseconds since the last frame (used for animation)
    handle_inputs()
    update(tick)
    draw_game()
