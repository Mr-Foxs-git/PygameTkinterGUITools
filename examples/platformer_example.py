"""
Platformer example - gravity, jumping, platforms, ladders and enemies.

Shows: PlatformerBody (gravity, collisions, coyote time, jump buffer,
small jumps, one-way platforms, ladders), MovingPlatform, and enemies built
from blocks: Patrol, PathFollower and Chaser. Everything is placed in Tiled.

Controls: LEFT / RIGHT (or A / D) move, SPACE jump (tap for a small jump),
UP / DOWN climb ladders, DOWN on a wooden plank drops through it,
F1 shows / hides debug drawing (paths, ranges, collision boxes).

-------------------------------------------------------------------------
How the level (assets/platformer.tmx) is made in Tiled
-------------------------------------------------------------------------
Open it in Tiled to look. The "Objects" layer holds:
  * Rectangles with Class "collision"  -> walls and floors (solids)
  * Rectangles with Class "platform"   -> one-way platforms (wooden planks)
  * Rectangles with Class "ladder"     -> ladders
  * A point named "player_spawn"       -> where the player starts
  * Paths (see below) named "lift_route" and "bat_route"
  * Objects with Class "moving_platform" and a custom property "path"
  * Objects with Class "enemy" and a custom property "ai"
    ("patrol", "path" or "chase"). "path" enemies also have a "path" property.

Drawing a path in Tiled:
  1. Select the "Objects" layer.
  2. Choose the Insert Polyline tool (press L) - or Insert Polygon (press P)
     for a path that loops back to the start.
  3. Click each point of the route. Double-click (or press Enter) to finish.
  4. In the Properties panel, give it a Name, e.g. "bat_route".
  5. Optional: add a custom property called "mode" (string) set to
     "loop", "ping_pong" or "once". Without it, a Polyline goes back and
     forth and a Polygon loops.
  6. To make something follow it, give that object a custom property
     "path" with the path's name (or use level.get_path("bat_route") in code).
-------------------------------------------------------------------------
"""
import os
import sys
import pygame as pg

# Lets this example find the library one folder up.
# In your own game, just put PygameTkinterGUITools.py next to your game file.
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from PygameTkinterGUITools import (TiledMap, World, Camera, SpriteObject, Animator,
                                   PlatformerBody, MovingPlatform, Patrol, PathFollower,
                                   Chaser, Path, KeyboardInput, SoundEffect, init_audio,
                                   Label)

# ---------- Settings ----------
WIDTH, HEIGHT = 800, 600
FPS = 60
ASSETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")


def asset(name):
    return os.path.join(ASSETS, name)


def make_sprite(x, y, sheet, frames=2, size=32):
    """A SpriteObject with a simple looping animation from a sprite sheet."""
    animator = Animator(asset(sheet), from_sheet=True, tile_width=size, tile_height=size,
                        rows=1, cols=frames, frame_rate=4)
    return SpriteObject(x, y, animator=animator)


def make_enemy(info):
    """Build an enemy from a Tiled object, using its "ai" property."""
    ai = info["properties"].get("ai", "patrol")
    x, y = info["x"], info["y"]
    if ai == "path":                     # flying: just follows a path, no gravity
        sprite = make_sprite(x, y, "bat_sheet.png")
        brain = PathFollower(sprite, level.get_path(info["properties"]["path"]), speed=90)
        return sprite, None, brain
    if ai == "chase":                    # walks about, chases the player when close
        sprite = make_sprite(x, y, "angry_slime_sheet.png")
        body = PlatformerBody(sprite, solids=solids, platforms=platforms)
        wander = Patrol(sprite, speed=50, body=body)
        brain = Chaser(sprite, player, speed=130, detect_range=220, solids=solids,
                       body=body, idle=wander)
        return sprite, body, brain
    sprite = make_sprite(x, y, "slime_sheet.png")       # "patrol"
    body = PlatformerBody(sprite, solids=solids, platforms=platforms)
    brain = Patrol(sprite, speed=60, body=body, turn_at_edges=True)
    return sprite, body, brain


def respawn():
    player_body.set_position(*level.spawn_points["player_spawn"])


