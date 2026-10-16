"""
Automatic checks for big-map speed-ups (v1.1):
World chunks, updating only animated tiles, and faster Body collisions.
Every check compares the new fast way with the old (v1.0) way, so we know
the game looks and plays exactly the same.

Run this file in Visual Studio (right-click > Start without Debugging).
"""
import os
import sys
import time
import random

os.environ["SDL_VIDEODRIVER"] = "dummy"
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

import pygame as pg
pg.init()
screen = pg.display.set_mode((640, 480))

import PygameTkinterGUITools as g

ASSETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "examples", "assets")
results = []


def check(name, condition):
    results.append(bool(condition))
    print(("PASS  " if condition else "FAIL  ") + name)


def picture(world, offset):
    world.camera.offset.update(*offset)
    surface = pg.Surface((640, 480))
    surface.fill((0, 0, 0))
    world.draw(surface)
    return pg.image.tostring(surface, "RGB")


# ---------- A real Tiled map: chunks draw exactly the same ----------
level = g.TiledMap(os.path.join(ASSETS, "level1.tmx"))
camera = g.Camera(level.width, level.height, (640, 480))
fast = g.World(level, camera)
slow = g.World(level, camera, chunks=False)
same = all(picture(fast, o) == picture(slow, o)
           for o in [(0, 0), (37, 91), (level.width - 640, level.height - 480), (300.6, 10.2)])
check("level1.tmx: chunks draw exactly the same picture", same)
check("Tiles remember their map layer", all(hasattr(t, "map_layer") for t in level.background))


# ---------- A big made-up map (200 x 200 tiles, 2 layers) ----------
class CountingTile(g.Tile):
    """An 'animated' tile that counts its updates."""
    updates = 0

    def update(self, tick):
        CountingTile.updates += 1


class BigMap:
    def __init__(self):
        self.background = pg.sprite.Group()
        self.foreground = pg.sprite.Group()
        colours = [pg.Surface((32, 32)) for _ in range(4)]
        for i, c in enumerate(colours):
            c.fill((60 * i, 120, 200 - 40 * i))
        top = pg.Surface((32, 48), pg.SRCALPHA)       # a tall tile that hangs down
        top.fill((255, 0, 0, 120))
        random.seed(1)
        for layer in (0, 1):
            for y in range(200):
                for x in range(200):
                    if layer == 1 and random.random() > 0.1:
                        continue
                    if (x * 7 + y * 3) % 97 == 0:
                        tile = CountingTile((x * 32, y * 32), colours[3])
                    else:
                        tile = g.Tile((x * 32, y * 32), top if layer else colours[(x + y) % 3])
                    tile.map_layer = layer
                    self.background.add(tile)
        self.width = self.height = 200 * 32


big = BigMap()
camera = g.Camera(big.width, big.height, (640, 480))
fast = g.World(big, camera)
slow = g.World(big, camera, chunks=False)
offsets = [(0, 0), (5000, 4000), (1234.5, 77.7), (big.width - 640, big.height - 480)]
check("Big map: chunks draw exactly the same picture",
      all(picture(fast, o) == picture(slow, o) for o in offsets))

changing = sum(1 for t in big.background if isinstance(t, CountingTile))
CountingTile.updates = 0
fast.update(16)
check("update() only updates tiles that change", CountingTile.updates == changing)
CountingTile.updates = 0
slow.update(16)
check("chunks=False still updates every tile (v1.0 way)", CountingTile.updates == changing)



def draw_time(world, frames=30):
    """Best of 3 tries: seconds to draw `frames` frames (world.draw only)."""
    surface = pg.Surface((640, 480))
    world.camera.offset.update(3000, 3000)
    best = None
    for _ in range(3):
        start = time.perf_counter()
        for _ in range(frames):
            world.draw(surface)
        took = time.perf_counter() - start
        best = took if best is None else min(best, took)
    return best


