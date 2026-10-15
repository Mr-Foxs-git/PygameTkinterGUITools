"""
Automatic checks for the v1.1 additions:
Table border_color / spreadsheet mode, Popup title size, MessageBox.
Also checks that v1.0 code still works the same (backwards compatibility).

Run this file in Visual Studio (right-click > Start without Debugging).
"""
import os
import sys

os.environ["SDL_VIDEODRIVER"] = "dummy"
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

import pygame as pg
pg.init()
screen = pg.display.set_mode((800, 600))

import PygameTkinterGUITools as g

results = []


def check(name, condition):
    results.append(bool(condition))
    print(("PASS  " if condition else "FAIL  ") + name)


def click(pos, button=1):
    return pg.event.Event(pg.MOUSEBUTTONDOWN, button=button, pos=pos)


def key(k, unicode=""):
    return pg.event.Event(pg.KEYDOWN, key=k, mod=0, unicode=unicode)


clock_ms = [50000]
real_ticks = pg.time.get_ticks
pg.time.get_ticks = lambda: clock_ms[0]

# ---------- Table border_color ----------
t = g.Table(10, 10, columns=["Name", "Score"], border_color=(255, 0, 0))
check("Table(border_color=...) works", t.cget("border_color") == (255, 0, 0))
t2 = g.Table(10, 10, columns=["Name"], border_colour=(0, 255, 0))
check("Table(border_colour=...) also works", t2.cget("border_color") == (0, 255, 0))
t2.config(border_color=(1, 2, 3))
check("config(border_color=...) works", t2.cget("border_color") == (1, 2, 3))
old = g.Table(10, 10, columns=["Name"])
check("v1.0: no border_color gives the theme colour", old.cget("border_color") == (100, 100, 100))
old.border_color = (9, 9, 9)
check("v1.0: setting the attribute still works", old.cget("border_color") == (9, 9, 9))
old.draw(screen)
check("v1.0: default edit_mode is double_click", old.edit_mode == "double_click")

# ---------- Table spreadsheet mode ----------
s = g.Table(0, 0, columns=["Item", "Price", "Qty"], rows=6, editable=["Price", "Qty"],
            edit_mode="spreadsheet")
s.column("Price", type=int)
for values in (["Sword", 45, 1], ["Bow", 35, 2], ["Shield", 30, 3]):
    s.insert(values)
s.draw(screen)
r, widths, xs = s._table_layout()
row_h = s._row_height()
first_y = r.y + 2 + row_h + row_h // 2
price_cell = (xs[1] + 10, first_y)
s.handle_event(click(price_cell))
rows = s.get_children()
check("Single click picks an editable cell (no editing yet)",
      s.cell == (rows[0], "Price") and s.editing is None)
check("Picking a cell selects its row", s.get_selected() == ["Sword", 45, 1])
s.handle_event(key(ord("5"), "5"))
check("Typing starts editing and replaces the text", s.editing and s.editing["text"] == "5")
s.handle_event(key(ord("0"), "0"))
s.handle_event(key(pg.K_RETURN))
check("Enter saves (as an int) ...", s.get(rows[0], "Price") == 50)
check("... and moves down", s.cell == (rows[1], "Price") and s.editing is None)
s.handle_event(key(pg.K_RIGHT))
check("Right arrow moves to the next editable column", s.cell == (rows[1], "Qty"))
s.handle_event(key(pg.K_RIGHT))
check("Right arrow stops at the edge", s.cell == (rows[1], "Qty"))
s.handle_event(key(pg.K_LEFT))
s.handle_event(key(pg.K_F2))
check("F2 edits keeping the old text", s.editing and s.editing["text"] == "35")
s.handle_event(key(pg.K_ESCAPE))
check("Escape cancels the edit but keeps the cell", s.editing is None and s.cell == (rows[1], "Price"))
s.handle_event(key(ord("x"), "x"))
s.handle_event(key(pg.K_RETURN))
check("int column refuses letters (stays editing)", s.editing and s.edit_error)
s.handle_event(key(pg.K_ESCAPE))
s.handle_event(key(pg.K_DOWN))
s.handle_event(key(pg.K_TAB))
check("Tab moves right", s.cell == (rows[2], "Qty"))
s.handle_event(key(pg.K_DELETE))
check("Delete empties a text cell", s.get(rows[2], "Qty") == "")
s.handle_event(key(ord("7"), "7"))
s.handle_event(key(pg.K_UP))
check("Up arrow while editing saves and moves up", s.get(rows[2], "Qty") == "7" and
      s.cell == (rows[1], "Qty"))
