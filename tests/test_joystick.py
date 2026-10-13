"""
Automatic checks for JoystickManager, using a pretend controller,
so nothing needs to be plugged in.

Run this file in Visual Studio (right-click > Start without Debugging).
"""
import os
import sys
import tempfile

os.environ["SDL_VIDEODRIVER"] = "dummy"
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

import pygame as pg
pg.init()
screen = pg.display.set_mode((400, 400))

import PygameTkinterGUITools as g


class FakeJoystick:
    """Pretends to be a pygame Joystick with 4 buttons, 2 axes and 1 hat."""
    def __init__(self):
        self.buttons = [0, 0, 0, 0]
        self.axes = [0.0, 0.0]
        self.hats = [(0, 0)]
    def get_name(self): return "Pretend controller"
    def get_instance_id(self): return 99
    def get_numbuttons(self): return len(self.buttons)
    def get_numaxes(self): return len(self.axes)
    def get_numhats(self): return len(self.hats)
    def get_button(self, n): return self.buttons[n]
    def get_axis(self, n): return self.axes[n]
    def get_hat(self, n): return self.hats[n]


results = []


def check(name, condition):
    results.append(condition)
    print(("PASS  " if condition else "FAIL  ") + name)


# No controller: everything is safe
pad = g.JoystickManager(index=5)
check("No controller: not connected", not pad.connected)
check("No controller: button False", pad.get_button(0) is False)
check("No controller: axis 0", pad.get_axis(0) == 0)
check("No controller: hat (0, 0)", pad.get_hat(0) == (0, 0))
pad.update()
pad.draw_debug(screen)

# Pretend controller
fake = FakeJoystick()
pad.joystick = fake
check("Connected", pad.connected)

# Original methods still work
fake.buttons[2] = 1
check("get_button(number)", pad.get_button(2) is True)
check("Button number out of range is False", pad.get_button(50) is False)

# Binding and was_pressed
pad.bind_button("jump", 2)
pad.update()
check("is_pressed('jump')", pad.is_pressed("jump"))
check("was_pressed on first frame", pad.was_pressed("jump"))
pad.update()
check("was_pressed only for one frame", not pad.was_pressed("jump"))
fake.buttons[2] = 0
pad.update()
check("was_released", pad.was_released("jump"))

# Unknown name gives a helpful error
try:
    pad.is_pressed("fly")
    check("Unknown name gives error", False)
except ValueError:
    check("Unknown name gives error", True)

# Axes: deadzone and smooth scaling
pad.bind_axis("move_x", 0)
pad.bind_axis("move_y", 1, invert=True)
fake.axes = [0.1, 0.0]
check("Small movement inside deadzone is 0", pad.get_axis("move_x") == 0)
fake.axes = [1.0, 0.5]
check("Full stick is 1.0", abs(pad.get_axis("move_x") - 1.0) < 0.001)
fake.axes = [0.16, 0.5]
check("Just past deadzone is small (smooth)", 0 < pad.get_axis("move_x") < 0.05)
check("invert=True flips direction", pad.get_axis("move_y") < 0)

# Hats
pad.bind_hat("dpad", 0)
fake.hats = [(-1, 0)]
check("get_hat('dpad')", pad.get_hat("dpad") == (-1, 0))

# command= runs when pressed
hits = []
pad.bind_button("pause", 3, command=lambda: hits.append("pause"))
pad.handle_event(pg.event.Event(pg.JOYBUTTONDOWN, button=3, instance_id=99))
check("command= runs on press", hits == ["pause"])
pad.handle_event(pg.event.Event(pg.JOYBUTTONDOWN, button=3, instance_id=7))
check("Other controllers' presses are ignored", hits == ["pause"])

# Debug printing doesn't crash
pad.debug = True
for ev in [pg.event.Event(pg.JOYBUTTONUP, button=3, instance_id=99),
           pg.event.Event(pg.JOYAXISMOTION, axis=0, value=0.9, instance_id=99),
           pg.event.Event(pg.JOYHATMOTION, hat=0, value=(0, 1), instance_id=99)]:
    pad.handle_event(ev)
pad.draw_debug(screen, 10, 10)
check("Debug printing and panel work", True)

# Save and load bindings
path = os.path.join(tempfile.gettempdir(), "test_controls.json")
pad.save_bindings(path)
pad2 = g.JoystickManager(index=5)
pad2.load_bindings(path)
check("save / load bindings",
      pad2.button_binds == pad.button_binds and pad2.axis_binds == pad.axis_binds
      and pad2.hat_binds == pad.hat_binds)

# Unplugging
pad.handle_event(pg.event.Event(pg.JOYDEVICEREMOVED, instance_id=99))
check("Unplugging disconnects", not pad.connected)

print()
print("ALL TESTS PASS" if all(results) else f"{results.count(False)} TEST(S) FAILED")
pg.quit()
