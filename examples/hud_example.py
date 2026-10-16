"""
HUD example - the game screen's text and bars.

Shows:
  Label        outline= and shadow= (easy to read over a busy background),
               "\\n" for several lines, justify="center"
  Progressbar  low_color= (turns red when nearly empty), animate=True
               (the lost health shows as a "ghost" that shrinks away)
  Health       draw_bar() - small health bars that float above enemies
  Frame        show(fade_ms=) / hide(fade_ms=) - a pause menu that fades
  Label        slide_to() - a title that glides onto the screen
  Style        the "high_contrast" theme

Arrow keys move, Space hurts the nearest enemy, H hurts you, J heals you,
Escape opens the pause menu, T switches to the high contrast theme.
"""
import os
import sys
import pygame as pg

# Lets this example find the library one folder up.
# In your own game, just put PygameTkinterGUITools.py next to your game file.
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from PygameTkinterGUITools import (Label, Progressbar, Health, SpriteObject, Camera,
                                   Frame, Button, KeyboardInput, Style)

# ---------- Settings ----------
WIDTH, HEIGHT = 800, 600
FPS = 60
WORLD_WIDTH = 1600            # the world is wider than the window, so the camera scrolls


def resume():
    pause_menu.hide(fade_ms=300)     # fades out, then hides


def switch_theme():
    if style.theme_use() == "high_contrast":
        style.theme_use("light")
    else:
        style.theme_use("high_contrast")


def init_pygame():
    """Set up pygame, the window, the clock and all game objects."""
    global screen, clock, keys, style, camera, player, enemies
    global health_bar, title, score_label, help_label, pause_menu
    pg.init()
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    pg.display.set_caption("HUD example")
    clock = pg.time.Clock()

    # >>> Create objects here (after pg.init)
    keys = KeyboardInput()
    keys.bind("hurt_enemy", "space")
    keys.bind("hurt_me", "h")
    keys.bind("heal_me", "j")
    keys.bind("pause", "escape")
    keys.bind("theme", "t")
    style = Style()

    camera = Camera(WORLD_WIDTH, HEIGHT, (WIDTH, HEIGHT))
    player = SpriteObject(380, 300, 36, 36, bg=(70, 160, 230))
    camera.follow(player)
    enemies = []
    for x in (250, 650, 1000, 1350):
        enemy = SpriteObject(x, 200 + x % 3 * 60, 40, 40, bg=(220, 70, 70))
        enemy.health = Health(30)
        enemies.append(enemy)

    health_bar = Progressbar(20, 20, length=220, thickness=22, show_text=True,
                             low_color=(230, 50, 50), low_at=0.3, animate=True)
    player.health = Health(100, bar=health_bar)

    score_label = Label(780, 20, "Score: 0", font_size=36, outline=2)
    help_label = Label(400, 520, "Arrows move   Space hits   H hurts you   J heals\n"
                                 "Escape = pause   T = high contrast",
                       font_size=24, shadow=True, justify="center", center=True)
    title = Label(-400, 90, "Level 1", font_size=64, outline=3, fg=(255, 220, 0))
    title.slide_to(300, 90, ms=900)          # glides in from the left

    pause_menu = Frame(250, 170, 300, 220, visible=False)
    Label(pause_menu, text="Paused", font_size=40).grid(row=0, column=0, pady=10)
    Button(pause_menu, text="Resume", command=resume).grid(row=1, column=0, pady=5)
    Button(pause_menu, text="Theme", command=switch_theme).grid(row=2, column=0, pady=5)


def handle_inputs():
    """Check every event: quitting, keys, mouse, controllers."""
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            sys.exit()

        # >>> Objects that react to events go here
        if pause_menu.handle_event(event):
            continue
        keys.handle_event(event)


def update(tick):
    """Move, animate and check things."""
    # >>> Objects with update(tick) go here
    keys.update(tick)
    if keys.was_pressed("pause"):
        pause_menu.toggle_visibility(fade_ms=300)
    if keys.was_pressed("theme"):
        switch_theme()
    if pause_menu.visible:
        pause_menu.update(tick)
        return                               # the game stops while paused

    speed = 0.3 * tick                       # pixels this frame
    dx = keys.is_pressed("right") - keys.is_pressed("left")
    dy = keys.is_pressed("down") - keys.is_pressed("up")
    player.move(dx * speed, dy * speed)
    player.rect.clamp_ip(pg.Rect(0, 0, WORLD_WIDTH, HEIGHT))
    camera.update(tick)

    if keys.was_pressed("hurt_enemy") and enemies:
        nearest = min(enemies, key=lambda e: abs(e.rect.centerx - player.rect.centerx))
        nearest.health.damage(10)
        if nearest.health.is_dead():
            enemies.remove(nearest)
            score_label.config(text=f"Score: {(4 - len(enemies)) * 100}")
    if keys.was_pressed("hurt_me"):
        player.health.damage(15)
    if keys.was_pressed("heal_me"):
        player.health.heal(25)


def draw_game():
    """Draw everything, then show it."""
    # A busy, stripy background - outlines and shadows keep the text readable
    screen.fill((40, 90, 60))
    for x in range(-int(camera.offset.x) % 80 - 80, WIDTH, 80):
        pg.draw.rect(screen, (230, 230, 180), (x, 0, 40, HEIGHT))

    # >>> Objects with draw(screen) go here
    for enemy in enemies:
        enemy.draw(screen, camera)
        enemy.health.draw_bar(screen, enemy, camera, low_color=(230, 50, 50),
                              animate=True)
    player.draw(screen, camera)

    health_bar.draw(screen)
    score_label.x = WIDTH - 20 - score_label.width     # keep it at the right edge
    score_label.draw(screen)
    title.draw(screen)
    help_label.draw(screen)
    pause_menu.draw(screen)                  # menus last, so they are on top

    pg.display.flip()


# ---------- Main program ----------
init_pygame()
while True:
    tick = clock.tick(FPS)   # tick = milliseconds since the last frame (used for animation)
    handle_inputs()
    update(tick)
    draw_game()
