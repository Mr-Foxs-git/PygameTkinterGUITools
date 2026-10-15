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

## Which example do I need?

Every example is in [`examples/`](examples/) and uses the same game loop as
[`_template.py`](examples/_template.py).

| I want to... | Example |
|---|---|
| Show text, a score or a timer | [`label_example.py`](examples/label_example.py) |
| Make clickable buttons | [`button_example.py`](examples/button_example.py) |
| Let the player type (e.g. their name) | [`textbox_example.py`](examples/textbox_example.py) |
| Make a menu that shows / hides | [`frame_example.py`](examples/frame_example.py) |
| Show a pop-up message (Game Over...) | [`popup_example.py`](examples/popup_example.py) |
| Tick boxes and "choose one" options | [`checkbutton_radiobutton_example.py`](examples/checkbutton_radiobutton_example.py) |
| Sliders and number pickers | [`scale_spinbox_example.py`](examples/scale_spinbox_example.py) |
| Lists and drop-down menus | [`listbox_combobox_example.py`](examples/listbox_combobox_example.py) |
| Dialogue / instructions that wrap | [`message_example.py`](examples/message_example.py) |
| Health, energy and loading bars | [`progressbar_example.py`](examples/progressbar_example.py) |
| Change how everything looks (themes, images) | [`style_example.py`](examples/style_example.py) |
| A pause menu with tabs, used with the keyboard | [`settings_menu_example.py`](examples/settings_menu_example.py) |
| Sounds on key presses (pressed vs held keys) | [`keyboard_sound_example.py`](examples/keyboard_sound_example.py) |
| Background music and volume controls | [`music_example.py`](examples/music_example.py) |
| Drag things with the mouse, inventory slots, item stats | [`drag_grid_example.py`](examples/drag_grid_example.py) |
| A platformer: gravity, jumping, ladders, enemies | [`platformer_example.py`](examples/platformer_example.py) |
| Top-down enemies: routes, spotting and chasing the player | [`topdown_ai_example.py`](examples/topdown_ai_example.py) |
| Lay out menus with grid / pack / place (+ debug view) | [`layout_example.py`](examples/layout_example.py) |
| Menu -> game -> game over screens, timers, high scores | [`scenes_example.py`](examples/scenes_example.py) |
| Health, shooting, hit effects, camera shake | [`shooter_example.py`](examples/shooter_example.py) |
| Animate a character from a sprite sheet | [`animator_example.py`](examples/animator_example.py) |
| Move a player and collect things | [`sprite_example.py`](examples/sprite_example.py) |
| Have a world bigger than the screen | [`camera_example.py`](examples/camera_example.py) |
| Load a level made in Tiled (with zoom) | [`tiled_example.py`](examples/tiled_example.py) |
| Find my controller's button numbers | [`joystick_debug.py`](examples/joystick_debug.py) |
| Move with a game controller | [`joystick_move.py`](examples/joystick_move.py) |

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
| `Checkbutton` | A tick box (on / off) |
| `Radiobutton` | Choose one option from a group |
| `Scale` | A slider for choosing a number |
| `Spinbox` | A number or choice with up / down arrows |
| `Listbox` | A scrolling list to choose from |
| `Combobox` | A drop-down list (ttk) |
| `Message` | Text that wraps onto several lines |
| `Progressbar` | A filling bar: health, energy, loading (ttk) |
| `LabelFrame` | A Frame with a title on its border |
| `Notebook` | Tabs, each with its own page (ttk) |
| `Separator` | A dividing line (ttk) |
| `IntVar`, `StringVar`, `BooleanVar`, `DoubleVar` | Values shared between widgets, like tkinter |
| `Style` | Colours and fonts for every widget, built-in themes (ttk) |
| `FocusGroup` | Use widgets with the keyboard or a controller |
| `KeyboardInput` | Was a key just pressed, is it held, was it let go? |
| `MouseInput` | The same for mouse buttons, plus position and scroll wheel |
| `SoundEffect` | Short sounds, safe to use in the game loop |
| `Music` | Background music with fades and playlists |
| `Audio`, `init_audio()` | Sound setup and volume (links to widgets) |
| `Grid` | Cells for inventories, boards and level editors |
| `DragObject`, `DragGroup` | Things you can drag with the mouse, with or without a grid |
| `Tooltip` | Text that appears when the mouse rests on anything |
| `Path`, `PathFollower` | Routes for enemies and moving platforms (can be drawn in Tiled) |
| `Patrol` | Walk left and right, turning at walls and ledges |
| `Chaser` | Spot a target (range + line of sight) and chase it, then go home |
| `NavGrid` | Path finding: find a way around walls |
| `TopDownBody` | Movement with wall collisions for top-down games |
| `PlatformerBody` | Gravity, jumping, one-way platforms and ladders |
| `MovingPlatform` | A platform that follows a path and carries the player |
| `grid()`, `pack()`, `place()`, `Root` | tkinter layout managers, with a debug view (F1) |
| `Scenes`, `Scene` | Menu, game and game-over screens, with fades and slides |
| `after()`, `after_repeat()`, `Countdown` | Timers, like tkinter's `root.after` |
| `save_data()`, `load_data()`, `HighScores` | Save files and high-score tables |
| `Health` | Hit points, invincibility, death, linked to a Progressbar |
| `Shooter`, `ProjectileGroup` | Bullets, arrows, shotguns |
| `flash()`, `blink()`, `knockback()`, `camera.shake()` | Hit effects |
| `Debug` | F1 turns every debug view on and off |
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

