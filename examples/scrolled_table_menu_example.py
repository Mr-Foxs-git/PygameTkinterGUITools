"""
ScrolledFrame, Table and Menu example - a little level editor screen.

Shows:
  * Menu: a menu bar (File / Edit / View) with shortcuts that really work
    (Ctrl+N, Ctrl+S, Ctrl+D...), tick and choice items, and a right-click menu.
  * Table: sortable columns (click a heading), EDITABLE cells (double-click a
    Damage or Price cell, type, press Enter / Tab / Escape), and a TREE view
    (click the arrows to open and close worlds).
  * ScrolledFrame: a long list of level buttons that scrolls.
F2 = layout debug view (it's a menu shortcut - see View).
"""
import os
import sys
import pygame as pg

# Lets this example find the library one folder up.
# In your own game, just put PygameTkinterGUITools.py next to your game file.
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from PygameTkinterGUITools import (Root, Menu, Table, ScrolledFrame, Label, Button, Debug,
                                   MouseInput, BooleanVar, StringVar, Style)

# ---------- Settings ----------
WIDTH, HEIGHT = 900, 620
FPS = 60
ITEMS = [["Wooden sword", "weapon", 3, 10], ["Iron sword", "weapon", 7, 45],
         ["Oak shield", "shield", 0, 30], ["Red potion", "potion", 0, 15],
         ["Fire staff", "weapon", 12, 120], ["Leather cap", "armour", 0, 20],
         ["Steel helm", "armour", 0, 75], ["Bow", "weapon", 5, 35], ["Blue potion", "potion", 0, 40]]


def say(words):
    status.config(text=words)


def new_item():
    row = items.insert(["New item", "weapon", 1, 1])
    items.selection_set(row)
    say("Added a new item (double-click a cell to edit it)")


def delete_item():
    if items.selection() is not None:
        say(f"Deleted {items.get_selected()[0]}")
        items.delete(items.selection())


def item_edited():
    row, column, old, new = items.last_edit
    say(f"{items.get(row, 'Item')}: {column} changed from {old} to {new}")


def change_theme():
    Style().theme_use(theme.get())


def open_level(name):
    say(f"Opening {name}...")


def init_pygame():
    """Set up pygame, the window, the clock and all game objects."""
    global screen, clock, root, items, levels, status, context, mouse, theme, show_grid
    pg.init()
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    pg.display.set_caption("ScrolledFrame, Table and Menu example")
    clock = pg.time.Clock()

    # >>> Create objects here (after pg.init)
    root = Root(screen, padding=15)
    theme, show_grid = StringVar("light"), BooleanVar(False)

    # ---- Menu bar ----
    menubar = Menu(root)
    file_menu = Menu(menubar)
    file_menu.add_command(label="New item", command=new_item, accelerator="Ctrl+N")
    file_menu.add_command(label="Save", command=lambda: say("Saved!"), accelerator="Ctrl+S")
    file_menu.add_command(label="Export", state="disabled")          # greyed out
    file_menu.add_separator()
    file_menu.add_command(label="Quit", command=lambda: (pg.quit(), sys.exit()),
                          accelerator="Ctrl+Q")
    edit_menu = Menu(menubar)
    edit_menu.add_command(label="Delete item", command=delete_item, accelerator="Ctrl+D")
    view_menu = Menu(menubar)
    view_menu.add_checkbutton(label="Debug view", variable=show_grid,
                              command=lambda: setattr(Debug, "on", show_grid.get()),
                              accelerator="F2")
    theme_menu = Menu(view_menu)                                       # a sub-menu
    for name in ("light", "dark", "retro"):
        theme_menu.add_radiobutton(label=name.title(), variable=theme, value=name,
                                   command=change_theme)
    view_menu.add_cascade(label="Theme", menu=theme_menu)
    menubar.add_cascade(label="File", menu=file_menu)
    menubar.add_cascade(label="Edit", menu=edit_menu)
    menubar.add_cascade(label="View", menu=view_menu)
    root.config(menu=menubar)                       # shows it across the top

    # ---- Right-click menu ----
    context = Menu()
    context.add_command(label="New item", command=new_item)
    context.add_command(label="Delete item", command=delete_item)

    # ---- Table with editable cells ----
    Label(root, text="Items (click a heading to sort, double-click to edit)").grid(
        row=0, column=0, sticky="w", pady=(10, 4))
    items = Table(root, columns=["Item", "Type", "Damage", "Price"], rows=9,
                  editable=["Item", "Damage", "Price"], on_edit=item_edited)
    items.column("Damage", anchor="e", type=int, width=90)
    items.column("Price", anchor="e", type=int, width=80,
                 check=lambda text: int(text) >= 0)       # no negative prices
    items.load(ITEMS)
    items.grid(row=1, column=0, sticky="nw", padx=(0, 20))

    # ---- Tree view ----
    Label(root, text="Worlds (tree view)").grid(row=2, column=0, sticky="w", pady=(15, 4))
    worlds = Table(root, columns=["Level", "Stars"], rows=6, tree=True)
    for w in range(1, 4):
        world = worlds.insert([f"World {w}", ""], open=(w == 1))
        for n in range(1, 5):
            worlds.insert([f"Level {w}-{n}", "*" * ((w + n) % 4)], parent=world)
    worlds.grid(row=3, column=0, sticky="nw")

    # ---- ScrolledFrame with lots of buttons ----
    Label(root, text="Level select (scroll)").grid(row=0, column=1, sticky="w", pady=(10, 4))
    levels = ScrolledFrame(root, width=220, height=430)
    levels.grid(row=1, column=1, rowspan=3, sticky="n")
    for n in range(1, 31):
        Button(levels, text=f"Level {n}", width=170, font_size=24,
               command=lambda n=n: open_level(f"Level {n}")).grid(row=n, column=0, pady=3)

    status = Label(root, text="Try the menus, Ctrl+N, right-click, or F2", fg=(255, 220, 0))
    status.grid(row=4, column=0, columnspan=2, sticky="w", pady=10)
    mouse = MouseInput()


def handle_inputs():
    """Check every event: quitting, keys, mouse, controllers."""
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            sys.exit()

        # >>> Objects that react to events go here
        if context.handle_event(event):           # an open right-click menu goes first
            continue
        mouse.handle_event(event)
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 3:
            context.post(*event.pos)              # right-click opens the menu
            continue
        root.handle_event(event)                  # the menu bar is part of root


def update(tick):
    """Move, animate and check things."""
    # >>> Objects with update(tick) go here
    mouse.update(tick)
    root.update(tick)


def draw_game():
    """Draw everything, then show it."""
    screen.fill((30, 30, 40))

    # >>> Objects with draw(screen) go here
    root.draw(screen)          # includes the menu bar
    context.draw(screen)       # right-click menu last, on top

    pg.display.flip()


# ---------- Main program ----------
init_pygame()
while True:
    tick = clock.tick(FPS)   # tick = milliseconds since the last frame (used for animation)
    handle_inputs()
    update(tick)
    draw_game()
