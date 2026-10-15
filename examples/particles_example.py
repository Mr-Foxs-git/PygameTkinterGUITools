"""
Particles example - every ready-made effect, plus a custom one.

Click anywhere = explosion. Keys:
  1 sparks   2 dust   3 confetti   4 smoke on/off   5 fire on/off
  6 rain on/off   7 snow on/off   8 magic on/off   9 custom "bubbles"
Move the mouse: a trail follows it.   F1 = debug (emitter positions and counts)

Every effect is just a ParticleEmitter with settings. Look at the
"bubbles" emitter below, then try changing its numbers.
"""
import os
import sys
import pygame as pg

# Lets this example find the library one folder up.
# In your own game, just put PygameTkinterGUITools.py next to your game file.
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from PygameTkinterGUITools import ParticleEmitter, Particles, Label, Debug

# ---------- Settings ----------
WIDTH, HEIGHT = 800, 600
FPS = 60


class MousePointer:
    """Something with a .rect at the mouse, for the trail to follow."""
    def __init__(self):
        self.rect = pg.Rect(0, 0, 1, 1)


def toggle(name, make):
    """Turn a continuous effect on or off."""
    if effects.get(name):
        effects[name].stop()              # stop making new ones; old ones fade out
        effects[name].once = True         # ...then it removes itself
        effects[name] = None
    else:
        effects[name] = make()


def init_pygame():
    """Set up pygame, the window, the clock and all game objects."""
    global screen, clock, effects, pointer, help_text, count_label
    pg.init()
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    pg.display.set_caption("Particles example")
    clock = pg.time.Clock()

    # >>> Create objects here (after pg.init)
    effects = {}
    pointer = MousePointer()
    Particles.trail(follow=pointer)               # follows the mouse
    help_text = Label(10, 10, "Click = explosion   1-9 = effects   F1 = debug")
    count_label = Label(10, 40, "")


def make_bubbles():
    """A custom effect: change these numbers and see what happens!"""
    return ParticleEmitter(pos=(WIDTH // 2, HEIGHT - 20), rate=25,
                           lifetime=(2000, 3500),       # ms each bubble lives
                           speed=(30, 80), angle=-90,   # upwards
                           spread=25,                   # +/- 25 degrees
                           gravity=-20, wind=10,        # float up, drift right
                           size=(6, 16),                # grow as they rise
                           color=[(180, 230, 255), (120, 180, 255)],
                           alpha=(200, 0),              # fade out
                           area=("rect", 300, 10))      # start along a line


def handle_inputs():
    """Check every event: quitting, keys, mouse, controllers."""
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            sys.exit()

        # >>> Objects that react to events go here
        Debug.handle_event(event)
        if event.type == pg.MOUSEBUTTONDOWN:
            Particles.explosion(event.pos)
        if event.type == pg.KEYDOWN:
            middle = (WIDTH // 2, HEIGHT // 2)
            if event.key == pg.K_1:
                Particles.sparks(middle)
            elif event.key == pg.K_2:
                Particles.dust((WIDTH // 2, HEIGHT - 40))
            elif event.key == pg.K_3:
                Particles.confetti((WIDTH // 2, HEIGHT - 40))
            elif event.key == pg.K_4:
                toggle("smoke", lambda: Particles.smoke(pos=(150, HEIGHT - 60)))
            elif event.key == pg.K_5:
                toggle("fire", lambda: Particles.fire(pos=(650, HEIGHT - 40), size=1.5))
            elif event.key == pg.K_6:
                toggle("rain", lambda: Particles.rain(screen.get_rect()))
            elif event.key == pg.K_7:
                toggle("snow", lambda: Particles.snow(screen.get_rect()))
            elif event.key == pg.K_8:
                toggle("magic", lambda: Particles.magic(pos=(WIDTH // 2, 200)))
            elif event.key == pg.K_9:
                toggle("bubbles", make_bubbles)


def update(tick):
    """Move, animate and check things."""
    # >>> Objects with update(tick) go here
    pointer.rect.center = pg.mouse.get_pos()
    Particles.update(tick)                         # updates every emitter
    count_label.config(text=f"Particles: {Particles.count()}")


def draw_game():
    """Draw everything, then show it."""
    screen.fill((15, 15, 30))

    # >>> Objects with draw(screen) go here
    Particles.draw(screen)                         # draws every emitter
    help_text.draw(screen)
    count_label.draw(screen)

    pg.display.flip()


# ---------- Main program ----------
init_pygame()
while True:
    tick = clock.tick(FPS)   # tick = milliseconds since the last frame (used for animation)
    handle_inputs()
    update(tick)
    draw_game()
