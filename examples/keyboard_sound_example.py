"""
KeyboardInput and SoundEffect example - pressed vs held keys.

The most common sound bug: playing a sound while a key is HELD runs it
60 times a second. KeyboardInput tells you exactly what happened:
    was_pressed  -> ONE frame when the key goes down   (jump sound)
    is_pressed   -> EVERY frame while held             (movement, engine loop)
    was_released -> ONE frame when the key comes up

SPACE = jump (one sound per press)
F (hold) = laser, limited by a cooldown
E (hold) = engine sound loops while held
Arrows = walk (random footsteps). Walk into the coin.
"""
import os
import sys
import pygame as pg

# Lets this example find the library one folder up.
# In your own game, just put PygameTkinterGUITools.py next to your game file.
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import random
from PygameTkinterGUITools import (KeyboardInput, SoundEffect, init_audio, Label,
                                   Progressbar)

# ---------- Settings ----------
WIDTH, HEIGHT = 800, 600
FPS = 60
SOUNDS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "sounds")
SPEED = 250


def sound(name):
    return os.path.join(SOUNDS, name)


def init_pygame():
    """Set up pygame, the window, the clock and all game objects."""
    global screen, clock, keys, player, coin, score, status, charge_bar
    global jump_sound, laser_sound, engine_sound, coin_sound, step_sound
    init_audio()                         # BEFORE pg.init(): sounds play with less delay
    pg.init()
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    pg.display.set_caption("KeyboardInput and SoundEffect example")
    clock = pg.time.Clock()

    # >>> Create objects here (after pg.init)
    keys = KeyboardInput()
    keys.bind("jump", "space")
    keys.bind("fire", "f")
    keys.bind("engine", "e")
    keys.bind("left", "left", "a")       # several keys can share a name
    keys.bind("right", "right", "d")
    keys.bind("up", "up", "w")
    keys.bind("down", "down", "s")

    jump_sound = SoundEffect(sound("jump.wav"))
    laser_sound = SoundEffect(sound("laser.wav"), volume=0.6, cooldown=150)  # max ~6 per second
    engine_sound = SoundEffect(sound("engine_loop.wav"), volume=0.5)
    coin_sound = SoundEffect(sound("coin.wav"))
    step_sound = SoundEffect([sound("step1.wav"), sound("step2.wav"), sound("step3.wav")],
                             cooldown=280)                                   # random footstep

    player = pg.Rect(380, 400, 40, 40)
    coin = pg.Rect(600, 300, 24, 24)
    score = 0
    status = Label(20, 20, "")
    charge_bar = Progressbar(20, 60, length=200, thickness=14, maximum=1000)


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
    global score
    # >>> Objects with update(tick) go here
    keys.update(tick)                    # always first: works out pressed / held / released

    # ONE sound per press
    if keys.was_pressed("jump"):
        jump_sound.play()

    # Held: play() every frame is fine because of the cooldown
    if keys.is_pressed("fire"):
        laser_sound.play()

    # Held: loops while True, stops when False (call it every frame)
    engine_sound.play_while(keys.is_pressed("engine"))

    # Walking: footsteps while moving (cooldown spaces them out)
    dx = keys.is_pressed("right") - keys.is_pressed("left")
    dy = keys.is_pressed("down") - keys.is_pressed("up")
    player.x += int(dx * SPEED * tick / 1000)
    player.y += int(dy * SPEED * tick / 1000)
    player.clamp_ip(screen.get_rect())
    if dx or dy:
        step_sound.play()

    # play_on: plays only when the True/False value CHANGES to True
    touching = player.colliderect(coin)
    if coin_sound.play_on(touching):
        score += 1
        coin.topleft = (random.randint(50, WIDTH - 80), random.randint(120, HEIGHT - 80))

    # Show what KeyboardInput sees for SPACE
    status.config(text=f"SPACE  was_pressed: {keys.was_pressed('jump')}   "
                       f"is_pressed: {keys.is_pressed('jump')}   "
                       f"was_released: {keys.was_released('jump')}   "
                       f"held_time: {keys.held_time('jump')} ms   coins: {score}")
    charge_bar.config(value=keys.held_time("jump"))


def draw_game():
    """Draw everything, then show it."""
    screen.fill((30, 30, 40))

    # >>> Objects with draw(screen) go here
    status.draw(screen)
    charge_bar.draw(screen)
    Label(240, 57, "hold SPACE to charge", font_size=20).draw(screen)
    pg.draw.circle(screen, (250, 200, 40), coin.center, 12)
    colour = (255, 120, 60) if keys.is_pressed("engine") else (70, 160, 230)
    pg.draw.rect(screen, colour, player, border_radius=8)
    if keys.is_pressed("fire"):
        pg.draw.line(screen, (255, 60, 60), player.midtop, (player.centerx, 0), 3)

    pg.display.flip()


# ---------- Main program ----------
init_pygame()
while True:
    tick = clock.tick(FPS)   # tick = milliseconds since the last frame (used for animation)
    handle_inputs()
    update(tick)
    draw_game()
