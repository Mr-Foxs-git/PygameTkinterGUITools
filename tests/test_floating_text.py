"""
Automatic checks for FloatingText (damage numbers / "+10" pop-ups).

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
    results.append(bool(condition))
    print(("PASS  " if condition else "FAIL  ") + name)


def red_pixels(surface):
    """How many pixels are (nearly) pure red."""
    count = 0
    for x in range(surface.get_width()):
        for y in range(surface.get_height()):
            r, gr, b, a = surface.get_at((x, y))
            if r > 200 and gr < 60 and b < 60:
                count += 1
    return count


# ---------- It joins Particles and floats up ----------
g.Particles.clear()
text = g.FloatingText(100, 200, "-10", color="red", speed=60, duration=1000)
check("adds itself to Particles", text in g.Particles.emitters)
check("Particles.count() not changed by text", g.Particles.count() == 0)
g.Particles.update(500)
check("floats up 30 px in half a second at speed 60", abs(text.y - 170) < 0.01)
check("x stays the same", text.x == 100)
check("not finished half way", not text.finished)

# ---------- It fades in the second half ----------
screen.fill((0, 0, 0))
g.Particles.draw(screen)
check("fully visible half way", text.image.get_alpha() == 255)
check("draws red text on the screen", red_pixels(screen) > 0)
g.Particles.update(250)
screen.fill((0, 0, 0))
g.Particles.draw(screen)
check("half faded at 3/4 of its life", 120 <= text.image.get_alpha() <= 135)

# ---------- It removes itself ----------
g.Particles.update(300)
check("finished after its duration", text.finished)
check("Particles removed it", text not in g.Particles.emitters)

# ---------- Camera ----------
g.Particles.clear()
camera = g.Camera(2000, 2000, (400, 300))
camera.offset.x, camera.offset.y = 1000, 0
far = g.FloatingText(1100, 150, "far", color="red", outline_color=None)
screen.fill((0, 0, 0))
g.Particles.draw(screen, camera)
check("camera moves it onto the screen", red_pixels(screen) > 0)
screen.fill((0, 0, 0))
g.Particles.draw(screen)
check("without the camera it is off screen", red_pixels(screen) == 0)

# ---------- Options ----------
number = g.FloatingText(0, 0, 25)
check("numbers become text", number.text == "25")
check("default colour is white", number.color == (255, 255, 255))
uk = g.FloatingText(0, 0, "hi", colour="blue", outline_colour="yellow")
check("colour= spelling works", uk.color == "blue")
check("outline_colour= spelling works", uk.outline_color == "yellow")
plain = g.FloatingText(0, 0, "hi", outline_color=None)
outlined = g.FloatingText(0, 0, "hi")
check("outline makes the picture 2 px bigger",
      outlined.image.get_width() == plain.image.get_width() + 2)
plain.remove()
check("remove() takes it away straight away", plain not in g.Particles.emitters)
g.Particles.clear()
check("Particles.clear() clears texts too", g.Particles.emitters == [])

# ---------- Works next to normal particle effects ----------
g.Particles.sparks((50, 50))
g.FloatingText(50, 50, "+10")
g.Particles.update(16)
g.Particles.draw(screen)
check("mixes with other effects", len(g.Particles.emitters) == 2)
g.Particles.clear()

pg.quit()
print()
print("ALL PASSED" if all(results) else f"{results.count(False)} CHECK(S) FAILED")
