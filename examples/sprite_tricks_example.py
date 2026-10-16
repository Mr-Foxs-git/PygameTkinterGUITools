"""
Sprite tricks example - turning, chasing and exact hits.

Shows:
  SpriteObject  angle / point_at() / turn()  - the turret aims at the mouse,
                image_faces="up"               the player faces where it walks
                distance_to() / direction_to() - slimes chase you when you are close
                smooth_move=True               - slow slimes still move smoothly
                collides_with_any(..., pixel=True) - round coins are only
                                                 picked up when you REALLY touch them

Arrow keys move. Hold Q or E to spin the turret (otherwise it aims at the mouse).
H shows the hitboxes (rects): see how the coin corners are empty.
"""
import os
import sys
import random
import pygame as pg

# Lets this example find the library one folder up.
# In your own game, just put PygameTkinterGUITools.py next to your game file.
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from PygameTkinterGUITools import SpriteObject, Animator, Label, KeyboardInput

# Folder with the images for the examples
ASSETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")

# ---------- Settings ----------
WIDTH, HEIGHT = 800, 600
FPS = 60
PLAYER_SPEED = 220           # pixels per second
SLIME_SPEED = 25             # very slow: less than 1 pixel a frame!
CHASE_RANGE = 220            # slimes chase you when you are this close
TURRET_SPIN = 180            # degrees per second with Q / E


def arrow_picture(size, colour):
    """A simple arrow that points UP (so image_faces="up")."""
    picture = pg.Surface((size, size), pg.SRCALPHA)
    pg.draw.polygon(picture, colour, [(size // 2, 0), (size, size), (size // 2, size * 3 // 4),
                                      (0, size)])
    return picture


def turret_picture():
    """A round base with a barrel pointing UP."""
    picture = pg.Surface((70, 70), pg.SRCALPHA)
    pg.draw.circle(picture, (150, 150, 170), (35, 35), 20)      # base
    pg.draw.rect(picture, (60, 60, 80), (29, 0, 12, 35))        # barrel (on top)
    return picture


def make_slime(x, y):
    animator = Animator(os.path.join(ASSETS, "slime_sheet.png"), from_sheet=True,
                        tile_width=32, tile_height=32, rows=1, cols=2, frame_rate=4, scale=1.5)
    # smooth_move=True: move() keeps the fractions of a pixel, so a speed of
    # 25 pixels a second (0.4 of a pixel each frame) still moves
    return SpriteObject(x, y, animator=animator, smooth_move=True)


def make_coin():
    x, y = random.randint(40, WIDTH - 80), random.randint(80, HEIGHT - 80)
    return SpriteObject(x, y, 36, 36, image=os.path.join(ASSETS, "coin.png"))


def init_pygame():
    """Set up pygame, the window, the clock and all game objects."""
    global screen, clock, keys, player, turret, slimes, coins, score, score_label
    global help_label, show_hitboxes
    pg.init()
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    pg.display.set_caption("Sprite tricks example")
    clock = pg.time.Clock()

    # >>> Create objects here (after pg.init)
    keys = KeyboardInput()
    keys.bind("spin_left", "q")
    keys.bind("spin_right", "e")
    keys.bind("hitboxes", "h")

    player = SpriteObject(120, 300, image=arrow_picture(36, (80, 180, 255)), image_faces="up")
    turret = SpriteObject(365, 265, image=turret_picture(), image_faces="up")
    slimes = [make_slime(650, 100), make_slime(650, 450), make_slime(100, 500)]
    coins = [make_coin() for _ in range(6)]
    score = 0
    show_hitboxes = False

    score_label = Label(20, 20, "Coins: 0", font_size=32, outline=2)
    help_label = Label(20, HEIGHT - 40, "Arrows move   Q / E spin the turret   H hitboxes",
                       font_size=24, outline=2)


def handle_inputs():
    """Check every event: quitting, keys, mouse, controllers."""
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            sys.exit()

        # >>> Objects that react to events go here
        keys.handle_event(event)


def update(tick):
    """Move, animate and check things."""
    global score, show_hitboxes
    # >>> Objects with update(tick) go here
    keys.update(tick)
    if keys.was_pressed("hitboxes"):
        show_hitboxes = not show_hitboxes

    # Player: move, then face the way it is walking
    dx = keys.is_pressed("right") - keys.is_pressed("left")
    dy = keys.is_pressed("down") - keys.is_pressed("up")
    if dx or dy:
        step = pg.Vector2(dx, dy).normalize() * PLAYER_SPEED * tick / 1000
        player.move(step.x, step.y)
        player.point_at(pg.Vector2(player.rect.center) + step)   # look where you go
    player.rect.clamp_ip(screen.get_rect())

    # Turret: spin with Q / E, otherwise aim at the mouse
    if keys.is_pressed("spin_left"):
        turret.turn(-TURRET_SPIN * tick / 1000)    # minus = anticlockwise
    elif keys.is_pressed("spin_right"):
        turret.turn(TURRET_SPIN * tick / 1000)
    else:
        turret.point_at(pg.mouse.get_pos())

    # Slimes chase you, but only when you are close
    for slime in slimes:
        slime.update(tick)                         # animation
        if slime.distance_to(player) < CHASE_RANGE:
            step = slime.direction_to(player) * SLIME_SPEED * tick / 1000
            slime.move(step.x, step.y)

    # Coins: pixel=True ignores the see-through corners of the round picture
    coin = player.collides_with_any(coins, pixel=True)
    if coin:
        coins.remove(coin)
        coins.append(make_coin())
        score += 1
        score_label.config(text=f"Coins: {score}")


def draw_game():
    """Draw everything, then show it."""
    screen.fill((40, 70, 50))

    # >>> Objects with draw(screen) go here
    for coin in coins:
        coin.draw(screen)
    for slime in slimes:
        # The chase range, so you can see when a slime notices you
        pg.draw.circle(screen, (60, 95, 70), slime.rect.center, CHASE_RANGE, 1)
        slime.draw(screen)
    turret.draw(screen)
    player.draw(screen)

    if show_hitboxes:
        # Only the PICTURE turns - the hitbox (rect) always stays the same
        for sprite in coins + slimes + [turret, player]:
            pg.draw.rect(screen, (255, 255, 0), sprite.rect, 1)

    score_label.draw(screen)
    help_label.draw(screen)
    pg.display.flip()


# ---------- Main program ----------
init_pygame()
while True:
    tick = clock.tick(FPS)   # tick = milliseconds since the last frame (used for animation)
    handle_inputs()
    update(tick)
    draw_game()
