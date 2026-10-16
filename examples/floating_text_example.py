"""
FloatingText example - damage numbers and "+10" pop-ups.

Click the training dummy = hit it (red damage number, big hits in yellow).
Space = pick up the coin ("+10" floats up from it).

FloatingText is a TEXT PARTICLE: Particles looks after it, just like an
explosion. This game has no other particle effects, but it still needs
Particles.update(tick) and Particles.draw(screen) - without them the
text would never move or show up.
"""
import os
import sys
import random
import pygame as pg

# Lets this example find the library one folder up.
# In your own game, just put PygameTkinterGUITools.py next to your game file.
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from PygameTkinterGUITools import (FloatingText, Particles, SpriteObject, Health,
                                   Label, MouseInput, KeyboardInput)

# ---------- Settings ----------
WIDTH, HEIGHT = 800, 600
FPS = 60
ASSETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")


def dummy_knocked_out():
    """Runs when the dummy's health reaches 0."""
    FloatingText(dummy.rect.centerx, dummy.rect.centery, "K.O.!", color="orange",
                 font_size=60, speed=30, duration=1500)
    dummy.health.value = dummy.health.maximum      # back to full for more practice


def init_pygame():
    """Set up pygame, the window, the clock and all game objects."""
    global screen, clock, mouse, keys, dummy, coin, score, help_text, score_label
    pg.init()
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    pg.display.set_caption("FloatingText example")
    clock = pg.time.Clock()

    # >>> Create objects here (after pg.init)
    mouse = MouseInput()
    mouse.bind("hit", "left")
    keys = KeyboardInput()
    keys.bind("collect", "space")

    dummy = SpriteObject(90, 80, 120, 160, bg=(150, 110, 70))   # a plain box
    dummy.health = Health(100, on_death=dummy_knocked_out)

    coin = SpriteObject(500, 300, 48, 48, image=os.path.join(ASSETS, "coin.png"))
    score = 0

    help_text = Label(10, 10, "Click the dummy to hit it.   Space = collect the coin")
    score_label = Label(10, HEIGHT - 40, "Score: 0")


def handle_inputs():
    """Check every event: quitting, keys, mouse, controllers."""
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            sys.exit()

        # >>> Objects that react to events go here
        mouse.handle_event(event)
        keys.handle_event(event)


def update(tick):
    """Move, animate and check things."""
    global score
    mouse.update(tick)
    keys.update(tick)

    # >>> Objects with update(tick) go here
    if mouse.was_pressed("hit") and dummy.rect.collidepoint(mouse.pos):
        damage = random.randint(5, 20)
        x = dummy.rect.centerx + random.randint(-30, 30)   # so numbers don't stack
        if damage >= 17:                                    # a big hit stands out
            FloatingText(x, dummy.rect.top, f"{damage}!", color="yellow", font_size=40)
        else:
            FloatingText(x, dummy.rect.top, damage, color="red")
        dummy.health.damage(damage)

    if keys.was_pressed("collect"):
        score += 10
        score_label.config(text=f"Score: {score}")
        FloatingText(coin.rect.centerx, coin.rect.top, "+10", color="gold", speed=40)
        coin.rect.topleft = (random.randint(300, WIDTH - 60), random.randint(80, HEIGHT - 120))

    Particles.update(tick)          # moves and fades every FloatingText


def draw_game():
    """Draw everything, then show it."""
    screen.fill((40, 60, 40))

    # >>> Objects with draw(screen) go here
    dummy.draw(screen)
    coin.draw(screen)
    help_text.draw(screen)
    score_label.draw(screen)
    Particles.draw(screen)          # draws every FloatingText (last, so it is on top)

    pg.display.flip()


# ---------- Main program ----------
init_pygame()
while True:
    tick = clock.tick(FPS)   # tick = milliseconds since the last frame (used for animation)
    handle_inputs()
    update(tick)
    draw_game()
