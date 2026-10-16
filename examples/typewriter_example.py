"""
Typewriter example - dialogue that types out one letter at a time
(like the text boxes in Pokemon).

Shows: Message(type_speed=...), a typing sound (type_sound), on_done,
and MessageBox(type_speed=...).
SPACE or click: the first press shows the rest of the line,
the next press goes to the next line. Drag the slider to change the speed.
"""
import os
import sys
import pygame as pg

# Lets this example find the library one folder up.
# In your own game, just put PygameTkinterGUITools.py next to your game file.
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from PygameTkinterGUITools import (Message, Label, Scale, IntVar, MessageBox,
                                   SoundEffect, init_audio)

# ---------- Settings ----------
WIDTH, HEIGHT = 800, 600
FPS = 60
SOUNDS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "sounds")
STORY = [
    "Hello there! Welcome to the world of pygame!",
    "This text types itself out one letter at a time. "
    "Press SPACE (or click) to see the rest of it straight away.",
    "Press SPACE again to go to the next line. Try the slider to change how fast "
    "the letters appear.",
    "That's the end of the story!",
]


def next_line():
    """Go to the next line of the story (or ask to start again at the end)."""
    global line
    if line == len(STORY) - 1:
        again_box.show()
        return
    line += 1
    dialogue.config(text=STORY[line])     # new text types out by itself
    arrow.hide()


def line_finished():
    """Runs (from on_done) when the last letter of a line has appeared."""
    box = dialogue.rect                  # put the hint in the box's bottom-right corner
    arrow.x, arrow.y = box.right - 90, box.bottom - 26
    arrow.show()


def play_again(answer):
    """The MessageBox gives the button the player clicked."""
    global line
    if answer == "Yes":
        line = 0
        dialogue.config(text=STORY[0])
        arrow.hide()


def change_speed():
    dialogue.config(type_speed=speed.get())


def init_pygame():
    """Set up pygame, the window, the clock and all game objects."""
    global screen, clock, line, dialogue, arrow, speed, speed_scale, title, again_box
    init_audio()                         # BEFORE pg.init(): sounds play with less delay
    pg.init()
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    pg.display.set_caption("Typewriter example")
    clock = pg.time.Clock()

    # >>> Create objects here (after pg.init)
    line = 0
    speed = IntVar(30)                   # letters per second
    click = SoundEffect(os.path.join(SOUNDS, "click.wav"), volume=0.3, cooldown=60)

    title = Label(WIDTH // 2, 50, "Typewriter example", font_size=48, center=True)
    speed_scale = Scale(250, 120, from_=5, to=80, length=300, variable=speed,
                        label="Letters per second", command=change_speed)
    dialogue = Message(60, 400, STORY[0], width=680, bg=(250, 250, 250),
                       fg=(30, 30, 30), padding=20, font_size=32,
                       type_speed=speed.get(), type_sound=click, on_done=line_finished)
    arrow = Label(0, 0, "SPACE >", fg=(200, 40, 40), font_size=22, visible=False)
    again_box = MessageBox("The end", "Do you want to read the story again?",
                           buttons=("Yes", "No"), command=play_again,
                           type_speed=40, type_sound=click)


def handle_inputs():
    """Check every event: quitting, keys, mouse, controllers."""
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            sys.exit()

        # >>> Objects that react to events go here
        # The MessageBox goes FIRST: while it is open it takes every press
        if again_box.handle_event(event):
            continue
        if speed_scale.handle_event(event):
            continue
        # True = the press was used to show the rest of the line,
        # so it must NOT also move on to the next line
        if dialogue.handle_event(event):
            continue
        if event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
            next_line()
        if event.type == pg.MOUSEBUTTONDOWN and dialogue.rect.collidepoint(event.pos):
            next_line()


def update(tick):
    """Move, animate and check things."""
    # >>> Objects with update(tick) go here
    dialogue.update(tick)                # types the next letters
    again_box.update(tick)


def draw_game():
    """Draw everything, then show it."""
    screen.fill((40, 120, 70))

    # >>> Objects with draw(screen) go here
    title.draw(screen)
    speed_scale.draw(screen)
    dialogue.draw(screen)
    arrow.draw(screen)
    again_box.draw(screen)               # LAST, so it is on top

    pg.display.flip()


# ---------- Main program ----------
init_pygame()
while True:
    tick = clock.tick(FPS)   # tick = milliseconds since the last frame (used for animation)
    handle_inputs()
    update(tick)
    draw_game()
