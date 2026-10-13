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
3. **tkinter-like API.** Keep names and parameters close to tkinter where
   sensible (e.g. `text`, `command`/`action`, `bg`, `fg`). Accept both
   `colour` and `color` spellings where already supported.
4. **Don't break student code.** Avoid renaming or removing public classes,
   methods or parameters. If a change is needed, keep the old name working
   (with a deprecation note) and document it.
5. **Consistency.** Every widget should follow the same pattern:
   `draw(screen, offset=(0, 0))`, `handle_event(event, offset=(0, 0))`,
   and `update(tick)` where it animates.
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
