"""
Automatic checks for paths, enemy AI, platformer / top-down movement,
item kinds and slots, and Tooltip.

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

ASSETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "examples", "assets")
results = []


def check(name, condition):
    results.append(bool(condition))
    print(("PASS  " if condition else "FAIL  ") + name)


def box(x, y, w=20, h=20):
    return g.SpriteObject(x, y, w, h)


def run(things, frames, tick=16):
    for _ in range(frames):
        for t in things:
            t.update(tick)


# ---------- Path / PathFollower ----------
square = g.Path([(0, 0), (100, 0), (100, 100), (0, 100)], mode="loop")
check("Path length (loop)", square.length() == 400)
s = box(0, 0)
f = g.PathFollower(s, square, speed=100)
check("Follower starts on the first point", s.rect.center == (0, 0))
run([f], 63)                                    # ~1 second at 100 px/s
check("Follower reaches the next point", s.rect.center == (100, 0) and f.index == 2)
check("facing", f.facing in ("right", "down"))
run([f], 250)
check("Loop mode keeps going round", not f.finished)

line = g.Path([(0, 0), (50, 0)], mode="ping_pong")
s2 = box(0, 0)
f2 = g.PathFollower(s2, line, speed=100)
run([f2], 60)               # 31 frames there, then back
check("Ping-pong comes back", s2.rect.centerx < 10)

once = g.Path([(0, 0), (30, 0)], mode="once")
s3 = box(0, 0)
f3 = g.PathFollower(s3, once, speed=100)
run([f3], 40)
check("Once mode finishes", f3.finished and s3.rect.center == (30, 0))

waiter = g.PathFollower(box(0, 0), g.Path([(0, 0), (20, 0), (40, 0)]), speed=1000, wait=200)
run([waiter], 3)
x_at_point = waiter.sprite.rect.centerx
run([waiter], 5)
check("wait pauses at points", waiter.sprite.rect.centerx == x_at_point == 20)
try:
    g.Path([(0, 0)], mode="sideways")
    check("Bad mode gives an error", False)
except ValueError:
    check("Bad mode gives an error", True)
g.Path.show_all = True
square.draw(screen)
check("Path.draw works", True)

# ---------- line of sight / NavGrid ----------
wall = pg.Rect(100, 0, 20, 200)
check("line_of_sight blocked by a wall", not g.line_of_sight((50, 50), (200, 50), [wall]))
check("line_of_sight clear", g.line_of_sight((50, 250), (200, 250), [wall]))
nav = g.NavGrid(400, 300, cell_size=20, solids=[wall])
route = nav.find_path((50, 50), (200, 50))
check("NavGrid finds a way around the wall", route is not None and
      all(not pg.Rect(98, 0, 24, 200).collidepoint(p) for p in route.points[1:-1]))
check("Route ends at the goal", route.points[-1] == pg.Vector2(200, 50))
boxed = g.NavGrid(400, 300, cell_size=20,
                  solids=[pg.Rect(140, 0, 20, 300)])
check("No way through returns None", boxed.find_path((50, 50), (300, 50)) is None)
nav.draw(screen)

# ---------- TopDownBody ----------
p = box(0, 0, 20, 20)
body = g.TopDownBody(p, solids=[pg.Rect(50, 0, 20, 100)], speed=100)
for _ in range(60):
    body.move(1, 0)
    body.update(16)
check("TopDownBody stops at a wall", p.rect.right == 50 and "right" in body.touching)
p2 = box(0, 0)
b2 = g.TopDownBody(p2, speed=100)
b2.move(1, 1)
b2.update(1000)
check("Diagonal isn't faster", abs(p2.rect.x - 71) <= 1 and abs(p2.rect.y - 71) <= 1)
p3 = box(0, 50)
b3 = g.TopDownBody(p3, solids=[pg.Rect(50, 0, 20, 100)], speed=100)
for _ in range(30):
    b3.move(1, 1)
    b3.update(16)
check("Slides along a wall", p3.rect.right == 50 and p3.rect.y > 60)

# ---------- PlatformerBody ----------
floor = pg.Rect(0, 200, 800, 40)
hero = box(100, 100, 20, 30)
pb = g.PlatformerBody(hero, solids=[floor])
run([pb], 60)
check("Gravity: falls and lands on the floor", hero.rect.bottom == 200 and pb.on_ground)
pb.jump()
pb.update(16)
check("Jump goes up", pb.velocity.y < 0 and not pb.on_ground)
top = hero.rect.y
run([pb], 10)
check("...and rises", hero.rect.y < top)
run([pb], 100)
check("...and lands again", pb.on_ground)

# Small jump vs full jump
def jump_height(release_after):
    h = box(100, 170, 20, 30)
    b = g.PlatformerBody(h, solids=[floor])
    b.update(16)
    b.jump()
    best = h.rect.y
    for frame in range(80):
        if frame == release_after:
            b.release_jump()
        b.update(16)
        best = min(best, h.rect.y)
    return 170 - best
check("Releasing jump early gives a smaller jump", jump_height(3) < jump_height(1000) * 0.6)

# Jump buffer: press jump just before landing
h = box(100, 150, 20, 30)
b = g.PlatformerBody(h, solids=[floor])
for _ in range(40):
    if h.rect.bottom > 190 and not b.on_ground:
        b.jump()
    b.update(16)
check("Jump buffer: jump pressed just before landing still happens", h.rect.bottom < 190)

# Coyote time: jump just after walking off a ledge
ledge = pg.Rect(0, 200, 100, 20)
h = box(60, 170, 20, 30)
b = g.PlatformerBody(h, solids=[ledge], move_speed=300)
b.update(16)
while h.rect.left < 100:
    b.move(1)
    b.update(16)
b.move(1); b.update(16)
b.jump(); b.update(16)
check("Coyote time: can still jump just after leaving the ledge", b.velocity.y < 0)

# Double jump
h = box(100, 170, 20, 30)
b = g.PlatformerBody(h, solids=[floor], max_jumps=2)
b.update(16); b.jump(); b.update(16)
run([b], 10)
b.jump(); b.update(16)
check("max_jumps=2 allows a double jump", b.velocity.y < -500)
b2 = g.PlatformerBody(box(100, 170, 20, 30), solids=[floor])
b2.update(16); b2.jump(); b2.update(16)
run([b2], 10)
b2.jump(); b2.update(16)
check("max_jumps=1: no jump in the air", b2.velocity.y > -500)

# One-way platform
plank = pg.Rect(0, 150, 300, 10)
h = box(100, 160, 20, 30)
b = g.PlatformerBody(h, solids=[floor], platforms=[plank], jump_speed=700)
run([b], 30)
b.jump()
for _ in range(80):
    b.update(16)
check("Jump up through a one-way platform and land on top",
      h.rect.bottom == 150 and b.on_ground and b.standing_on is plank)
b.drop_down()
run([b], 40)
check("drop_down falls through it", h.rect.bottom == 200)

# Ladder
ladder = pg.Rect(200, 60, 32, 140)
h = box(206, 170, 20, 30)
b = g.PlatformerBody(h, solids=[floor], ladders=[ladder])
b.update(16)
for _ in range(30):
    b.climb(-1)
    b.update(16)
check("Climbing a ladder goes up (no gravity)", h.rect.bottom < 170 and b.climbing)
y_now = h.rect.y
run([b], 10)
check("Stays still on the ladder when not pressing", h.rect.y == y_now)

# Ground ahead (ledge detection)
h = box(78, 170, 20, 30)
b = g.PlatformerBody(h, solids=[ledge])
b.update(16)
check("ground_ahead finds the ledge edge", b.ground_ahead(-1) and not b.ground_ahead(1))

# Moving platform carries the player
lift = g.MovingPlatform(300, 300, 80, 16, g.Path([(340, 308), (540, 308)]), speed=100)
h = box(330, 260, 20, 30)
b = g.PlatformerBody(h, platforms=[lift])
for _ in range(30):
    lift.update(16)
    b.update(16)
start_x = h.rect.x
for _ in range(30):
    lift.update(16)
    b.update(16)
check("MovingPlatform carries the player", b.on_ground and h.rect.x - start_x > 40)

# ---------- Patrol ----------
slime = box(40, 170, 20, 30)
sb = g.PlatformerBody(slime, solids=[ledge, pg.Rect(0, 100, 10, 100)])
patrol = g.Patrol(slime, speed=100, body=sb)
xs = []
for _ in range(200):
    patrol.update(16)
    sb.update(16)
    xs.append(slime.rect.x)
check("Patrol turns at ledge edges and walls (stays on the ledge)",
      sb.on_ground and max(xs) <= 100 and min(xs) >= 10 and len(set(xs)) > 20)

# ---------- Chaser ----------
target = box(300, 50)
enemy = box(50, 50)
chaser = g.Chaser(enemy, target, speed=200, detect_range=150, lose_range=250)
chaser.update(16)
check("Chaser idle when the target is far away", chaser.state == "idle")
target.rect.topleft = (150, 50)
run([chaser], 5)
check("Chaser chases when the target comes close", chaser.state == "chase"
      and enemy.rect.x > 50)
target.rect.topleft = (700, 500)
chaser.update(16)
check("Chaser gives up when the target gets away", chaser.state == "return")
run([chaser], 200)
check("...and goes back home", chaser.state == "idle" and abs(enemy.rect.x - 50) < 8)

walled = g.Chaser(box(50, 50), box(200, 50), detect_range=300, solids=[wall])
walled.update(16)
check("Line of sight: can't see through walls", walled.state == "idle"
      and not walled.can_see_target)

hunter = box(50, 50, 16, 16)
hb = g.TopDownBody(hunter, solids=[pg.Rect(100, 0, 20, 200)])
smart = g.Chaser(hunter, box(200, 50), speed=200, detect_range=400,
                 line_of_sight=False, nav=g.NavGrid(400, 300, 20, [pg.Rect(100, 0, 20, 200)], agent_size=16),
                 solids=[pg.Rect(100, 0, 20, 200)], body=hb)
for _ in range(300):
    smart.update(16)
    hb.update(16)
check("Chaser + NavGrid gets around the wall", hunter.rect.x > 120)
smart.draw_debug(screen)

# ---------- Tiled paths ----------
level = g.TiledMap(os.path.join(ASSETS, "platformer.tmx"))
lift_route = level.get_path("lift_route")
bat_route = level.get_path("bat_route")
check("Tiled Polyline with mode property -> ping_pong", lift_route.mode == "ping_pong")
check("Tiled Polygon -> loop", bat_route.mode == "loop" and len(bat_route) == 4)
check("rects_of_type / objects_of_type",
      len(level.rects_of_type("ladder")) == 2 and len(level.objects_of_type("enemy")) == 3)
check("Custom properties are read", level.objects_of_type("moving_platform")[0]
      ["properties"]["path"] == "lift_route")
try:
    level.get_path("nope")
    check("Unknown path name gives a helpful error", False)
except ValueError as error:
    check("Unknown path name gives a helpful error", "lift_route" in str(error))

# ---------- Item kinds, slots, stats ----------
equip = g.Grid(0, 0, cols=2, rows=1, cell_size=50)
equip.set_slot(0, 0, accepts="weapon", label="Weapon")
equip.set_slot(1, 0, accepts=lambda item: item.stats.get("weight", 0) < 3)
sword = g.DragObject(0, 0, 40, 40, kind=["weapon", "sword"], stats={"damage": 7, "weight": 3},
                     name="Sword", grid=equip)
ring = g.DragObject(0, 0, 40, 40, kind="trinket", stats={"weight": 1})
check("kind / kinds / is_kind", sword.kind == "weapon" and sword.is_kind("sword"))
check("stats dictionary", sword.stats["damage"] == 7)
check("Slot accepts the right kind", equip.can_place(sword, 0, 0))
check("Slot refuses the wrong kind", not equip.can_place(ring, 0, 0))
check("accepts can be a function", equip.can_place(ring, 1, 0) and not equip.can_place(sword, 1, 0))
potions = g.Grid(0, 100, cols=3, rows=1, cell_size=50, accepts="potion")
check("Whole-grid accepts", not potions.can_place(sword, 0, 0))
backpack = g.Grid(200, 0, cols=2, rows=1, cell_size=50)
backpack.place(sword, 0, 0)
sword.grids = [backpack, equip]
sword.handle_event(pg.event.Event(pg.MOUSEBUTTONDOWN, button=1, pos=sword.rect.center))
sword.handle_event(pg.event.Event(pg.MOUSEBUTTONUP, button=1, pos=(75, 25)))
check("Dropping into a slot that refuses it goes back", sword.grid is backpack)
sword.handle_event(pg.event.Event(pg.MOUSEBUTTONDOWN, button=1, pos=sword.rect.center))
sword.handle_event(pg.event.Event(pg.MOUSEBUTTONUP, button=1, pos=(25, 25)))
check("Dropping into the right slot works", sword.grid is equip and sword.cell == (0, 0))
equip.draw(screen)

# ---------- Tooltip ----------
tips = g.Tooltip(delay=300)
button = g.Button(400, 400, 100, 40, "Hi")
button.draw(screen)
tips.attach(button, "Hello")
tips.attach(sword, lambda item: f"{item.name}: {item.stats['damage']}")
original = pg.mouse.get_pos
pg.mouse.get_pos = lambda: (450, 420)
tips.update(100)
check("Tooltip waits for the delay", tips._timer < tips.delay)
tips.update(300)
tips.draw(screen)
check("Tooltip shows after the delay", tips.current[0] is button and tips._timer >= 300)
pg.mouse.get_pos = lambda: sword.rect.center
tips.update(400)
check("Tooltip text can be a function", tips._text_for(*tips.current) == "Sword: 7")
pg.mouse.get_pos = original

print()
print("ALL TESTS PASS" if all(results) else f"{results.count(False)} TEST(S) FAILED")
pg.quit()
