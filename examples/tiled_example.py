"""
Tiled map example - a level made in Tiled.

Shows: TiledMap, World, Camera + ZoomCamera, the spawn point,
walls from collision objects, coins from custom objects, and a trigger.
Arrow keys to move, + and - to zoom. Find the exit on the right!

Open assets/level1.tmx in Tiled to see (and change) how it is made:
  - "Ground" layer: grass, path, walls, animated water
  - "Foreground" layer: tree tops, drawn in front of the player
  - "Objects" layer: player_spawn, collision boxes, coins, exit trigger
Needs: pip install pytmx
"""
import os
import sys
import pygame as pg

# Lets this example find the library one folder up.
# In your own game, just put PygameTkinterGUITools.py next to your game file.
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from PygameTkinterGUITools import (TiledMap, World, Camera, ZoomCamera,
                                   SpriteObject, Animator, Label, Button, Popup)

# Folder with the images and maps for the examples
ASSETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")

# ---------- Settings ----------
WIDTH, HEIGHT = 800, 600
FPS = 60
SPEED = 200


def make_coin(x, y):
    spin = Animator(os.path.join(ASSETS, "coin_sheet.png"), from_sheet=True,
                    tile_width=16, tile_height=16, rows=1, cols=4, frame_rate=8)
    return SpriteObject(x, y, animator=spin)


def restart():
    """Send the player back to the start."""
    player.rect.topleft = level.spawn_points["player_spawn"]
    win_popup.hide()


def init_pygame():
    """Set up pygame, the window, the clock and all game objects."""
    global screen, clock, level, world, camera, zoom_camera, player, coins
    global walls, score, score_label, win_popup
    pg.init()
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    pg.display.set_caption("Tiled map example")
    clock = pg.time.Clock()

    # >>> Create objects here (after pg.init and set_mode)
    level = TiledMap(os.path.join(ASSETS, "level1.tmx"))

    # Player starts at the "player_spawn" object
    walk = Animator(os.path.join(ASSETS, "player_sheet.png"), from_sheet=True,
                    tile_width=32, tile_height=32, rows=3, cols=4)
    walk.add_animation("walk", [(1, 0), (1, 1), (1, 2), (1, 3)])
    walk.add_animation("idle", [(0, 0), (0, 1), (0, 2), (0, 3)])
    sx, sy = level.spawn_points["player_spawn"]
    player = SpriteObject(sx, sy, 28, 28, animator=walk)

    # Walls come from objects with the class "collision"
    walls = [obj["rect"] for obj in level.collision_objects]

    # Coins come from objects with the class "coin"
    coins = [make_coin(obj["x"], obj["y"])
             for obj in level.custom_objects if obj["type"] == "coin"]

    camera = Camera(level.width, level.height, (WIDTH, HEIGHT))
    camera.follow(player)
    zoom_camera = ZoomCamera(camera, (WIDTH, HEIGHT), zoom=1.5)   # crisp pixels

    world = World(level, camera)
    world.add_sprite(player, *coins)

    score = 0
    score_label = Label(10, 10, "Coins: 0", fg=(255, 220, 0), bg=(0, 0, 0), font_size=32)
    win_popup = Popup(WIDTH // 2, HEIGHT // 2, 300, 180, "You found the exit!", center=True)
    win_popup.add(Button(65, 60, 150, 50, "Play again", command=restart))


def move_player(dx, dy):
    """Move, then push the player back out of any wall it hit."""
    player.move(dx, 0)
    for wall in walls:
        if player.rect.colliderect(wall):
            if dx > 0:
                player.rect.right = wall.left
            elif dx < 0:
                player.rect.left = wall.right
    player.move(0, dy)
    for wall in walls:
        if player.rect.colliderect(wall):
            if dy > 0:
                player.rect.bottom = wall.top
            elif dy < 0:
                player.rect.top = wall.bottom


def handle_inputs():
    """Check every event: quitting, keys, mouse, controllers."""
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            sys.exit()

        # >>> Objects that react to events go here
        win_popup.handle_event(event)
        if event.type == pg.KEYDOWN:
            if event.key in (pg.K_PLUS, pg.K_EQUALS, pg.K_KP_PLUS):
                zoom_camera.set_zoom(zoom_camera.zoom + 0.25)
            if event.key in (pg.K_MINUS, pg.K_KP_MINUS):
                zoom_camera.set_zoom(zoom_camera.zoom - 0.25)


def update(tick):
    """Move, animate and check things."""
    global score
    if win_popup.visible:
        return

    keys = pg.key.get_pressed()
    step = max(1, int(SPEED * tick / 1000))
    dx = (keys[pg.K_RIGHT] - keys[pg.K_LEFT]) * step
    dy = (keys[pg.K_DOWN] - keys[pg.K_UP]) * step
    move_player(dx, dy)
    player.animator.play("walk" if dx or dy else "idle")

    # >>> Objects with update(tick) go here
    world.update(tick)                 # animates water, coins and the player
    zoom_camera.update(tick)

    # Collect coins
    for coin in coins[:]:
        if player.collides_with(coin):
            coins.remove(coin)
            world.sprites.remove(coin)
            score += 1
            score_label.config(text=f"Coins: {score}")

    # Triggers are areas that make something happen
    for trigger in level.triggers:
        if trigger["name"] == "exit" and player.rect.colliderect(trigger["rect"]):
            win_popup.show()


def draw_game():
    """Draw everything, then show it."""
    screen.fill((0, 0, 0))

    # >>> Objects with draw(screen) go here
    zoom_camera.draw_world(world, screen)   # map, sprites, then tree tops
    score_label.draw(screen)
    win_popup.draw(screen)

    pg.display.flip()


# ---------- Main program ----------
init_pygame()
while True:
    tick = clock.tick(FPS)   # tick = milliseconds since the last frame (used for animation)
    handle_inputs()
    update(tick)
    draw_game()
