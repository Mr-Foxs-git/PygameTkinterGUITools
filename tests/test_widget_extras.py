"""
Automatic checks for the widget extras (ideas 1 - 14):
TextBox show / placeholder / allowed / on_change, askstring / askinteger,
Label outline / shadow / "\\n" / justify, Button active_bg / sound / repeat,
Progressbar low_color / animate, Health.draw_bar, Combobox editable,
Listbox selectmode="multiple", fades and slides, the high_contrast theme.
Also checks that the defaults still work exactly like v1.0.

Run this file in Visual Studio (right-click > Start without Debugging).
"""
import os
import sys

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

import pygame as pg
pg.init()
screen = pg.display.set_mode((800, 600))

import PygameTkinterGUITools as g

ASSETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "examples", "assets")
results = []

# A pretend clock, so fades and animations can be checked without waiting
clock_now = [100000]
pg.time.get_ticks = lambda: clock_now[0]


def wait(ms):
    clock_now[0] += ms


def check(name, condition):
    results.append(bool(condition))
    print(("PASS  " if condition else "FAIL  ") + name)


def key(character, code=None):
    if code is None:
        code = ord(character.lower())
    return pg.event.Event(pg.KEYDOWN, key=code, unicode=character, mod=0)


ENTER = key("\r", pg.K_RETURN)
ESCAPE = key("", pg.K_ESCAPE)


def click(x, y):
    return pg.event.Event(pg.MOUSEBUTTONDOWN, button=1, pos=(x, y))


# ---- TextBox (#1 - #3) ----
changes = []
pin = g.TextBox(10, 10, max_chars=4, allowed="digits", show="*", placeholder="PIN",
                on_change=lambda: changes.append(1))
check("on_change is not run for the starting text", changes == [])
pin.typing = True
for ch in "1a2b3":
    pin.handle_event(key(ch))
check("allowed='digits' only lets digits in", pin.get() == "123")
check("show='*' draws stars, get() gives the real text", pin._shown_text() == "***")
check("on_change runs once per change", len(changes) == 3)
pin.config(show="#")
check("config(show='#') changes the character", pin._shown_text() == "###")
pin.show()
pin.hide()
pin.show()
check("box.show() still shows the box (show= doesn't replace it)", pin.visible)
pin.set_text("abc")
check("set_text() is not limited by allowed", pin.get() == "abc")
letters = g.TextBox(10, 10, allowed="letters")
letters.typing = True
for ch in "a1b2":
    letters.handle_event(key(ch))
check("allowed='letters'", letters.get() == "ab")
custom = g.TextBox(10, 10, allowed="0123456789.")
custom.typing = True
for ch in "3.5x":
    custom.handle_event(key(ch))
check("allowed='0123456789.'", custom.get() == "3.5")
plain = g.TextBox(10, 10)
plain.typing = True
for ch in "Hi 5!":
    plain.handle_event(key(ch))
check("v1.0: any key can be typed", plain.get() == "Hi 5!")
empty = g.TextBox(10, 10, max_chars=3, placeholder="a long hint that does not fit")
empty.draw(screen)
check("placeholder draws without crashing (even when too long)", True)

# ---- askstring / askinteger (#4) ----
answers = []
box = g.askstring("Name", "Your name?", command=lambda value: answers.append(value))
check("askstring opens straight away", box.visible)
for ch in "Sam":
    box.handle_event(key(ch))
box.draw(screen)
box.handle_event(ENTER)
check("askstring gives the typed text", answers == ["Sam"] and not box.visible)
box = g.askstring("Name", "Your name?", command=lambda value: answers.append(value))
box.handle_event(key("x"))
box.handle_event(ESCAPE)
check("askstring gives None for Escape", answers[-1] is None)
numbers = []
box = g.askinteger("Age", "How old?", command=lambda value: numbers.append(value),
                   minvalue=5, maxvalue=99)
for ch in "1x2":
    box.handle_event(key(ch))
check("askinteger only lets digits in", box.entry.get() == "12")
box.handle_event(ENTER)
check("askinteger gives an int", numbers == [12])
box = g.askinteger("Age", "How old?", command=lambda value: numbers.append(value),
                   minvalue=5, maxvalue=99)
box.handle_event(key("3"))
box.handle_event(ENTER)
check("too small: the box stays open and says the range",
      box.visible and "5 to 99" in box.message and numbers == [12])
box.draw(screen)
box.handle_event(ESCAPE)
check("askinteger gives None for Escape", numbers == [12, None])

