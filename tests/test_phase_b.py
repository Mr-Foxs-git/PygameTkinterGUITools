"""
Automatic checks for the Phase B refactor (consistent widgets).

Run this file in Visual Studio (right-click > Start without Debugging).
"""
import os
import sys

os.environ["SDL_VIDEODRIVER"] = "dummy"
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

import pygame as pg
pg.init()
screen = pg.display.set_mode((400, 300))

import PygameTkinterGUITools as g

results = []


def check(name, condition):
    results.append(condition)
    print(("PASS  " if condition else "FAIL  ") + name)


def click(pos):
    return pg.event.Event(pg.MOUSEBUTTONDOWN, button=1, pos=pos)


def key(k, unicode=""):
    return pg.event.Event(pg.KEYDOWN, key=k, unicode=unicode, mod=0)


# ---- Every widget has the same methods ----
widgets = [g.Label(0, 0, "hi"), g.Button(0, 0, 10, 10, "b"), g.TextBox(0, 0),
           g.Frame(0, 0, 10, 10), g.Popup(0, 0, 100, 100)]
same = all(hasattr(w, m) for w in widgets
           for m in ("draw", "handle_event", "update", "config", "configure",
                     "show", "hide", "toggle_visibility", "rect"))
check("All widgets share the same methods", same)
for w in widgets:
    w.show()
    w.draw(screen)
    w.handle_event(click((5, 5)))
    w.update(16)
check("All widgets draw / handle_event / update without errors", True)

# ---- Label ----
lab = g.Label(20, 30, "Score: 0", fg=(255, 0, 0), bg=(0, 0, 0))
check("Label(x, y, text) order", (lab.x, lab.y, lab.text) == (20, 30, "Score: 0"))
w_before = lab.rect.width
lab.config(text="Score: 1000")
check("Label config(text=) changes text and size",
      lab.text == "Score: 1000" and lab.rect.width > w_before)
lab.configure(fg=(0, 255, 0))
check("configure() works like config()", lab.fg == (0, 255, 0))
try:
    lab.config(colr=(1, 1, 1))
    check("Unknown option gives an error", False)
except ValueError:
    check("Unknown option gives an error", True)
lab.text = "changed directly"
lab.draw(screen)
check("Label size updates when text is changed directly",
      lab.rect.width == g.get_font(None, 24).size("changed directly")[0])
cl = g.Label(100, 100, "centre", center=True)
check("Label center=True", cl.rect.center == (100, 100))

# ---- Button ----
hits = []
b = g.Button(10, 10, 100, 40, "Go", command=lambda: hits.append(1),
             border_colour=(1, 2, 3), border_width=2, shadow=True, shadow_colour=(0, 0, 0, 50))
check("Button border_colour (UK spelling) accepted", b.border_color == (1, 2, 3))
check("Button shadow_colour (UK spelling) accepted", b.shadow_color == (0, 0, 0, 50))
b.draw(screen)
b.handle_event(click((50, 30)))
check("Button command= runs when clicked", hits == [1])
b.config(text="Stop", command=lambda: hits.append(2), border_colour=(9, 9, 9))
b.handle_event(click((50, 30)))
check("Button config(command=, border_colour=)",
      hits == [1, 2] and b.text == "Stop" and b.border_color == (9, 9, 9))
b.hide()
b.handle_event(click((50, 30)))
check("Hidden Button can't be clicked", hits == [1, 2])

# ---- TextBox ----
entered = []
tb = g.TextBox(10, 10, max_chars=5, label="Name:", on_enter=lambda: entered.append(tb.get()))
box = tb.box_rect.move(tb.rect.topleft)
tb.handle_event(click(box.center))
check("Click TextBox makes it active", tb.active)
for ch in "abcdefg":
    tb.handle_event(key(ord(ch), ch))
check("TextBox max_chars", tb.get() == "abcde")
tb.handle_event(key(pg.K_BACKSPACE))
check("Backspace", tb.get() == "abcd")
tb.handle_event(key(pg.K_RETURN))
check("on_enter runs when Enter pressed", entered == ["abcd"])
check("get_text() still works", tb.get_text() == "abcd")
tb.clear()
check("clear()", tb.get() == "")
for pos in ("left", "right", "top", "bottom"):
    t = g.TextBox(0, 0, label="Hi", label_position=pos)
    inside = t.rect.contains(t.box_rect.move(t.rect.topleft)) and \
        t.rect.contains(t.label_rect.move(t.rect.topleft))
    check(f"TextBox label {pos}: box and label inside rect", inside)
    t.draw(screen)

