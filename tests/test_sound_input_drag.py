"""
Automatic checks for KeyboardInput, MouseInput, sound (SoundEffect, Music,
Audio), Grid and DragObject. No window opens and no sound plays.

Run this file in Visual Studio (right-click > Start without Debugging).
"""
import os
import sys

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

import pygame as pg
import PygameTkinterGUITools as g

g.init_audio()
pg.init()
screen = pg.display.set_mode((800, 600))
SOUNDS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "examples",
                      "assets", "sounds")

results = []


def check(name, condition):
    results.append(bool(condition))
    print(("PASS  " if condition else "FAIL  ") + name)


def down(k):
    return pg.event.Event(pg.KEYDOWN, key=k, mod=0, unicode="")


def up(k):
    return pg.event.Event(pg.KEYUP, key=k, mod=0, unicode="")


def mouse(kind, pos, button=1):
    if kind == "motion":
        return pg.event.Event(pg.MOUSEMOTION, pos=pos, rel=(0, 0), buttons=(1, 0, 0))
    t = pg.MOUSEBUTTONDOWN if kind == "down" else pg.MOUSEBUTTONUP
    return pg.event.Event(t, pos=pos, button=button)


# ---------- KeyboardInput ----------
keys = g.KeyboardInput()
keys.bind("jump", "space", "w")
keys.handle_event(down(pg.K_SPACE))
keys.update(16)
check("Frame 1: was_pressed and is_pressed", keys.was_pressed("jump") and keys.is_pressed("jump"))
keys.update(16)
check("Frame 2 (still held): was_pressed is False, is_pressed True",
      not keys.was_pressed("jump") and keys.is_pressed("jump"))
keys.update(16)
check("held_time counts while held", keys.held_time("jump") == 32)
keys.handle_event(up(pg.K_SPACE))
keys.update(16)
check("Released: was_released for one frame, not held",
      keys.was_released("jump") and not keys.is_pressed("jump"))
keys.update(16)
check("was_released only lasts one frame", not keys.was_released("jump"))
keys.handle_event(down(pg.K_w))
keys.update(16)
check("Second key bound to the same name works", keys.was_pressed("jump"))
check("Key names work without bind ('w')", keys.is_pressed("w"))
check("pygame keys work (pg.K_w)", keys.is_pressed(pg.K_w))
check("any_pressed()", keys.any_pressed())
try:
    keys.is_pressed("fly")
    check("Unknown name gives a helpful error", False)
except ValueError:
    check("Unknown name gives a helpful error", True)
if hasattr(pg, "WINDOWFOCUSLOST"):
    keys.handle_event(pg.event.Event(pg.WINDOWFOCUSLOST))
    keys.update(16)
    check("Losing window focus lets go of held keys", not keys.is_pressed("w"))

# Quick press and release in the same frame still counts as a press
keys2 = g.KeyboardInput()
keys2.handle_event(down(pg.K_x))
keys2.handle_event(up(pg.K_x))
keys2.update(16)
check("Very quick tap (down + up in one frame) is still a press", keys2.was_pressed("x"))

# ---------- MouseInput ----------
m = g.MouseInput()
m.bind("shoot", "left")
m.handle_event(mouse("down", (10, 10)))
m.handle_event(pg.event.Event(pg.MOUSEWHEEL, x=0, y=1))
m.handle_event(mouse("motion", (12, 12)))
m.update(16)
check("Mouse was_pressed / is_pressed", m.was_pressed("shoot") and m.is_pressed("left"))
check("Mouse wheel and moved", m.wheel == 1 and m.moved)
m.update(16)
check("Wheel / moved reset next frame", m.wheel == 0 and not m.moved)
m.handle_event(mouse("up", (12, 12)))
m.update(16)
check("Mouse was_released", m.was_released("shoot"))

# ---------- Sound ----------
print("      (sound output available:", g.Audio.available, ")")
jump = g.SoundEffect(os.path.join(SOUNDS, "jump.wav"))
laser = g.SoundEffect(os.path.join(SOUNDS, "laser.wav"), cooldown=150)
if g.Audio.available:
    check("SoundEffect plays", jump.play())
    check("Cooldown: first play works", laser.play())
    check("Cooldown: playing again straight away is skipped", not laser.play())
    pg.time.wait(170)
    check("Cooldown: works again after 150 ms", laser.play())
    limited = g.SoundEffect(os.path.join(SOUNDS, "explosion.wav"), max_playing=2)
    plays = [limited.play() for _ in range(5)]
    check("max_playing stops sounds piling up", plays.count(True) == 2)
    steps = g.SoundEffect([os.path.join(SOUNDS, f"step{n}.wav") for n in (1, 2, 3)])
    check("A list of files loads them all", len(steps._sounds) == 3)
    engine = g.SoundEffect(os.path.join(SOUNDS, "engine_loop.wav"))
    engine.play_while(True)
    first = engine._loop_channel
    engine.play_while(True)
    check("play_while(True) every frame doesn't restart the loop",
          first is not None and engine._loop_channel is first)
    engine.play_while(False)
    check("play_while(False) stops it", engine._loop_channel is None)
else:
    print("SKIP  playing sounds (no sound output on this computer)")


class CountingSound(g.SoundEffect):
    """Counts plays instead of making a noise, to test play_on."""
    def __init__(self):
        self.count = 0
        self._last_condition = False

    def play(self, loops=0):
        self.count += 1
        return True


coin = CountingSound()
for touching in [False, True, True, True, False, True, True]:
    coin.play_on(touching)
check("play_on only plays when the value changes to True (2 times)", coin.count == 2)

