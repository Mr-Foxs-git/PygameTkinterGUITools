"""
Chain example - things that follow a leader.

Shows four uses of the same Chain object:
  * a worm (drawn links that shrink towards the tail) chasing the mouse
  * party members (real SpriteObjects) following the player, by time delay
  * a train of carriages that turn to face the way they move
  * a fading afterimage trail
Arrow keys move the player. Press SPACE to add a party member,
BACKSPACE to remove one. F1 = debug (link hitboxes).
"""
import os
import sys
import pygame as pg

# Lets this example find the library one folder up.
# In your own game, just put PygameTkinterGUITools.py next to your game file.
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import math
from PygameTkinterGUITools import (Chain, SpriteObject, Animator, KeyboardInput, Label,
                                   Debug)

# ---------- Settings ----------
WIDTH, HEIGHT = 800, 600
FPS = 60
ASSETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")


def make_follower():
    animator = Animator(os.path.join(ASSETS, "ghost_sheet.png"), from_sheet=True,
                        tile_width=32, tile_height=32, rows=1, cols=2, frame_rate=4)
    return SpriteObject(0, 0, animator=animator)


def init_pygame():
    """Set up pygame, the window, the clock and all game objects."""
    global screen, clock, keys, player, party, worm_head, worm, engine, train, trail, time
    pg.init()
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    pg.display.set_caption("Chain example")
    clock = pg.time.Clock()

    # >>> Create objects here (after pg.init)
    keys = KeyboardInput()
    player = SpriteObject(200, 300, 32, 32, bg=(70, 160, 230))
    # Party members follow 300 ms behind each other
    party = Chain(player, segments=[make_follower(), make_follower()], delay_ms=300,
                  rotate=False)
    trail = Chain(player, count=6, spacing=8, size=28, color=(70, 160, 230), fade=True)

    # A worm: drawn links that shrink, following its head
    worm_head = SpriteObject(500, 300, 26, 26, bg=(220, 120, 80))
    worm = Chain(worm_head, count=16, spacing=12, size=24, color=(200, 110, 70), shrink=True)

    # A train going round in a circle: carriages turn to face along the track
    engine = SpriteObject(0, 0, 40, 24, bg=(200, 50, 50))
    carriages = [SpriteObject(0, 0, 36, 20, bg=(90, 90, 200)) for _ in range(4)]
    train = Chain(engine, segments=carriages, spacing=44)
    time = 0


def handle_inputs():
    """Check every event: quitting, keys, mouse, controllers."""
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            sys.exit()

        # >>> Objects that react to events go here
        Debug.handle_event(event)
        keys.handle_event(event)


def update(tick):
    """Move, animate and check things."""
    global time
    # >>> Objects with update(tick) go here
    keys.update(tick)
    time += tick
    speed = 4
    player.move((keys.is_pressed("right") - keys.is_pressed("left")) * speed,
                (keys.is_pressed("down") - keys.is_pressed("up")) * speed)
    if keys.was_pressed("space"):
        party.attach(make_follower())
    if keys.was_pressed("backspace") and party.segments:
        party.detach(party.segments[-1])

    # Worm head chases the mouse
    to_mouse = pg.Vector2(pg.mouse.get_pos()) - pg.Vector2(worm_head.rect.center)
    if to_mouse.length() > 5:
        worm_head.rect.center = pg.Vector2(worm_head.rect.center) + to_mouse.normalize() * 3

    # Engine drives round a circle
    engine.rect.center = (WIDTH // 2 + math.cos(time / 1500) * 220,
                          HEIGHT // 2 + math.sin(time / 1500) * 160)

    party.update(tick)
    trail.update(tick)
    worm.update(tick)
    train.update(tick)


def draw_game():
    """Draw everything, then show it."""
    screen.fill((25, 35, 30))

    # >>> Objects with draw(screen) go here
    pg.draw.ellipse(screen, (60, 70, 60), (WIDTH // 2 - 220, HEIGHT // 2 - 160, 440, 320), 6)
    train.draw(screen)
    engine.draw(screen)
    worm.draw(screen)
    worm_head.draw(screen)
    trail.draw(screen)
    party.draw(screen)
    player.draw(screen)
    Label(10, 10, f"Arrows move. SPACE = add party member ({len(party)}). "
                  f"BACKSPACE = remove. F1 = debug", font_size=22).draw(screen)

    pg.display.flip()


# ---------- Main program ----------
init_pygame()
while True:
    tick = clock.tick(FPS)   # tick = milliseconds since the last frame (used for animation)
    handle_inputs()
    update(tick)
    draw_game()
