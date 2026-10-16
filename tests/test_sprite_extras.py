"""
Automatic checks for the sprite and animation extras (ideas 17 - 23):
Animator play_once(then=, on_finish=) / busy, frame_rate for each animation,
on_frame, SpriteObject angle / point_at / turn / image_faces,
collides_with(pixel=True) / collides_with_any, distance_to / direction_to,
smooth_move. Also checks that the defaults still work exactly like v1.0.

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

results = []


def check(name, condition):
    results.append(bool(condition))
    print(("PASS  " if condition else "FAIL  ") + name)


def frames(count, size=(10, 10)):
    """Plain coloured frames, so no image files are needed."""
    pictures = []
    for i in range(count):
        picture = pg.Surface(size)
        picture.fill((i * 20, 100, 100))
        pictures.append(picture)
    return pictures


def make_animator():
    # 8 frames: 0-3 = "idle", 4-7 = "attack"; frame_rate 10 = 100 ms a frame
    animator = g.Animator(frames(8), frame_rate=10)
    animator.add_animation("idle", [0, 1, 2, 3])
    animator.add_animation("attack", [4, 5, 6, 7])
    animator.play("idle")
    return animator


# ---------------- 17. play_once then= / on_finish= / busy ----------------
a = make_animator()
a.play_once("attack")
for _ in range(10):
    a.update(100)
check("v1.0 play_once stops on the last frame",
      a.current_animation == "attack" and not a.playing and a.current_frame_index == 3)
check("busy is False once it has stopped", not a.busy)

a = make_animator()
finished = []
a.play_once("attack", then="idle", on_finish=lambda: finished.append(1))
a.update(0)
check("busy while the one-off plays", a.busy)
a.update(100); a.update(100); a.update(100)
check("still on attack before the end", a.current_animation == "attack" and a.busy)
a.update(100)
check("then= goes back to idle", a.current_animation == "idle" and a.playing and a.loop)
check("on_finish ran once", finished == [1])
check("busy is False after then=", not a.busy)
for _ in range(20):
    a.update(100)
check("on_finish does not run again", finished == [1])

a = make_animator()
finished = []
a.play_once("attack", then="idle", on_finish=lambda: finished.append(1))
a.update(100)
a.play("idle")                       # interrupted (e.g. the player got hit)
for _ in range(10):
    a.update(100)
check("play() cancels then= / on_finish=", finished == [] and not a.busy)

a = make_animator()
a.play_once("attack", then="idle")
a.update(450)                        # one big tick goes past the end
check("a big tick still lands on idle", a.current_animation == "idle")

# ---------------- 18. frame_rate for each animation ----------------
a = g.Animator(frames(8), frame_rate=10)
a.add_animation("walk", [0, 1, 2, 3])
a.add_animation("run", [4, 5, 6, 7], frame_rate=20)      # 50 ms a frame
a.play("walk")
a.update(100)
check("walk uses the Animator frame_rate", a.current_frame_index == 1)
a.play("run")
a.update(100)
check("run uses its own frame_rate", a.current_frame_index == 2)

# ---------------- 19. on_frame ----------------
a = make_animator()
steps = []
a.on_frame("idle", 2, lambda: steps.append("step"))
a.update(0)
a.update(100)
check("not before the frame", steps == [])
a.update(100)
check("runs when the frame shows", steps == ["step"])
a.update(100); a.update(100)                       # frame 3, then back to 0
a.update(250)                                      # jumps over frame 1 to frame 2
check("a big tick never skips the frame", steps == ["step", "step"])

a = make_animator()
starts = []
a.on_frame("attack", 0, lambda: starts.append(1))
a.play_once("attack")
a.update(10)
check("frame 0 runs when an animation starts", starts == [1])
a.update(10)
check("...only once", starts == [1])

a = make_animator()
hits = []
a.on_frame("idle", 0, lambda: hits.append("idle0"))
a.play_once("attack", then="idle")
a.update(0)
a.update(400)
check("frame 0 of the then= animation runs too", hits == ["idle0"])

# ---------------- 20. angle / point_at / turn ----------------
s = g.SpriteObject(100, 100, 40, 20)
check("angle starts at 0 (up) with no turning", s.angle == 0 and s._drawn_image() is s.image)
s.point_at((500, 110))
check("point_at right = 90", round(s.angle) == 90)
s.point_at((120, 0))
check("point_at up = 0", round(s.angle) == 0)
s.point_at((120, 400))
check("point_at down = 180", round(s.angle) == 180)
s.point_at((0, 110))
check("point_at left = 270", round(s.angle) == 270)
s.point_at(g.SpriteObject(400, 100, 40, 20))
check("point_at works with a sprite", round(s.angle) == 90)
s.point_at(s.rect.center)
check("point_at its own centre keeps the angle", round(s.angle) == 90)
s.angle = 0
s.turn(-30)
check("turn() wraps round", round(s.angle) == 330)

rect_before = s.rect.copy()
s.angle = 45
s.draw(screen)
check("turning never changes the hitbox", s.rect == rect_before)
turned = s._drawn_image()
check("the drawn picture is turned (bigger)", turned.get_width() > 40)
check("turned pictures are cached", s._drawn_image() is turned)

s.angle = 90
picture = s._drawn_image()
check("90 = turned a quarter, clockwise", picture.get_size() == (20, 40))

right = g.SpriteObject(0, 0, 40, 20, image_faces="right")
check("image_faces='right' starts at 90 and is not turned",
      right.angle == 90 and right._drawn_image() is right.image)
right.point_at((20, 500))            # down
check("image_faces='right' turned to face down", right._drawn_image().get_size() == (20, 40))
try:
    g.SpriteObject(0, 0, image_faces="north")
    check("bad image_faces gives a clear error", False)
except ValueError as error:
    check("bad image_faces gives a clear error", "image_faces" in str(error))

# Drawn in the right place: centred on the hitbox, also with a camera
s = g.SpriteObject(200, 200, 40, 20, bg=(255, 0, 0))
s.angle = 90
screen.fill((0, 0, 0))
s.draw(screen)
check("turned picture centred on the hitbox",
      screen.get_at((220, 192))[:3] == (255, 0, 0) and screen.get_at((205, 210))[:3] == (0, 0, 0))

# Animator + angle + flip_x together
anim = make_animator()
walker = g.SpriteObject(0, 0, animator=anim)
walker.flip_x = True
walker.angle = 90
walker.update(100)
walker.draw(screen)
check("animated, flipped, turned sprite draws", True)

# ---------------- 21. pixel=True and collides_with_any ----------------
def circle_sprite(x, y):
    picture = pg.Surface((40, 40), pg.SRCALPHA)
    pg.draw.circle(picture, (255, 200, 0), (20, 20), 20)
    return g.SpriteObject(x, y, image=picture)

a, b = circle_sprite(0, 0), circle_sprite(34, 34)     # only the see-through corners touch
check("rects touch", a.collides_with(b))
check("pixels don't touch", not a.collides_with(b, pixel=True))
c = circle_sprite(20, 0)
check("pixels do touch when they overlap", a.collides_with(c, pixel=True))
wall = pg.sprite.Sprite()
wall.rect = pg.Rect(38, 0, 10, 40)                    # no image: solid rect
check("thing with no picture counts as solid", a.collides_with(wall, pixel=True))

coins = [circle_sprite(500, 500), b, c]
check("collides_with_any finds the first hit", a.collides_with_any(coins) is b)
check("collides_with_any pixel=True skips corner-only hits", a.collides_with_any(coins, pixel=True) is c)
check("collides_with_any never returns itself", a.collides_with_any([a]) is None)
check("collides_with_any with nothing hit is None", a.collides_with_any([circle_sprite(500, 500)]) is None)
group = pg.sprite.Group(circle_sprite(500, 500), c)
check("collides_with_any works with a Group", a.collides_with_any(group) is c)

stick = g.SpriteObject(100, 100, 60, 6, bg=(255, 255, 255))      # a long thin sprite
dot = g.SpriteObject(127, 70, 6, 6, bg=(255, 255, 255))           # above its middle
check("flat stick misses the dot", not stick.collides_with(dot, pixel=True))
stick.image_faces = "right"         # the stick picture points right...
stick.angle = 0                     # ...so angle 0 stands it up
check("stood-up stick hits the dot (pixel=True uses the turned picture)",
      stick.collides_with(dot, pixel=True))

# ---------------- 22. distance_to / direction_to ----------------
p = g.SpriteObject(0, 0, 20, 20)                  # centre (10, 10)
check("distance_to a position", p.distance_to((40, 50)) == 50)
check("distance_to a sprite", p.distance_to(g.SpriteObject(30, 40, 20, 20)) == 50)
check("distance_to a Rect", p.distance_to(pg.Rect(30, 40, 20, 20)) == 50)
d = p.direction_to((40, 50))
check("direction_to has length 1", round(d.length(), 6) == 1 and round(d.x, 2) == 0.6)
check("direction_to the same spot is (0, 0)", p.direction_to((10, 10)) == pg.Vector2(0, 0))

# ---------------- 23. smooth_move ----------------
old = g.SpriteObject(0, 0, 10, 10)
for _ in range(10):
    old.move(0.4, 0)
check("v1.0 move() still drops fractions", old.rect.x == 0)
snail = g.SpriteObject(0, 0, 10, 10, smooth_move=True)
for _ in range(10):
    snail.move(0.4, 0.25)
check("smooth_move keeps fractions", snail.rect.topleft == (4, 2))
snail.rect.x = 100                                 # moved from outside
snail.move(0.4, 0)
check("smooth_move follows a rect moved from outside", snail.rect.x == 100)
snail.move(0.4, 0)
check("...and carries on from there", snail.rect.x == 101)
snail.move(-0.8, 0)
check("smooth_move goes backwards too", snail.rect.x == 100)

# ---------------- v1.0 defaults unchanged ----------------
plain = g.SpriteObject(10, 10, 30, 30, bg=(0, 255, 0))
screen.fill((0, 0, 0))
plain.draw(screen)
check("an unturned sprite draws exactly where v1.0 did",
      screen.get_at((10, 10))[:3] == (0, 255, 0) and screen.get_at((9, 9))[:3] == (0, 0, 0))
bullet = g.Projectile(100, 100, (300, 0))
check("Projectile is not turned by angle", bullet._drawn_image() is bullet.image)

# Chain must not turn sprites that follow it (it sets angles on its links)
leader = g.SpriteObject(100, 100, 20, 20)
elf = g.SpriteObject(0, 0, 20, 20)
party = g.Chain(leader, segments=[elf], spacing=30)
for y in range(100, 300, 10):                     # walking down: Chain angle -90
    leader.rect.y = y
    party.update(16)
check("Chain does not turn a SpriteObject that follows it",
      elf._drawn_image() is elf.image and elf.angle == 0)

print()
print("ALL TESTS PASS" if all(results) else f"{results.count(False)} TEST(S) FAILED")
pg.quit()