## Quick reference

### Label
```python
score_label = Label(20, 20, "Score: 0", fg=(255, 220, 0), font_size=36)
score_label.config(text=f"Score: {score}")     # change it later
score_label.draw(screen)
```

### Button
```python
play = Button(100, 100, 200, 60, "Play", command=start_game,
              bg=(250, 200, 60), hover_bg=(255, 230, 120), border_radius=15)
play.handle_event(event)        # in handle_inputs()
play.draw(screen)
```

### TextBox
```python
name_box = TextBox(50, 100, max_chars=15, label="Name:", on_enter=say_hello)
name_box.handle_event(event)    # in handle_inputs()
name_box.update(tick)           # cursor blink
name = name_box.get()
```

### Frame and Popup
```python
menu = Frame(250, 120, 300, 300)
menu.add(Label(10, 10, "Menu"), Button(10, 60, 200, 50, "Start", command=start_game))
menu.toggle_visibility()        # hides / shows everything inside

game_over = Popup(400, 300, 320, 200, "Game Over", center=True)
game_over.show()
```
Call `handle_event`, `update` and `draw` on the Frame or Popup only - it passes
them on to everything inside. Draw popups last so they are on top.

### Animator
```python
animator = Animator("player_sheet.png", from_sheet=True,
                    tile_width=32, tile_height=32, rows=3, cols=4, scale=2)
animator.add_animation("walk", [(1, 0), (1, 1), (1, 2), (1, 3)])   # (row, col)
animator.play("walk")
animator.play_once("jump")
image = animator.update(tick, flip_x=facing_left)   # the frame to draw
```

### SpriteObject
```python
player = SpriteObject(100, 100, image="player.png")      # or animator=...
player.move(5, 0)
if player.collides_with(coin): ...
player.update(tick)
player.draw(screen)             # or player.draw(screen, camera)
```

### Camera and ZoomCamera
```python
camera = Camera(world_width, world_height, (WIDTH, HEIGHT))
camera.follow(player)
camera.update(tick)
player.draw(screen, camera)     # world things are drawn through the camera

zoom_camera = ZoomCamera(camera, (WIDTH, HEIGHT), zoom=2)   # smooth=True to blur
zoom_camera.draw_world(world, screen)
```