def init_pygame():
    """Set up pygame, the window, the clock and all game objects."""
    global screen, clock, level, world, camera, keys, player, player_body
    global solids, platforms, ladders, lifts, enemies, jump_sound, hint
    init_audio()
    pg.init()
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    pg.display.set_caption("Platformer example")
    clock = pg.time.Clock()

    # >>> Create objects here (after pg.init and set_mode)
    level = TiledMap(asset("platformer.tmx"))
    solids = [obj["rect"] for obj in level.collision_objects]
    platforms = level.rects_of_type("platform")
    ladders = level.rects_of_type("ladder")

    # Moving platforms follow paths drawn in Tiled
    lifts = []
    for info in level.objects_of_type("moving_platform"):
        lift = MovingPlatform(info["x"], info["y"], info["width"], info["height"],
                              path=level.get_path(info["properties"]["path"]),
                              speed=int(info["properties"].get("speed", 80)))
        lifts.append(lift)
    platforms += lifts                   # you can stand on them (one-way)

    # The player
    animator = Animator(asset("player_sheet.png"), from_sheet=True, tile_width=32,
                        tile_height=32, rows=3, cols=4)
    animator.add_animation("idle", [(0, 0), (0, 1), (0, 2), (0, 3)])
    animator.add_animation("walk", [(1, 0), (1, 1), (1, 2), (1, 3)])
    animator.add_animation("jump", [(2, 1)])
    sx, sy = level.spawn_points["player_spawn"]
    player = SpriteObject(sx, sy, 28, 30, animator=animator)
    player_body = PlatformerBody(player, solids=solids, platforms=platforms, ladders=ladders,
                                 move_speed=220, jump_speed=620)

    # Enemies come from objects with the Class "enemy"
    enemies = [make_enemy(info) for info in level.objects_of_type("enemy")]

    keys = KeyboardInput()
    keys.bind("left", "left", "a")
    keys.bind("right", "right", "d")
    keys.bind("up", "up", "w")
    keys.bind("down", "down", "s")
    keys.bind("jump", "space")
    keys.bind("debug", "f1")
    jump_sound = SoundEffect(asset("sounds/jump.wav"), volume=0.6)

    camera = Camera(level.width, level.height, (WIDTH, HEIGHT))
    camera.follow(player)
    world = World(level, camera)
    world.add_sprite(*[enemy[0] for enemy in enemies], player)   # World animates these
    Path.show_all = False
    hint = Label(10, 10, "Arrows / WASD move and climb, SPACE jump, F1 debug", bg=(0, 0, 0))


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
    keys.update(tick)
    if keys.was_pressed("debug"):
        Path.show_all = not Path.show_all

    for lift in lifts:                   # platforms move BEFORE the things on them
        lift.update(tick)

    # Player controls -> body
    player_body.move(keys.is_pressed("right") - keys.is_pressed("left"))
    player_body.climb(keys.is_pressed("down") - keys.is_pressed("up"))
    if keys.was_pressed("jump"):
        player_body.jump()
        if player_body.on_ground or player_body.climbing:
            jump_sound.play()
    if keys.was_released("jump"):
        player_body.release_jump()       # let go early = small jump
    if keys.was_pressed("down") and not player_body.on_ladder:
        player_body.drop_down()
    player_body.update(tick)

    # Animation
    player.flip_x = player_body.facing == "left"
    if not player_body.on_ground and not player_body.climbing:
        player.animator.play("jump")
    elif player_body.velocity.x:
        player.animator.play("walk")
    else:
        player.animator.play("idle")

    # Enemies: the "brain" decides, then the body moves
    for sprite, body, brain in enemies:
        brain.update(tick)
        if body is not None:
            body.update(tick)
        sprite.flip_x = getattr(brain, "facing", "right") == "left"
        if sprite.rect.colliderect(player.rect):
            respawn()

    # Spikes and falling off the map
    for trigger in level.triggers:
        if trigger["name"] == "spikes" and player.rect.colliderect(trigger["rect"]):
            respawn()
    if player.rect.top > level.height:
        respawn()

    world.update(tick)                   # animations
    camera.update(tick)


def draw_box(rect, colour):
    pg.draw.rect(screen, colour, camera.apply(rect), 1)


def draw_game():
    """Draw everything, then show it."""
    screen.fill((120, 180, 230))

    # >>> Objects with draw(screen) go here
    world.draw(screen)
    for lift in lifts:
        lift.draw(screen, camera)

    if Path.show_all:                    # debug drawing (F1)
        for rect in solids:
            draw_box(rect, (255, 0, 0))
        for rect in platforms:
            draw_box(_rect(rect), (255, 200, 0))
        for rect in ladders:
            draw_box(rect, (0, 255, 255))
        for path in level.paths:
            Path.from_tiled(path).draw(screen, camera)
        for sprite, body, brain in enemies:
            if isinstance(brain, Chaser):
                brain.draw_debug(screen, camera)
        draw_box(player.rect, (255, 255, 255))
    hint.draw(screen)

    pg.display.flip()


def _rect(thing):
    return thing if isinstance(thing, pg.Rect) else thing.rect


# ---------- Main program ----------
init_pygame()
while True:
    tick = clock.tick(FPS)   # tick = milliseconds since the last frame (used for animation)
    handle_inputs()
    update(tick)
    draw_game()
