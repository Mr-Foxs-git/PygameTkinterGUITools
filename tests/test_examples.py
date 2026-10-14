"""
Runs every example for about 2 seconds (no window opens) to check
nothing crashes. Some key presses and clicks are sent automatically.

Run this file in Visual Studio (right-click > Start without Debugging).
Then run the examples yourself to check they look right.
"""
import os
import sys
import runpy
import glob
import traceback

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"          # no sound plays while testing
import pygame as pg

HERE = os.path.dirname(os.path.abspath(__file__))
EXAMPLES = sorted(glob.glob(os.path.join(HERE, "..", "examples", "*.py")))
FRAMES = 120

real_get = pg.event.get
real_get_pressed = pg.key.get_pressed


class FakeKeys:
    """Pretends the RIGHT and DOWN arrow keys are held."""
    def __getitem__(self, key):
        return key in (pg.K_RIGHT, pg.K_DOWN)


def make_fake_get():
    frame = [0]

    def fake_get(*args, **kwargs):
        frame[0] += 1
        events = list(real_get(*args, **kwargs))
        n = frame[0]
        if n == 20:
            events.append(pg.event.Event(pg.KEYDOWN, key=pg.K_SPACE, unicode=" ", mod=0))
        if n == 30:
            events.append(pg.event.Event(pg.MOUSEBUTTONDOWN, button=1, pos=(150, 130)))
        if n == 40:
            for ch in "Sam":
                events.append(pg.event.Event(pg.KEYDOWN, key=ord(ch.lower()), unicode=ch, mod=0))
            events.append(pg.event.Event(pg.KEYDOWN, key=pg.K_RETURN, unicode="\r", mod=0))
        if n == 50:
            events.append(pg.event.Event(pg.KEYDOWN, key=pg.K_m, unicode="m", mod=0))
            events.append(pg.event.Event(pg.KEYDOWN, key=pg.K_MINUS, unicode="-", mod=0))
        if n >= FRAMES:
            return [pg.event.Event(pg.QUIT)]
        return events
    return fake_get


sys.path.insert(0, os.path.join(HERE, ".."))
import PygameTkinterGUITools

results = []
for path in EXAMPLES:
    PygameTkinterGUITools._font_cache.clear()    # fonts don't survive pg.quit()
    PygameTkinterGUITools._image_cache.clear()
    PygameTkinterGUITools.Style().reset()         # each example starts with the light theme
    PygameTkinterGUITools.Audio._sounds.clear()
    PygameTkinterGUITools.Music._playlist = []
    PygameTkinterGUITools.Music._next = None
    name = os.path.basename(path)
    pg.event.get = make_fake_get()
    pg.key.get_pressed = lambda: FakeKeys()
    try:
        runpy.run_path(path, run_name="__main__")
        ok, error = False, "example finished without quitting"
    except SystemExit:
        ok, error = True, ""
    except Exception:
        ok, error = False, traceback.format_exc()
    finally:
        pg.event.get = real_get
        pg.key.get_pressed = real_get_pressed
        pg.quit()
    results.append(ok)
    print(("PASS  " if ok else "FAIL  ") + name)
    if error:
        print(error)

print()
print("ALL EXAMPLES RAN" if all(results) else f"{results.count(False)} EXAMPLE(S) FAILED")