### TiledMap and World
```python
level = TiledMap("level1.tmx")
player_start = level.spawn_points["player_spawn"]
walls = [obj["rect"] for obj in level.collision_objects]

world = World(level, camera)
world.add_sprite(player)
world.update(tick)
world.draw(screen)              # background, sprites, then foreground
```
In Tiled, give objects a **Class** of `collision` or `trigger`, name spawn
points with "spawn" in the name, and put a layer named "Foreground" in front
of the player.

### Layout managers (like tkinter)
Make widgets with their parent first, then grid / pack / place them:
```python
root = Root(screen)                         # the whole window, like tk.Tk()
form = Frame(root)                          # no size = grows to fit
form.grid(row=0, column=0)
Label(form, text="Name:").grid(row=0, column=0, sticky="e", padx=5)
TextBox(form).grid(row=0, column=1, sticky="w")
Button(form, text="Play", command=play).grid(row=1, column=0, columnspan=2, pady=10)
form.columnconfigure(1, weight=1)

Button(toolbar, text="Save").pack(side="left", padx=4)
Button(root, text="?").place(relx=1.0, rely=0.0, anchor="ne")

root.handle_event(event)    root.update(tick)    root.draw(screen)
```
**Debug view:** put `Debug.handle_event(event)` in `handle_inputs()` and press
**F1**. You see every row and column (numbered), padding (yellow), each widget
with its (row, column) and sticky arrows, and red warnings for common mistakes:
a widget never gridded, two widgets in one cell, a layout too big for its Frame.
Hover a widget to see its settings, or call `frame.layout_report()`.
Unlike tkinter, `grid()` returns the widget, and mixing grid and pack in one
Frame gives a clear error instead of freezing. `bg=""` makes a Frame see-through.

### Scenes and timers
```python
scenes = Scenes()
scenes.add("menu", start=menu_start, handle_event=menu_event, draw=menu_draw)  # functions
scenes.add("game_over", GameOver())                                             # or a class
scenes.switch("game_over", transition="fade", ms=500, score=score)  # data -> start()

# in the game loop
scenes.handle_event(event)      scenes.update(tick)      scenes.draw(screen)

after(2000, spawn_enemy)                 # once, in 2 seconds
timer_id = after_repeat(500, blink)      # every half second
after_cancel(timer_id)
level_timer = Countdown(60000, on_finish=time_up)     # level_timer.text() -> "0:59"
```
`scenes.update()` runs the timers. Without Scenes, call `update_timers()` in
`update(tick)`. Timers made in a scene stop when you leave it.

### Saving and high scores
```python
save_data("save.json", level=3, coins=coins, volume=volume_var)
data = load_data("save.json", default={"level": 1, "coins": 0})
scores = HighScores("scores.json", keep=10)
if scores.is_high_score(score):
    scores.add(name, score)
scores.table()      # ["1. Sam  120", ...]
```
Files are saved next to your game. Add them to `.gitignore` if you don't
want them on GitHub. A missing or broken save file never crashes the game.

### Health, shooting and effects
```python
player.health = Health(100, invincible_ms=800, on_death=game_over, bar=health_bar)
player.health.damage(10)

bullets = ProjectileGroup()
gun = Shooter(bullets, cooldown=150, speed=700, damage=10, owner=player)
gun.fire(player.rect.center, target=mouse.pos)
bullets.update(tick)
for hit in bullets.hits(enemies):
    hit.target.health.damage(hit.damage)
    flash(hit.target)
    knockback(hit.target.body, hit.projectile.rect.center, strength=200)
camera.shake(200, strength=6)
```

### Variables (shared values)
```python
volume = IntVar(50)                     # also StringVar, BooleanVar, DoubleVar
Scale(50, 100, from_=0, to=100, variable=volume)
Label(50, 150, textvariable=volume)     # always shows the current value
volume.get()   volume.set(80)
```
Radiobuttons with the same variable form a group:
```python
difficulty = StringVar("Normal")
Radiobutton(50, 50, "Easy", variable=difficulty, value="Easy")
Radiobutton(50, 80, "Hard", variable=difficulty, value="Hard")
```

