"""
Automatic checks for the camera, Tiled and World extras (ideas 24 - 30):
camera.snap(), deadzone= / lookahead=, on_screen(), apply(parallax=),
Background, shake() on game time, level.tile_properties_at(),
"midground" layers and World(y_sort=True).
Also checks that the defaults still work exactly like v1.0.

Run this file in Visual Studio (right-click > Start without Debugging).
"""
import os
import sys
import tempfile

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
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


def old_camera_offset(camera_offset, target, size, world, smooth, tick):
    """The v1.0 camera maths, copied here so we can compare."""
    wanted = pg.Vector2(target.rect.centerx - size[0] / 2, target.rect.centery - size[1] / 2)
    wanted.x = max(0, min(wanted.x, world[0] - size[0]))
    wanted.y = max(0, min(wanted.y, world[1] - size[1]))
    amount = 1 - (1 - smooth) ** (tick / (1000 / 60))
    return camera_offset + (wanted - camera_offset) * min(1, amount)


# ---------------- v1.0 camera unchanged ----------------
player = box(1000, 700)
camera = g.Camera(3000, 2000, (800, 600))
camera.follow(player)
expected = pg.Vector2(0, 0)
same = True
for step in range(40):
    player.rect.x += 7
    player.rect.y += (step % 5) - 2
    expected = old_camera_offset(expected, player, (800, 600), (3000, 2000), 0.1, 16)
    camera.update(16)
    same = same and camera.offset.distance_to(expected) < 0.001
check("a Camera with no new options moves exactly like v1.0", same)
check("apply() with no parallax is the v1.0 apply",
      camera.apply(pg.Rect(100, 100, 5, 5)).topleft == pg.Rect(100, 100, 5, 5).move(
          -camera.offset.x, -camera.offset.y).topleft)

# ---------------- 24. snap ----------------
player = box(1000, 700)
camera = g.Camera(3000, 2000, (800, 600))
camera.follow(player)
camera.snap()
check("snap() jumps straight to the target", camera.offset == pg.Vector2(610, 410))
player.rect.topleft = (10, 10)
camera.snap()
check("snap() keeps inside the map edges", camera.offset == pg.Vector2(0, 0))
g.Camera(100, 100, (800, 600)).snap()
check("snap() with nothing to follow does nothing (no crash)", True)

zoom = g.ZoomCamera(g.Camera(3000, 2000, (800, 600)), (800, 600), zoom=2)
zoom.base.follow(box(1000, 700))
zoom.snap()
check("ZoomCamera.snap() centres the zoomed view",
      zoom.base.offset == pg.Vector2(1010 - 200, 710 - 150))

# ---------------- 25. deadzone ----------------
player = box(1490, 990)                     # centre (1500, 1000)
camera = g.Camera(3000, 2000, (800, 600), smooth=1, deadzone=(200, 100))
camera.follow(player)
camera.snap()
start = pg.Vector2(camera.offset)
player.rect.x += 90                         # still inside the box (half width 100)
player.rect.y -= 40
for _ in range(10):
    camera.update(16)
check("deadzone: small moves don't move the camera", camera.offset == start)
player.rect.x += 30                         # now 120 right of the middle: 20 past the edge
camera.update(16)
check("deadzone: pushing past the edge moves the camera just enough",
      camera.offset == start + pg.Vector2(20, 0))
check("deadzone=number works for both ways",
      g.Camera(10, 10, (8, 8), deadzone=50).deadzone == (50, 50))

# ---------------- 25. lookahead ----------------
player = box(1490, 990)
camera = g.Camera(3000, 2000, (800, 600), smooth=1, lookahead=100)
camera.follow(player)
camera.snap()
for _ in range(120):                        # walk right (and a little down)
    player.rect.x += 3
    player.rect.y += 1
    camera.update(16)
centre = camera.offset + pg.Vector2(400, 300)
ahead = centre.x - player.rect.centerx
check("lookahead: the view looks ahead to the right", 95 < ahead <= 100)
check("lookahead=number is sideways only", abs(centre.y - player.rect.centery) < 0.01)
for _ in range(60):                         # stand still: keep looking the same way
    camera.update(16)
