"""
Shop editor example - spreadsheet-style Table and question boxes.

Shows: Table(edit_mode="spreadsheet"), Table(border_color=...),
MessageBox / askyesnocancel / askokcancel, and Popup(title_font_size=...).

Click a Price or Qty cell and just type - like a spreadsheet.
Enter saves and moves down, Tab moves right, arrow keys move around.
Press Escape to quit (it asks first). Click "Reset" to put prices back.
"""
import os
import sys
import pygame as pg

# Lets this example find the library one folder up.
# In your own game, just put PygameTkinterGUITools.py next to your game file.
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from PygameTkinterGUITools import (Table, Button, Label, Popup, askyesnocancel,
                                   askokcancel)

# ---------- Settings ----------
WIDTH, HEIGHT = 800, 600
FPS = 60
START_ITEMS = [["Iron sword", 45, 1], ["Bow", 35, 2], ["Oak shield", 30, 1],
               ["Red potion", 15, 5], ["Steel helm", 75, 1]]


def quit_answer(answer):
    """askyesnocancel gives True (Yes), False (No) or None (Cancel)."""
    if answer is True:                   # Yes: save, then quit
        print("Saved:", shop.all_rows())
    if answer is not None:               # Yes or No: quit
        pg.quit()
        sys.exit()


def reset_answer(answer):
    """askokcancel gives True (OK) or False (Cancel)."""
    if answer:
        shop.load(START_ITEMS)


def ask_reset():
    global question
    question = askokcancel("Reset?", "Put every price back to the start?",
                           command=reset_answer)


def init_pygame():
    """Set up pygame, the window, the clock and all game objects."""
    global screen, clock, shop, reset_button, hint, question, total_box
    pg.init()
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    pg.display.set_caption("Shop editor example")
    clock = pg.time.Clock()

    # >>> Create objects here (after pg.init)
    shop = Table(40, 80, columns=["Item", "Price", "Qty"], rows=8, width=420,
                 editable=["Price", "Qty"], edit_mode="spreadsheet",
                 border_color=(255, 200, 0))
    shop.column("Price", type=int, anchor="e")
    shop.column("Qty", type=int, anchor="e")
    shop.load(START_ITEMS)
    reset_button = Button(500, 80, 160, 50, "Reset", command=ask_reset)
    hint = Label(40, 30, "Click a Price or Qty and type. Escape = quit.")
    question = None                       # the question box that is open (if any)
    total_box = Popup(580, 380, 300, 140, "Total", center=True, dim=False,
                      title_font_size=36)


def handle_inputs():
    """Check every event: quitting, keys, mouse, controllers."""
    global question
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            sys.exit()

        # >>> Objects that react to events go here
        if question and question.handle_event(event):
            continue                     # an open question box takes everything
        if shop.handle_event(event):
            continue
        reset_button.handle_event(event)
        if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
            question = askyesnocancel("Quit?", "Save the shop before you quit?",
                                      command=quit_answer)


def update(tick):
    """Move, animate and check things."""
    # >>> Objects with update(tick) go here
    total = sum(price * qty for item, price, qty in shop.all_rows()
                if isinstance(price, int) and isinstance(qty, int))
    total_box.title = f"Total: {total} gold"
    total_box.show()


def draw_game():
    """Draw everything, then show it."""
    screen.fill((30, 30, 40))

    # >>> Objects with draw(screen) go here
    hint.draw(screen)
    shop.draw(screen)
    reset_button.draw(screen)
    total_box.draw(screen)
    if question:
        question.draw(screen)            # question boxes LAST so they are on top

    pg.display.flip()


# ---------- Main program ----------
init_pygame()
while True:
    tick = clock.tick(FPS)   # tick = milliseconds since the last frame (used for animation)
    handle_inputs()
    update(tick)
    draw_game()