### More widgets
```python
Checkbutton(50, 50, "Music", variable=music_on)            # BooleanVar
Spinbox(50, 100, from_=1, to=4, variable=players)
Listbox(50, 150, 200, rows=5, items=["Level 1", "Level 2"]) # .get_selected()
Combobox(300, 50, 200, values=["Knight", "Wizard"], textvariable=hero)
Message(50, 300, "Long text that wraps...", width=400)
health = Progressbar(20, 20, 200, maximum=100, value=100)   # health.step(-10)
settings = Notebook(100, 50, 400, 300)
sound_tab = settings.new_tab("Sound")                       # a Frame to add() to
```
Draw a Combobox after the widgets below it, so its open list is on top
(inside a Frame or Notebook this is done for you).

### Style and themes
```python
style = Style()
style.theme_use("dark")                          # "light", "dark" or "retro"
style.configure("Button", border_radius=10)      # every Button
style.configure("Danger.Button", bg=(200, 0, 0)) # a named style...
Button(10, 10, 120, 40, "Quit", style="Danger.Button")
```
Options you give a widget always beat the Style. Use your own pictures with
`image=` (Button, Label, Checkbutton, Radiobutton), `handle_image=` (Scale)
and `bar_image=` / `trough_image=` (Progressbar).

### Keyboard and controller control (FocusGroup)
```python
menu_focus = FocusGroup(play_button, volume_slider, music_check, keys="arrows")
menu_focus.active = True        # only while the menu is open!

# in handle_inputs():
if not menu_focus.handle_event(event):   # True means the menu used the key
    ...your game's own controls...
```
It does nothing until `active` is True, and only uses the keys you choose
(`"arrows"`, `"tab"`, `"wasd"`), so it won't fight with your game controls.
`menu_focus.use_joystick(pad, "dpad", "A")` lets a controller use it too.

### Pressed or held? (KeyboardInput / MouseInput)
```python
keys = KeyboardInput()                  # in init_pygame()
keys.bind("jump", "space", "w")

keys.handle_event(event)                # in handle_inputs()
keys.update(tick)                       # FIRST thing in update(tick)

if keys.was_pressed("jump"):            # ONE frame -> one jump, one sound
    jump_sound.play()
if keys.is_pressed("right"):            # EVERY frame while held -> movement
    player.move(5, 0)
```
`MouseInput` works the same way with `"left"`, `"middle"` and `"right"`,
plus `mouse.pos`, `mouse.moved` and `mouse.wheel`.

### Sound
```python
init_audio()                            # in init_pygame(), BEFORE pg.init()
jump = SoundEffect("jump.wav")
laser = SoundEffect("laser.wav", cooldown=150)   # safe to call while held
steps = SoundEffect(["step1.wav", "step2.wav"])  # random choice each time

jump.play()
coin.play_on(player.collides_with(coin))         # only when it BECOMES True
engine.play_while(keys.is_pressed("thrust"))     # loops while True

Music.play("menu.wav")                  # loops forever
Music.switch("level.wav", fade_ms=800)  # needs Music.update(tick) in update
Audio.link(music_volume=volume_var, sfx_volume=sfx_var, muted=mute_var)
```
If a computer has no sound output, sounds are skipped and the game still runs.

### Dragging and grids
```python
backpack = Grid(60, 120, cols=5, rows=3, cell_size=72)
sword = DragObject(0, 0, 56, 56, image="sword.png", grid=backpack)
backpack.place(sword, 0, 0)
note = DragObject(100, 400, 140, 90, bounds=screen.get_rect())   # no grid: drag anywhere

items = DragGroup(sword, note)          # only the top item is picked up
items.handle_event(event)               # in handle_inputs()
backpack.draw(screen)                   # shows where a dragged item will land
items.draw(screen)
```
`grid=[backpack, equipment]` lets items move between grids. Items dropped on a
taken cell or outside the grid go back where they came from.

