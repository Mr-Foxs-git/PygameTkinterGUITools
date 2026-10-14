"""
Message example - wrapping text for dialogue and instructions.

Shows: Message (text that wraps onto several lines), justify,
and changing the text with config(). Click Next (or press SPACE).
"""
import os
import sys
import pygame as pg

# Lets this example find the library one folder up.
# In your own game, just put PygameTkinterGUITools.py next to your game file.
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from PygameTkinterGUITools import Message, Button, Separator

# ---------- Settings ----------
WIDTH, HEIGHT = 800, 600
FPS = 60
STORY = [
    "Welcome, traveller! This text is a Message. It wraps onto new lines by itself, "
    "so you don't have to work out where each line ends.",
    "Messages are great for dialogue, instructions and story text.\nYou can also "
    "start a new line yourself with \\n.",
    "Change the words with config(text=...), just like a Label. That's the end - "
    "press Next to start again.",
]


def next_line():
    global line
    line = (line + 1) % len(STORY)
    dialogue.config(text=STORY[line])


def init_pygame():
    """Set up pygame, the window, the clock and all game objects."""
    global screen, clock, line, dialogue, title, next_button, rule
    pg.init()
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    pg.display.set_caption("Message example")
    clock = pg.time.Clock()

    # >>> Create objects here (after pg.init)
    line = 0
    title = Message(WIDTH // 2, 60, "Message example", width=500, font_size=48,
                    justify="center", center=True)
    rule = Separator(150, 100, length=500)
    dialogue = Message(100, 380, STORY[0], width=600, bg=(20, 20, 60),
                       fg=(255, 255, 255), padding=16, font_size=28)
    next_button = Button(580, 520, 120, 45, "Next", command=next_line, font_size=26)


def handle_inputs():
    """Check every event: quitting, keys, mouse, controllers."""
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            sys.exit()

        # >>> Objects that react to events go here
        next_button.handle_event(event)
        if event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
            next_line()


def update(tick):
    """Move, animate and check things."""
    # >>> Objects with update(tick) go here
    pass


def draw_game():
    """Draw everything, then show it."""
    screen.fill((30, 30, 30))

    # >>> Objects with draw(screen) go here
    title.draw(screen)
    rule.draw(screen)
    dialogue.draw(screen)
    next_button.draw(screen)

    pg.display.flip()


# ---------- Main program ----------
init_pygame()
while True:
    tick = clock.tick(FPS)   # tick = milliseconds since the last frame (used for animation)
    handle_inputs()
    update(tick)
    draw_game()
