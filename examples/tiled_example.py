"""
Tiled map example - a level made in Tiled.

Shows: TiledMap, World, Camera + ZoomCamera, the spawn point,
walls from collision objects, coins from custom objects, and a trigger.
Also: camera.snap(), tile properties (water slows you down),
World(y_sort=True) and a feet hitbox (TopDownBody(..., hitbox=10)) so you can
walk behind and in front of the signposts and bushes.
Arrow keys to move, + and - to zoom. F1 shows the debug view.
Find the exit on the right!

Open assets/level1.tmx in Tiled to see (and change) how it is made:
  - "Ground" layer: grass, path, walls, animated water
  - "Ground details" layer: grass at the foot of each signpost. It is on
    the ground, so it must stay UNDER the player's feet - a background layer
  - "Midground" layer: signposts and bushes, in front of or behind the player
    (a layer named "midground" is sorted by height with the sprites)
  - "Foreground" layer: empty - put things here that are ALWAYS in front
    of the player (roofs, bridges, tree canopies)
  - "Objects" layer: player_spawn, collision boxes, coins, exit trigger.
    The signs and bushes have small collision boxes over their BASE only
    (sign_base, bush_base): the player's feet bump into those, while their
    head can overlap the picture
  - The water tile has custom properties (select it in the tileset):
        water = true, speed = 0.5
    The outside edge of the pond is shallow enough to wade through.
Needs: pip install pytmx
"""
import os
import sys
import pygame as pg

# Lets this example find the library one folder up.
# In your own game, just put PygameTkinterGUITools.py next to your game file.
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from PygameTkinterGUITools import (TiledMap, World, Camera, ZoomCamera,
                                   SpriteObject, Animator, Label, Button, Popup, Debug,
                                   TopDownBody)

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
    body.set_position(*level.spawn_points["player_spawn"])
    zoom_camera.snap()           # jump straight back to the player
    win_popup.hide()


def init_pygame():
    """Set up pygame, the window, the clock and all game objects."""
    global screen, clock, level, world, camera, zoom_camera, player, body, coins
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

    # hitbox=10: only the bottom 10 pixels (the feet) bump into walls, so the
    # player can walk in front of a sign with their head over its picture
    body = TopDownBody(player, solids=walls, speed=SPEED, hitbox=10)

    # Coins come from objects with the class "coin"
    coins = [make_coin(obj["x"], obj["y"])
             for obj in level.custom_objects if obj["type"] == "coin"]

    camera = Camera(level.width, level.height, (WIDTH, HEIGHT))
    camera.follow(player)
    zoom_camera = ZoomCamera(camera, (WIDTH, HEIGHT), zoom=1.5)   # crisp pixels
    zoom_camera.snap()           # start on the player (no glide from the corner)

    # y_sort=True: whatever is lower on the screen is drawn in front
    world = World(level, camera, y_sort=True)
    world.add_sprite(player, *coins)

    score = 0
    score_label = Label(10, 50, "Coins: 0", fg=(255, 220, 0), bg=(0, 0, 0), font_size=32)
    win_popup = Popup(WIDTH // 2, HEIGHT // 2, 300, 180, "You found the exit!", center=True)
    win_popup.add(Button(65, 60, 150, 50, "Play again", command=restart))


def handle_inputs():
    """Check every event: quitting, keys, mouse, controllers."""
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            sys.exit()

        # >>> Objects that react to events go here
        win_popup.handle_event(event)
        Debug.handle_event(event)      # F1: depth lines under sprites and signposts
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
    # Tile properties: the water tile has speed = 0.5 in Tiled.
    # The middle of the feet hitbox is where the player stands.
    ground = level.tile_properties_at(body.hitbox_rect.center)
    speed = SPEED * ground.get("speed", 1)
    dx = keys[pg.K_RIGHT] - keys[pg.K_LEFT]
    dy = keys[pg.K_DOWN] - keys[pg.K_UP]
    body.move(dx, dy, speed)
    body.update(tick)                  # moves, stopping the feet at walls
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
    zoom_camera.draw_world(world, screen)   # ground, then signs, bushes + sprites by height
    if Debug.on:
        body.draw_debug(screen, zoom_camera)   # F1: the feet hitbox (and the walls)
        for wall in walls:
            pg.draw.rect(screen, (255, 0, 0), zoom_camera.apply(wall), 1)
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