Item kinds, slots and stats:
```python
sword = DragObject(0, 0, 56, 56, image="sword.png", name="Iron Sword",
                   kind=["weapon", "sword"], stats={"damage": 7, "weight": 3})
equipment.set_slot(0, 0, accepts="weapon", label="Weapon")      # only weapons
potion_belt = Grid(..., accepts="potion")                        # a whole grid
heavy_slot = ...set_slot(1, 0, accepts=lambda item: item.stats.get("weight", 0) > 5)
sword.stats["damage"]   sword.is_kind("weapon")
```
`stats` can hold anything you like. Show it with a `Tooltip`:
```python
tips = Tooltip()
tips.attach(sword, lambda item: f"{item.name}\nDamage: {item.stats['damage']}")
tips.update(tick)          # in update(tick)
tips.draw(screen)          # LAST in draw_game()
```

### Movement building blocks
Mix and match these for any kind of game:

| Block | What it does | Top-down | Platformer |
|---|---|---|---|
| `TopDownBody` | moves with wall collisions | yes | |
| `PlatformerBody` | gravity, jumps, platforms, ladders | | yes |
| `PathFollower` | follows a `Path` | yes | yes (`axis="x"` or flying) |
| `Patrol` | walks left / right, turns at walls and ledges | | yes |
| `Chaser` | spots a target, chases it, goes home | yes (with `NavGrid`) | yes |

```python
# Platformer player
body = PlatformerBody(player, solids=walls, platforms=planks, ladders=ladders)
body.move(keys.is_pressed("right") - keys.is_pressed("left"))
if keys.was_pressed("jump"):   body.jump()
if keys.was_released("jump"):  body.release_jump()     # small jump
body.update(tick)

# An enemy that walks a route, and chases the player if it sees them
route = level.get_path("guard_route")
walk = PathFollower(guard, route, speed=90, wait=400)
brain = Chaser(guard, player, speed=140, detect_range=220, solids=walls,
               nav=NavGrid.from_tiled(level, agent_size=28), idle=walk)
brain.update(tick)
brain.draw_debug(screen, camera)     # ranges, line of sight, route
Path.show_all = False                # hide all debug paths when finished
```
Things that move with a body: update the "brain" (PathFollower, Patrol, Chaser)
first, then the body.

### Drawing a path in Tiled
1. Select your object layer (e.g. "Objects").
2. Choose **Insert Polyline** (press **L**) for a route that goes there and
   back, or **Insert Polygon** (press **P**) for a route that loops.
3. Click each point of the route. Double-click (or press Enter) to finish.
4. In the **Properties** panel, type a **Name**, e.g. `guard_route`.
5. Optional: add a custom property `mode` (string): `loop`, `ping_pong` or `once`.
6. In your code: `route = level.get_path("guard_route")`.
7. To link an enemy to a path in Tiled, give the enemy object a custom
   property `path` = `guard_route` and read it with
   `info["properties"]["path"]` (see `platformer_example.py`).

Other objects the examples use: **Class** `collision` (walls), `platform`
(one-way platforms), `ladder`, `trigger`, `enemy` - read them with
`level.collision_objects`, `level.rects_of_type("ladder")`,
`level.objects_of_type("enemy")`.

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

## Example art

The images and map in `examples/assets/` were drawn for this library and can
be used freely in student games.

## Testing

Run the files in `tests/` to check the library works.
`tests/test_examples.py` runs every example for a couple of seconds.
The example sounds in `examples/assets/sounds/` were generated for this library
and are free to use. It prints
`ALL TESTS PASS` if everything is OK.

## Opening in Visual Studio

Open `PygameTkinterGUITools.slnx` in Visual Studio (with the *Python
development* workload installed), or clone this repository using
**Git → Clone Repository…**.
