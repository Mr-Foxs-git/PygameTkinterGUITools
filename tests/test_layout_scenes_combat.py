"""
Automatic checks for grid / pack / place, Scenes, timers, saving,
high scores, Health, projectiles and effects.

Run this file in Visual Studio (right-click > Start without Debugging).
"""
import os
import sys
import tempfile

os.environ["SDL_VIDEODRIVER"] = "dummy"
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

import pygame as pg
pg.init()
screen = pg.display.set_mode((800, 600))

import PygameTkinterGUITools as g

results = []


def check(name, condition):
    results.append(bool(condition))
    print(("PASS  " if condition else "FAIL  ") + name)


# A pretend clock, so timer tests don't depend on how fast the computer is
clock_ms = [100000]
real_get_ticks = pg.time.get_ticks
pg.time.get_ticks = lambda: clock_ms[0]


def wait(ms, step=16):
    """Move the pretend clock forward, running timers like a game would."""
    for _ in range(ms // step):
        clock_ms[0] += step
        g.update_timers(step)


# ---------- grid ----------
form = g.Frame(100, 100, pad_x=10, pad_y=10)
a = g.Label(form, text="Name:")
b = g.Button(form, text="Go", width=100, height=40)
check("Widgets made with a parent are added to it", a.parent is form and a in form.children)
check("grid() returns the widget (no 'None' surprise)", a.grid(row=0, column=0) is a)
b.grid(row=0, column=1, padx=5)
form._arrange()
check("Column 1 starts after column 0", b.x >= a.width)
check("padx moves the widget in", b.x == a.width + 5)
check("Frame without a size grows to fit", form.width == a.width + 110 + 20)
tall = g.Button(form, text="Tall", width=50, height=100).grid(row=1, column=0, columnspan=2)
form._arrange()
check("Row 1 starts below row 0", tall.y >= 40)
check("columnspan centres across both columns",
      abs(tall.get_rect().centerx - (a.width + 110) / 2) <= 1)

stretchy = g.Frame(0, 0, 400, 200, pad_x=0, pad_y=0)
s1 = g.Label(stretchy, text="L").grid(row=0, column=0, sticky="ew")
s2 = g.Button(stretchy, text="B", width=50, height=30).grid(row=0, column=1, sticky="e")
stretchy.columnconfigure(0, weight=1)
stretchy._arrange()
check("weight=1 gives the spare space to that column", s1.get_rect().width == 350)
check("sticky='e' sits on the right", s2.get_rect().right == 400)
check("sticky='ew' stretches the widget", s1.get_rect().width > s1.width)

# Mistakes are caught
forgot = g.Frame(0, 0, 200, 100)
lost = g.Label(forgot, text="Lost")
forgot._arrange()
check("Forgetting grid(): widget not shown, with a warning",
      lost not in forgot._visible_children() and
      any("no grid()" in w for w in forgot._debug_info["warnings"]))
clash = g.Frame(0, 0, 300, 100)
g.Label(clash, text="A").grid(row=0, column=0)
g.Label(clash, text="B").grid(row=0, column=0)
clash._arrange()
check("Two widgets in one cell gives a warning",
      any("both in row 0, column 0" in w for w in clash._debug_info["warnings"]))
mixed = g.Frame(0, 0, 300, 100)
g.Label(mixed, text="A").grid(row=0, column=0)
try:
    g.Label(mixed, text="B").pack()
    check("Mixing grid and pack gives a clear error", False)
except g.LayoutError as error:
    check("Mixing grid and pack gives a clear error", "same Frame" in str(error))
small = g.Frame(0, 0, 60, 40)
g.Label(small, text="Far too long to fit in here").grid(row=0, column=0)
small._arrange()
check("Too big for the Frame gives a warning",
      any("don't fit" in w for w in small._debug_info["warnings"]))
try:
    g.Label(10, 10, "x").grid()
    check("grid() without a parent gives a helpful error", False)
except g.LayoutError:
    check("grid() without a parent gives a helpful error", True)

# Clicking a gridded button works
hits = []
click_frame = g.Frame(50, 50, pad_x=10, pad_y=10)
cb = g.Button(click_frame, text="Hi", width=80, height=30, command=lambda: hits.append(1))
cb.grid(row=0, column=0, padx=20, pady=20)
click_frame.draw(screen)
click_frame.handle_event(pg.event.Event(pg.MOUSEBUTTONDOWN, button=1,
                                        pos=cb.get_rect(cb._last_offset).center))
check("A gridded Button can be clicked", hits == [1])

# ---------- pack ----------
bar = g.Frame(0, 0, 300, 200, pad_x=0, pad_y=0)
top = g.Button(bar, text="Top", width=80, height=30).pack(side="top")
fill = g.Label(bar, text="fill").pack(side="bottom", fill="x")    # before left / right
left = g.Button(bar, text="L", width=40, height=30).pack(side="left")
right = g.Button(bar, text="R", width=40, height=30).pack(side="right")
bar._arrange()
check("pack top: at the top, centred", top.get_rect().top == 0 and top.get_rect().centerx == 150)
check("pack left / right go to the sides", left.get_rect().left == 0 and right.get_rect().right == 300)
check("fill='x' stretches across", fill.get_rect().width == 300)

# ---------- place ----------
area = g.Frame(0, 0, 400, 300, pad_x=0, pad_y=0)
corner = g.Button(area, text="?", width=30, height=30).place(relx=1.0, rely=0.0, anchor="ne")
middle = g.Button(area, text="M", width=60, height=20).place(relx=0.5, rely=0.5, anchor="center")
area._arrange()
check("place relx=1 anchor='ne' = top-right corner", corner.get_rect().topright == (400, 0))
check("place anchor='center' = middle", middle.get_rect().center == (200, 150))

# ---------- Debug view ----------
g.Debug.on = False
g.Debug.handle_event(pg.event.Event(pg.KEYDOWN, key=pg.K_F1, mod=0, unicode=""))
check("F1 turns debug on (and paths)", g.Debug.on and g.Path.show_all)
for frame in (form, stretchy, clash, bar, area, forgot):
    frame.draw(screen)
root = g.Root(screen)
g.Label(root, text="Root").grid(row=0, column=0)
root.draw(screen)
form.layout_report()
check("Debug view and layout_report draw / print without errors", True)
g.Debug.toggle()

# ---------- Timers ----------
fired = []
g.after(500, fired.append, "once")
wait(400)
check("after(): not yet", fired == [])
wait(200)
check("after(): runs once", fired == ["once"])
rid = g.after_repeat(100, fired.append, "r")
wait(350)
check("after_repeat runs again and again", fired.count("r") == 3)
g.after_cancel(rid)
wait(300)
check("after_cancel stops it", fired.count("r") == 3)
done = []
cd = g.Countdown(3000, on_finish=lambda: done.append(True))
wait(1000)
check("Countdown seconds_left / text", abs(cd.seconds_left() - 2) < 0.05 and cd.text() == "0:03")   # rounds up, like a real countdown
cd.pause()
wait(5000)
check("Countdown pause", abs(cd.seconds_left() - 2) < 0.05 and not done)
cd.resume()
wait(2100)
check("Countdown finishes and runs on_finish", cd.finished and done == [True])

# ---------- Scenes ----------
log = []


class Over(g.Scene):
    def start(self, score=0):
        log.append(("over", score))
        g.after(100, log.append, "timer from over")

    def stop(self):
        log.append("over stopped")


def game_start():
    log.append("game started")
    g.after(1000, log.append, "game timer")


scenes = g.Scenes()
scenes.add("game", start=game_start, draw=lambda s: s.fill((0, 0, 0)))
scenes.add("over", Over())
check("First scene added starts straight away", scenes.current_name == "game"
      and log == ["game started"])
scenes.switch("over", score=42)
check("switch() passes data to start()", ("over", 42) in log and scenes.current_name == "over")
clock_ms[0] += 2000
scenes.update(16)
check("Timers from the old scene are cancelled", "game timer" not in log)
check("Timers in the new scene run", "timer from over" in log)
scenes.switch("game", transition="fade", ms=400)
for _ in range(10):
    clock_ms[0] += 16
    scenes.update(16)
    scenes.draw(screen)
check("Fade: still the old scene halfway through", scenes.current_name == "over")
for _ in range(20):
    clock_ms[0] += 16
    scenes.update(16)
    scenes.draw(screen)
check("Fade: then the new scene", scenes.current_name == "game" and not scenes.transitioning
      and "over stopped" in log)
scenes.switch("over", transition="slide_left", ms=200)
for _ in range(15):
    scenes.update(16)
    scenes.draw(screen)
check("Slide transition works", scenes.current_name == "over" and not scenes.transitioning)
try:
    scenes.switch("nowhere")
    check("Unknown scene gives a helpful error", False)
except ValueError:
    check("Unknown scene gives a helpful error", True)
g.cancel_all_timers()

# ---------- Saving ----------
folder = tempfile.mkdtemp()
path = os.path.join(folder, "save.json")
volume = g.IntVar(70)
g.save_data(path, level=3, volume=volume, items=["sword"])
data = g.load_data(path, default={"level": 1, "coins": 5})
check("save_data / load_data (Variables saved as values)",
      data["level"] == 3 and data["volume"] == 70 and data["items"] == ["sword"])
check("Missing values come from default", data["coins"] == 5)
check("Missing file gives the default", g.load_data(os.path.join(folder, "nope.json"),
                                                    {"a": 1}) == {"a": 1})
with open(os.path.join(folder, "broken.json"), "w") as f:
    f.write("{not json")
check("Broken file gives the default (no crash)",
      g.load_data(os.path.join(folder, "broken.json"), {"a": 1}) == {"a": 1})
volume.set(10)
g.load_variables(path, volume=volume)
check("load_variables sets Variables", volume.get() == 70)
check("Save files go next to the game", os.path.isabs(g._save_path("x.json")))

scores = g.HighScores(os.path.join(folder, "scores.json"), keep=3)
for name, score in [("A", 10), ("B", 30), ("C", 20), ("D", 5)]:
    scores.add(name, score)
check("HighScores keeps the best, sorted", scores.scores == [("B", 30), ("C", 20), ("A", 10)])
check("is_high_score", scores.is_high_score(15) and not scores.is_high_score(1))
again = g.HighScores(os.path.join(folder, "scores.json"), keep=3)
check("HighScores are saved and loaded", again.best() == ("B", 30)
      and again.table()[0] == "1. B  30")
times = g.HighScores(os.path.join(folder, "times.json"), lower_is_better=True)
times.add("Fast", 12.5); times.add("Slow", 40)
check("lower_is_better (for times)", times.best() == ("Fast", 12.5))

# ---------- Health ----------
events = []
bar = g.Progressbar(0, 0)
hp = g.Health(100, invincible_ms=500, on_damage=lambda: events.append("ouch"),
              on_death=lambda: events.append("dead"), bar=bar)
check("Health links the bar", bar.value == 100 and bar.maximum == 100)
check("damage() works", hp.damage(30) and hp.value == 70 and bar.value == 70)
check("Invincible straight after a hit", not hp.damage(30) and hp.value == 70)
clock_ms[0] += 600
hp.damage(30)
hp.heal(50)
check("heal() (not above maximum)", hp.value == 90)
clock_ms[0] += 600
hp.damage(500)
check("Death runs on_death once", hp.is_dead() and events.count("dead") == 1)
hp.heal(10)
check("Can't heal when dead", hp.value == 0)
hp.reset()
check("reset()", hp.value == 100 and not hp.is_dead())
regen = g.Health(100, value=50, regen_per_second=10)
regen.update(1000)
check("Regeneration", regen.value == 60)

# ---------- Projectiles ----------
bullets = g.ProjectileGroup()
shooter_sprite = g.SpriteObject(0, 0, 20, 20)
gun = g.Shooter(bullets, cooldown=200, speed=500, damage=4, owner=shooter_sprite)
check("Shooter fires", len(gun.fire((100, 100), direction=(1, 0))) == 1)
check("Cooldown stops the next shot", gun.fire((100, 100), direction=(1, 0)) == [])
clock_ms[0] += 250
gun.fire((100, 100), target=(100, 300))
check("Firing at a target", list(bullets)[-1].velocity.y > 0)
bullets.update(100)
check("Projectiles move", list(bullets)[0].rect.centerx == 150)
enemy = g.SpriteObject(148, 90, 30, 30)
found = bullets.hits([enemy, shooter_sprite])
check("hits() finds the hit, and the bullet is used up", len(found) == 1
      and found[0].damage == 4 and len(bullets) == 1)
shotgun = g.Shooter(bullets, count=5, fan=10)
check("count=5 fires five", len(shotgun.fire((0, 0))) == 5)
old = g.ProjectileGroup()
old.add(g.Projectile(0, 0, (100, 0), lifetime=100))
old.update(150)
check("Projectiles disappear after their lifetime", len(old) == 0)
walls = g.ProjectileGroup()
walls.add(g.Projectile(0, 0, (1000, 0), solids=[pg.Rect(50, -10, 10, 20)]))
walls.update(50)
check("Projectiles stop at walls", len(walls) == 0)
piercer = g.ProjectileGroup()
piercer.add(g.Projectile(100, 100, (0, 0), pierce=True))
two = [g.SpriteObject(90, 90, 20, 20), g.SpriteObject(95, 95, 20, 20)]
check("pierce hits several targets, once each",
      len(piercer.hits(two)) == 2 and len(piercer.hits(two)) == 0)

# ---------- Effects ----------
target = g.SpriteObject(100, 100, 20, 20)
g.flash(target, 100)
target.draw(screen)
check("flash() draws without errors", target._flash_until > clock_ms[0])
g.blink(target, 300)
target.draw(screen)
body = g.TopDownBody(target)
g.knockback(body, (90, 110), strength=400)
body.update(16)
check("knockback pushes away", target.rect.x > 100)
for _ in range(60):
    body.update(16)
moved = target.rect.x
body.update(16)
check("...and the push fades away", target.rect.x == moved)
plat = g.PlatformerBody(g.SpriteObject(100, 100, 20, 20), solids=[pg.Rect(0, 120, 400, 20)])
plat.update(16)
g.knockback(plat, (90, 110), strength=300, lift=300)
plat.update(16)
check("Platformer knockback bounces up", plat.velocity.y < 0)
cam = g.Camera(1000, 1000, (400, 300))
cam.shake(200, 5)
cam.update(16)
check("camera.shake moves the view", cam.shake_offset.length() > 0)
clock_ms[0] += 300
cam.update(16)
check("...then stops", cam.shake_offset.length() == 0)

pg.time.get_ticks = real_get_ticks
print()
print("ALL TESTS PASS" if all(results) else f"{results.count(False)} TEST(S) FAILED")
pg.quit()
