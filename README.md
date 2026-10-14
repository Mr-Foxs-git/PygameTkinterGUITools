# PygameTkinterGUITools

A helper library for building games and GUIs in **pygame**. The GUI objects
(`Button`, `Label`, `Frame` ...) are modelled on the tkinter widgets you may
already know, and there are extra helpers for cameras, sprite animation and
maps made in [Tiled](https://www.mapeditor.org/).

## Getting started

1. Install the requirements (once per computer):

   ```
   pip install -r requirements.txt
   ```

   or `pip install pygame pytmx`.

2. Copy `PygameTkinterGUITools.py` into the same folder as your game.

   `pytmx` is only needed if you use `TiledMap`.

3. Import it in your game:

   ```python
   import pygame as pg
   from PygameTkinterGUITools import Button, Label, Frame
   ```

## Quick example

Every example uses the same game loop: `init_pygame()`, then a `while True`
loop that calls `handle_inputs()`, `update(tick)` and `draw_game()`.
Copy [`examples/_template.py`](examples/_template.py) to start a new game.

```python
import sys
import pygame as pg
from PygameTkinterGUITools import Button, Label

WIDTH, HEIGHT = 800, 600
FPS = 60


def say_hello():
    print("Hello!")


def init_pygame():
    global screen, clock, title, hello_button
    pg.init()
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    clock = pg.time.Clock()

    # >>> Create objects here (after pg.init)
    title = Label(20, 20, "My game", font_size=40)
    hello_button = Button(20, 80, 150, 50, "Hello", command=say_hello)


def handle_inputs():
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            sys.exit()

        # >>> Objects that react to events go here
        hello_button.handle_event(event)


def update(tick):
    # >>> Objects with update(tick) go here
    pass


def draw_game():
    screen.fill((30, 30, 30))

    # >>> Objects with draw(screen) go here
    title.draw(screen)
    hello_button.draw(screen)

    pg.display.flip()


init_pygame()
while True:
    tick = clock.tick(FPS)   # tick = milliseconds since the last frame (used for animation)
    handle_inputs()
    update(tick)
    draw_game()
```

## How every object works

All objects follow the same rules, so once you know one you know them all:

| Where in your game | What to call |
|---|---|
| `init_pygame()` | create it, e.g. `Button(x, y, width, height, text, command=...)` |
| `handle_inputs()` | `obj.handle_event(event)` |
| `update(tick)` | `obj.update(tick)` |
| `draw_game()` | `obj.draw(screen)` |

GUI widgets use tkinter option names:

| Option | Meaning |
|---|---|
| `text` | the words shown |
| `fg` | text colour |
| `bg` | background colour |
| `hover_bg` | button colour when the mouse is over it |
| `command` | function to run (Button). `on_enter` for TextBox |
| `font_name`, `font_size` | the font |
| `border_color`, `border_width` | the border (`border_colour` also works) |
| `center=True` | (x, y) is the centre instead of the top-left |

Change options while the game runs with `config()`, like tkinter:

```python
score_label.config(text=f"Score: {score}")
```

Widgets put in a `Frame` or `Popup` are positioned from its inside corner
and move, hide and update with it.

## What's in the library

### GUI widgets (tkinter style)

| Class / function | What it does |
|---|---|
| `Frame` | A box that holds other widgets and draws them together |
| `Label` | Displays text |
| `Button` | A clickable button that runs a `command` function |
| `TextBox` | A box the player can type into (like tkinter `Entry`) |
| `Popup` | A pop-up window with a title and close button |
| `draw_text()` | Quickly draw text on the screen |

### Game helpers

| Class | What it does |
|---|---|
| `SpriteObject` | A basic game object with an image or animation |
| `Animator` | Plays animations from image files or a sprite sheet |
| `Camera` / `ZoomCamera` | Follows a target and scrolls (and zooms) the world. Zoom is crisp for pixel art; use `smooth=True` for smooth scaling |
| `TiledMap` | Loads a `.tmx` map made in Tiled |
| `Tile` / `AnimatedTile` | Map tiles (static or animated) |
| `World` | Puts a map, camera and sprites together |
| `JoystickManager` | Reads any game controller (see below) |

### Game controllers

Every controller numbers its buttons differently, so:

1. Run [`examples/joystick_debug.py`](examples/joystick_debug.py) and press
   things to see pygame's numbers.
2. Give the numbers names, then use the names in your game:

```python
pad = JoystickManager(0)                 # in init_pygame()
pad.bind_button("jump", 0)
pad.bind_axis("move_x", 0)
pad.bind_hat("dpad", 0)

pad.handle_event(event)                  # in handle_inputs()

pad.update(tick)                         # at the start of update(tick)
if pad.was_pressed("jump"):
    ...
speed_x = pad.get_axis("move_x")         # -1.0 to 1.0
```

See [`examples/joystick_move.py`](examples/joystick_move.py) for a full game.

## Testing

Run the files in `tests/` to check the library works. It prints
`ALL TESTS PASS` if everything is OK.

## Opening in Visual Studio

Open `PygameTkinterGUITools.slnx` in Visual Studio (with the *Python
development* workload installed), or clone this repository using
**Git → Clone Repository…**.
