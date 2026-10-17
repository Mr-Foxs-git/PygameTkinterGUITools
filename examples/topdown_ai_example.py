"""
Top-down enemies example - paths, line of sight and path finding.

Shows: TopDownBody (walls), PathFollower (a guard walking a route drawn in
Tiled), Chaser + NavGrid (a hunter that spots you and finds its way around
walls, then goes home when it loses you), and Path debug drawing.

Arrow keys / WASD move. F1 shows / hides the debug drawing:
yellow = paths, circles = how far enemies can see, green / red line =
whether they can see you, red squares = where path finding can't go.

-------------------------------------------------------------------------
How it is set up in Tiled (assets/level1.tmx, "Objects" layer)
-------------------------------------------------------------------------
  * "guard_route" was drawn with the Insert Polygon tool (P), so it loops.
    (Use Insert Polyline (L) for a route that goes there and back.)
    Click each corner, double-click to finish, then type its Name.
  * "guard" and "hunter" are rectangles with Class "enemy" and a custom
    property "ai" ("path" or "chase"). The guard also has a custom
    property "path" = "guard_route".
  * Walls are rectangles with Class "collision" - the NavGrid is built from them.
-------------------------------------------------------------------------
"""
import os
import sys
import pygame as pg

# Lets this example find the library one folder up.
# In your own game, just put PygameTkinterGUITools.py next to your game file.
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from PygameTkinterGUITools import (TiledMap, World, Camera, SpriteObject, Animator,
                                   TopDownBody, PathFollower, Chaser, NavGrid, Path,
                                   KeyboardInput, Label)

# ---------- Settings ----------
WIDTH, HEIGHT = 800, 600
FPS = 60
ASSETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")


def ghost(x, y):
    animator = Animator(os.path.join(ASSETS, "ghost_sheet.png"), from_sheet=True,
                        tile_width=32, tile_height=32, rows=1, cols=2, frame_rate=4)
    return SpriteObject(x, y, 28, 28, animator=animator)


def init_pygame():
    """Set up pygame, the window, the clock and all game objects."""
    global screen, clock, level, world, camera, keys, player, player_body, walls
    global brains, nav, message, caught_timer
    pg.init()
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    pg.display.set_caption("Top-down enemies example")
    clock = pg.time.Clock()

    # >>> Create objects here (after pg.init and set_mode)
    level = TiledMap(os.path.join(ASSETS, "level1.tmx"))
    walls = [obj["rect"] for obj in level.collision_objects]
    nav = NavGrid.from_tiled(level, agent_size=28)          # for path finding

    walk = Animator(os.path.join(ASSETS, "player_sheet.png"), from_sheet=True,
                    tile_width=32, tile_height=32, rows=3, cols=4)
    walk.add_animation("walk", [(1, 0), (1, 1), (1, 2), (1, 3)])
    player = SpriteObject(*level.spawn_points["player_spawn"], 28, 28, animator=walk)
    # hitbox=10: only the feet bump into walls, so you can walk in front of
    # and behind the bushes and signs (with World(..., y_sort=True))
    player_body = TopDownBody(player, solids=walls, speed=180, hitbox=10)

    brains = []
    for info in level.objects_of_type("enemy"):
        enemy = ghost(info["x"], info["y"])
        if info["properties"].get("ai") == "path":
            route = level.get_path(info["properties"]["path"])
            brains.append((enemy, PathFollower(enemy, route, speed=90, wait=400)))
        else:
            body = TopDownBody(enemy, solids=walls)
            brains.append((enemy, Chaser(enemy, player, speed=140, detect_range=220,
                                         solids=walls, nav=nav, body=body)))

    camera = Camera(level.width, level.height, (WIDTH, HEIGHT))
    camera.follow(player)
    world = World(level, camera, y_sort=True)     # lower on the screen = in front
    world.add_sprite(player, *[enemy for enemy, brain in brains])

    keys = KeyboardInput()
    keys.bind("left", "left", "a")
    keys.bind("right", "right", "d")
    keys.bind("up", "up", "w")
    keys.bind("down", "down", "s")
    keys.bind("debug", "f1")
    Path.show_all = True
    message = Label(10, 10, "Arrows / WASD to move, F1 = debug", bg=(0, 0, 0))
    caught_timer = 0


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
    global caught_timer
    # >>> Objects with update(tick) go here
    keys.update(tick)
    if keys.was_pressed("debug"):
        Path.show_all = not Path.show_all

    player_body.move(keys.is_pressed("right") - keys.is_pressed("left"),
                     keys.is_pressed("down") - keys.is_pressed("up"))
    player_body.update(tick)
    player.flip_x = player_body.facing == "left"

    for enemy, brain in brains:
        brain.update(tick)
        if isinstance(brain, Chaser):
            brain.body.update(tick)
        enemy.flip_x = brain.facing == "left"
        if enemy.rect.colliderect(player.rect):
            player_body.set_position(*level.spawn_points["player_spawn"])
            caught_timer = 1500

    caught_timer -= tick
    message.config(text="Caught! Back to the start." if caught_timer > 0
                   else "Arrows / WASD to move, F1 = debug")
    world.update(tick)
    camera.update(tick)


def draw_game():
    """Draw everything, then show it."""
    screen.fill((0, 0, 0))

    # >>> Objects with draw(screen) go here
    world.draw(screen)
    if Path.show_all:
        nav.draw(screen, camera)
        player_body.draw_debug(screen, camera)      # the feet hitbox
        for enemy, brain in brains:
            if isinstance(brain, Chaser):
                brain.draw_debug(screen, camera)
            else:
                brain.path.draw(screen, camera)
    message.draw(screen)

    pg.display.flip()


# ---------- Main program ----------
init_pygame()
while True:
    tick = clock.tick(FPS)   # tick = milliseconds since the last frame (used for animation)
    handle_inputs()
    update(tick)
    draw_game()