check("lookahead: standing still keeps looking ahead",
      camera.offset.x + 400 - player.rect.centerx > 95)
for _ in range(120):                        # turn round
    player.rect.x -= 3
    camera.update(16)
check("lookahead: turning round looks the other way",
      camera.offset.x + 400 - player.rect.centerx < -95)

camera = g.Camera(3000, 2000, (800, 600), smooth=1, lookahead=(100, 50))
player = box(1490, 990)
camera.follow(player)
for _ in range(120):
    player.rect.y += 2
    camera.update(16)
check("lookahead=(x, y) also looks down",
      camera.offset.y + 300 - player.rect.centery > 45)

# ---------------- 26. on_screen ----------------
camera = g.Camera(3000, 2000, (800, 600))
camera.offset.update(1000, 500)
check("on_screen: a sprite in view", camera.on_screen(box(1300, 700)))
check("on_screen: a sprite out of view", not camera.on_screen(box(1900, 700)))
check("on_screen: margin counts things near the screen", camera.on_screen(box(1850, 700), margin=100))
check("on_screen: a Rect", camera.on_screen(pg.Rect(990, 490, 20, 20)))
check("on_screen: a point", camera.on_screen((1799, 1099)) and not camera.on_screen((999, 700)))
zoom = g.ZoomCamera(camera, (800, 600), zoom=2)          # now shows only 400 x 300
check("ZoomCamera.on_screen uses the zoomed view",
      zoom.on_screen((1350, 700)) and not zoom.on_screen((1500, 700)))
zoom.set_zoom(1)

# ---------------- 27. parallax apply / Background ----------------
camera = g.Camera(3000, 2000, (800, 600))
camera.offset.update(400, 200)
check("apply(parallax=0) stays put", camera.apply(pg.Rect(10, 10, 5, 5), parallax=0).topleft == (10, 10))
check("apply(parallax=0.5) moves half as far",
      camera.apply(pg.Rect(10, 10, 5, 5), parallax=0.5).topleft == (-190, -90))
check("apply_pos(parallax=0.25)", camera.apply_pos((10, 10), parallax=0.25) == (-90, -40))

stripe = pg.Surface((100, 50))
stripe.fill((0, 0, 255))
pg.draw.rect(stripe, (255, 0, 0), (0, 0, 10, 50))       # a red edge every 100 pixels
back = g.Background(stripe, parallax=0.5, y=100)
canvas = pg.Surface((800, 600))
camera.offset.update(0, 0)
canvas.fill((0, 0, 0))
back.draw(canvas, camera)
check("Background repeats across the screen",
      canvas.get_at((5, 120))[:3] == (255, 0, 0) and canvas.get_at((705, 120))[:3] == (255, 0, 0)
      and canvas.get_at((795, 120))[:3] == (0, 0, 255))
check("repeat_y=False: only one row", canvas.get_at((50, 200))[:3] == (0, 0, 0))
camera.offset.update(40, 0)                 # half of 40 = 20 pixels
canvas.fill((0, 0, 0))
back.draw(canvas, camera)
check("Background parallax 0.5 scrolls half as far",
      canvas.get_at((85, 120))[:3] == (255, 0, 0) and canvas.get_at((95, 120))[:3] == (0, 0, 255))
camera.offset.update(40, 300)
canvas.fill((0, 0, 0))
g.Background(stripe, parallax=0.5, repeat_y=True).draw(canvas, camera)
check("repeat_y=True fills the screen", (0, 0, 0) not in
      [canvas.get_at((x, y))[:3] for x in range(0, 800, 37) for y in range(0, 600, 41)])
