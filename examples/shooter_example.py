"""
Shooter example - health, projectiles and effects.

Shows: Health (with a Progressbar and invincibility), Shooter and
ProjectileGroup, hit flash, blink while invincible, knockback, camera
shake, waves of enemies with after_repeat(), and a saved best score.

WASD to move, aim with the mouse, hold the left button to shoot,
right button for a shotgun blast. F1 = debug (hitboxes).
"""
import os
import sys
import pygame as pg

# Lets this example find the library one folder up.
# In your own game, just put PygameTkinterGUITools.py next to your game file.
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import random
from PygameTkinterGUITools import (SpriteObject, TopDownBody, Health, Progressbar, Label,
                                   Shooter, ProjectileGroup, KeyboardInput, MouseInput,
                                   Camera, flash, blink, knockback, after_repeat,
                                   update_timers, cancel_all_timers, HighScores, Debug)

# ---------- Settings ----------
WIDTH, HEIGHT = 800, 600
FPS = 60
ARENA = pg.Rect(20, 60, WIDTH - 40, HEIGHT - 80)


def player_hurt():
    blink(player, player.health.invincible_ms)   # flicker while invincible
    camera.shake(250, 8)


def new_game():
    global score, enemies, game_over
    cancel_all_timers()
    player.rect.center = ARENA.center
    player.health.reset()
    enemies = []
    bullets.clear()
    score = 0
    game_over = False
    after_repeat(1500, spawn_enemy)               # a new enemy every 1.5 s


def spawn_enemy():
    side = random.choice(["left", "right", "top", "bottom"])
    x = {"left": ARENA.left, "right": ARENA.right - 30}.get(side, random.randint(ARENA.left, ARENA.right - 30))
    y = {"top": ARENA.top, "bottom": ARENA.bottom - 30}.get(side, random.randint(ARENA.top, ARENA.bottom - 30))
    enemy = SpriteObject(x, y, 30, 30, bg=(220, 70, 70))
    enemy.body = TopDownBody(enemy, speed=random.randint(70, 120))
    enemy.health = Health(30)
    enemies.append(enemy)


def end_game():
    global game_over
    game_over = True
    cancel_all_timers()
    best.add("You", score)


def init_pygame():
    """Set up pygame, the window, the clock and all game objects."""
    global screen, clock, player, player_body, bullets, gun, shotgun, keys, mouse
    global camera, health_bar, info, best
    pg.init()
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    pg.display.set_caption("Shooter example")
    clock = pg.time.Clock()

    # >>> Create objects here (after pg.init)
    player = SpriteObject(0, 0, 32, 32, bg=(70, 160, 230))
    player_body = TopDownBody(player, solids=[], speed=230)
    health_bar = Progressbar(20, 20, length=200, thickness=18, bar_color=(80, 200, 120),
                             show_text=True)
    player.health = Health(100, invincible_ms=900, on_damage=player_hurt,
                           on_death=end_game, bar=health_bar)

    bullets = ProjectileGroup()
    gun = Shooter(bullets, cooldown=150, speed=700, damage=10, owner=player)
    shotgun = Shooter(bullets, cooldown=700, speed=550, damage=8, count=5, fan=12,
                      spread=3, lifetime=400, bg=(255, 150, 60), owner=player)

    keys = KeyboardInput()
    keys.bind("left", "a"); keys.bind("right", "d"); keys.bind("up", "w"); keys.bind("down", "s")
    keys.bind("restart", "return")
    mouse = MouseInput()
    camera = Camera(WIDTH, HEIGHT, (WIDTH, HEIGHT))    # no scrolling - just for shake
    info = Label(240, 18, "")
    best = HighScores("shooter_scores.json", keep=1)
    new_game()


def handle_inputs():
    """Check every event: quitting, keys, mouse, controllers."""
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            sys.exit()

        # >>> Objects that react to events go here
        Debug.handle_event(event)
        keys.handle_event(event)
        mouse.handle_event(event)


def update(tick):
    """Move, animate and check things."""
    global score
    # >>> Objects with update(tick) go here
    keys.update(tick)
    mouse.update(tick)
    update_timers(tick)                      # runs after_repeat (no Scenes here)
    camera.update(tick)
    bullets.update(tick)

    best_score = best.best()[1] if best.best() else 0
    info.config(text=f"Score: {score}   Best: {best_score}" +
                ("     GAME OVER - press Enter" if game_over else ""))
    if game_over:
        if keys.was_pressed("restart"):
            new_game()
        return

    # Player
    player_body.move(keys.is_pressed("right") - keys.is_pressed("left"),
                     keys.is_pressed("down") - keys.is_pressed("up"))
    player_body.update(tick)
    player.rect.clamp_ip(ARENA)
    if mouse.is_pressed("left"):
        gun.fire(player.rect.center, target=mouse.pos)
    if mouse.is_pressed("right"):
        shotgun.fire(player.rect.center, target=mouse.pos)

    # Enemies
    for enemy in enemies:
        enemy.body.move_towards(player.rect.center)
        enemy.body.update(tick)
        if enemy.rect.colliderect(player.rect):
            if player.health.damage(10):
                knockback(player_body, enemy.rect.center, strength=500)
            knockback(enemy.body, player.rect.center, strength=300)

    # Bullets hitting enemies
    for hit in bullets.hits(enemies):
        hit.target.health.damage(hit.damage)
        flash(hit.target, 80)
        knockback(hit.target.body, hit.projectile.rect.center, strength=200)
    for enemy in enemies[:]:
        if enemy.health.is_dead():
            enemies.remove(enemy)
            score += 1
            camera.shake(100, 3)


def draw_game():
    """Draw everything, then show it."""
    screen.fill((20, 20, 30))

    # >>> Objects with draw(screen) go here
    pg.draw.rect(screen, (60, 60, 80), camera.apply(ARENA), 2)
    for enemy in enemies:
        enemy.draw(screen, camera)
        # small health bar over each enemy
        r = camera.apply(enemy.rect)
        pg.draw.rect(screen, (60, 0, 0), (r.x, r.y - 6, r.width, 4))
        pg.draw.rect(screen, (240, 60, 60), (r.x, r.y - 6, r.width * enemy.health.fraction(), 4))
    bullets.draw(screen, camera)
    if not game_over:
        player.draw(screen, camera)
    if Debug.on:
        for thing in [player] + enemies + list(bullets):
            pg.draw.rect(screen, (0, 255, 0), camera.apply(thing.rect), 1)
    health_bar.draw(screen)
    info.draw(screen)

    pg.display.flip()


# ---------- Main program ----------
init_pygame()
while True:
    tick = clock.tick(FPS)   # tick = milliseconds since the last frame (used for animation)
    handle_inputs()
    update(tick)
    draw_game()
