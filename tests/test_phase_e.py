"""
Automatic checks for the new widgets, Variables, Style and FocusGroup.

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


def click(pos):
    return pg.event.Event(pg.MOUSEBUTTONDOWN, button=1, pos=pos)


def release(pos):
    return pg.event.Event(pg.MOUSEBUTTONUP, button=1, pos=pos)


def drag(pos):
    return pg.event.Event(pg.MOUSEMOTION, pos=pos, rel=(0, 0), buttons=(1, 0, 0))


def key(k, mod=0, unicode=""):
    return pg.event.Event(pg.KEYDOWN, key=k, mod=mod, unicode=unicode)


# ---------- Variables ----------
v = g.IntVar(5)
changes = []
v.trace_add("write", lambda: changes.append(v.get()))
v.set("7")
check("IntVar converts and stores", v.get() == 7)
check("trace_add runs on change", changes == [7])
check("BooleanVar / StringVar / DoubleVar",
      g.BooleanVar(1).get() is True and g.StringVar(3).get() == "3" and g.DoubleVar(2).get() == 2.0)

# ---------- Style ----------
style = g.Style()
style.reset()
b = g.Button(10, 10, 100, 40, "B")
check("Button gets its bg from the light theme", b.cget("bg") == (100, 150, 255))
style.configure("TButton", bg=(1, 2, 3))          # ttk name
check("style.configure('TButton') changes existing buttons", b.cget("bg") == (1, 2, 3))
b2 = g.Button(10, 10, 100, 40, "B", bg=(9, 9, 9))
check("A widget's own option beats the Style", b2.cget("bg") == (9, 9, 9))
style.configure("Danger.Button", bg=(255, 0, 0))
b3 = g.Button(10, 10, 100, 40, "B", style="Danger.Button")
check("Named style (Danger.Button)", b3.cget("bg") == (255, 0, 0) and b3.cget("fg") == g.BLACK)
style.configure(".", font_size=40)
check("'.' sets every widget", g.Label(0, 0, "x").cget("font_size") == 40)
check("Specific beats '.' (Button font_size 30)", b.cget("font_size") == 30)
style.theme_use("dark")
check("theme_use('dark')", g.Frame(0, 0, 10, 10).cget("bg") == (40, 40, 50))
check("Label stays see-through in dark theme", g.Label(0, 0, "x").cget("bg") is None)
try:
    style.theme_use("pink")
    check("Unknown theme gives an error", False)
except ValueError:
    check("Unknown theme gives an error", True)
style.reset()
check("reset() goes back to light", b.cget("bg") == (100, 150, 255))

# ---------- Every widget draws in every theme ----------
music = g.BooleanVar(True)
level = g.StringVar("Easy")
all_widgets = [
    g.Label(0, 0, "hi"), g.Message(0, 0, "a long message " * 10, width=200),
    g.Button(0, 0, 80, 30, "b"), g.Separator(0, 0, 100), g.TextBox(0, 0, label="n"),
    g.Checkbutton(0, 0, "c", variable=g.BooleanVar()),
    g.Radiobutton(0, 0, "r", variable=g.StringVar(), value="Easy"),
    g.Scale(0, 0), g.Scale(0, 0, orient="vertical"), g.Spinbox(0, 0),
    g.Listbox(0, 0, items=list(range(20))), g.Combobox(0, 0, values=["a", "b"]),
    g.Progressbar(0, 0, value=50, show_text=True), g.Progressbar(0, 0, mode="indeterminate"),
    g.Progressbar(0, 0, orient="vertical", value=30),
    g.Frame(0, 0, 100, 100), g.LabelFrame(0, 0, 100, 100, "LF"),
    g.Notebook(0, 0, 200, 200), g.Popup(0, 0, 200, 200, visible=True),
]
ok = True
for theme in ("light", "dark", "retro"):
    style.theme_use(theme)
    for w in all_widgets:
        try:
            w.update(16)
            w.draw(screen)
            w.handle_event(click((5, 5)))
        except Exception as error:
            ok = False
            print("   ", theme, type(w).__name__, error)
check("Every widget draws / updates / handles events in every theme", ok)
style.reset()

# ---------- Message ----------
m = g.Message(0, 0, "one two three four five six seven eight nine ten", width=120)
check("Message wraps onto several lines", len(m._lines()) > 1)
check("Message \\n starts a new line", len(g.Message(0, 0, "a\nb", width=500)._lines()) == 2)

# ---------- Checkbutton / Radiobutton ----------
hits = []
c = g.Checkbutton(100, 100, "Music", variable=music, command=lambda: hits.append("c"))
c.handle_event(click(c.rect.center))
check("Checkbutton click unticks and runs command", music.get() is False and hits == ["c"])
c.handle_event(click(c.rect.center))
check("Checkbutton click ticks again", music.get() is True)
r1 = g.Radiobutton(100, 200, "Easy", variable=level, value="Easy")
r2 = g.Radiobutton(100, 240, "Hard", variable=level, value="Hard")
r2.handle_event(click(r2.rect.center))
check("Radiobutton group: one choice", level.get() == "Hard" and r2.is_selected()
      and not r1.is_selected())
r1.config(state="disabled")
r1.handle_event(click(r1.rect.center))
check("Disabled widget ignores clicks", level.get() == "Hard")

# ---------- Scale ----------
vol = g.IntVar(0)
s = g.Scale(100, 100, from_=0, to=100, length=200, variable=vol)
bar = s._bar(s.rect)
s.handle_event(click((bar.x + 100, bar.centery)))
check("Scale click sets value", vol.get() == 50)
s.handle_event(drag((bar.x + 150, bar.centery)))
check("Scale drag", vol.get() == 75)
s.handle_event(release((bar.x + 150, bar.centery)))
s.handle_event(drag((bar.x + 10, bar.centery)))
check("Scale stops after release", vol.get() == 75)
s.set(500)
check("Scale value limited to 'to'", vol.get() == 100)
fine = g.Scale(0, 0, from_=0, to=1, resolution=0.1)
fine.set(0.37)
check("Scale resolution 0.1", fine.get() == 0.4)

# ---------- Spinbox ----------
sp = g.Spinbox(100, 100, from_=1, to=3)
up, down = sp._buttons(sp.rect)
sp.handle_event(click(up.center)); sp.handle_event(click(up.center)); sp.handle_event(click(up.center))
check("Spinbox up stops at 'to'", sp.get() == 3)
sp.handle_event(click(down.center))
check("Spinbox down", sp.get() == 2)
cols = g.Spinbox(0, 0, values=["Red", "Green", "Blue"], wrap=True)
cols.step(-1)
check("Spinbox values + wrap", cols.get() == "Blue")

# ---------- Listbox ----------
chosen = []
lb = g.Listbox(100, 100, 200, rows=3, items=["a", "b", "c", "d", "e"],
               command=lambda: chosen.append(lb.get_selected()))
row_h = lb._row_height()
lb.handle_event(click((150, 100 + 2 + row_h + 2)))
check("Listbox click chooses item", lb.curselection() == (1,) and chosen == ["b"])
lb.see(4)
check("Listbox see() scrolls", lb.scroll == 2)
lb.insert("end", "f"); lb.delete(0)
check("Listbox insert / delete", lb.items == ["b", "c", "d", "e", "f"] and lb.size() == 5)

# ---------- Combobox ----------
hero = g.StringVar("Knight")
cb = g.Combobox(100, 100, 200, values=["Knight", "Wizard", "Archer"], textvariable=hero)
under = g.Button(100, 140, 200, 40, "under", command=lambda: chosen.append("under"))
frame = g.Frame(0, 0, 800, 600, pad_x=0, pad_y=0)
frame.add(under, cb)
frame.handle_event(click(cb.rect.center))
check("Combobox opens on click", cb.is_open)
lst = cb._list_rect(cb.rect)
frame.handle_event(click((lst.x + 20, lst.y + 2 + cb._row_height() + 3)))
check("Combobox choice, and the click doesn't reach the button underneath",
      hero.get() == "Wizard" and not cb.is_open and "under" not in chosen)
check("Combobox current()", cb.current() == 1)
frame.draw(screen)

# ---------- Progressbar ----------
hp = g.Progressbar(0, 0, maximum=100, value=100)
hp.step(-30)
check("Progressbar step", hp.value == 70)
hp.config(value=500)
check("Progressbar value limited to maximum", hp.value == 100)
check("Progressbar fraction", g.Progressbar(0, 0, maximum=5, value=2).fraction() == 0.4)

# ---------- Notebook / LabelFrame / parents ----------
nb = g.Notebook(100, 100, 400, 300)
tab1 = nb.new_tab("One")
tab2 = nb.new_tab("Two")
b_tab1 = tab1.add(g.Button(0, 0, 80, 30, "t1", command=lambda: chosen.append("t1")))
b_tab2 = tab2.add(g.Button(0, 0, 80, 30, "t2", command=lambda: chosen.append("t2")))
check("Widget on the shown tab is active", b_tab1.active and not b_tab2.active)
tab_rects = nb._tab_rects(nb.rect)
nb.handle_event(click(tab_rects[1].center))
check("Click a tab to switch", nb.select() == 1 and b_tab2.active and not b_tab1.active)
inside = tab2.child_offset((nb.rect.x, nb.rect.y + nb.tab_height))
nb.handle_event(click((inside[0] + 5, inside[1] + 5)))
check("Button on a tab clicks", chosen[-1] == "t2")
lf = g.LabelFrame(0, 0, 200, 100, "Group")
lf.add(g.Label(0, 0, "x"))
lf.draw(screen)
check("LabelFrame children start below the title", lf.child_offset()[1] > 10)
pop = g.Popup(0, 0, 200, 200)
pb = pop.add(g.Button(0, 0, 50, 20, "p"))
check("Widgets in a closed Popup are not active", not pb.active)

# ---------- FocusGroup ----------
pressed = []
fb1 = g.Button(0, 0, 50, 20, "1", command=lambda: pressed.append(1))
fb2 = g.Button(0, 40, 50, 20, "2", command=lambda: pressed.append(2))
fs = g.Scale(0, 80, from_=0, to=10)
focus = g.FocusGroup(fb1, fb2, fs)
check("FocusGroup is off by default", not focus.handle_event(key(pg.K_DOWN)) and not fb1.focused)
focus.active = True
check("Turning it on highlights the first widget", fb1.focused)
check("Arrow down moves focus (and returns True)", focus.handle_event(key(pg.K_DOWN)) and fb2.focused)
focus.handle_event(key(pg.K_RETURN))
check("Enter presses the focused button", pressed == [2])
focus.handle_event(key(pg.K_DOWN))
focus.handle_event(key(pg.K_RIGHT)); focus.handle_event(key(pg.K_RIGHT))
check("Left / right change a focused Scale", fs.get() == 2)
check("Other keys are left for the game", focus.handle_event(key(pg.K_a)) is False)
fb2.hide()
focus.handle_event(key(pg.K_UP))
check("Hidden widgets are skipped", fb1.focused)
focus.active = False
check("Turning it off removes the highlight and ignores keys",
      not fb1.focused and focus.handle_event(key(pg.K_DOWN)) is False)

tab_focus = g.FocusGroup(fb1, fs, keys="tab", active=True)
tab_focus.handle_event(key(pg.K_DOWN))
check("keys='tab': arrow keys don't move focus", fb1.focused)
tab_focus.handle_event(key(pg.K_TAB))
check("keys='tab': Tab moves focus", fs.focused)
tab_focus.handle_event(key(pg.K_TAB, mod=pg.KMOD_SHIFT))
check("keys='tab': Shift+Tab goes back", fb1.focused)

tb = g.TextBox(0, 0, max_chars=10)
text_focus = g.FocusGroup(tb, fb1, active=True)
text_focus.handle_event(key(pg.K_RETURN))
for ch in "hi":
    text_focus.handle_event(key(ord(ch), unicode=ch))
text_focus.handle_event(key(pg.K_DOWN))
check("Focused TextBox: Enter starts typing, keys type (even arrows)", tb.get() == "hi" and tb.focused)
text_focus.handle_event(key(pg.K_RETURN))
text_focus.handle_event(key(pg.K_DOWN))
check("Enter stops typing, then arrows move focus again", fb1.focused)

name = g.StringVar("Sam")
tv = g.TextBox(0, 0, textvariable=name)
tv.insert_text("!")
check("TextBox textvariable stays in sync", name.get() == "Sam!" and tv.get() == "Sam!")
name.set("Alex")
check("Changing the variable changes the TextBox", tv.get() == "Alex")

print()
print("ALL TESTS PASS" if all(results) else f"{results.count(False)} TEST(S) FAILED")
pg.quit()
