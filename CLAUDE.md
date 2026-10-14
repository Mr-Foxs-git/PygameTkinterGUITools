# Guidance for Claude working on this repository

## Purpose
A pygame helper library for **Year 10 students**. GUI classes imitate tkinter
widgets (Button, Label, Frame, ...). It also contains game helpers (cameras,
Animator, Tiled map loading, and soon a Joystick class).

## Rules
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
   - Use `get_font()` (cached) instead of `pg.font.SysFont()`.
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
