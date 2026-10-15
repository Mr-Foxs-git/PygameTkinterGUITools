# Guidance for Claude working on this repository

## Purpose
A pygame helper library for **Year 10 students**. GUI classes imitate tkinter
widgets (Button, Label, Frame, ...). It also contains game helpers (cameras,
Animator, Tiled map loading, and soon a Joystick class).

## Rules
0. **Improve on tkinter, openly.** When planning a tkinter-style feature,
   point out tkinter quirks that confuse students or make code harder, and
   suggest a clearer behaviour. Only build an improvement once Adam approves
   it, and always add it to the "Differences from tkinter" table in README.md
   (what tkinter does, what this library does, why).
1. **Plan before coding.** Before changing code, write a clear plan (what,
   why, which classes/methods, any effect on existing student code) and wait
   for the teacher's (Adam's) approval.
2. **Readable for beginners.** Prefer simple, explicit code over clever code.
   Use docstrings and comments that explain *why*. Avoid advanced Python
   features unless they clearly help students.
3. **tkinter-like API.** Keep names and parameters close to tkinter.
4. **Student access status: NOT YET RELEASED.** Students have not used the
   library yet, so classes may be refactored freely for consistency.
   Once Adam says students have access, change this rule: from then on avoid
   renaming or removing public classes, methods or parameters; keep old names
   working (with a deprecation note) and document changes.
5. **Consistency.** Follow the shared design:
   - GUI widgets subclass `Widget` (containers subclass `Container`) and take
     position first: `Label(x, y, text)`, `Button(x, y, width, height, text)`.
   - Widgets: `draw(screen, offset=(0, 0))`, `handle_event(event, offset=(0, 0))`,
     `update(tick)`, `config()`/`configure()`, `show()`/`hide()`.
     offset = parent position (Frame/Popup).
   - World objects (SpriteObject, Tile): `draw(screen, camera=None)`.
   - Everything that changes over time uses `update(tick)` (tick in ms).
   - Option names follow tkinter: `text`, `fg`, `bg`, `hover_bg`, `command`,
     `font_name`, `font_size`, `border_color`, `border_width`, `center`.
   - Colour options: US spelling `color` is the main name; also accept the
     `colour` spelling (via `_pick()` in `__init__` and `_aliases` for config).
   - Use `get_font()` (cached) instead of `pg.font.SysFont()`, and
     `load_image()` (cached, scaled) for image skins.
   - Widget options default to None and are read with `self.cget("option")`,
     which falls back to the `Style` (your configure() -> theme -> "light").
     New widgets need an entry in `THEMES["light"]` for any option they add.
   - Shared values use `IntVar`/`StringVar`/`BooleanVar`/`DoubleVar`
     (`variable=` / `textvariable=`). `command` functions take no arguments.
   - `handle_event` returns True if the widget used the event.
   - Keyboard focus: widgets set `takes_focus = True` and implement
     `focus_action(action)`. `FocusGroup` must stay opt-in (off until
     `active = True`) and only use the keys chosen, so it never clashes with
     the student's game controls.
   - Containers set `child.parent`; use `widget.active` / `widget.showing`
     (which check the parents) rather than just `visible`.
   - Input: KeyboardInput / MouseInput / JoystickManager share the API
     `bind`, `handle_event`, `update(tick)`, `is_pressed` / `was_pressed` /
     `was_released`. Examples use them instead of `pg.key.get_pressed()` for
     anything that should happen once per press.
   - Sound must never crash without an audio device: always go through
     `Audio.check()`. Examples call `init_audio()` before `pg.init()`.
   - DragObject works with no grid, one Grid, or a list of Grids. Items have
     `kinds` and a free-form `stats` dict; Grid / slot `accepts` can be a
     kind, a list of kinds or a function.
   - Movement is modular: "brains" (PathFollower, Patrol, Chaser) decide and
     call `body.move()`; bodies (TopDownBody, PlatformerBody) do collisions.
     Any brain must work with no body too. Bodies keep float positions in
     `_pos` and re-sync if the rect is moved from outside.
   - Debug drawing (paths, ranges, NavGrid) is controlled by `Path.show_all`.
   - Keep the library modular and genre-neutral: building blocks, not
     whole games. Tiled conventions: Classes collision / platform / ladder /
     trigger / enemy; paths are named Polylines / Polygons.
   - Widgets accept a parent first (`Label(frame, text=...)`) and then need
     grid / pack / place; Containers arrange children in `_arrange()` (called
     from draw / handle_event / update). Every layout feature must show up in
     the F1 debug view (`_draw_layout_debug`) and give clear warnings -
     layout problems are hard for students to see.
   - One debug switch: `Debug.on` (F1) for everything.
   - Timers use game time (`_now()`); Scenes run `update_timers()` and cancel a
     scene's timers when it ends. Save files go next to the game
     (`game_folder()`) and loading must never crash.
   - Popups that sit on top (Combobox lists, Menus, context menus) must take
     events first and be drawn last; menus take clicks while open so they
     never reach the game underneath.
   - Particles: every ParticleEmitter registers itself with `Particles`, so a
     game only needs `Particles.update(tick)` and `Particles.draw(screen)`.
     Presets are plain emitters with settings (students copy and change them).
   - Chain is generic (snakes, followers, trains, trails): keep both modes
     ("path" and "grid") sharing the same methods.
   - Only `TiledMap` may import pytmx (inside the class).
6. **Dependencies.** Only `pygame` and `pytmx`. Ask before adding any more.
7. **Examples.** New features should come with a small runnable example in
   `examples/` and an update to `README.md`.
8. **Example game loop.** Every example (and the README) must follow
   `examples/_template.py` exactly:
   - functions in this order: `init_pygame()`, `handle_inputs()`,
     `update(tick)`, `draw_game()`; keep all four even if one only has `pass`
   - globals declared in `init_pygame()`; objects created there after `pg.init()`
   - `# >>>` comments mark where each object's code goes
   - main program: `init_pygame()` then `while True:` with
     `tick = clock.tick(FPS)`, `handle_inputs()`, `update(tick)`, `draw_game()`
   - quitting is `pg.quit()` then `sys.exit()` inline in `handle_inputs()`
     (no `quit_game()` function)
   - `tick` is new to students: explain it with a short comment
9. **Tests.** Add checks to `tests/` for bug fixes and new features. Tests use
   `SDL_VIDEODRIVER=dummy` so no window opens.

## Project layout
- `PygameTkinterGUITools.py` - the whole library (single file for now)
- `examples/` - runnable examples (`_template.py` is the starting point)
- `tests/` - automatic checks (`test_phase_a.py`, `test_map.tmx`)
- `PygameTkinterGUITools.pyproj` / `.slnx` - Visual Studio 2026 project files
