"""
Parallax example - a side-view world with far-away backgrounds.

Shows:
  Background(image, parallax=...)  - clouds and hills scroll slower than the
                                     ground, so they look far away
  Camera(..., deadzone=, lookahead=) - the camera only moves when you leave
                                     the box in the middle, and it looks ahead
                                     the way you are walking
  camera.snap()                    - start on the player (no glide)
  camera.on_screen(thing, margin)  - only slimes near the screen move
  camera.shake()                   - S shakes the screen
  pause_timers() / resume_timers() - P: shaking stops while timers are paused

LEFT / RIGHT walk, SPACE jumps, S shakes, P pauses timers.
F1 shows the deadzone box and where the camera is looking ahead.
"""
import os
import sys
import pygame as pg

# Lets this example find the library one folder up.
# In your own game, just put PygameTkinterGUITools.py next to your game file.
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from PygameTkinterGUITools import (SpriteObject, Animator, Camera, Background, Label,
                                   KeyboardInput, PlatformerBody, Debug,
                                   pause_timers, resume_timers)

# Folder with the images for the examples
ASSETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")

# ---------- Settings ----------
WIDTH, HEIGHT = 800, 600
WORLD_WIDTH, WORLD_HEIGHT = 4000, 900
GROUND_Y = 800                 # top of the ground in the world
FPS = 60
SLIME_SPEED = 60               # pixels per second


def tile(number):
    """One 32 x 32 tile from platform_tiles.png (0 = grass, 1 = dirt, 4 = stone)."""
    sheet = pg.image.load(os.path.join(ASSETS, "platform_tiles.png")).convert_alpha()
    return sheet.subsurface((number * 32, 0, 32, 32)).copy()


def ground_picture():
    """A strip of grass on top of dirt, repeated along the ground by Background."""
    picture = pg.Surface((32, WORLD_HEIGHT - GROUND_Y))
    picture.blit(tile(0), (0, 0))
    for y in range(32, picture.get_height(), 32):
        picture.blit(tile(1), (0, y))
    return picture


def make_slime(x):
    animator = Animator(os.path.join(ASSETS, "slime_sheet.png"), from_sheet=True,
                        tile_width=32, tile_height=32, rows=1, cols=2, frame_rate=4)
    slime = SpriteObject(x, GROUND_Y - 32, animator=animator, smooth_move=True)
    slime.walk = 1             # 1 = right, -1 = left
    slime.home = x             # walks up to 100 pixels each side of here
    return slime


def init_pygame():
    """Set up pygame, the window, the clock and all game objects."""
    global screen, clock, keys, camera, player, body, blocks, slimes
    global clouds, hills, ground, info_label, help_label, paused
    pg.init()
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    pg.display.set_caption("Parallax example")
    clock = pg.time.Clock()

    # >>> Create objects here (after pg.init and set_mode)
    keys = KeyboardInput()
    keys.bind("jump", "space")
    keys.bind("shake", "s")
    keys.bind("pause", "p")
    paused = False

    # Backgrounds, furthest away first.
    # parallax: 0 = stuck to the screen, 1 = moves with the world
    clouds = Background(os.path.join(ASSETS, "clouds.png"), parallax=0.1, y=30)
    hills = Background(os.path.join(ASSETS, "hills.png"), parallax=0.3, y=410)
    ground = Background(ground_picture(), parallax=1, y=GROUND_Y)

    # A staircase of stone blocks to jump up (so the camera moves up and down too)
    stone = tile(4)
    blocks = []
    for i, (x, y) in enumerate([(600, 768), (700, 704), (800, 640), (900, 576),
                                (1500, 736), (1600, 672), (2600, 768), (2700, 704)]):
        blocks.append(SpriteObject(x, y, image=stone))

    player = SpriteObject(200, GROUND_Y - 40, 28, 40, bg=(70, 160, 230))
    floor = pg.Rect(0, GROUND_Y, WORLD_WIDTH, WORLD_HEIGHT - GROUND_Y)
    walls = [pg.Rect(-10, 0, 10, WORLD_HEIGHT), pg.Rect(WORLD_WIDTH, 0, 10, WORLD_HEIGHT)]
    body = PlatformerBody(player, solids=[floor] + walls + blocks)

    slimes = [make_slime(x) for x in range(500, WORLD_WIDTH, 300)]

    # deadzone: walk freely inside a 200 x 150 box before the camera moves
    # lookahead: show 150 more pixels in the direction you walk (sideways only)
    camera = Camera(WORLD_WIDTH, WORLD_HEIGHT, (WIDTH, HEIGHT),
                    deadzone=(200, 150), lookahead=150)
    camera.follow(player)
    camera.snap()              # start on the player

    info_label = Label(10, 10, "", font_size=26, outline=2)
    help_label = Label(10, HEIGHT - 34, "LEFT / RIGHT walk   SPACE jump   S shake   "
                       "P pause timers   F1 debug", font_size=24, outline=2)


def handle_inputs():
    """Check every event: quitting, keys, mouse, controllers."""
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            sys.exit()

        # >>> Objects that react to events go here
        keys.handle_event(event)
        Debug.handle_event(event)      # F1: deadzone box and lookahead line


def update(tick):
    """Move, animate and check things."""
    global paused
    # >>> Objects with update(tick) go here
    keys.update(tick)

    # Player
    body.move(keys.is_pressed("right") - keys.is_pressed("left"))
    if keys.was_pressed("jump"):
        body.jump()
    if keys.was_released("jump"):
        body.release_jump()
    body.update(tick)

    # S: shake. P: pause timers - the shake (game time) stops until you resume
    if keys.was_pressed("shake"):
        camera.shake(1500, 8)
    if keys.was_pressed("pause"):
        paused = not paused
        if paused:
            pause_timers()
        else:
            resume_timers()

    # Slimes far off the screen don't need to move: it saves work in big levels
    moving = 0
    for slime in slimes:
        if camera.on_screen(slime, margin=100):
            moving += 1
            slime.update(tick)
            slime.move(slime.walk * SLIME_SPEED * tick / 1000, 0)
            if abs(slime.rect.x - slime.home) > 100:
                slime.walk = -slime.walk          # turn round
                slime.flip_x = slime.walk < 0

    camera.update(tick)

    text = f"Slimes moving: {moving} of {len(slimes)} (only the ones near the screen)"
    if paused:
        text += "   TIMERS PAUSED"
    info_label.config(text=text)


def draw_game():
    """Draw everything, then show it."""
    screen.fill((140, 200, 240))           # the sky

    # >>> Objects with draw(screen) go here
    # Backgrounds first, furthest away first
    clouds.draw(screen, camera)
    hills.draw(screen, camera)
    ground.draw(screen, camera)

    for block in blocks:
        block.draw(screen, camera)
    for slime in slimes:
        slime.draw(screen, camera)
    player.draw(screen, camera)

    if Debug.on:
        camera.draw_debug(screen)          # the deadzone box

    info_label.draw(screen)
    help_label.draw(screen)
    pg.display.flip()


# ---------- Main program ----------
init_pygame()
while True:
    tick = clock.tick(FPS)   # tick = milliseconds since the last frame (used for animation)
    handle_inputs()
    update(tick)
    draw_game()
