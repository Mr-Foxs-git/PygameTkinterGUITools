"""
Automatic checks for HeartsBar (health shown as hearts).

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


# ---- Counting hearts ----
health = g.Health(6)
hearts = g.HeartsBar(10, 10, health=health, hearts=3)
check("3 hearts drawn", hearts.heart_count() == 3)
check("full health = 3 full hearts", hearts.hearts_filled() == 3)
health.damage(1)
check("1 damage (2 HP per heart) = 2.5 hearts", hearts.hearts_filled() == 2.5)
health.damage(2)
check("3 damage = 1.5 hearts", hearts.hearts_filled() == 1.5)
health.heal(1)
check("heal 1 = 2 hearts", hearts.hearts_filled() == 2)
health.damage(10)
check("dead = 0 hearts", hearts.hearts_filled() == 0)

check("no hearts= gives one heart per HP", g.HeartsBar(0, 0, health=g.Health(4)).heart_count() == 4)

big = g.Health(100)
five = g.HeartsBar(0, 0, health=big, hearts=5)
big.damage(97)
check("3 HP of 100 still shows half a heart", five.hearts_filled() == 0.5)
whole = g.HeartsBar(0, 0, health=big, hearts=5, half_hearts=False)
check("half_hearts=False rounds up to a whole heart", whole.hearts_filled() == 1)

# ---- Without a Health object (like Progressbar) ----
plain = g.HeartsBar(0, 0, maximum=4, value=3)
check("maximum / value work without Health", plain.hearts_filled() == 3)
plain.config(value=1)
check("config(value=...) works", plain.hearts_filled() == 1)
plain.value = 99
check("value is kept between 0 and maximum", plain.value == 4)
var = g.IntVar(2)
check("variable= works", g.HeartsBar(0, 0, maximum=4, variable=var).hearts_filled() == 2)

linked = g.HeartsBar(0, 0)
linked_health = g.Health(8, bar=linked)
linked_health.damage(3)
check("Health(..., bar=hearts) keeps the HeartsBar up to date",
      linked.maximum == 8 and linked.value == 5 and linked.hearts_filled() == 5)

# ---- Size and rows ----
sized = g.HeartsBar(0, 0, maximum=5, heart_size=20, gap=5)
check("width = 5 hearts + 4 gaps", sized.width == 5 * 20 + 4 * 5 and sized.height == 20)
rows = g.HeartsBar(0, 0, maximum=12, heart_size=10, gap=2, per_row=5)
check("per_row wraps onto 3 rows", rows.width == 5 * 10 + 4 * 2 and rows.height == 3 * 10 + 2 * 2)
rows.config(per_row=6)
check("config(per_row=...) changes the size", rows.height == 2 * 10 + 2)
check("heart_size can be (width, height)",
      g.HeartsBar(0, 0, maximum=1, heart_size=(45, 40)).rect.size == (45, 40))

# ---- Drawing ----
try:
    screen.fill((0, 0, 0))
    hearts_drawn = g.HeartsBar(0, 0, maximum=4, value=3, heart_size=20, gap=0)
    hearts_drawn.draw(screen)
    full_colour = hearts_drawn.cget("heart_color")
    check("drawn hearts use the Style's heart_color",
          tuple(screen.get_at((10, 12)))[:3] == full_colour)
    check("the 4th heart is empty",
          tuple(screen.get_at((70, 12)))[:3] == hearts_drawn.cget("empty_color"))
    pictures = g.HeartsBar(0, 100, maximum=6, value=3, hearts=3,
                           full_image=os.path.join(ASSETS, "heart_full.png"),
                           half_image=os.path.join(ASSETS, "heart_half.png"),
                           empty_image=os.path.join(ASSETS, "heart_empty.png"))
    pictures.draw(screen)
    no_half = g.HeartsBar(0, 200, maximum=6, value=3, hearts=3,
                          full_image=os.path.join(ASSETS, "heart_full.png"),
                          empty_image=os.path.join(ASSETS, "heart_empty.png"))
    no_half.draw(screen)
    red = g.HeartsBar(0, 300, maximum=2, value=1, heart_colour=(0, 255, 0))
    red.draw(screen)
    check("drawing with and without pictures works", True)
    check("heart_colour spelling works", red.cget("heart_color") == (0, 255, 0))
except Exception as error:
    check(f"drawing works ({error})", False)

# ---- Flashing ----
flash_health = g.Health(4, invincible_ms=1000)
flashing = g.HeartsBar(0, 0, health=flash_health, flash_when_hurt=True)
flash_health.damage(1)
flashing.update(150)
check("flash_when_hurt counts while invincible", flashing._flash_time == 150)
not_flashing = g.HeartsBar(0, 0, health=flash_health)
not_flashing.update(150)
check("no flashing unless flash_when_hurt=True", not_flashing._flash_time == 0)

# ---- Works inside a Frame (parent first) ----
frame = g.Frame(100, 100, 300, 200)
in_frame = g.HeartsBar(frame, health=g.Health(3))
in_frame.grid(row=0, column=0)
frame.draw(screen)
check("HeartsBar(frame, ...) goes in the frame", in_frame.parent is frame)
check("handle_event never uses events",
      in_frame.handle_event(pg.event.Event(pg.MOUSEBUTTONDOWN, pos=(110, 110), button=1)) is False)

print()
print("ALL TESTS PASS" if all(results) else f"{results.count(False)} TEST(S) FAILED")
pg.quit()
