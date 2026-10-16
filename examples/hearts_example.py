"""
HeartsBar example - show health as hearts (like Zelda or Minecraft).

Shows: HeartsBar reading a Health object, half hearts, heart pictures,
hearts wrapping onto two rows, and flash_when_hurt.
D = take 1 damage, H = heal 1, R = reset.
"""
import os
import sys
import pygame as pg

# Lets this example find the library one folder up.
# In your own game, just put PygameTkinterGUITools.py next to your game file.
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from PygameTkinterGUITools import HeartsBar, Health, KeyboardInput, Label

# Folder with the images for the examples
ASSETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")

# ---------- Settings ----------
WIDTH, HEIGHT = 800, 600
FPS = 60


def init_pygame():
    """Set up pygame, the window, the clock and all game objects."""
    global screen, clock, keys, player_health, drawn_hearts, picture_hearts
    global many_hearts, help_text, status
    pg.init()
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    pg.display.set_caption("HeartsBar example")
    clock = pg.time.Clock()

    # >>> Create objects here (after pg.init)
    keys = KeyboardInput()
    keys.bind("hurt", "d")
    keys.bind("heal", "h")
    keys.bind("reset", "r")

    # 10 HP. After a hit you can't be hurt again for 0.6 seconds.
    player_health = Health(10, invincible_ms=600)

    # 1. Drawn hearts: 5 hearts, so each heart is 2 HP (1 HP = half a heart).
    #    flash_when_hurt makes them blink while you are invincible.
    drawn_hearts = HeartsBar(50, 100, health=player_health, hearts=5,
                             flash_when_hurt=True)

    # 2. The same Health with pictures of ONE heart each.
    #    The pictures are 9 x 8 pixels, so keep that shape when scaling.
    picture_hearts = HeartsBar(50, 200, health=player_health, hearts=5,
                               heart_size=(45, 40), gap=6,
                               full_image=os.path.join(ASSETS, "heart_full.png"),
                               half_image=os.path.join(ASSETS, "heart_half.png"),
                               empty_image=os.path.join(ASSETS, "heart_empty.png"))

    # 3. One heart per HP (no hearts=), smaller, 5 per row, whole hearts only.
    many_hearts = HeartsBar(50, 300, health=player_health, heart_size=20,
                            per_row=5, half_hearts=False)

    help_text = Label(50, 30, "D = damage    H = heal    R = reset", font_size=28)
    status = Label(50, 400, "")


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
    # >>> Objects with update(tick) go here
    keys.update(tick)                    # always first: works out pressed / held / released
    drawn_hearts.update(tick)            # needed for flash_when_hurt

    if keys.was_pressed("hurt"):
        player_health.damage(1)
    if keys.was_pressed("heal"):
        player_health.heal(1)
    if keys.was_pressed("reset"):
        player_health.reset()

    # The HeartsBars read player_health by themselves - nothing else to do!
    status.config(text=f"Health: {player_health.value} / {player_health.maximum}"
                       f"    Hearts: {drawn_hearts.hearts_filled()}")


def draw_game():
    """Draw everything, then show it."""
    screen.fill((30, 30, 40))

    # >>> Objects with draw(screen) go here
    help_text.draw(screen)
    drawn_hearts.draw(screen)
    picture_hearts.draw(screen)
    many_hearts.draw(screen)
    status.draw(screen)

    pg.display.flip()


# ---------- Main program ----------
init_pygame()
while True:
    tick = clock.tick(FPS)   # tick = milliseconds since the last frame (used for animation)
    handle_inputs()
    update(tick)
    draw_game()