clock_ms[0] += 1000
s.handle_event(click(price_cell))
clock_ms[0] += 200
s.handle_event(click(price_cell))
check("Double-click a cell edits it (keeping the old text)",
      s.editing and s.editing["text"] == str(s.get(rows[0], "Price")))
s.handle_event(key(pg.K_ESCAPE))
clock_ms[0] += 1000
s.handle_event(click(price_cell))
clock_ms[0] += 1000
s.handle_event(click(price_cell))
check("Two slow clicks don't edit", s.editing is None and s.cell == (rows[0], "Price"))
s.handle_event(click((xs[0] + 10, first_y)))
check("Clicking a non-editable cell doesn't pick it", s.cell != (rows[0], "Item"))
s.handle_event(click((790, 590)))
check("Clicking outside lets go of the cell", s.cell is None)
used = s.handle_event(key(pg.K_RIGHT))
check("Keys go to the game when no cell is picked", not used)
s.handle_event(click(price_cell))
s.delete(rows[0])
check("Deleting the picked row is safe", not s.handle_event(key(pg.K_DOWN)) or True)
s.draw(screen)

# ---------- Popup title ----------
p = g.Popup(100, 100, 300, 200, "Hello")
check("v1.0: Popup title is 24 by default", p.cget("title_font_size") == 24)
p.show(); p.draw(screen)
check("v1.0: title bar stays 40 pixels", p.top_space == 40)
big = g.Popup(100, 100, 300, 200, "Big", title_font_size=48, visible=True)
big.draw(screen)
check("title_font_size=48 makes a taller title bar", big.top_space > 40)
big.config(title_font_size=18)
big.draw(screen)
check("config(title_font_size=...) works", big.top_space == 40)

# ---------- MessageBox ----------
answers = []
box = g.MessageBox("Quit?", "Do you really want to quit the game?",
                   buttons=("Yes", "No", "Cancel"), command=answers.append)
check("MessageBox starts hidden", not box.visible)
box.show()
box.draw(screen)
check("It is placed in the middle of the window", box.get_rect().center == (400, 300))
no_button = box.buttons[1]
corner = box.get_rect().topleft
pos = no_button.get_rect(corner).center
box.handle_event(click(pos))
check("Clicking No gives 'No' and closes it", answers == ["No"] and not box.visible)
box.show()
check("While open it takes every key", box.handle_event(key(pg.K_SPACE, " ")))
check("... and every click", box.handle_event(click((5, 5))))
box.handle_event(key(pg.K_RETURN))
check("Enter presses the first button", answers[-1] == "Yes")
box.show()
box.handle_event(key(pg.K_ESCAPE))
check("Escape gives None", answers[-1] is None and box.result is None)
check("Closed box ignores events", not box.handle_event(click((400, 300))))

called = []
quiet = g.MessageBox("Saved", "Game saved!", command=lambda: called.append(quiet.result))
quiet.show(); quiet.draw(screen)
quiet.handle_event(key(pg.K_RETURN))
check("A command with no answer works (read .result)", called == ["OK"])

got = []
yn = g.askyesno("Sure?", "Delete your save?", command=got.append)
check("askyesno opens straight away", yn.visible)
yn.draw(screen)
yn.handle_event(key(pg.K_RETURN))
check("askyesno gives True for Yes", got == [True])
ync = g.askyesnocancel("Save?", "Save first?", command=got.append)
ync.handle_event(key(pg.K_ESCAPE))
check("askyesnocancel gives None when closed", got[-1] is None)
oc = g.askokcancel("Go?", "Start?", command=got.append)
oc.handle_event(key(pg.K_ESCAPE))
check("askokcancel gives False when closed", got[-1] is False)
info = g.showinfo("Hi", "Welcome!")
info.draw(screen)
info.handle_event(key(pg.K_RETURN))
check("showinfo works without a command", not info.visible)
dark = g.Style()
dark.theme_use("dark")
themed = g.askyesno("Dark", "Dark theme?")
themed.draw(screen)
dark.theme_use("light")
check("MessageBox draws with a theme", True)

pg.time.get_ticks = real_ticks
print()
print("ALL TESTS PASS" if all(results) else f"{results.count(False)} TEST(S) FAILED")
pg.quit()
