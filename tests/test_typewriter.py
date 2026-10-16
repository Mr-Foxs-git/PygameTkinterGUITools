"""
Automatic checks for typing text out one letter at a time
(Message / MessageBox type_speed, type_sound, on_done).
Also checks that v1.0 Message and MessageBox code still works the same.

Run this file in Visual Studio (right-click > Start without Debugging).
"""
import os
import sys

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"          # no sound plays while testing
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

import pygame as pg
pg.init()
screen = pg.display.set_mode((800, 600))

import PygameTkinterGUITools as g

results = []


def check(name, condition):
    results.append(bool(condition))
    print(("PASS  " if condition else "FAIL  ") + name)


def click(pos=(10, 10), button=1):
    return pg.event.Event(pg.MOUSEBUTTONDOWN, button=button, pos=pos)


def key(k):
    return pg.event.Event(pg.KEYDOWN, key=k, unicode="", mod=0)


def picture(widget):
    """Draw a widget on a blank surface and return its pixels."""
    surface = pg.Surface((800, 600))
    widget.draw(surface)
    return pg.image.tostring(surface, "RGB")


class FakeSound:
    """Counts plays instead of making a noise."""
    def __init__(self):
        self.plays = 0

    def play(self):
        self.plays += 1


# ---------- v1.0 behaviour is kept (no type_speed) ----------
old = g.Message(0, 0, "Hello there, this is old code", width=300)
check("v1.0 Message is not typing", not old.typing)
check("v1.0 Message ignores clicks", old.handle_event(click()) is False)
check("v1.0 Message ignores Space", old.handle_event(key(pg.K_SPACE)) is False)
before = picture(old)
old.update(1000)
check("v1.0 Message looks the same after update()", picture(old) == before)
old_box = g.MessageBox("Quit?", "Really quit?", buttons=("Yes", "No"))
old_box.show()
old_box.handle_event(key(pg.K_RETURN))
check("v1.0 MessageBox: Enter still answers straight away", old_box.result == "Yes")

# ---------- Typing out ----------
done = []
sound = FakeSound()
talk = g.Message(0, 0, "abcdefghij klmnopqrst", width=600, type_speed=10,
                 type_sound=sound, on_done=lambda: done.append(True))
check("starts typing", talk.typing and talk._letters_shown() == 0)
talk.update(500)                                    # 0.5 s at 10 letters per second
check("update(500) at 10 per second shows 5 letters", talk._letters_shown() == 5)
check("a sound plays when letters appear", sound.plays == 1)
talk.update(50)                                     # half a letter: no new letter yet
check("no sound when no new letter appears", sound.plays == 1)
check("on_done not called yet", done == [])
check("Escape doesn't skip", talk.handle_event(key(pg.K_ESCAPE)) is False)
check("right click doesn't skip", talk.handle_event(click(button=3)) is False)
check("click while typing returns True", talk.handle_event(click()) is True)
check("click shows the whole text", not talk.typing and talk._letters_shown() == 21)
check("on_done runs when skipped", done == [True])
check("second click returns False (game gets it)", talk.handle_event(click()) is False)
talk.update(5000)
check("on_done runs only once", done == [True])

talk.config(text="New line")
check("config(text=...) starts typing again", talk.typing and talk._letters_shown() == 0)
talk.update(10000)                                  # a huge tick
check("a huge tick stops at the end", talk._letters_shown() == len("New line"))
check("on_done runs at the end of typing", done == [True, True])
talk.restart()
check("restart() types again", talk.typing)
check("Space while typing returns True", talk.handle_event(key(pg.K_SPACE)) is True)

# Spaces are quiet
quiet = FakeSound()
spaces = g.Message(0, 0, "a    b", width=300, type_speed=10, type_sound=quiet)
spaces.update(100)                                  # "a"
spaces.update(300)                                  # three spaces
check("no sound for spaces", quiet.plays == 1)

# textvariable
words = g.StringVar("Hi")
shown = g.Message(0, 0, textvariable=words, width=300, type_speed=10)
shown.update(1000)
words.set("Bye now")
check("changing the textvariable starts typing again", shown.typing)

# Wrapping and size stay the same while typing
long_text = "The quick brown fox jumps over the lazy dog " * 3
typed = g.Message(0, 0, long_text, width=200, type_speed=20)
whole = g.Message(0, 0, long_text, width=200)
check("height is the same while typing", typed.height == whole.height)
check("lines are the same while typing", typed._lines() == whole._lines())
typed.update(500)
typed.draw(screen)
typed.skip()
check("finished typed text looks the same as normal text", picture(typed) == picture(whole))
for justify in ("center", "right"):
    a = g.Message(0, 0, long_text, width=200, justify=justify, type_speed=5)
    a.skip()
    b = g.Message(0, 0, long_text, width=200, justify=justify)
    check(f"justify={justify} looks the same when finished", picture(a) == picture(b))

# config can change the speed
typed.config(type_speed=None)
check("config(type_speed=None) shows everything", not typed.typing)

# A real SoundEffect doesn't crash (even with no audio device)
CLICK = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "examples",
                     "assets", "sounds", "click.wav")
real = g.Message(0, 0, "Hello", width=300, type_speed=50, type_sound=g.SoundEffect(CLICK))
real.update(100)
check("a SoundEffect type_sound doesn't crash", True)

# ---------- MessageBox ----------
answers = []
box = g.MessageBox("Shop", "Buy the sword?", buttons=("Buy", "No"),
                   command=answers.append, type_speed=10)
box.show()
box.draw(screen)
box.update(300)
check("MessageBox types its message", box.text.typing)
check("first Enter only shows the message", box.handle_event(key(pg.K_RETURN))
      and box.visible and answers == [])
box.handle_event(key(pg.K_RETURN))
check("second Enter answers", answers == ["Buy"] and not box.visible)
box.show()
check("show() types the message again", box.text.typing)
box.handle_event(key(pg.K_ESCAPE))
check("Escape still closes while typing", answers == ["Buy", None] and not box.visible)
yes = g.askyesno("Sure?", "Are you sure?", type_speed=30)
check("askyesno passes type_speed on", yes.text.typing)

print()
print("ALL TESTS PASS" if all(results) else f"{results.count(False)} TEST(S) FAILED")
pg.quit()