# ---- Label (#5, #6) ----
font = g.get_font(None, 24)
score = g.Label(10, 10, "Score: 0")
check("v1.0: a plain Label is exactly its text's size", (score.width, score.height) == font.size("Score: 0"))
two_lines = g.Label(10, 10, "One\nTwo longer", justify="center")
two_lines.draw(screen)
check("'\\n' makes two lines", two_lines.height >= font.get_height() * 2)
check("the Label is as wide as its longest line", two_lines.width == font.size("Two longer")[0])
outlined = g.Label(10, 10, "Hi", outline=2)
check("outline makes room on each side", outlined.width == font.size("Hi")[0] + 4)
shadowed = g.Label(10, 10, "Hi", shadow=True, shadow_colour=(0, 0, 0))
check("shadow makes room for itself", shadowed.width == font.size("Hi")[0] + 2)
shadowed.config(outline_colour=(255, 0, 0), outline=1)
shadowed.draw(screen)
check("outline_colour works in config()", shadowed.outline_color == (255, 0, 0))
picture = outlined._text_picture()
check("the outlined text is kept, not drawn again every frame",
      outlined._text_picture() is picture)

# ---- Button (#7, #8) ----
presses = []
plus = g.Button(0, 0, 100, 50, "+", command=lambda: presses.append(1),
                repeatdelay=400, repeatinterval=100, active_bg=(1, 2, 3),
                sound=os.path.join(ASSETS, "sounds", "click.wav"))
check("sound= with a file name makes a SoundEffect", isinstance(plus.sound, g.SoundEffect))
plus.handle_event(click(10, 10))
check("the command runs on the click", presses == [1] and plus.pressed)
plus.is_hovered = lambda offset=(0, 0): True        # pretend the mouse stays on it
for frame in range(10):
    plus.update(50)                                  # held for 500 ms
check("held: repeats after repeatdelay, then every repeatinterval", len(presses) == 3)
plus.draw(screen)
up = pg.event.Event(pg.MOUSEBUTTONUP, button=1, pos=(10, 10))
check("letting go is not used up (other code gets it too)", plus.handle_event(up) is False)
plus.update(1000)
check("no repeats after letting go", len(presses) == 3 and not plus.pressed)
normal = g.Button(0, 0, 100, 50, "x", command=lambda: presses.append(2))
normal.handle_event(click(10, 10))
normal.update(5000)
check("v1.0: no repeat unless asked for", presses.count(2) == 1)

# ---- Progressbar (#9) ----
bar = g.Progressbar(0, 0, 200, value=100, animate=True, low_colour=(255, 0, 0))
bar.draw(screen)
bar.value = 50
bar.draw(screen)
check("animate: the bar drops at once, the ghost stays", bar._shown == 50 and bar._ghost == 100)
wait(500)
bar.draw(screen)
wait(50)
bar.draw(screen)
check("the ghost shrinks after a moment", 50 <= bar._ghost < 100)
bar.value = 10
screen.fill((0, 0, 0))
bar.draw(screen)
check("low_color when nearly empty", screen.get_at((5, 10))[:3] == (255, 0, 0))
bar.value = 60
bar.draw(screen)
check("going up slides up", 10 <= bar._shown < 60)
plain_bar = g.Progressbar(0, 0, 200, value=10)
screen.fill((0, 0, 0))
plain_bar.draw(screen)
check("v1.0: the bar colour doesn't change when low", screen.get_at((5, 10))[:3] == (80, 200, 120))
picture_bar = g.Progressbar(0, 0, 200, orient="vertical", value=100, animate=True,
                            bar_image=os.path.join(ASSETS, "hearts_full.png"))
picture_bar.draw(screen)
picture_bar.value = 40
picture_bar.draw(screen)
check("animate works with a bar picture", picture_bar._ghost == 100)

# ---- Health.draw_bar (#10) ----
health = g.Health(30)
enemy = g.SpriteObject(100, 100, 32, 32)
camera = g.Camera(2000, 2000, (800, 600))
health.damage(10)
health.draw_bar(screen, enemy, camera, low_color=(255, 0, 0))
floating = health._floating_bar
check("draw_bar shows the health", floating.value == 20 and floating.maximum == 30)
check("draw_bar sits above the sprite", floating.x == 100 and floating.y == 100 - 6 - 6)
health.draw_bar(screen, enemy, camera)
check("draw_bar keeps the same bar", health._floating_bar is floating)
full = g.Health(10)
full.draw_bar(screen, enemy, hide_when_full=True)
check("hide_when_full draws nothing at full health", not hasattr(full, "_floating_bar"))

# ---- Combobox (#11) ----
chosen = []
heroes = g.Combobox(10, 10, 200, values=["Knight", "Wizard", "Archer", "Witch"],
                    editable=True, command=lambda: chosen.append(1))