# ---- Frame and Popup ----
hits.clear()
fr = g.Frame(100, 100, 200, 100, border_colour=(5, 5, 5))
btn = g.Button(0, 0, 50, 20, "in", command=lambda: hits.append("frame"))
fr.add(btn, g.Label(0, 30, "label"))
check("Frame.add() takes several widgets", len(fr.children) == 2)
fr.handle_event(click((115, 115)))                 # 100 + 10 pad + 5
check("Button in Frame clicks", hits == ["frame"])
fr.config(x=200)
fr.handle_event(click((215, 115)))
check("Moving a Frame moves its children", hits == ["frame", "frame"])

pop = g.Popup(50, 50, 200, 150, "Hello")
check("Popup starts hidden", not pop.visible)
pop.show()
pop.draw(screen)
pop.handle_event(click((50 + 200 - 25, 50 + 15)))  # the X button
check("Popup close button hides it", not pop.visible)

# ---- Fonts are cached ----
check("Fonts are reused", g.get_font(None, 30) is g.get_font(None, 30))
g.draw_text(screen, "hello", 10, 10, fg=(255, 255, 255), font_size=30, center=True)
check("draw_text works", True)

# ---- Animator timing keeps leftover time ----
frames = [pg.Surface((4, 4)) for _ in range(10)]
anim = g.Animator(frames, frame_rate=10)          # 1 frame every 100 ms
for _ in range(10):
    anim.update(30)                                # 300 ms total
check("Animator: 300 ms at 10 fps = frame 3", anim.current_frame_index == 3)
check("Animator.image is the current frame", anim.image is not None)

# ---- SpriteObject ----
sp = g.SpriteObject(10, 10, 20, 20, animator=g.Animator(frames))
sp.update(150)
check("SpriteObject keeps its size", sp.image.get_size() == (20, 20))
cam = g.Camera(1000, 1000, (400, 300))
cam.offset.update(5, 5)
sp.draw(screen, cam)
check("SpriteObject.draw(screen, camera)", True)

# ---- Camera ----
target = g.SpriteObject(500, 500)
cam = g.Camera(1000, 1000, (400, 300), smooth=0.1)
cam.follow(target)
cam_a = g.Camera(1000, 1000, (400, 300), smooth=0.1)
cam_a.follow(target)
for _ in range(60):          # 60 fps for 1 second
    cam.update(1000 / 60)
for _ in range(30):          # 30 fps for 1 second
    cam_a.update(1000 / 30)
check("Camera smoothing is the same at 30 and 60 fps",
      abs(cam.offset.x - cam_a.offset.x) < 1)
check("Camera screen_to_world", cam.screen_to_world((0, 0)) == (cam.offset.x, cam.offset.y))

# ---- ZoomCamera ----
base = g.Camera(1000, 1000, (400, 300))
zc = g.ZoomCamera(base, (400, 300), zoom=0.5)
check("ZoomCamera zoom out shows a bigger area", (base.screen_w, base.screen_h) == (800, 600))
check("ZoomCamera is crisp by default", zc.smooth is False)
zc.set_zoom(100)
check("ZoomCamera zoom is limited", zc.zoom == g.ZoomCamera.MAX_ZOOM)

# ---- TiledMap + World (needs tests/test_map.tmx) ----
tmx = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_map.tmx")
m = g.TiledMap(tmx)
check("TiledMap object with class= (Tiled 1.9+) is a trigger",
      any(t["name"] == "door" for t in m.triggers))
world_cam = g.Camera(m.width, m.height, (400, 300))
world = g.World(m, world_cam)
world.add_sprite(g.SpriteObject(0, 0, 8, 8))
world.update(16)
world.draw(screen)
zc2 = g.ZoomCamera(world_cam, (400, 300), zoom=2)
zc2.update(16)
zc2.draw_world(world, screen)
check("World and ZoomCamera draw", True)

# ---- pytmx only needed for maps ----
import inspect
top_level_imports = [line for line in inspect.getsource(g).splitlines()
                     if line.startswith(("import ", "from "))]
check("pytmx is not imported at the top of the library",
      not any("pytmx" in line for line in top_level_imports))

print()
print("ALL TESTS PASS" if all(results) else f"{results.count(False)} TEST(S) FAILED")
pg.quit()
