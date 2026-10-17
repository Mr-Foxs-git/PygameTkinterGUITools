"""
Automatic checks for Cursor (changing the mouse pointer) and the cursor= option.

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
from PygameTkinterGUITools import Cursor

ASSETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "examples", "assets")
results = []


def check(name, condition):
    results.append(bool(condition))
    print(("PASS  " if condition else "FAIL  ") + name)


# The mouse is moved by changing what pg.mouse.get_pos() returns
mouse_at = [(0, 0)]
real_get_pos = pg.mouse.get_pos
pg.mouse.get_pos = lambda: mouse_at[0]


def frame(*widgets, at=(0, 0)):
    """One game frame: draw the widgets, then Cursor.update() picks the pointer."""
    mouse_at[0] = at
    for widget in widgets:
        widget.draw(screen)
    Cursor.update(16)
    return Cursor.current


# ---- Names ----
Cursor.reset()
check("starts as the normal arrow", Cursor.current == "arrow" and Cursor.normal == "arrow")
Cursor.set("crosshair")
check("set() a built-in name", Cursor.current == "crosshair")
Cursor.set("hand2")
check("tkinter name hand2 -> hand", Cursor.current == "hand")
check("tkinter names xterm / watch / fleur",
      [Cursor._name_of(n) for n in ("xterm", "watch", "fleur")] == ["text", "wait", "move"])
try:
    Cursor.set("hnad")
    check("a typo gives a clear error", False)
except ValueError as error:
    check("a typo gives a clear error that lists the names", "crosshair" in str(error))
Cursor.reset()

# ---- Pictures and hotspots ----
Cursor.add("aim", os.path.join(ASSETS, "crosshair.png"), hotspot="center")
check("hotspot='center' is the middle", Cursor.pictures["aim"]["hotspot"] == (16, 16))
Cursor.add("big", os.path.join(ASSETS, "crosshair.png"), hotspot="center", size=64)
check("size= scales the picture", Cursor.pictures["big"]["image"].get_size() == (64, 64)
      and Cursor.pictures["big"]["hotspot"] == (32, 32))
Cursor.add("hand_pic", os.path.join(ASSETS, "hand.png"), hotspot=(11, 1))
check("hotspot (x, y)", Cursor.pictures["hand_pic"]["hotspot"] == (11, 1))
try:
    Cursor.add("bad", os.path.join(ASSETS, "hand.png"), hotspot=(50, 1))
    check("hotspot outside the picture is an error", False)
except ValueError:
    check("hotspot outside the picture is an error", True)

Cursor.set("aim")
check("set() a picture name", Cursor.current == "aim")
# The dummy video driver can't show picture pointers, so it must switch to drawing it
check("falls back to drawn mode when pictures can't be pointers",
      Cursor.pictures["aim"]["drawn"] is True)
screen.fill((0, 0, 0))
mouse_at[0] = (100, 100)
Cursor.draw(screen)
check("draw() puts the picture's hotspot on the mouse",
      screen.get_at((100, 100))[:3] != (0, 0, 0) or screen.get_at((84, 100))[:3] != (0, 0, 0))
Cursor.set(pg.Surface((10, 10)))
check("set() a Surface makes a picture", Cursor.current == "picture")
Cursor.set(os.path.join(ASSETS, "crosshair_red.png"), hotspot="center")
check("set() a file name makes a picture", Cursor.pictures[Cursor.current]["hotspot"] == (16, 16))
Cursor.add("drawn_aim", os.path.join(ASSETS, "crosshair.png"), drawn=True)
check("drawn=True asks for drawn mode", Cursor.pictures["drawn_aim"]["drawn"] is True)
Cursor.hide()
screen.fill((0, 0, 0))
Cursor.set("drawn_aim")
Cursor.draw(screen)
check("hide() draws nothing", screen.get_at((101, 101))[:3] == (0, 0, 0))
Cursor.show()
Cursor.reset()

# ---- Widgets with cursor= ----
play = g.Button(10, 10, 100, 40, "Play", cursor="hand")
check("Button(cursor=...) keyword", play.cursor == "hand")
label = g.Label(10, 100, "Hi")
check("widgets without cursor= have None", label.cursor is None)
label.config(cursor="text")
check("config(cursor=...) works on any widget", label.cget("cursor") == "text")
label.config(cursor=None)

Cursor.set("crosshair")
check("mouse over a widget with a cursor", frame(play, at=(20, 20)) == "hand")
check("mouse away from it -> normal pointer", frame(play, at=(300, 300)) == "crosshair")
check("a widget not drawn this frame is ignored", frame(at=(20, 20)) == "crosshair")
play.config(state="disabled")
check("disabled widget -> normal pointer", frame(play, at=(20, 20)) == "crosshair")
play.config(state="normal")
play.hide()
check("hidden widget -> normal pointer", frame(play, at=(20, 20)) == "crosshair")
play.show()

# Top-most (drawn last) wins
under = g.Button(10, 10, 100, 40, "Under", cursor="wait")
check("the widget drawn last is on top", frame(under, play, at=(20, 20)) == "hand")
check("...in either order", frame(play, under, at=(20, 20)) == "wait")

# A Frame's cursor is used by the children that don't have one (like tkinter)
panel = g.Frame(300, 0, 200, 300, cursor="arrow")
inside_label = g.Label(panel, text="Name")
inside_label.place(x=10, y=10)
inside_button = g.Button(panel, text="OK", cursor="hand")
inside_button.place(x=10, y=100)
check("a child without a cursor uses its Frame's", frame(panel, at=(325, 25)) == "arrow")
button_rect = inside_button.get_rect(inside_button._last_offset)
check("a child with a cursor uses its own", frame(panel, at=button_rect.center) == "hand")
inside_button.config(state="disabled")
check("a disabled child falls back to the Frame's", frame(panel, at=button_rect.center) == "arrow")

# A Popup covers what is under it
cover = g.Popup(0, 0, 200, 200, title="Paused", dim=False, visible=True)
check("a Popup on top hides the cursor of widgets under it",
      frame(play, cover, at=(20, 20)) == "crosshair")
check("...but not widgets beside it", frame(play, cover, at=(20, 20)) == "crosshair"
      and frame(g.Button(300, 300, 50, 50, cursor="hand"), cover, at=(310, 310)) == "hand")
dimmed = g.Popup(0, 0, 200, 200, title="Paused", visible=True)
check("a dimmed Popup covers the whole screen",
      frame(g.Button(300, 300, 50, 50, cursor="hand"), dimmed, at=(310, 310)) == "crosshair")

# Widgets that scrolled out of a ScrolledFrame's view don't count
scroller = g.ScrolledFrame(0, 400, 200, 100)
hidden_button = g.Button(scroller, text="Far down", width=100, height=40, cursor="hand")
hidden_button.place(x=0, y=300)
spacer = g.Label(scroller, text="spacer")
spacer.place(x=0, y=0)
spot = hidden_button.get_rect(scroller.child_offset((0, 0))).center
scroller.draw(screen)
check("button scrolled out of view -> normal pointer", frame(scroller, at=spot) == "crosshair")

# ---- attach() ----
Cursor.reset()
Cursor.add("aim", os.path.join(ASSETS, "crosshair.png"), hotspot="center")
enemy = g.SpriteObject(400, 400, 40, 40)
Cursor.attach(enemy, "aim")
check("attach: mouse over the sprite", frame(at=(410, 410)) == "aim")
check("attach: mouse away", frame(at=(10, 10)) == "arrow")
check("a widget's cursor beats an attach()", frame(g.Button(400, 400, 50, 50, cursor="hand"),
                                                   at=(410, 410)) == "hand")


class FakeCamera:
    """The world is scrolled 1000 pixels to the right."""
    def screen_to_world(self, pos):
        return (pos[0] + 1000, pos[1])


far_enemy = g.SpriteObject(1400, 100, 40, 40)
Cursor.attach(far_enemy, "wait", camera=FakeCamera())
check("attach with a camera uses world positions", frame(at=(410, 110)) == "wait")

group = pg.sprite.Group()
dying = g.SpriteObject(100, 300, 40, 40)
group.add(dying)
Cursor.attach(dying, "no")
check("attach: sprite in a group", frame(at=(110, 310)) == "no")
dying.kill()
check("attach: killed sprites are forgotten", frame(at=(110, 310)) == "arrow"
      and all(t[0] is not dying for t in Cursor.targets))
Cursor.detach(enemy)
check("detach()", frame(at=(410, 410)) == "arrow")

# ---- Scenes undo set() and attach() ----
Cursor.reset()
scenes = g.Scenes()
scenes.add("game", start=lambda: (Cursor.set("crosshair"), Cursor.attach(enemy, "wait")))
scenes.add("menu")
check("scene set the pointer", Cursor.normal == "crosshair" and len(Cursor.targets) == 1)
scenes.switch("menu")
check("leaving the scene undoes set() and attach()",
      Cursor.normal == "arrow" and Cursor.targets == [])

# ---- Backwards compatibility (v1.0) ----
Cursor.reset()
old_button = g.Button(10, 10, 100, 40, "Old")
check("old Button positional call still works", old_button.text == "Old" and old_button.cursor is None)
box = g.TextBox(10, 10)
check("TextBox's text cursor is a different thing",
      box.cursor is None and hasattr(box, "cursor_pos"))
check("widgets without a cursor never change the pointer", frame(old_button, at=(20, 20)) == "arrow")
widget_types = [g.Label(0, 0), g.Message(0, 0), g.Button(0, 0), g.Separator(0, 0), g.TextBox(0, 0),
                g.Checkbutton(0, 0), g.Radiobutton(0, 0), g.Scale(0, 0), g.Spinbox(0, 0),
                g.Listbox(0, 0), g.Combobox(0, 0), g.Progressbar(0, 0), g.Frame(0, 0),
                g.ScrolledFrame(0, 0), g.Table(0, 0), g.LabelFrame(0, 0), g.Notebook(0, 0),
                g.Popup(0, 0), g.HeartsBar(0, 0), g.Dialogue(0, 0)]
check("every widget has a cursor option (None)", all(w.cursor is None for w in widget_types))
made = [cls(0, 0, cursor="hand") for cls in (g.Label, g.Message, g.Button, g.Separator,
        g.TextBox, g.Checkbutton, g.Radiobutton, g.Scale, g.Spinbox, g.Listbox, g.Combobox,
        g.Progressbar, g.Frame, g.ScrolledFrame, g.Table, g.LabelFrame, g.Notebook, g.Popup,
        g.HeartsBar, g.Dialogue)]
check("every widget accepts cursor=", all(w.cursor == "hand" for w in made))
check("MessageBox and Root accept cursor=",
      g.MessageBox("Hi", "There", cursor="hand").cursor == "hand"
      and g.Root(screen, cursor="hand").cursor == "hand")

pg.mouse.get_pos = real_get_pos
Cursor.reset()
print()
print("ALL TESTS PASS" if all(results) else f"{results.count(False)} TEST(S) FAILED")
pg.quit()