canvas.fill((0, 0, 0))
g.Background(stripe, parallax=0, repeat_x=False, x=300, y=300).draw(canvas, camera)
check("parallax=0 never moves", canvas.get_at((305, 305))[:3] == (255, 0, 0))
zoom = g.ZoomCamera(camera, (800, 600), zoom=2)
canvas.fill((0, 0, 0))
# the base camera offset (40, 300) is doubled by the zoom: (80, 600)
g.Background(stripe, parallax=1, repeat_x=False, x=100, y=605).draw(canvas, zoom)
check("Background works with a ZoomCamera", canvas.get_at((25, 10))[:3] == (255, 0, 0)
      and canvas.get_at((35, 10))[:3] == (0, 0, 255))
zoom.set_zoom(1)
hills = g.Background(os.path.join(ASSETS, "hills.png"), parallax=0.3)
hills.draw(canvas, camera)
check("Background loads a picture file", hills.image.get_width() > 0)

# ---------------- 28. shake on game time ----------------
camera = g.Camera(3000, 2000, (800, 600))
camera.shake(300, 6)
camera.update(16)
check("shake shakes", camera.shake_offset != pg.Vector2(0, 0))
g.pause_timers()
camera.update(16)
check("no shaking while timers are paused", camera.shake_offset == pg.Vector2(0, 0))
pg.time.wait(400)                           # longer than the shake
g.resume_timers()
camera.update(16)
check("the rest of the shake happens after resume", camera.shake_offset != pg.Vector2(0, 0))
pg.time.wait(400)
camera.update(16)
check("...and then it stops", camera.shake_offset == pg.Vector2(0, 0))

# ---------------- debug drawing ----------------
camera = g.Camera(3000, 2000, (800, 600), deadzone=(200, 100), lookahead=50)
camera.follow(box(1000, 700))
camera.snap()
canvas.fill((0, 0, 0))
camera.draw_debug(canvas)
check("draw_debug draws the deadzone box", canvas.get_at((300, 250))[:3] == (255, 0, 255))
canvas.fill((0, 0, 0))
g.Camera(3000, 2000, (800, 600)).draw_debug(canvas)
check("draw_debug draws nothing for a v1.0 camera",
      pg.transform.average_color(canvas)[:3] == (0, 0, 0))


# ---------------- 29. tile_properties_at ----------------
level = g.TiledMap(os.path.join(ASSETS, "level1.tmx"))
water = level.tile_properties_at((19 * 32 + 5, 4 * 32 + 5))
check("water tile properties from Tiled", water == {"water": True, "speed": 0.5})
check("x, y works too", level.tile_properties_at(19 * 32 + 5, 4 * 32 + 5) == water)
check("pytmx's own keys are hidden", "frames" not in water and "id" not in water)
check("a tile with no properties gives {}", level.tile_properties_at((40, 40)) == {})
check("outside the map gives {}", level.tile_properties_at((-5, 20)) == {}
      and level.tile_properties_at((99999, 20)) == {})
check("level1: bushes and signs are in the midground", len(level.midground) == 13)
check("level1: grass at a sign's foot is on the ground (background)",
      any(t.rect.topleft == (224, 288) for t in level.background))
check("tile_property_at with a default", level.tile_property_at((40, 40), "speed", 1) == 1
      and level.tile_property_at((19 * 32, 4 * 32), "speed", 1) == 0.5)


# ---------------- 30. midground layers + y_sort ----------------
# A tiny test map made here: 8 x 8 pixel tiles. Tile 1 = red, 2 = green, 3 = blue.
folder = tempfile.mkdtemp()
tiles = pg.Surface((24, 8))
for i, colour in enumerate([(255, 0, 0), (0, 255, 0), (0, 0, 255)]):
    tiles.fill(colour, (i * 8, 0, 8, 8))
pg.image.save(tiles, os.path.join(folder, "tiles.png"))


def layer(layer_id, name, rows, properties=""):
    data = ",\n".join(",".join(str(n) for n in row) for row in rows)
    return (f' <layer id="{layer_id}" name="{name}" width="4" height="4">\n{properties}'
            f'  <data encoding="csv">\n{data}\n</data>\n </layer>\n')


