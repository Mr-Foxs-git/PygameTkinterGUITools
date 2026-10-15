"""
Layout example - grid(), pack() and place(), like tkinter.

Shows: widgets made with their parent first (Label(form, text=...)),
grid with sticky / padx / columnspan / columnconfigure, pack for a row of
buttons, place for a corner button, Root for the whole screen,
and the DEBUG VIEW.

Press F1 to turn the debug view on / off:
  * blue lines      = grid rows and columns (with their numbers and weights)
  * pink boxes      = each widget, with (row, column) and sticky arrows
  * yellow shading  = padding (padx / pady)
  * orange boxes    = pack() spaces, numbered in pack order
  * green cross     = place() position
  * red text        = layout mistakes (also printed in the console)
Hover over a widget in debug view to see its exact settings.
Press R to print a layout report in the console.

Try the COMMON MISTAKES section at the bottom of init_pygame(): remove the #
from one line at a time, run, and press F1.
"""
import os
import sys
import pygame as pg

# Lets this example find the library one folder up.
# In your own game, just put PygameTkinterGUITools.py next to your game file.
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from PygameTkinterGUITools import (Root, Frame, LabelFrame, Label, Button, TextBox,
                                   Checkbutton, Combobox, Scale, Debug, BooleanVar,
                                   StringVar, IntVar)

# ---------- Settings ----------
WIDTH, HEIGHT = 800, 600
FPS = 60


def save():
    status.config(text=f"Saved: {name.get()}, {hero.get()}, volume {volume.get()}")


def init_pygame():
    """Set up pygame, the window, the clock and all game objects."""
    global screen, clock, root, form, status, name, hero, volume
    pg.init()
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    pg.display.set_caption("Layout example - press F1")
    clock = pg.time.Clock()

    # >>> Create objects here (after pg.init)
    name, hero, volume = StringVar("Sam"), StringVar("Knight"), IntVar(60)

    # Root = the whole window, like tkinter's Tk()
    root = Root(screen, padding=20)
    root.columnconfigure(0, weight=1)          # column 0 gets the spare width

    Label(root, text="Player settings", font_size=44).grid(row=0, column=0, pady=(0, 30))

    # A form laid out with grid: labels on the left, inputs on the right
    form = LabelFrame(root, text="Your player")
    form.grid(row=1, column=0)
    Label(form, text="Name:").grid(row=0, column=0, sticky="e", padx=8, pady=6)
    TextBox(form, max_chars=12, textvariable=name).grid(row=0, column=1, sticky="w")
    Label(form, text="Hero:").grid(row=1, column=0, sticky="e", padx=8, pady=6)
    Combobox(form, width=200, values=["Knight", "Wizard", "Archer"],
             textvariable=hero).grid(row=1, column=1, sticky="w")
    Label(form, text="Volume:").grid(row=2, column=0, sticky="e", padx=8, pady=6)
    Scale(form, from_=0, to=100, variable=volume).grid(row=2, column=1, sticky="w")
    Checkbutton(form, text="Show hints", variable=BooleanVar(True)).grid(
        row=3, column=0, columnspan=2, pady=6)              # spans both columns

    # A row of buttons laid out with pack (in their own Frame)
    buttons = Frame(root, bg="", border_width=0)      # "" = see-through
    buttons.grid(row=2, column=0, pady=20)
    Button(buttons, text="Save", command=save).pack(side="left", padx=6)
    Button(buttons, text="Reset").pack(side="left", padx=6)
    Button(buttons, text="Quit", command=lambda: (pg.quit(), sys.exit())).pack(side="left", padx=6)

    status = Label(root, text="", fg=(255, 220, 0))
    status.grid(row=3, column=0)

    # place(): an exact spot - here the top-right corner of the window
    Button(root, text="?", font_size=24).place(relx=1.0, rely=0.0, anchor="ne")

    # ---------- COMMON MISTAKES: remove the # from one line, run, press F1 ----------
    # 1. Forgetting grid(): the widget never appears (a warning tells you why)
    #Label(form, text="I was never gridded")

    # 2. Two widgets in the same cell: they overlap
    #Label(form, text="Me too!").grid(row=0, column=1)

    # 3. Mixing grid() and pack() in one Frame: tkinter freezes. Here the program
    #    stops with a message showing YOUR file and line number - read the
    #    ">>> The mistake is in YOUR code" part of the error.
    #Label(form, text="Packed").pack()

    # 4. Too much in too little space
    #Label(form, text="A very very very long label that does not fit").grid(row=4, column=0)


def handle_inputs():
    """Check every event: quitting, keys, mouse, controllers."""
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            sys.exit()

        # >>> Objects that react to events go here
        Debug.handle_event(event)              # F1 = debug view
        if event.type == pg.KEYDOWN and event.key == pg.K_r:
            form.layout_report()
        root.handle_event(event)


def update(tick):
    """Move, animate and check things."""
    # >>> Objects with update(tick) go here
    root.update(tick)


def draw_game():
    """Draw everything, then show it."""
    screen.fill((30, 30, 40))

    # >>> Objects with draw(screen) go here
    root.draw(screen)

    pg.display.flip()


# ---------- Main program ----------
init_pygame()
while True:
    tick = clock.tick(FPS)   # tick = milliseconds since the last frame (used for animation)
    handle_inputs()
    update(tick)
    draw_game()