fast_time = draw_time(fast)
slow_time = draw_time(slow)
print(f"      drawing 30 frames: chunks {fast_time:.3f}s, v1.0 way {slow_time:.3f}s "
      f"({slow_time / max(fast_time, 1e-9):.1f}x faster)")
check("Chunks are faster on a big map", fast_time < slow_time)

new_tile = g.Tile((3100, 3100), pg.Surface((32, 32)))
new_tile.image.fill((255, 255, 255))
big.background.add(new_tile)
check("Adding a tile: it shows straight away",
      picture(fast, (3000, 3000)) == picture(slow, (3000, 3000)))
new_tile.rect.topleft = (3300, 3200)
fast.refresh()
check("Moving a tile + world.refresh(): it shows in the new place",
      picture(fast, (3000, 3000)) == picture(slow, (3000, 3000)))
big.background.remove(new_tile)
check("Removing a tile: it disappears",
      picture(fast, (3000, 3000)) == picture(slow, (3000, 3000)))

g.Debug.on = True
picture(fast, (0, 0))
check("F1 debug shows tiles drawn", fast.tiles_drawn > 0)
g.Debug.on = False


# ---------- Collisions: exactly the same results as v1.0 ----------
def old_move_and_collide(body, dx, dy):
    """The v1.0 code, copied here to compare against."""
    body.touching = set()
    r = body.sprite.rect
    solids = body._solid_rects()
    body._pos.x += dx
    r.x = round(body._pos.x)
    for s in solids:
        if r.colliderect(s):
            if dx > 0:
                r.right = s.left
                body.touching.add("right")
            elif dx < 0:
                r.left = s.right
                body.touching.add("left")
            body._pos.x = r.x
            body.velocity.x = 0
    body._pos.y += dy
    r.y = round(body._pos.y)
    for s in solids:
        if r.colliderect(s):
            if dy > 0:
                r.bottom = s.top
                body.touching.add("bottom")
            elif dy < 0:
                r.top = s.bottom
                body.touching.add("top")
            body._pos.y = r.y
            body.velocity.y = 0


class Thing:
    def __init__(self, x, y):
        self.rect = pg.Rect(x, y, 24, 30)


random.seed(7)
walls = [pg.Rect(random.randrange(0, 1500), random.randrange(0, 1500),
                 random.randrange(8, 120), random.randrange(8, 120)) for _ in range(400)]
differences = 0
for trial in range(3000):
    x, y = random.randrange(0, 1500), random.randrange(0, 1500)   # sometimes inside a wall
    dx, dy = random.uniform(-40, 40), random.uniform(-40, 40)
    a = g.TopDownBody(Thing(x, y), solids=walls)
    b = g.TopDownBody(Thing(x, y), solids=walls)
    a.velocity.update(5, 5)
    b.velocity.update(5, 5)
    a.move_and_collide(dx, dy)
    old_move_and_collide(b, dx, dy)
    if (a.sprite.rect != b.sprite.rect or a.touching != b.touching
            or a.velocity != b.velocity or a._pos != b._pos):
        differences += 1
check("3000 random moves give exactly the same results as v1.0", differences == 0)

group_walls = pg.sprite.Group()
floor = pg.sprite.Sprite()
floor.rect = pg.Rect(0, 100, 400, 20)
group_walls.add(floor)
hero = Thing(50, 70)
body = g.PlatformerBody(hero, solids=group_walls)
for _ in range(60):
    body.update(16)
check("PlatformerBody stands on a floor given as a sprite Group",
      body.on_ground and body.standing_on is floor)

start = time.perf_counter()
for _ in range(2000):
    a.move_and_collide(3, 3)
new_time = time.perf_counter() - start
start = time.perf_counter()
for _ in range(2000):
    old_move_and_collide(b, 3, 3)
old_time = time.perf_counter() - start
print(f"      2000 moves past 400 walls: new {new_time:.3f}s, v1.0 way {old_time:.3f}s")
check("Collisions are faster with lots of walls", new_time < old_time)

print()
print("ALL TESTS PASS" if all(results) else f"{results.count(False)} TEST(S) FAILED")
pg.quit()