# Volume linking
music_var, sfx_var, mute_var = g.IntVar(50), g.IntVar(40), g.BooleanVar(False)
g.Audio.link(music_volume=music_var, sfx_volume=sfx_var, muted=mute_var)
sfx_var.set(90)
check("Audio.link: changing the variable changes the volume", g.Audio.sfx_volume == 90)
mute_var.set(True)
check("Audio.link: mute", g.Audio.muted and g.Audio.sfx_factor() == 0)
mute_var.set(False)

# Music
g.Music.play(os.path.join(SOUNDS, "music_menu.wav"))
g.Music.update(16)
check("Music.play sets current", g.Music.current.endswith("music_menu.wav"))
g.Music.switch(os.path.join(SOUNDS, "music_level.wav"), fade_ms=100)
for _ in range(10):
    g.Music.update(16)
check("Music.switch moves to the new track after the fade",
      g.Music.current.endswith("music_level.wav"))
g.Music.pause(); g.Music.unpause(); g.Music.stop()
check("Music pause / unpause / stop", g.Music.current is None)

# No sound device: nothing crashes
saved = g.Audio.available
g.Audio.available = False
quiet = g.SoundEffect(os.path.join(SOUNDS, "jump.wav"))
ok = quiet.play() is False
quiet.play_on(True); quiet.play_while(True); quiet.stop()
g.Music.play("anything.wav"); g.Music.switch("other.wav"); g.Music.update(16)
g.Music.pause(); g.Music.stop()
check("With no sound device everything runs silently", ok)
g.Audio.available = saved

# ---------- Grid ----------
grid = g.Grid(100, 100, cols=4, rows=3, cell_size=50)
check("cell_at inside", grid.cell_at((175, 160)) == (1, 1))
check("cell_at outside is None", grid.cell_at((10, 10)) is None)
check("cell_rect", grid.cell_rect(2, 1) == pg.Rect(200, 150, 50, 50))
a = g.DragObject(0, 0, 40, 40, grid=grid)
b = g.DragObject(0, 0, 40, 40, grid=grid)
check("place() snaps to the cell centre", grid.place(a, 0, 0) and a.rect.center == (125, 125))
check("item_at / cell / grid", grid.item_at(0, 0) is a and a.cell == (0, 0) and a.grid is grid)
check("one_per_cell stops a second item", grid.place(b, 0, 0) is False)
grid.place(b, 1, 0)
check("first_free_cell", grid.first_free_cell() == (2, 0))

# ---------- Dragging ----------
group = g.DragGroup(a, b)
group.handle_event(mouse("down", a.rect.center))
check("Click picks up the item", a.dragging)
group.handle_event(mouse("motion", (275, 225)))
check("Grid highlights the cell under the dragged item", grid.hover_cell == (3, 2))
group.handle_event(mouse("up", (275, 225)))
check("Drop snaps into the new cell", a.cell == (3, 2) and a.rect.center == (275, 225)
      and grid.is_free(0, 0) and not a.dragging)

group.handle_event(mouse("down", a.rect.center))
group.handle_event(mouse("motion", b.rect.center))
group.handle_event(mouse("up", b.rect.center))
check("Dropping on a taken cell goes back to the start", a.cell == (3, 2) and b.cell == (1, 0))

group.handle_event(mouse("down", a.rect.center))
group.handle_event(mouse("up", (700, 500)))
check("Dropping outside the grid goes back", a.cell == (3, 2))

# Two grids
other = g.Grid(500, 100, cols=1, rows=2, cell_size=50)
c = g.DragObject(0, 0, 40, 40, grid=[grid, other])
grid.place(c, 2, 2)
c.handle_event(mouse("down", c.rect.center))
c.handle_event(mouse("up", (525, 175)))
check("Moving between two grids", c.grid is other and c.cell == (0, 1)
      and grid.is_free(2, 2))

# No grid: free dragging, kept inside bounds
free = g.DragObject(10, 10, 40, 40, bounds=pg.Rect(0, 0, 300, 300))
free.handle_event(mouse("down", (20, 20)))
free.handle_event(mouse("motion", (150, 120)))
free.handle_event(mouse("up", (150, 120)))
check("No grid: dropped where you let go", free.rect.topleft == (140, 110))
free.handle_event(mouse("down", free.rect.center))
free.handle_event(mouse("up", (900, 900)))
check("bounds keeps it inside the area", pg.Rect(0, 0, 300, 300).contains(free.rect))

# Overlapping: only the top one is picked up
top = g.DragObject(400, 400, 50, 50)
bottom = g.DragObject(400, 400, 50, 50)
stack = g.DragGroup(bottom, top)
stack.handle_event(mouse("down", (420, 420)))
check("DragGroup picks up only the top item", top.dragging and not bottom.dragging)
stack.handle_event(mouse("up", (420, 420)))
stack.handle_event(mouse("down", (420, 420)))
check("...and the picked-up item stays on top", stack.items[-1] is top)
stack.handle_event(mouse("up", (420, 420)))

drops = []
d = g.DragObject(0, 0, 20, 20, on_pick_up=lambda: drops.append("up"),
                 on_drop=lambda: drops.append("drop"))
d.handle_event(mouse("down", (5, 5))); d.handle_event(mouse("up", (50, 50)))
check("on_pick_up and on_drop run", drops == ["up", "drop"])
grid.draw(screen); group.draw(screen); stack.draw(screen)
check("Grid and DragGroup draw", True)

print()
print("ALL TESTS PASS" if all(results) else f"{results.count(False)} TEST(S) FAILED")
pg.quit()
