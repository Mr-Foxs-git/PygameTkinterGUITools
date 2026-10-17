"""
Spawner and Waves example - enemies that come in waves, and coins that
keep appearing.

Arrow keys / WASD = move.   Click a slime = squash it.
Walk over coins to collect them.   F1 = show the spawn places.
R = play again after the last wave.

Two Spawners:
  * slimes come from the 4 corners, in 3 waves (Waves). The last wave
    adds angry slimes. Each slime chases you with a Chaser.
  * coins appear every 2 seconds somewhere in the arena (a Rect), never
    more than 3 at once and never right next to you (avoid=player).
You write a function that makes ONE slime or coin. The Spawner decides
when and where to call it, and kill() takes it away again.
"""
import os
import sys
import pygame as pg

# Lets this example find the library one folder up.
# In your own game, just put PygameTkinterGUITools.py next to your game file.
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from PygameTkinterGUITools import (Spawner, Waves, SpriteObject, Animator, Chaser,
                                   TopDownBody, KeyboardInput, MouseInput, Label,
                                   SoundEffect, init_audio, Debug)

# ---------- Settings ----------
WIDTH, HEIGHT = 800, 600
FPS = 60
ASSETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
ARENA = pg.Rect(60, 80, 680, 460)                  # where coins can appear
CORNERS = [(20, 60), (WIDTH - 52, 60), (20, HEIGHT - 52), (WIDTH - 52, HEIGHT - 52)]


def make_slime(x, y, sheet="slime_sheet.png", speed=70):
    """Make ONE slime at x, y. The Spawner calls this for us."""
    animator = Animator(os.path.join(ASSETS, sheet), from_sheet=True,
                        tile_width=32, tile_height=32, rows=1, cols=2, frame_rate=4)
    slime = SpriteObject(x, y, animator=animator)
    # detect_range is big, so slimes always see you and chase
    slime.brain = Chaser(slime, player, speed=speed, detect_range=2000)
    return slime


def make_angry_slime(x, y):
    """Angry slimes are faster (used in wave 3)."""
    return make_slime(x, y, sheet="angry_slime_sheet.png", speed=120)


def make_coin(x, y):
    """Make ONE spinning coin at x, y."""
    spin = Animator(os.path.join(ASSETS, "coin_sheet.png"), from_sheet=True,
                    tile_width=16, tile_height=16, rows=1, cols=4, frame_rate=8, scale=2)
    return SpriteObject(x, y, animator=spin)


def all_waves_done():
    """Waves runs this after the last wave is cleared."""
    help_text.config(text="You win!  Press R to play again")


def init_pygame():
    """Set up pygame, the window, the clock and all game objects."""
    global screen, clock, keys, mouse, player, player_body, slimes, waves, coins
    global score, wave_label, score_label, help_text, squash_sound, coin_sound
    init_audio()                         # BEFORE pg.init(): sounds play with less delay
    pg.init()
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    pg.display.set_caption("Spawner and Waves example")
    clock = pg.time.Clock()

    # >>> Create objects here (after pg.init)
    keys = KeyboardInput()
    keys.bind("left", "left", "a")
    keys.bind("right", "right", "d")
    keys.bind("up", "up", "w")
    keys.bind("down", "down", "s")
    keys.bind("again", "r")
    mouse = MouseInput()
    mouse.bind("squash", "left")

    walk = Animator(os.path.join(ASSETS, "player_sheet.png"), from_sheet=True,
                    tile_width=32, tile_height=32, rows=3, cols=4)
    player = SpriteObject(WIDTH // 2, HEIGHT // 2, 28, 28, animator=walk)
    player_body = TopDownBody(player, speed=200)

    # Slimes: a new one every second from a corner, at most 6 alive at once.
    # Waves says how many come in each wave (3, then 5, then 8 angry ones).
    slimes = Spawner(make_slime, points=CORNERS, every=1000, max_alive=6)
    waves = Waves(slimes, [3, 5, {"count": 8, "every": 500, "make": make_angry_slime}],
                  break_ms=3000, on_all_done=all_waves_done)

    # Coins: one every 2 seconds inside ARENA, at most 3, never close to you
    coins = Spawner(make_coin, points=ARENA, every=2000, max_alive=3,
                    avoid=player, min_distance=120)

    score = 0
    wave_label = Label(WIDTH // 2, 20, "", font_size=32, center=True)
    score_label = Label(10, 10, "Score: 0")
    help_text = Label(10, HEIGHT - 34, "Arrows / WASD move, click slimes, F1 = debug")
    squash_sound = SoundEffect(os.path.join(ASSETS, "sounds", "click.wav"))
    coin_sound = SoundEffect(os.path.join(ASSETS, "sounds", "coin.wav"))


def handle_inputs():
    """Check every event: quitting, keys, mouse, controllers."""
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            sys.exit()

        # >>> Objects that react to events go here
        keys.handle_event(event)
        mouse.handle_event(event)
        Debug.handle_event(event)        # F1 shows the spawn places


def update(tick):
    """Move, animate and check things."""
    global score
    keys.update(tick)
    mouse.update(tick)

    # >>> Objects with update(tick) go here
    player_body.move(keys.is_pressed("right") - keys.is_pressed("left"),
                     keys.is_pressed("down") - keys.is_pressed("up"))
    player_body.update(tick)
    player.rect.clamp_ip(screen.get_rect())       # stay on the screen
    player.update(tick)

    waves.update(tick)          # runs the waves (and the slime Spawner)
    coins.update(tick)

    for slime in slimes:        # every slime that is still alive
        slime.brain.update(tick)
        slime.update(tick)      # animation
        if mouse.was_pressed("squash") and slime.rect.collidepoint(mouse.pos):
            slime.kill()        # kill() = it leaves the Spawner (and the wave)
            squash_sound.play()
            score += 1
        elif slime.rect.colliderect(player.rect):
            slime.kill()        # it bumped you: it's gone, but you lose points
            score = max(0, score - 3)

    for coin in coins:
        coin.update(tick)
        if coin.rect.colliderect(player.rect):
            coin.kill()
            coin_sound.play()
            score += 5

    if waves.finished and keys.was_pressed("again"):
        waves.restart()
        coins.clear()
        score = 0
        help_text.config(text="Arrows / WASD move, click slimes, F1 = debug")

    wave_label.config(text=waves.text())     # e.g. "Wave 2 of 3 - 4 left"
    score_label.config(text=f"Score: {score}")


def draw_game():
    """Draw everything, then show it."""
    screen.fill((40, 70, 50))
    pg.draw.rect(screen, (60, 95, 70), ARENA)

    # >>> Objects with draw(screen) go here
    coins.draw(screen)          # draws every coin (and the debug view with F1)
    slimes.draw(screen)
    player.draw(screen)
    wave_label.draw(screen)
    score_label.draw(screen)
    help_text.draw(screen)

    pg.display.flip()


# ---------- Main program ----------
init_pygame()
while True:
    tick = clock.tick(FPS)   # tick = milliseconds since the last frame (used for animation)
    handle_inputs()
    update(tick)
    draw_game()
