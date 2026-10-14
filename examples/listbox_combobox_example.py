"""
Listbox and Combobox example - choosing from lists.

Shows: Listbox (scrolling list) with insert / delete, and Combobox
(drop-down). Scroll the list with the mouse wheel.
"""
import os
import sys
import pygame as pg

# Lets this example find the library one folder up.
# In your own game, just put PygameTkinterGUITools.py next to your game file.
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from PygameTkinterGUITools import Listbox, Combobox, Button, Label, StringVar

# ---------- Settings ----------
WIDTH, HEIGHT = 800, 600
FPS = 60


def level_chosen():
    chosen.config(text=f"Level: {levels.get_selected()}   Hero: {hero.get()}")


def add_level():
    levels.insert("end", f"Level {levels.size() + 1}")
    levels.see(levels.size() - 1)          # scroll to show it


def remove_level():
    if levels.curselection():              # () if nothing is chosen
        levels.delete(levels.curselection()[0])


def init_pygame():
    """Set up pygame, the window, the clock and all game objects."""
    global screen, clock, levels, hero, hero_box, buttons, chosen
    pg.init()
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    pg.display.set_caption("Listbox and Combobox example")
    clock = pg.time.Clock()

    # >>> Create objects here (after pg.init)
    levels = Listbox(50, 80, 220, rows=6,
                     items=[f"Level {n}" for n in range(1, 9)], command=level_chosen)
    buttons = [Button(50, 300, 105, 40, "Add", command=add_level, font_size=24),
               Button(165, 300, 105, 40, "Remove", command=remove_level, font_size=24)]

    hero = StringVar("Knight")
    hero_box = Combobox(350, 80, 220, values=["Knight", "Wizard", "Archer", "Rogue",
                                             "Healer", "Robot", "Dragon"],
                        textvariable=hero, command=level_chosen)
    chosen = Label(50, 500, "Choose a level and a hero", fg=(255, 220, 0))


def handle_inputs():
    """Check every event: quitting, keys, mouse, controllers."""
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            sys.exit()

        # >>> Objects that react to events go here
        # An open drop-down goes first, so clicking a choice doesn't click things under it
        if hero_box.handle_event(event):
            continue
        levels.handle_event(event)
        for button in buttons:
            button.handle_event(event)


def update(tick):
    """Move, animate and check things."""
    # >>> Objects with update(tick) go here
    pass


def draw_game():
    """Draw everything, then show it."""
    screen.fill((30, 30, 30))

    # >>> Objects with draw(screen) go here
    Label(50, 40, "Levels").draw(screen)
    Label(350, 40, "Hero").draw(screen)
    levels.draw(screen)
    for button in buttons:
        button.draw(screen)
    chosen.draw(screen)
    hero_box.draw(screen)          # drop-downs last, so the open list is on top

    pg.display.flip()


# ---------- Main program ----------
init_pygame()
while True:
    tick = clock.tick(FPS)   # tick = milliseconds since the last frame (used for animation)
    handle_inputs()
    update(tick)
    draw_game()
