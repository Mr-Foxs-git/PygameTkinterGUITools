"""
Automatic checks for Spawner and Waves.

Run this file in Visual Studio (right-click > Start without Debugging).
"""
import os
import sys

os.environ["SDL_VIDEODRIVER"] = "dummy"
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))

import pygame as pg
pg.init()
screen = pg.display.set_mode((400, 300))

import PygameTkinterGUITools as g

results = []


def check(name, condition):
    results.append(bool(condition))
    print(("PASS  " if condition else "FAIL  ") + name)


def make(x, y):
    return g.SpriteObject(x, y, 10, 10)


def run(thing, ms, step=10):
    """Pretend ms milliseconds go by, one small tick at a time."""
    for _ in range(ms // step):
        thing.update(step)


# ---------- Timing ----------
s = g.Spawner(make, points=(50, 50), every=1000)
run(s, 990)
check("nothing before `every` ms", len(s) == 0)
run(s, 20)
check("one after `every` ms", len(s) == 1 and s.spawned == 1)
run(s, 3000)
check("one more every second", len(s) == 4)
check("spawns at the point", all(t.rect.topleft == (50, 50) for t in s))

s = g.Spawner(make, points=(50, 50), every=1000, first_after=0)
s.update(10)
check("first_after=0 spawns straight away", len(s) == 1)

s = g.Spawner(make, points=(50, 50), every=(200, 400), first_after=0)
run(s, 2000)
check("every=(200, 400) gives between 5 and 11", 5 <= len(s) <= 11)

s = g.Spawner(make, points=(50, 50), every=100, start=False)
run(s, 500)
check("start=False waits", len(s) == 0)
s.start()
run(s, 500)
check("start() starts it", len(s) == 5)
s.stop()
run(s, 500)
check("stop() stops spawning", len(s) == 5)

# ---------- max_alive / kill / total ----------
s = g.Spawner(make, points=(50, 50), every=100, max_alive=3)
run(s, 1000)
check("max_alive holds", len(s) == 3)
first = s.alive()[0]
first.kill()
check("kill() removes it from the spawner", len(s) == 2 and first not in s.alive())
s.update(10)
check("spawns again as soon as one dies", len(s) == 3)

health_thing = []


def make_with_health(x, y):
    thing = g.SpriteObject(x, y, 10, 10)
    thing.health = g.Health(10, on_death=thing.kill)
    health_thing.append(thing)
    return thing


s = g.Spawner(make_with_health, points=(0, 0), every=100)
run(s, 100)
health_thing[0].health.damage(10)
check("Health(on_death=thing.kill) removes it", len(s) == 0)

s = g.Spawner(make, points=(50, 50), every=100, total=4)
run(s, 1000)
check("total stops it", s.spawned == 4 and s.done_spawning)
check("not cleared while some are alive", not s.cleared)
for thing in s:          # killing while looping is safe
    thing.kill()
check("cleared when all are gone", s.cleared)
s.reset()
check("reset() starts counting again", s.spawned == 0 and not s.done_spawning)

# ---------- Kinds of points ----------
order = []
s = g.Spawner(lambda x, y: order.append(x) or make(x, y),
              points=[(10, 10), (100, 10), (200, 10)], every=100, pick="in_turn")
run(s, 600)
check("in_turn order is 10, 100, 200, 10...", order == [10, 100, 200, 10, 100, 200])

area = pg.Rect(100, 100, 50, 40)
s = g.Spawner(make, points=area, every=100)
run(s, 2000)
check("a Rect spawns inside the area", all(area.contains(t.rect) for t in s))

s = g.Spawner(make, points={"a_spawn": (5, 6), "b_spawn": (7, 8)}, every=100)
run(s, 1000)
check("a dict of points (like map.spawn_points)",
      {t.rect.topleft for t in s} <= {(5, 6), (7, 8)} and len(s) == 10)

tiled_objects = [{"rect": pg.Rect(300, 0, 40, 40), "name": "", "type": "spawner",
                  "x": 300, "y": 0, "width": 40, "height": 40, "properties": {}},
                 {"rect": pg.Rect(20, 30, 0, 0), "name": "", "type": "spawner",
                  "x": 20, "y": 30, "width": 0, "height": 0, "properties": {}}]
s = g.Spawner(make, points=tiled_objects, every=100)
run(s, 2000)
check("Tiled objects: inside the rectangle, or at a point object",
      all(t.rect.topleft == (20, 30) or pg.Rect(300, 0, 40, 40).contains(t.rect) for t in s))

portal = g.SpriteObject(0, 0, 20, 20)
s = g.Spawner(make, points=portal, every=100)
run(s, 100)
portal.rect.topleft = (200, 200)
run(s, 100)
check("a sprite as a point follows it",
      [t.rect.topleft for t in s.alive()] in ([(10, 10), (210, 210)], [(210, 210), (10, 10)]))

s = g.Spawner(make, points=None, every=100)
run(s, 100)
check("points=None uses the middle of the screen", s.alive()[0].rect.topleft == (200, 150))

try:
    level = g.TiledMap(os.path.join(HERE, "test_map.tmx"))
    s = g.Spawner(make, points=level.spawn_points, every=100)
    run(s, 100)
    check("works with a real TiledMap's spawn_points", s.alive()[0].rect.topleft == (8, 8))
except ImportError:
    print("SKIP  TiledMap check (pytmx is not installed)")

# ---------- avoid / min_distance ----------
player = g.SpriteObject(0, 0, 20, 20)            # middle is (10, 10)
s = g.Spawner(make, points=[(15, 15), (300, 200)], every=100, avoid=player, min_distance=100)
run(s, 1000)
check("never spawns next to `avoid`", all(t.rect.topleft == (300, 200) for t in s) and len(s) == 10)

s = g.Spawner(make, points=(15, 15), every=100, avoid=player, min_distance=100)
run(s, 1000)
check("waits if every place is too close", len(s) == 0)
player.rect.topleft = (300, 300)
s.update(10)
check("spawns once the player moves away", len(s) == 1)

# ---------- world=, spawn_now, clear, make() returning None, config ----------
camera = g.Camera(400, 300, (400, 300))


class FakeMap:
    width, height = 400, 300
    background = pg.sprite.Group()
    foreground = pg.sprite.Group()


try:
    world = g.World(FakeMap(), camera)
except Exception:
    world = None
if world is not None:
    s = g.Spawner(make, points=(0, 0), every=100, world=world)
    run(s, 200)
    check("world= adds them to the World", len(world.sprites) == 2)
    s.alive()[0].kill()
    check("kill() takes them out of the World too", len(world.sprites) == 1)

s = g.Spawner(make, points=(0, 0), every=100000, max_alive=2)
check("spawn_now() makes one straight away", s.spawn_now() is not None and len(s) == 1)
s.spawn_now()
check("spawn_now() keeps to max_alive", s.spawn_now() is None and len(s) == 2)
s.clear()
check("clear() removes everything", len(s) == 0)

s = g.Spawner(lambda x, y: None, points=(0, 0), every=100)
run(s, 500)
check("make() returning None skips that spawn", len(s) == 0 and s.spawned == 0)

s = g.Spawner(make, points=(0, 0), every=1000)
s.config(every=100, max_alive=2)
check("config() changes settings", s.cget("every") == 100 and s.cget("max_alive") == 2)
try:
    s.config(colour="red")
    check("config() with a wrong name gives a clear error", False)
except ValueError:
    check("config() with a wrong name gives a clear error", True)


class Box:
    """Not a sprite, but has a rect and draw()."""
    def __init__(self, x, y):
        self.rect = pg.Rect(x, y, 5, 5)

    def draw(self, screen, camera=None):
        pass


s = g.Spawner(Box, points=(0, 0), every=100)
run(s, 300)
check("works with objects that aren't sprites", len(s) == 3)
s.remove(s.alive()[0])
check("remove() for objects that aren't sprites", len(s) == 2)

# ---------- Drawing ----------
s = g.Spawner(lambda x, y: g.SpriteObject(x, y, 10, 10, bg=(255, 0, 0)),
              points=[(20, 20), pg.Rect(100, 100, 50, 50)], every=100,
              avoid=player, min_distance=50)
run(s, 300)
screen.fill((0, 0, 0))
s.draw(screen)
check("draw() draws what it made", screen.get_at((s.alive()[0].rect.x + 2, s.alive()[0].rect.y + 2))[:3] == (255, 0, 0))
g.Debug.on = True
s.draw(screen, camera)
g.Debug.on = False
check("debug view draws without crashing", True)

# ---------- Waves ----------
started, ended, done = [], [], []
s = g.Spawner(make, points=(0, 0), every=100)
w = g.Waves(s, [2, 3], break_ms=1000, on_wave_start=lambda: started.append(w.wave),
            on_wave_end=lambda: ended.append(w.wave), on_all_done=lambda: done.append(True))
check("Waves starts with a break", w.state == "break" and len(s) == 0)
check("text() during the first break", w.text() == "Wave 1 in 1")
run(w, 990)
check("nothing spawns in the break", len(s) == 0)
run(w, 20)
check("wave 1 starts after the break and spawns at once",
      w.wave == 1 and started == [1] and len(s) == 1)
run(w, 500)
check("wave 1 spawns its count only", s.spawned == 2 and w.state == "clearing")
check("text() during a wave", w.text() == "Wave 1 of 2 - 2 left")
for thing in s:
    thing.kill()
w.update(10)
check("wave ends when all are killed", ended == [1] and w.state == "break")
run(w, 1010)
run(w, 500)
check("wave 2 has its own count", w.wave == 2 and s.spawned == 3)
s.clear()
w.update(10)
check("on_all_done after the last wave", done == [True] and w.finished)
check("text() when done", w.text() == "All waves done!")

s = g.Spawner(make, points=(0, 0), every=1000)
w = g.Waves(s, [{"count": 3, "every": 100}, {"count": 1, "make": Box}], break_ms=0)
run(w, 400)
check("a wave dict changes `every` for that wave", s.spawned == 3 and s.cget("every") == 100)
s.clear()
run(w, 20)
check("the next wave goes back to the Spawner's own settings",
      w.wave == 2 and s.cget("every") == 1000 and isinstance(s.alive()[0], Box))

s = g.Spawner(make, points=(0, 0), every=100)
w = g.Waves(s, [1], break_ms=0, loop=True)
for _ in range(3):
    run(w, 20)
    s.clear()
    run(w, 20)
check("loop=True keeps going", w.wave >= 3 and not w.finished)

s = g.Spawner(make, points=(0, 0), every=100)
w = g.Waves(s, [2], break_ms=5000, start=False)
run(w, 6000)
check("Waves(start=False) waits", w.state == "waiting" and w.text() == "Get ready")
w.start()
w.skip_break()
w.update(10)
check("skip_break() starts the wave now", w.wave == 1)
w.stop()
run(w, 1000)
check("stop() pauses the waves", s.spawned == 1)
w.start()
run(w, 200)
check("start() carries on", s.spawned == 2)
w.restart()
check("restart() goes back before wave 1", w.wave == 0 and len(s) == 0 and w.state == "break")

# ---------- The old way still works the same (backwards compatible) ----------
made = []
timer_id = g.after_repeat(100, lambda: made.append(1))
g.update_timers()
check("after_repeat() is unchanged", timer_id in g._timers)
g.after_cancel(timer_id)

print()
print(f"{sum(results)} of {len(results)} checks passed")
if not all(results):
    sys.exit(1)
