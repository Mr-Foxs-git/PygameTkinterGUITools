"""
Automatic checks for the Phase A bug fixes.

Run this file in Visual Studio (right-click > Start without Debugging) or with
    python tests/test_phase_a.py
No window opens. It prints PASS/FAIL for each check.
"""
import os
import sys

os.environ["SDL_VIDEODRIVER"] = "dummy"          # no real window needed
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

import pygame as pg
pg.init()
screen = pg.display.set_mode((400, 300))

import PygameTkinterGUITools as g


def click(pos):
    return pg.event.Event(pg.MOUSEBUTTONDOWN, button=1, pos=pos)


results = []


def check(name, condition):
    results.append(condition)
    print(("PASS  " if condition else "FAIL  ") + name)


# A1 Button clicks at its real position
hits = []
b = g.Button(100, 100, 50, 30, "Hi", action=lambda: hits.append("b"))
b.handle_event(click((120, 110)))
b.handle_event(click((10, 10)))
check("A1 Button clicks where it is drawn", hits == ["b"])

hits.clear()
bc = g.Button(100, 100, 50, 30, "C", center=True, action=lambda: hits.append("c"))
bc.handle_event(click((100, 100)))
check("A1 Centred Button clicks", hits == ["c"])

# A4 Frame alternative spellings
f = g.Frame(50, 50, 200, 150, bg=(1, 2, 3), border_colour=(4, 5, 6), border=5)
check("A4 Frame bg / border_colour / border work",
      (f.background, f.border_color, f.border_width) == ((1, 2, 3), (4, 5, 6), 5))
f2 = g.Frame(0, 0, 10, 10)
check("A4 Frame defaults still work", (f2.background, f2.border_width) == ((60, 60, 60), 2))

# A5 Button inside Frame (frame 50 + pad 10 + button 10 = 70)
hits.clear()
f.add(g.Button(10, 10, 40, 20, "x", action=lambda: hits.append("f")))
f.draw(screen)
f.handle_event(click((75, 75)))
check("A5 Button inside Frame clicks in the right place", hits == ["f"])

# A6 Hidden Frame ignores clicks
f.toggle_visibility()
f.handle_event(click((75, 75)))
f.draw(screen)
check("A6 Hidden Frame ignores clicks", hits == ["f"])
f.toggle_visibility()

# A7 Frame passes update() to children
tb = g.TextBox(0, 60)
f.add(tb)
before = tb.cursor_visible
f.update(500)
check("A7 TextBox cursor blinks inside Frame", tb.cursor_visible != before)

# A8 / A9 Animator with surfaces and frame numbers
frames = [pg.Surface((8, 8)) for _ in range(4)]
a = g.Animator(frames)
a.add_animation("walk", [0, 1])
a.add_animation("attack", [2, 3])
check("A9 add_animation with frame numbers", a.animations["walk"]["frames"] == [0, 1])
a.play_once("attack")
for _ in range(5):
    a.update(200)
finished = not a.playing
a.play("walk")
for _ in range(5):
    a.update(200)
check("A8 play() loops again after play_once()", finished and a.playing and a.loop)

# A10 SpriteObject size kept and no-image default
s = g.SpriteObject(0, 0, 16, 16, animator=g.Animator(frames))
s.update(200)
check("A10 SpriteObject keeps its size when animating", s.image.get_size() == (16, 16))
check("A10 SpriteObject with no image", g.SpriteObject(5, 5).rect.size == (32, 32))

# A11 Popup children below title, close button, offset
hits.clear()
p = g.Popup(100, 50, 200, 150)
p.add(g.Button(0, 0, 50, 20, "ok", action=lambda: hits.append("p")))
p.show()
p.draw(screen)
p.handle_event(click((105, 95)))                # 50 + 40 title bar + 5
check("A11 Popup child below title bar clicks", hits == ["p"])
p.handle_event(click((275, 65)))                # close button "X"
check("A11 Popup close button", not p.visible)
p.show()
p.draw(screen, offset=(10, 10))
check("A11 Popup accepts offset", True)

# A2 / A3 TiledMap (only if a test map exists)
tmx = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_map.tmx")
if os.path.exists(tmx):
    m = g.TiledMap(tmx)
    check("A2 TiledMap spawn point", m.spawn_points.get("player_spawn") == (8, 8))
    check("A2 TiledMap collision object", len(m.collision_objects) == 1)
    check("A2 TiledMap path", len(m.paths) == 1)
    if m.paths:
        check("A2 TiledMap path points in map coordinates",
              m.paths[0]["points"] == [(4, 4), (20, 20)])
    animated = [t for t in m.background if isinstance(t, g.AnimatedTile)]
    check("A3 TiledMap animated tile found", len(animated) == 1)
    first = animated[0].image
    animated[0].update(250)
    check("A3 Animated tile changes frame", animated[0].image is not first)
else:
    print("SKIP  A2/A3 TiledMap (put a map at tests/test_map.tmx to test it)")

print()
print("ALL TESTS PASS" if all(results) else f"{results.count(False)} TEST(S) FAILED")
pg.quit()