heroes.handle_event(click(20, 20))
check("editable: clicking opens it for typing", heroes.is_open and heroes.typed == "")
heroes.handle_event(key("w"))
heroes.handle_event(key("i"))
check("typing filters the list", heroes._shown_values() == ["Wizard", "Witch"])
heroes.draw(screen)
heroes.handle_event(key("", pg.K_DOWN))
heroes.handle_event(ENTER)
check("Enter picks the highlighted match", heroes.get() == "Witch" and chosen == [1])
heroes._open()
for ch in "zz":
    heroes.handle_event(key(ch))
heroes.draw(screen)
heroes.handle_event(ENTER)
check("no match: Enter keeps the typed words", heroes.get() == "zz")
old_style = g.Combobox(10, 10, 200, values=["a", "b"])
old_style.handle_event(click(20, 20))
check("v1.0: choose-only, keys are not used", old_style.handle_event(key("x")) is False)
old_style.focus_action("down")
old_style.focus_action("activate")
check("v1.0: arrow keys still choose", old_style.get() == "b")

# ---- Listbox (#12) ----
skills = g.Listbox(0, 0, 200, items=list("abcdef"), selectmode="multiple")
for index in (1, 3, 4, 3):
    skills._choose(index)
check("multiple: clicks tick and untick", skills.curselection() == (1, 4))
check("get_all_selected()", skills.get_all_selected() == ["b", "e"])
check("selection_includes()", skills.selection_includes(4) and not skills.selection_includes(3))
skills.delete(2)
check("deleting moves the chosen items up", skills.curselection() == (1, 3))
skills.draw(screen)
skills.selection_clear()
check("selection_clear() clears every item", skills.curselection() == ())
single = g.Listbox(0, 0, 200, items=list("abc"))
single._choose(1)
single._choose(2)
check("v1.0: one item at a time", single.curselection() == (2,) and single.get_selected() == "c")
check("tkinter's 'browse' works as 'single'",
      g.Listbox(0, 0, items=["x"], selectmode="browse").selectmode == "single")
try:
    g.Listbox(0, 0, selectmode="extended")
    check("'extended' gives a clear error", False)
except ValueError as error:
    check("'extended' gives a clear error", "multiple" in str(error))

# ---- Fades and slides (#13) ----
menu = g.Frame(0, 0, 200, 200, bg=(255, 0, 0), visible=False)
menu.add(g.Button(10, 10, 50, 30, "x"))
menu.show(fade_ms=200)
screen.fill((0, 0, 0))
menu.draw(screen)
check("fading in starts see-through", screen.get_at((100, 100))[0] < 60)
wait(250)
screen.fill((0, 0, 0))
menu.draw(screen)
check("after the fade it is solid", screen.get_at((100, 100))[:3] == (255, 0, 0))
menu.hide(fade_ms=100)
check("fading out: still visible, but closing", menu.visible and menu.closing)
check("fading out: no more clicks", menu.handle_event(click(20, 20)) is False)
wait(150)
menu.draw(screen)
check("after fading out it is hidden", not menu.visible)
menu.toggle_visibility()
check("v1.0: toggle_visibility() is instant", menu.visible and menu._fade is None)
menu.hide()
check("v1.0: hide() is instant", not menu.visible)
popup = g.Popup(100, 100, 300, 200, "Hi")
popup.show(fade_ms=100)
popup.draw(screen)
question = g.askyesno("Q", "Sure?")
question.hide()
question.show(fade_ms=100)
question.draw(screen)
check("Popup and MessageBox fade without crashing", popup.visible and question.visible)
title = g.Label(0, 0, "Title")
title.hide(fade_ms=300)
check("a Label (not a container) hides straight away", not title.visible)
title.show()
title.slide_to(100, 50, ms=100)
check("slide_to: sliding", title.sliding)
wait(50)
title.get_rect()
check("slide_to: part way there", 0 < title.x < 100)
wait(60)
title.draw(screen)
check("slide_to: arrives", (title.x, title.y) == (100, 50) and not title.sliding)

# ---- high_contrast theme (#14) ----
style = g.Style()
check("high_contrast is a theme", "high_contrast" in style.theme_names())
style.theme_use("high_contrast")
button = g.Button(0, 0, 100, 40, "A")
check("high_contrast colours", button.cget("bg") == (255, 230, 0) and button.cget("fg") == g.BLACK)
for widget in (button, g.TextBox(0, 0, placeholder="x"), g.Listbox(0, 0, items=["a"]),
               g.Combobox(0, 0, values=["a"]), g.Progressbar(0, 0), g.Label(0, 0, "a", outline=1),
               g.Notebook(0, 0), g.Table(0, 0)):
    widget.draw(screen)
check("every widget draws in high_contrast", True)
style.reset()
check("style.reset() goes back to light", style.theme_use() == "light")

print()
print("ALL TESTS PASS" if all(results) else f"{results.count(False)} TEST(S) FAILED")
pg.quit()