EMPTY = [[0] * 4 for _ in range(4)]
with open(os.path.join(folder, "depth.tmx"), "w") as f:
    f.write('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<map version="1.10" orientation="orthogonal" renderorder="right-down" width="4" '
            'height="4" tilewidth="8" tileheight="8" infinite="0" nextlayerid="5" nextobjectid="1">\n'
            ' <tileset firstgid="1" name="t" tilewidth="8" tileheight="8" tilecount="3" columns="3">\n'
            '  <image source="tiles.png" width="24" height="8"/>\n'
            '  <tile id="0"><properties><property name="speed" type="float" value="0.5"/>'
            '<property name="mud" type="bool" value="true"/></properties></tile>\n'
            '  <tile id="1"><properties><property name="speed" type="float" value="2"/></properties></tile>\n'
            ' </tileset>\n'
            + layer(1, "Ground", [[1] * 4 for _ in range(4)])
            + layer(2, "Trees midground", [[0, 2, 0, 0], [0, 2, 0, 0], [0, 0, 0, 0], [0, 0, 0, 2]])
            + layer(3, "Rocks", [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 3, 0], [0, 0, 0, 0]],
                    '  <properties><property name="y_sort" type="bool" value="true"/></properties>\n')
            + layer(4, "Foreground", EMPTY)
            + '</map>\n')
depth_map = g.TiledMap(os.path.join(folder, "depth.tmx"))

check("a layer named ...midground goes in map.midground", len(depth_map.midground) == 4)
check("a layer with y_sort = true goes in map.midground too",
      any(t.rect.topleft == (16, 16) for t in depth_map.midground))
check("other layers still go in background", len(depth_map.background) == 16)
stack = sorted((t.rect.y, t.sort_y) for t in depth_map.midground if t.rect.x == 8)
check("tiles stacked in a column sort by the bottom of the stack", stack == [(0, 16), (8, 16)])
check("a single tile sorts by its own bottom",
      [t.sort_y for t in depth_map.midground if t.rect.topleft == (24, 24)] == [32])
check("top layer wins in tile_properties_at",
      depth_map.tile_properties_at((9, 1)) == {"speed": 2.0, "mud": True})

camera = g.Camera(32, 32, (32, 32))
little = pg.Surface((32, 32))


def colour_at(world, x, y):
    little.fill((0, 0, 0))
    world.draw(little)
    return little.get_at((x, y))[:3]


walker = g.SpriteObject(4, 4, 8, 8, bg=(255, 255, 255))   # white, over the tree trunk
for y_sort in (False, True):
    world = g.World(depth_map, camera, y_sort=y_sort)
    world.add_sprite(walker)
    walker.rect.topleft = (8, 2)            # bottom 10: behind the tree (stack bottom 16)
    behind = colour_at(world, 10, 6)
    walker.rect.topleft = (8, 10)           # bottom 18: in front of it
    in_front = colour_at(world, 10, 12)
    if y_sort:
        check("y_sort: walking behind the tree hides the sprite", behind == (0, 255, 0))
        check("y_sort: below the tree the sprite is in front", in_front == (255, 255, 255))
    else:
        check("no y_sort: sprites are always drawn over the midground",
              behind == (255, 255, 255) and in_front == (255, 255, 255))

back_one = g.SpriteObject(0, 0, 10, 10, bg=(255, 0, 255))
front_one = g.SpriteObject(4, 4, 10, 10, bg=(0, 255, 255))
for y_sort, wanted in ((False, (255, 0, 255)), (True, (0, 255, 255))):
    world = g.World(depth_map, g.Camera(32, 32, (32, 32)), y_sort=y_sort)
    world.add_sprite(front_one, back_one)    # added in the "wrong" order
    check(f"y_sort={y_sort}: sprite order", colour_at(world, 6, 6) == wanted)

world = g.World(depth_map, g.Camera(32, 32, (32, 32), deadzone=10), y_sort=True)
world.add_sprite(walker)
g.Debug.on = True
world.draw(little)
g.Debug.on = False
check("World draws the F1 debug view with y_sort (no crash)", True)
world.update(16)
check("World.update with a midground (no crash)", True)

