"""
Joystick move - move a square with a controller.

The numbers below suit most Xbox-style controllers. If yours behaves
differently, run joystick_debug.py and change the numbers in init_pygame().
"""
import os
import sys
import pygame as pg

# Lets this example find the library one folder up.
# In your own game, just put PygameTkinterGUITools.py next to your game file.
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from PygameTkinterGUITools import JoystickManager, Label

# ---------- Settings ----------
WIDTH, HEIGHT = 800, 600
FPS = 60
SPEED = 300          # pixels per second at full stick


def change_colour():
    global player_colour
    player_colour = (255, 200, 0) if player_colour == (0, 200, 255) else (0, 200, 255)


def init_pygame():
    """Set up pygame, the window, the clock and all game objects."""
    global screen, clock, pad, player, player_colour, message
    pg.init()
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    pg.display.set_caption("Joystick move")
    clock = pg.time.Clock()

    # >>> Create objects here (after pg.init)
    pad = JoystickManager(0)
    pad.bind_axis("move_x", 0)                         # left stick left/right
    pad.bind_axis("move_y", 1)                         # left stick up/down
    pad.bind_hat("dpad", 0)
    pad.bind_button("jump", 0)                         # A on Xbox
    pad.bind_button("colour", 1, command=change_colour)  # B on Xbox

    player = pg.Rect(WIDTH // 2, HEIGHT // 2, 40, 40)
    player_colour = (0, 200, 255)
    message = Label(20, 20, "")


def handle_inputs():
    """Check every event: quitting, keys, mouse, controllers."""
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            sys.exit()

        # >>> Objects that react to events go here
        pad.handle_event(event)            # runs command= functions too


def update(tick):
    """Move, animate and check things."""
    # >>> Objects with update go here
    pad.update(tick)                       # always first

    seconds = tick / 1000                  # tick is in milliseconds
    dx = pad.get_axis("move_x")
    dy = pad.get_axis("move_y")

    hat_x, hat_y = pad.get_hat("dpad")
    if hat_x != 0 or hat_y != 0:
        dx, dy = hat_x, -hat_y             # hat up is +1, but screen up is -y

    player.x += int(dx * SPEED * seconds)
    player.y += int(dy * SPEED * seconds)
    player.clamp_ip(screen.get_rect())     # stay on screen

    if pad.was_pressed("jump"):
        print("Jump!")

    if pad.connected:
        message.config(text="Stick or D-pad to move, A to jump, B to change colour")
    else:
        message.config(text="Plug in a controller")


def draw_game():
    """Draw everything, then show it."""
    screen.fill((30, 30, 30))

    # >>> Objects with draw go here
    pg.draw.rect(screen, player_colour, player)
    message.draw(screen)

    pg.display.flip()


# ---------- Main program ----------
init_pygame()
while True:
    tick = clock.tick(FPS)   # tick = milliseconds since the last frame (used for animation)
    handle_inputs()
    update(tick)
    draw_game()
