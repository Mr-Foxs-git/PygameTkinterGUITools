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
| A form: passwords, hints, numbers only, type-to-search lists, choose several, hold-to-repeat buttons, "type your name" boxes | [`form_example.py`](examples/form_example.py) |
| Make a menu that shows / hides | [`frame_example.py`](examples/frame_example.py) |
| Show a pop-up message (Game Over...) | [`popup_example.py`](examples/popup_example.py) |
| Ask Yes / No / Cancel, edit a table like a spreadsheet | [`shop_editor_example.py`](examples/shop_editor_example.py) |
| Tick boxes and "choose one" options | [`checkbutton_radiobutton_example.py`](examples/checkbutton_radiobutton_example.py) |
| Sliders and number pickers | [`scale_spinbox_example.py`](examples/scale_spinbox_example.py) |
| Lists and drop-down menus | [`listbox_combobox_example.py`](examples/listbox_combobox_example.py) |
| Dialogue / instructions that wrap | [`message_example.py`](examples/message_example.py) |
| Dialogue that types out letter by letter, with a typing sound | [`typewriter_example.py`](examples/typewriter_example.py) |
| Health, energy and loading bars | [`progressbar_example.py`](examples/progressbar_example.py) |
| Health as a row of hearts (Zelda style) | [`hearts_example.py`](examples/hearts_example.py) |
| Game-screen text and bars: outlined text, bars that go red, health bars over enemies, a fading pause menu, high contrast | [`hud_example.py`](examples/hud_example.py) |
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
| Menu bar, right-click menu, editable table, tree view, scrolling list | [`scrolled_table_menu_example.py`](examples/scrolled_table_menu_example.py) |
| Explosions, fire, smoke, rain, snow, sparks... | [`particles_example.py`](examples/particles_example.py) |
| Damage numbers and "+10" pop-ups that float up and fade | [`floating_text_example.py`](examples/floating_text_example.py) |
| Enemies that keep coming, in waves; coins that keep appearing | [`spawner_example.py`](examples/spawner_example.py) |
| Things following a leader (worms, party members, trains, trails) | [`chain_example.py`](examples/chain_example.py) |
| A complete Snake game | [`snake_example.py`](examples/snake_example.py) |
| Animate a character from a sprite sheet (walk, run, jump back to idle, footstep sounds) | [`animator_example.py`](examples/animator_example.py) |
| Turn to face the mouse, chase the player when close, exact (pixel) hits, very slow movement | [`sprite_tricks_example.py`](examples/sprite_tricks_example.py) |
| Move a player and collect things | [`sprite_example.py`](examples/sprite_example.py) |
| Have a world bigger than the screen | [`camera_example.py`](examples/camera_example.py) |
| Far-away backgrounds that scroll slower (parallax), a camera that looks ahead, only moving enemies near the screen | [`parallax_example.py`](examples/parallax_example.py) |
| Load a level made in Tiled (zoom, tile properties like water, walking behind and in front of things) | [`tiled_example.py`](examples/tiled_example.py) |
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
| `MessageBox`, `askyesno()`, `askyesnocancel()`, `askokcancel()`, `showinfo()` | Ready-made question boxes (like tkinter's `messagebox`) |
| `askstring()`, `askinteger()` | Question boxes the player types into (like tkinter's `simpledialog`) |
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
| `HeartsBar` | Shows health as a row of hearts, with half hearts |
| `Shooter`, `ProjectileGroup` | Bullets, arrows, shotguns |
| `flash()`, `blink()`, `knockback()`, `camera.shake()` | Hit effects |
| `Debug` | F1 turns every debug view on and off |
| `ScrolledFrame` | A Frame whose contents scroll |
| `Table` | Rows and columns (like ttk.Treeview): sorting, editable cells, tree view |
| `Menu` | Menu bars, sub-menus and right-click menus, with working shortcuts |
| `ParticleEmitter`, `Particles` | Particle effects, with ready-made presets |
| `FloatingText` | Damage numbers and "+10" pop-ups - a text particle that `Particles` looks after |
| `Spawner`, `Waves` | Make enemies, coins... every few seconds at chosen places, with a limit on how many are alive; run them in waves |
| `Chain` | Things that follow a leader - snakes, worms, followers, trains, trails |
| `draw_text()` | Quickly draw text on the screen |

### Game helpers

| Class | What it does |
|---|---|
| `SpriteObject` | A basic game object with an image or animation. It can turn (`point_at`), measure (`distance_to`, `direction_to`) and do pixel-perfect hits |
| `Animator` | Plays animations from image files or a sprite sheet, with `then=`, `on_frame` and a speed for each animation |
| `Camera` / `ZoomCamera` | Follows a target and scrolls (and zooms) the world. Zoom is crisp for pixel art; use `smooth=True` for smooth scaling. Also `snap()`, `deadzone=`, `lookahead=` and `on_screen()` |
| `Background` | A picture that scrolls slower than the world (parallax), repeated left and right |
| `TiledMap` | Loads a `.tmx` map made in Tiled, with background / midground / foreground layers and `tile_properties_at()` |
| `Tile` / `AnimatedTile` | Map tiles (static or animated) |
| `World` | Puts a map, camera and sprites together. `y_sort=True` draws whatever is lower on the screen in front |
| `JoystickManager` | Reads any game controller (see below) |

## Quick reference

### Label
```python
score_label = Label(20, 20, "Score: 0", fg=(255, 220, 0), font_size=36)
score_label.config(text=f"Score: {score}")     # change it later
score_label.draw(screen)

title = Label(20, 60, "Level 1", font_size=64, outline=3)    # easy to read on any background
help_text = Label(400, 500, "Arrows to move\nSpace to jump", shadow=True,
                  justify="center", center=True)              # "\n" = new line
```
`outline_color` and `shadow_color` (or `colour`) change the colours.

### Button
```python
play = Button(100, 100, 200, 60, "Play", command=start_game,
              bg=(250, 200, 60), hover_bg=(255, 230, 120), border_radius=15)
play.handle_event(event)        # in handle_inputs()
play.draw(screen)

plus = Button(100, 200, 50, 50, "+", command=add_one,
              active_bg=(60, 100, 200),        # colour while held down
              sound="click.wav",               # or a SoundEffect
              repeatdelay=400, repeatinterval=80)   # hold it to keep adding
plus.update(tick)               # in update(tick) - only needed for repeat (a Frame does it)
```

### TextBox
```python
name_box = TextBox(50, 100, max_chars=15, label="Name:", on_enter=say_hello)
name_box.handle_event(event)    # in handle_inputs()
name_box.update(tick)           # cursor blink
name = name_box.get()

password = TextBox(50, 150, show="*", placeholder="Password")   # grey hint while empty
age_box = TextBox(50, 200, max_chars=3, allowed="digits", on_change=check_age)
```
`allowed` can be `"digits"`, `"letters"` or your own characters, e.g. `"0123456789."`.
`on_change` runs (no arguments) every time the text changes.

### Frame and Popup
```python
menu = Frame(250, 120, 300, 300)
menu.add(Label(10, 10, "Menu"), Button(10, 60, 200, 50, "Start", command=start_game))
menu.toggle_visibility()        # hides / shows everything inside

game_over = Popup(400, 300, 320, 200, "Game Over", center=True,
                  title_font_size=36)          # title size (24 if left out)
game_over.show()

pause_menu.show(fade_ms=300)    # fade in
pause_menu.hide(fade_ms=300)    # fade out (it stops taking clicks straight away)
pause_menu.toggle_visibility(fade_ms=300)
title.slide_to(300, 90, ms=900) # any widget placed with x, y glides there
```
Call `handle_event`, `update` and `draw` on the Frame or Popup only - it passes
them on to everything inside. Draw popups last so they are on top.
Fades and slides need no `update(tick)` and keep going while timers are paused.
Fades work on Frame, LabelFrame, ScrolledFrame, Notebook, Popup and MessageBox;
other widgets show / hide straight away.

### Question boxes (MessageBox)
```python
def quit_answer(answer):              # True (Yes), False (No) or None (Cancel / closed)
    if answer is not None:
        pg.quit()
        sys.exit()

quit_box = askyesnocancel("Quit?", "Save before you quit?", command=quit_answer)
quit_box.handle_event(event)          # FIRST in handle_inputs()
quit_box.draw(screen)                 # LAST in draw_game()

# Your own buttons: the answer is the button's text (None if closed with X / Escape)
box = MessageBox("Shop", "Buy the sword?", buttons=("Buy", "Not now"), command=answer)
box.show()
```
Enter presses the first button, Escape closes it. While it is open it takes
every click and key, so the game underneath doesn't react.
Add `type_speed=30` to type the message out (then call `box.update(tick)`);
the first click or Enter only shows the rest of the message.

Boxes the player types into (like tkinter's `simpledialog`):
```python
def got_name(name):                   # the text, or None (Cancel / closed)
    if name:
        scores.add(name, score)

name_box = askstring("New high score!", "Enter your name:", command=got_name)
age_box = askinteger("Age", "How old are you?", command=got_age, minvalue=5, maxvalue=99)
```
Handle and draw them like any question box (`box.update(tick)` makes the
cursor blink). `askinteger` only lets numbers be typed, and stays open with a
message if the number is outside `minvalue` / `maxvalue`.

### Animator
```python
animator = Animator("player_sheet.png", from_sheet=True,
                    tile_width=32, tile_height=32, rows=3, cols=4, scale=2)
animator.add_animation("walk", [(1, 0), (1, 1), (1, 2), (1, 3)])   # (row, col)
animator.play("walk")
animator.play_once("jump")
image = animator.update(tick, flip_x=facing_left)   # the frame to draw

animator.add_animation("run", [(1, 0), (1, 1), (1, 2), (1, 3)], frame_rate=16)  # faster
animator.play_once("attack", then="idle")       # goes back to idle by itself
animator.play_once("die", on_finish=game_over)  # run a function at the end
if not animator.busy: ...                       # busy = a play_once is still playing
animator.on_frame("walk", 1, step_sound.play)   # frame 1 of "walk" (counted from 0)
```

### SpriteObject
```python
player = SpriteObject(100, 100, image="player.png")      # or animator=...
player.move(5, 0)
if player.collides_with(coin): ...
player.update(tick)
player.draw(screen)             # or player.draw(screen, camera)

# Turning: only the picture turns, the hitbox (rect) stays the same
turret = SpriteObject(400, 300, image="turret.png", image_faces="up")
turret.point_at(pg.mouse.get_pos())   # or point_at(enemy)
turret.turn(90 * tick / 1000)         # clockwise; minus = anticlockwise
turret.angle = 90                     # compass: 0 up, 90 right, 180 down, 270 left

if player.collides_with(spikes, pixel=True): ...   # only the drawn pixels count
coin = player.collides_with_any(coins)             # first one touched, or None
enemy.distance_to(player)                          # pixels, centre to centre
step = enemy.direction_to(player) * SPEED * tick / 1000
enemy.move(step.x, step.y)
snail = SpriteObject(0, 0, image="snail.png", smooth_move=True)  # move(0.4, 0) works
```

### Camera and ZoomCamera
```python
camera = Camera(world_width, world_height, (WIDTH, HEIGHT))
camera.follow(player)
camera.update(tick)
player.draw(screen, camera)     # world things are drawn through the camera

zoom_camera = ZoomCamera(camera, (WIDTH, HEIGHT), zoom=2)   # smooth=True to blur
zoom_camera.draw_world(world, screen)

camera.snap()                   # jump to the player (start of a level, respawn)
camera = Camera(world_width, world_height, (WIDTH, HEIGHT),
                deadzone=(200, 120),   # walk freely in a box before the camera moves
                lookahead=100)         # see further the way you walk ((x, y) for top-down)
if camera.on_screen(enemy, margin=100):   # only update enemies near the screen
    enemy.update(tick)
camera.shake(300, 8)            # stops while pause_timers() is on
camera.apply(rect, parallax=0.5)          # draw something half as far as the world moves
```
With **F1** on (`Debug.handle_event(event)`), `World` draws the deadzone box
(or call `camera.draw_debug(screen)` yourself).

### Background (parallax)
```python
clouds = Background("clouds.png", parallax=0.1, y=30)   # far away: barely moves
hills = Background("hills.png", parallax=0.3, y=410)    # repeat_x=True by default
# in draw_game(), before the world, furthest away first:
screen.fill(SKY_BLUE)
clouds.draw(screen, camera)
hills.draw(screen, camera)
world.draw(screen)
```
`parallax=0` stays still on the screen, `1` moves with the world. Use
`repeat_y=True` to fill the screen up and down too.

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

#### Depth: walking behind and in front of things
The **name** of each tile layer in Tiled decides how deep it is:

| Layer name contains | Goes in | Drawn |
|---|---|---|
| (anything else, e.g. "Ground") | `level.background` | always behind the sprites |
| `midground` (or the layer property `y_sort` = true) | `level.midground` | in front of or behind each sprite, by height |
| `foreground` | `level.foreground` | always in front of the sprites |

```python
world = World(level, camera, y_sort=True)   # lower on the screen = in front
```
With `y_sort=True`, sprites and midground tiles are drawn in order of the
bottom of their rect, so the player walks behind a signpost from above and in
front of it from below. Tiles stacked in a column (a tree top on its trunk)
count as one thing, sorted by the bottom of the lowest tile, so a tree is never
cut in half. Without `y_sort` the midground is drawn under the sprites. Press
**F1** to see the line each thing is sorted by.

Anything flat on the ground at the foot of a midground object (grass, a
shadow) goes on a **background** layer such as "Ground details", not in the
midground tile. Otherwise it is drawn over the player's feet when they walk
behind it.

**Walking around things.** Give the player a feet hitbox
(`TopDownBody(..., hitbox=10)`, see Movement building blocks) and give each
fence, sign or tree a `collision` box over its **base** only. The feet can
never go into the base, so a player who walks up to it from below stops
below it and is drawn in front, and one who comes from above stops above
it and is drawn behind - with no extra code. This is how most top-down games
(Zelda, Pokemon, Stardew Valley) do it.

#### Tile properties
In Tiled, select a tile in the **tileset** and add a custom property (e.g.
`water` = true, `speed` = 0.5). Then read it where the player stands:
```python
ground = level.tile_properties_at(player.rect.midbottom)   # {} if nothing is set
speed = SPEED * ground.get("speed", 1)
if level.tile_property_at(player.rect.center, "lava", False):
    player.health.damage(1)
```
All tile layers are checked (the top one wins). It reads the map as it was
made in Tiled, not tiles your game moves later.

#### Making big maps run fast
`World` only looks at the part of the map on screen and only updates
animated tiles, so a big map runs about as fast as a small one. Press **F1**
(with `Debug.handle_event(event)`) to see the frame rate (FPS) and how many
tiles are drawn - if FPS is below 60, something is slow.
- Load images, maps and sounds in `init_pygame()` - **never** inside the game loop.
- Call `pg.display.set_mode(...)` **before** `TiledMap(...)` so tiles load in the
  fast screen format.
- Draw one big collision box over a wall instead of one per tile.
- Animated tiles cost a little every frame - use them where they matter.
- Moved a tile yourself? Call `world.refresh()`.
- `World(level, camera, chunks=False)` goes back to the v1.0 way (checks every tile).

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
enemy.health.draw_bar(screen, enemy, camera)   # a small bar floating above the enemy

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

### Hearts (HeartsBar)
```python
player_health = Health(6, invincible_ms=800)
hearts = HeartsBar(20, 20, health=player_health, hearts=3)  # 2 HP per heart
hearts.draw(screen)                  # damage / heal show up by themselves
```
Leave out `hearts=` for one heart per HP. Options: `heart_size=32` (or
`(w, h)`), `gap=4`, `per_row=` (wrap onto rows), `half_hearts=False`,
`full_image=` / `half_image=` / `empty_image=` (pictures of one heart, e.g.
`examples/assets/heart_full.png`) and `flash_when_hurt=True` (blinks while
invincible; call `hearts.update(tick)`). Without a Health it works like a
Progressbar: `HeartsBar(20, 20, maximum=5, value=3)`.

### ScrolledFrame, Table and Menu
```python
levels = ScrolledFrame(root, width=250, height=300)        # visible size
Button(levels, text="Level 1").grid(row=0, column=0)       # add as many as you like

items = Table(root, columns=["Item", "Damage"], rows=8, editable=["Damage"], on_edit=changed)
items.column("Damage", type=int, anchor="e")               # numbers only when editing
sheet = Table(root, columns=["Item", "Price"], editable=["Price"],
              edit_mode="spreadsheet", border_color=(255, 200, 0))
row = items.insert(["Sword", 7])
items.get_selected()        # ["Sword", 7]
world = levels_tree.insert(["World 1"], open=True)          # Table(..., tree=True)
levels_tree.insert(["Level 1-1"], parent=world)

menubar = Menu(root)
file_menu = Menu(menubar)
file_menu.add_command(label="Save", command=save, accelerator="Ctrl+S")   # shortcut works
menubar.add_cascade(label="File", menu=file_menu)
root.config(menu=menubar)

context = Menu()                       # right-click menu
context.post(*mouse.pos)               # open it; handle_event first, draw last
```
Click a heading to sort. Double-click an editable cell (or Enter) to type;
Enter saves, Tab moves on, Escape cancels.
With `edit_mode="spreadsheet"`: click a cell and just type (it replaces the
text), double-click / Enter / F2 edits the old text, Enter saves and moves down, Tab moves
right, arrow keys move around, Delete empties the cell.

### Particles
```python
Particles.explosion(pos)     Particles.sparks(pos)     Particles.dust(pos)
smoke = Particles.smoke(follow=chimney)     # keeps going until smoke.stop()
Particles.update(tick)                      # once, in update(tick)
Particles.draw(screen, camera)              # once, in draw_game()

bubbles = ParticleEmitter(pos=(400, 580), rate=25, lifetime=(2000, 3500),
                          speed=(30, 80), angle=-90, spread=25, gravity=-20,
                          size=(6, 16), color=[(180, 230, 255), (120, 180, 255)],
                          alpha=(200, 0))
bubbles.burst(50)
```
Any setting can be a (low, high) range. `color` can be a list to fade through.
Shapes: `"circle"`, `"square"`, `"line"` or an image. `glow=True` for fire and magic.

### FloatingText (damage numbers, "+10")
`FloatingText` is a **text particle**: it belongs to `Particles`, just like an
explosion. So your game needs the two `Particles` lines, **even if it uses no
other particle effects** - without them the text never moves or shows up.
```python
Particles.update(tick)                      # once, in update(tick)
Particles.draw(screen, camera)              # once, in draw_game() (camera optional)

FloatingText(enemy.rect.centerx, enemy.rect.top, "-10", color="red")
FloatingText(coin.rect.centerx, coin.rect.top, "+10", color="gold", speed=40)
FloatingText(x, y, damage)                  # numbers work too
```
No list to keep and nothing to delete: it floats up (`speed` pixels per second),
fades out in the second half of its `duration` (ms) and `Particles` removes it.
Options: `color`, `font_name`, `font_size`, `outline_color` (`None` = no outline).

### Spawner and Waves (enemies every few seconds, wave 1, wave 2...)
You write a function that makes **one** object. The Spawner decides when and
where to call it, and an object stops counting as alive when you `kill()` it.
```python
def make_slime(x, y):                       # your function: ONE slime at x, y
    slime = SpriteObject(x, y, animator=slime_walk())
    slime.brain = Chaser(slime, player, speed=90)
    slime.health = Health(20, on_death=slime.kill)
    return slime

slimes = Spawner(make_slime, points=[(20, 60), (760, 60)], every=1500,
                 max_alive=6, avoid=player, min_distance=150)
slimes.update(tick)                         # in update(tick)
for slime in slimes:                        # every slime still alive
    slime.brain.update(tick)
slimes.draw(screen, camera)                 # in draw_game() (or give it world=)

waves = Waves(slimes, [3, 5, {"count": 8, "every": 500, "make": make_boss}],
              break_ms=3000, on_all_done=you_win)
waves.update(tick)                          # instead of slimes.update(tick)
wave_label.config(text=waves.text())        # "Wave 2 of 3 - 4 left" / "Wave 3 in 2"
```
`points` can be one `(x, y)`, a list of them, a `pg.Rect` (a random spot inside),
`level.spawn_points`, `level.objects_of_type("spawner")` or a sprite (it can move).
`every=(800, 2000)` = a random time each go. Also `total=`, `first_after=`,
`pick="in_turn"`, `spawn_now()`, `stop()` / `start()`, `clear()`, `done_spawning`,
`cleared` and `config(every=...)` to speed up as the game goes on.
Waves: `wave`, `state`, `left()`, `break_left()`, `skip_break()`, `restart()`,
`loop=True` (endless). F1 shows the spawn places.

### Chain (snakes, followers, trains...)
```python
worm = Chain(head, count=12, spacing=14, size=20, shrink=True)
party = Chain(hero, segments=[elf, dwarf], delay_ms=300)    # real sprites follow
party.attach(new_friend)
worm.update(tick)    worm.draw(screen)

snake = Chain(mode="grid", grid=board, head_cell=(5, 5), length=3,
              move_every=120, images="snake_sheet.png")
snake.turn("left")                      # queued - quick presses aren't lost
if snake.moved and snake.head_cell == food: snake.grow()
if snake.hits_self() or snake.hits_wall(): game_over()
food = random.choice(snake.free_cells())
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
Listbox(50, 300, 200, items=skills, selectmode="multiple")  # .get_all_selected()
Combobox(300, 50, 200, values=["Knight", "Wizard"], textvariable=hero)
Combobox(300, 100, 200, values=countries, editable=True)    # type to search the list
Message(50, 300, "Long text that wraps...", width=400)
health = Progressbar(20, 20, 200, maximum=100, value=100)   # health.step(-10)
health = Progressbar(20, 20, 200, value=100, low_color=(220, 50, 50),  # red when low
                     animate=True)        # lost health shows as a shrinking "ghost"
settings = Notebook(100, 50, 400, 300)
sound_tab = settings.new_tab("Sound")                       # a Frame to add() to
```
Draw a Combobox after the widgets below it, so its open list is on top
(inside a Frame or Notebook this is done for you).

### Typing text out (like Pokemon dialogue)
```python
click = SoundEffect("click.wav", cooldown=60)        # optional typing sound
talk = Message(60, 400, "Hello there!", width=680,
               type_speed=30,                         # letters per second
               type_sound=click, on_done=show_arrow)  # on_done: last letter shown

talk.update(tick)                    # in update(tick) - types the next letters
if talk.handle_event(event):         # in handle_inputs() - True = it used the press
    continue                         # (to show the rest), so don't go to the next line
talk.config(text="Next line...")     # new text types out by itself
```
`talk.typing` is True while letters are appearing, `talk.skip()` shows the rest,
`talk.restart()` types it again. A left click, Space or Enter shows the rest
(change the keys with `skip_keys=`). No sound is played for spaces.

### Style and themes
```python
style = Style()
style.theme_use("dark")             # "light", "dark", "retro" or "high_contrast"
style.configure("Button", border_radius=10)      # every Button
style.configure("Danger.Button", bg=(200, 0, 0)) # a named style...
Button(10, 10, 120, 40, "Quit", style="Danger.Button")
```
`"high_contrast"` uses black, white and yellow, thick borders and bigger text,
for players who find the other themes hard to read.
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

#### Feet hitbox (top-down games)
```python
body = TopDownBody(player, solids=walls, speed=200, hitbox=10)
body.hitbox_rect                     # the feet as a Rect (e.g. for tile_properties_at)
body.draw_debug(screen, camera)      # F1: draws the feet hitbox
```
`hitbox` is the part of the sprite that bumps into walls:

| `hitbox=` | What hits walls |
|---|---|
| `None` (default) | the whole sprite rect (as in v1.0) |
| `10` | the **feet**: a strip 10 pixels tall along the bottom of the sprite, as wide as the sprite |
| `(16, 8)` | a feet strip 16 wide and 8 tall, centred along the bottom of the sprite |

`player.rect` doesn't change: drawing, pickups, bullets and `collides_with()`
still use the whole sprite. Only walls use the hitbox.

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

## Differences from tkinter

The library copies tkinter's names and ideas, but changes a few things that
often trip students up. Everything here is deliberate.

| Feature | tkinter | This library | Why |
|---|---|---|---|
| `grid()` / `pack()` / `place()` | return `None`, so `b = Button(...).grid()` makes `b` None | return the widget | removes a very common bug |
| Mixing `grid()` and `pack()` in one Frame | program freezes | stops with an error naming **your** file and line | the mistake is easy to find |
| Widget made in a Frame but never gridded | silently doesn't appear | doesn't appear, **and** a warning says which widget | no more "where did my button go?" |
| Seeing the layout | not possible | **F1** debug view: rows, columns, padding, sticky, warnings | layout problems become visible |
| Menu `accelerator="Ctrl+S"` | only text - you must bind the key yourself | the shortcut really works (`accelerators=False` to turn off) | less code to write |
| Scale `command` | called with the new value as a string | called with no arguments (read the Variable) | every `command` works the same way |
| `variable.trace_add("write", f)` | `f` gets 3 confusing arguments | `f()` gets none | simpler functions |
| Entry: run code on Enter | needs `entry.bind("<Return>", ...)` | `TextBox(..., on_enter=function)` | one option instead of an event binding |
| Scroll bars on lists | a separate `Scrollbar` you connect yourself | built into Listbox, Table and ScrolledFrame | works straight away |
| Scrolling a whole Frame | needs a Canvas + Frame trick | `ScrolledFrame` | one widget |
| Editing cells in a Treeview | not possible | `Table(..., editable=[...])` with number checks | spreadsheet-style tables |
| `Notebook` tabs | make a Frame, then `add()` it | also `notebook.new_tab("Sound")` (returns the Frame) | one line per tab |
| Pop-up messages | `messagebox` stops the program until closed | `Popup` doesn't stop the game loop | games keep running |
| `messagebox.askyesno()` etc. | stops the program and **returns** the answer | `askyesno(..., command=f)` opens a `MessageBox` and gives the answer to `f(answer)` (a `f()` with no answer also works - read `box.result`) | a game can't stop and wait |
| Editing a Treeview like a spreadsheet | not possible | `Table(..., edit_mode="spreadsheet")`: click and type, Enter moves down | quick data entry |
| Colour option names | `color` only in some places, `fg` / `bg` mostly | `fg` / `bg` everywhere, and `color` **or** `colour` | consistent, and Australian spelling works |
| See-through Frame | not possible | `bg=""` | layouts over a game background |
| Frames and size | shrink to fit their contents | grow to fit when no `width` / `height` is given | the same idea, but you can also fix the size |
| Style changes | `ttk.Style` | `Style()` - also changes widgets that already exist | live theme switching |
| Health as hearts | no widget for it; a `ttk.Progressbar` with pictures stretches them and cuts hearts at any percent | `HeartsBar` draws whole and half hearts and reads a `Health` | looks like real games, no maths needed |
| Typewriter text (one letter at a time) | not built in - you write an `after()` loop that adds a letter and reschedules itself | `Message(..., type_speed=30, type_sound=...)`; a click or Space shows the rest | game dialogue in one option |
| Entry `show="*"` | `show="*"` | the same, but it is kept in `box.show_char` (`box.show()` is the method that shows the box) | `show` can't be an option and a method |
| Hint text in an empty Entry | not possible | `TextBox(..., placeholder="Your name")` | forms explain themselves |
| Only allow some keys in an Entry | `validate=` + `validatecommand=` with `register()` and `%P` codes | `TextBox(..., allowed="digits")` (or `"letters"`, or your own characters) | one simple option |
| Run code when an Entry changes | a `StringVar` and `trace_add` | `TextBox(..., on_change=function)` | no Variable needed |
| `simpledialog.askstring()` / `askinteger()` | stop the program and **return** the answer | `askstring(..., command=f)` / `askinteger(...)` give the answer to `f(answer)` | a game can't stop and wait |
| Several lines in a Label | `"\n"`, lines centred by default (`justify="center"`) | `"\n"` too, but lines line up on the left by default | a score or HUD Label doesn't jump around |
| Outlined / shadowed text | not possible | `Label(..., outline=2)` / `Label(..., shadow=True)` | text stays readable over a game |
| Button colour while held down | `activebackground`, but on Windows it is the colour when the mouse is **over** it | `active_bg` is only the held-down colour; `hover_bg` is for the mouse over it | two clear options |
| Click sound on a Button | not possible | `Button(..., sound="click.wav")` | no extra code in the command |
| Progressbar warning colour / damage animation | not possible | `low_color=`, `low_at=`, `animate=True` | game-style health bars |
| Combobox typing | you can type by default (`state="readonly"` stops it); the list is not filtered | choose-only by default; `editable=True` lets you type **and** the list shows only the matches | v1.0 code keeps working; searching long lists is easy |
| Listbox `selectmode` | `"browse"`, `"single"`, `"multiple"`, `"extended"` | `"single"` (default, `"browse"` also works) and `"multiple"`; `"extended"` (Shift / Ctrl-click) gives an error that suggests `"multiple"` | one click = tick / untick is easier to understand |
| Fading / sliding widgets | not possible | `show(fade_ms=300)`, `hide(fade_ms=300)`, `slide_to(x, y, ms)` | menus that animate in and out |
| Turning a picture | no sprites in tkinter; pygame's `rotate()` turns anticlockwise, the picture grows and drifts away from its spot | `sprite.angle` is a compass direction (0 up, 90 right, clockwise), `point_at()` does the maths, the picture stays centred and the hitbox doesn't change | angles match a compass and the screen; collisions stay steady |
| Moving less than a pixel | pygame rects only hold whole numbers, so `rect.x += 0.4` does nothing | `SpriteObject(..., smooth_move=True)` keeps the fractions | slow speeds and `speed * tick / 1000` work |
| Which sprite is in front | (pygame) a `Group` draws in the order things were added | `World(..., y_sort=True)` draws whatever is lower on the screen in front, mixed with "midground" map layers | walk behind trees and signs with no extra code |
| Repeating something (spawning enemies) | a function that re-schedules itself with `root.after()` - easy to start twice, forget to re-schedule, or leave running after the level ends | `Spawner(make, every=1500, max_alive=6)` and `Waves(spawner, [3, 5, 8])`, run by `update(tick)` | less code, an alive limit and waves built in, and it stops when you stop updating it |
| Going back to idle after an attack | (pygame) check every frame whether the animation has ended | `play_once("attack", then="idle")`, `on_finish=`, `animator.busy` | less code in `update()` |

**Things tkinter has that this library doesn't (yet):** multi-line text
editing (`Text`), `Canvas` drawing items, and Shift / Ctrl-click choosing
in a Listbox (`selectmode="extended"`).

## Changes since v1.0

Everything here is **added** - code written for v1.0 still works the same.

**v1.1**
- `Table(border_color=...)` (and `border_colour`) - before, it could only be set
  as an attribute (`table.border_color = ...`), which still works.
- `Table(edit_mode="spreadsheet")` - click a cell and type; the default is still
  `"double_click"`.
- `Popup(title_font_size=..., title_font_name=...)` - the title is still 24 if
  left out; a bigger title makes the title bar taller.
- New `MessageBox` and `askyesno()`, `askyesnocancel()`, `askokcancel()`,
  `showinfo()`.
- New example `shop_editor_example.py`, new test `test_table_popup_messagebox.py`.
- Big maps run faster: `World` sorts tiles into chunks and only updates animated
  tiles (`chunks=False` for the old way, `world.refresh()` after moving tiles).
  Tiles loaded by `TiledMap` have a `map_layer` number. With F1 on, `World` shows
  the FPS and tiles drawn.
- Bodies (`TopDownBody`, `PlatformerBody`) check walls faster - the results are
  exactly the same. New test `test_big_maps.py`.
- New `HeartsBar` - shows a `Health` (or any value) as a row of hearts. New
  single-heart pictures `heart_full.png`, `heart_half.png`, `heart_empty.png`,
  new example `hearts_example.py`, new test `test_hearts.py`.
- `Message(type_speed=..., type_sound=..., on_done=..., skip_keys=...)` types the
  text out one letter at a time, with `update(tick)`, `handle_event()`, `skip()`,
  `restart()` and `typing`. `MessageBox(type_speed=..., type_sound=...)` and
  `box.update(tick)` do the same for question boxes. Without `type_speed` both
  show the text at once like before. New example `typewriter_example.py`, new
  test `test_typewriter.py`.
- New `FloatingText(x, y, text)` for damage numbers and "+10" pop-ups that float
  up and fade. It is a text particle, so `Particles.update(tick)` and
  `Particles.draw(screen)` move, draw and remove it. New example
  `floating_text_example.py`, new test `test_floating_text.py`.
- `TextBox(show="*", placeholder=..., allowed=..., on_change=...)` - passwords,
  grey hint text, numbers / letters only, and a function that runs when the
  text changes. `config(show=...)` works; the value is kept in `show_char`.
- New `askstring()` and `askinteger()` (like tkinter's `simpledialog`), and
  `MessageBox(entry=a_textbox)` to put a typing box in any question box.
- `Label(outline=..., shadow=True, justify=...)` and their colours.
  **One change you might notice:** `"\n"` in a Label now starts a new line
  (before, it showed as a box character).
- `Button(active_bg=..., active_image=..., sound=..., repeatdelay=...,
  repeatinterval=...)`, `button.pressed`, and `button.update(tick)` for repeating.
  Buttons now also notice the mouse button being let go (the event is not used up).
- `Progressbar(low_color=..., low_at=..., animate=True, ghost_color=...)`.
- `health.draw_bar(screen, sprite, camera)` - a small bar floating above a sprite.
- `Combobox(editable=True)` - type to search the list.
- `Listbox(selectmode="multiple")`, `get_all_selected()`, `selection_includes()`.
- `show(fade_ms=...)`, `hide(fade_ms=...)`, `toggle_visibility(fade_ms=...)`,
  `widget.closing`, `slide_to(x, y, ms)` and `widget.sliding` on every widget.
- New theme `"high_contrast"`.
- New examples `form_example.py` and `hud_example.py`, new test
  `test_widget_extras.py`.
- Copyright notices now name the State of Victoria (Department of Education),
  as the DET Intellectual Property and Copyright Policy requires, and the
  Student Guide and Cheat Sheet are marked CC BY 4.0. No code changed.
- `Animator`: `play_once(name, then=..., on_finish=...)`, `animator.busy`,
  `add_animation(..., frame_rate=...)` and `on_frame(name, frame_number, function)`.
- `SpriteObject`: `angle`, `point_at()`, `turn()`, `image_faces=`,
  `collides_with(other, pixel=True)`, `collides_with_any()`, `distance_to()`,
  `direction_to()` and `smooth_move=True`.
  **One thing to check:** if your own SpriteObject class already uses
  `self.angle` for something else, the sprite will now turn its picture -
  rename your attribute (e.g. `steering`).
- `Chain` no longer sets `.angle` on SpriteObjects that follow it (they are
  turned with `rotate=True` as before).
- `animator_example.py` now runs (Shift), jumps back to idle with `then="idle"`
  and plays footsteps with `on_frame`. New example `sprite_tricks_example.py`,
  new test `test_sprite_extras.py`.
- `Camera`: `snap()`, `deadzone=`, `lookahead=`, `on_screen()`,
  `apply(rect, parallax=...)`, `apply_pos(pos, parallax=...)` and
  `draw_debug(screen)`. `ZoomCamera` has `snap()`, `on_screen()` and `shake()` too.
  **One change you might notice:** `camera.shake()` now uses game time, so it
  stops while `pause_timers()` is on and finishes after `resume_timers()`.
- New `Background` for parallax backgrounds, with new pictures `hills.png` and
  `clouds.png`, new example `parallax_example.py`.
- `TiledMap`: `tile_properties_at()`, `tile_property_at()` and a new
  `midground` group (layer name contains "midground", or the layer property
  `y_sort` = true). Midground tiles have a `sort_y`.
- `World(y_sort=True)` draws sprites and midground tiles lowest-in-front. With
  F1 on it also shows the camera's deadzone box and the depth lines.
- `level1.tmx`: the water tile has the properties `water` and `speed`, a new
  "Midground" layer has three signposts (new picture `props.png`) and the
  bushes (moved from "Foreground", so you can walk in front of them; the
  "Foreground" layer is now empty), a new "Ground details" layer has the grass
  at the foot of each sign, and the
  pond's collision box is one tile smaller so its edge can be waded through
  (enemies in `topdown_ai_example.py` can step in too). `tiled_example.py`
  uses all of these, and `camera.snap()`. New test `test_camera_world_extras.py`.
- `TopDownBody(..., hitbox=...)`: a feet hitbox, so only the bottom of the
  sprite bumps into walls. New `body.hitbox_rect` and `body.draw_debug()`;
  `move_towards()` aims the feet when a hitbox is set. The default (`None`)
  is the whole rect, as before.
- `ZoomCamera.apply(rect)` and `apply_pos(pos)` - where a world thing appears on
  the zoomed screen (for debug boxes drawn on top).
- `level1.tmx`: small `collision` boxes over the bases of the signs and bushes.
  `tiled_example.py` now moves the player with `TopDownBody(..., hitbox=10)`
  (F1 shows the feet and the walls); `topdown_ai_example.py` gives the player a
  feet hitbox and uses `World(..., y_sort=True)`.
- New `Spawner` (makes objects every few seconds at points, a Rect or Tiled
  objects, with `max_alive`, `total`, `avoid=` and `world=`) and `Waves` (runs a
  Spawner in waves with breaks). New example `spawner_example.py`, new test
  `test_spawner.py`. `after_repeat()` is unchanged, so the old way still works.

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

## Licence

PygameTkinterGUITools was written by Adam Fox at Greater Shepparton Secondary
College for teaching Year 10 students.

Under the Victorian Department of Education's
[Intellectual Property and Copyright Policy](https://www2.education.vic.gov.au/pal/intellectual-property-and-copyright/policy),
material that school staff create as part of their work is owned by the
Department on behalf of the State of Victoria, and the policy asks schools to
share it for free.

- **Code** (`PygameTkinterGUITools.py`, `examples/`, `tests/`, `docs/make_guide_pictures.py`):
  © 2026 State of Victoria (Department of Education), released under the
  [MIT Licence](LICENSE). Creative Commons licences are not meant for software,
  so the code uses MIT, which gives the same freedom: use it, change it and
  share it, as long as the copyright notice is kept.
- **Student Guide and Cheat Sheet** (`docs/*.docx`) and the pictures in
  `docs/pictures/`: © 2026 State of Victoria (Department of Education),
  licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
  Please credit "Adam Fox, Greater Shepparton Secondary College and the
  Victorian Department of Education".