# ---------------- Feet hitbox: TopDownBody(..., hitbox=) ----------------
def walk(body, dx, dy, frames=60):
    for _ in range(frames):
        body.move(dx, dy)
        body.update(16)


walls = [pg.Rect(0, 100, 200, 10), pg.Rect(300, 0, 10, 400)]
old = g.TopDownBody(g.SpriteObject(50, 150, 20, 30), solids=walls, speed=300)
check("no hitbox: the whole rect is the hitbox", old.hitbox_rect == old.sprite.rect)
same = True
new_way = g.TopDownBody(g.SpriteObject(50, 150, 20, 30), solids=walls, speed=300, hitbox=None)
for dx, dy in [(0, -1), (1, 0), (1, 1), (-1, 1), (0, -1)] * 4:
    walk(old, dx, dy, 10)
    walk(new_way, dx, dy, 10)
    same = same and old.sprite.rect == new_way.sprite.rect and old.touching == new_way.touching
check("hitbox=None moves and stops exactly like v1.0", same)

fence = pg.Rect(0, 100, 200, 10)            # the BASE of a fence
player = g.SpriteObject(50, 150, 20, 30)
feet = g.TopDownBody(player, solids=[fence], speed=300, hitbox=8)
check("hitbox=8 is a strip along the bottom", feet.hitbox_rect == pg.Rect(50, 172, 20, 8))
walk(feet, 0, -1)
check("from below: the feet stop under the fence base", feet.hitbox_rect.top == fence.bottom)
check("...while the head overlaps the fence picture", player.rect.top < fence.top)
below_bottom = player.rect.bottom
player.rect.topleft = (50, 0)
walk(feet, 0, 1)
check("from above: the feet stop on top of the base", feet.hitbox_rect.bottom == fence.top)
check("so the player is higher (drawn behind) from above, lower (in front) from below",
      player.rect.bottom < fence.bottom < below_bottom)
check("touching works with a hitbox", "bottom" in feet.touching)

narrow = g.TopDownBody(g.SpriteObject(0, 0, 20, 30), hitbox=(10, 6))
check("hitbox=(w, h) is centred along the bottom", narrow.hitbox_rect == pg.Rect(5, 24, 10, 6))
narrow.sprite.rect.topleft = (100, 100)
check("hitbox_rect follows the sprite", narrow.hitbox_rect == pg.Rect(105, 124, 10, 6))
huge = g.TopDownBody(g.SpriteObject(0, 0, 20, 30), hitbox=(50, 50))
check("a hitbox bigger than the sprite is cut down to it", huge.hitbox_rect == huge.sprite.rect)

slide = g.TopDownBody(g.SpriteObject(50, 150, 20, 30), solids=[fence], speed=300, hitbox=8)
walk(slide, 1, -1, 30)
check("diagonal moves slide along a wall with a hitbox",
      slide.hitbox_rect.top == fence.bottom and slide.sprite.rect.x > 50)

aim = g.TopDownBody(g.SpriteObject(0, 0, 20, 30), hitbox=8)
aim.move_towards((10, 200))                 # straight below the feet
check("move_towards aims the feet", aim._direction.x == 0 and aim._direction.y > 0)

canvas.fill((0, 0, 0))
feet.draw_debug(canvas)
check("draw_debug draws the hitbox", canvas.get_at(feet.hitbox_rect.topleft)[:3] == (0, 255, 255))
zoom = g.ZoomCamera(g.Camera(1000, 1000, (800, 600)), (800, 600), zoom=2)
check("ZoomCamera.apply makes rects bigger by the zoom",
      zoom.apply(pg.Rect(10, 20, 5, 5)) == pg.Rect(20, 40, 10, 10))
check("level1: signs and bushes have base collision boxes",
      len([o for o in level.collision_objects if o["rect"].height <= 10]) == 10)

print()
print("ALL TESTS PASS" if all(results) else f"{results.count(False)} TEST(S) FAILED")
pg.quit()
