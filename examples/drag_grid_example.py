"""
Drag and Grid example - an inventory with equipment slots.

Shows: DragObject with a kind and stats, DragGroup, Grid (snapping, one item
per cell, moving between grids), equipment slots that only accept the right
kind of item (set_slot), Tooltip showing an item's stats, free dragging
without a grid, and MouseInput.

Drag items between the backpack and the equipment slots - the sword only
goes in the Weapon slot, etc. Hover over an item to see its stats.
Drag the sticky notes anywhere. Right-click an item to use a potion.
"""
import os
import sys
import pygame as pg

# Lets this example find the library one folder up.
# In your own game, just put PygameTkinterGUITools.py next to your game file.
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from PygameTkinterGUITools import (Grid, DragObject, DragGroup, MouseInput, Label,
                                   Tooltip)

# ---------- Settings ----------
WIDTH, HEIGHT = 800, 600
FPS = 60
ASSETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")

# Every item: name, kinds, picture, and any stats you like
ITEMS = [
    ("Iron Sword", ["weapon", "sword"], "item_sword.png", {"damage": 7, "weight": 3}),
    ("Oak Shield", ["shield"], "item_shield.png", {"defence": 5, "weight": 4}),
    ("Red Potion", ["potion"], "item_potion.png", {"heals": 25}),
    ("Blue Potion", ["potion"], "item_potion.png", {"heals": 50, "rarity": "rare"}),
    ("Emerald", ["gem", "trinket"], "item_gem.png", {"value": 120, "rarity": "rare"}),
    ("Old Key", ["key", "trinket"], "item_key.png", {"opens": "Dungeon door"}),
]


def describe(item):
    """Tooltip text: the name, then every stat (works for any stats you add)."""
    lines = [item.name, "(" + ", ".join(item.kinds) + ")"]
    for stat, value in item.stats.items():
        lines.append(f"{stat.title()}: {value}")
    return "\n".join(lines)


def update_totals():
    """Add up the stats of everything equipped."""
    damage = sum(i.stats.get("damage", 0) for i in items if i.grid is equipment)
    defence = sum(i.stats.get("defence", 0) for i in items if i.grid is equipment)
    totals.config(text=f"Damage: {damage}   Defence: {defence}")


def init_pygame():
    """Set up pygame, the window, the clock and all game objects."""
    global screen, clock, backpack, equipment, items, notes, mouse, message, totals, tips
    pg.init()
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    pg.display.set_caption("Drag and Grid example")
    clock = pg.time.Clock()

    # >>> Create objects here (after pg.init and set_mode)
    backpack = Grid(40, 120, cols=5, rows=3, cell_size=72, bg=(50, 45, 40))

    # Equipment: each slot only accepts one kind of item
    equipment = Grid(520, 120, cols=2, rows=2, cell_size=72, bg=(40, 50, 70))
    equipment.set_slot(0, 0, accepts="weapon", label="Weapon")
    equipment.set_slot(1, 0, accepts="shield", label="Shield")
    equipment.set_slot(0, 1, accepts="potion", label="Potion")
    equipment.set_slot(1, 1, accepts="trinket", label="Trinket")
    # (accepts can also be a function, e.g. accepts=lambda item: item.stats.get("weight", 0) < 4)

    items = DragGroup()
    tips = Tooltip()
    for i, (name, kinds, picture, stats) in enumerate(ITEMS):
        item = DragObject(0, 0, 56, 56, image=os.path.join(ASSETS, picture), name=name,
                          kind=kinds, stats=stats, grid=[backpack, equipment],
                          on_drop=update_totals)
        backpack.place(item, i % 5, i // 5)
        items.add(item)
        tips.attach(item, describe)                 # a function: always up to date

    # Free dragging: no grid, just kept inside the window
    notes = DragGroup(
        DragObject(40, 420, 140, 90, bg=(250, 230, 120), bounds=screen.get_rect()),
        DragObject(220, 440, 140, 90, bg=(150, 220, 250), bounds=screen.get_rect()),
    )
    tips.attach(notes.items[0], "Sticky notes have no grid - drop them anywhere.")

    mouse = MouseInput()
    mouse.bind("use", "right")
    message = Label(520, 340, "", fg=(120, 255, 160))
    totals = Label(520, 290, "")
    update_totals()


def handle_inputs():
    """Check every event: quitting, keys, mouse, controllers."""
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            sys.exit()

        # >>> Objects that react to events go here
        mouse.handle_event(event)
        if not items.handle_event(event):      # the items get the mouse first
            notes.handle_event(event)


def update(tick):
    """Move, animate and check things."""
    # >>> Objects with update(tick) go here
    mouse.update(tick)
    items.update(tick)
    tips.update(tick)

    if mouse.was_pressed("use"):
        for item in items:
            if item.rect.collidepoint(mouse.pos):
                if item.is_kind("potion"):
                    message.config(text=f"Drank the {item.name}: +{item.stats['heals']} HP")
                    items.remove(item)                  # also takes it out of its grid
                    tips.detach(item)
                else:
                    message.config(text=f"You can't use the {item.name}")


def draw_game():
    """Draw everything, then show it."""
    screen.fill((30, 30, 30))

    # >>> Objects with draw(screen) go here
    Label(40, 80, "Backpack", font_size=30).draw(screen)
    Label(520, 80, "Equipment", font_size=30).draw(screen)
    backpack.draw(screen)                      # green / red shows if a drop is allowed
    equipment.draw(screen)
    notes.draw(screen)
    items.draw(screen)                         # the dragged item is drawn on top
    totals.draw(screen)
    message.draw(screen)
    Label(40, 560, "Drag items into the slots. Hover for stats. Right-click a potion.",
          font_size=22).draw(screen)
    tips.draw(screen)                          # tooltips last, on top of everything

    pg.display.flip()


# ---------- Main program ----------
init_pygame()
while True:
    tick = clock.tick(FPS)   # tick = milliseconds since the last frame (used for animation)
    handle_inputs()
    update(tick)
    draw_game()
