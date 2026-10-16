"""
Makes the pictures for the student guide.

Run this file in Visual Studio (right-click > Start without Debugging).
No window opens. The pictures are saved in docs/pictures/.
Run it again whenever the library changes, so the guide stays up to date.
"""
import os
import sys
import random
import traceback

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))

import pygame as pg
pg.init()
pg.display.set_mode((1000, 800))
import PygameTkinterGUITools as g

ASSETS = os.path.join(HERE, "..", "examples", "assets")
OUT = os.path.join(HERE, "pictures")
os.makedirs(OUT, exist_ok=True)
GAME_BG = (30, 30, 40)
random.seed(4)
made, failed = [], []

# Pretend the mouse is far away, so nothing looks "hovered" unless we say so
mouse_pos = [(-100, -100)]
pg.mouse.get_pos = lambda: mouse_pos[0]


def asset(name):
    return os.path.join(ASSETS, name)


def text(surface, words, x, y, size=22, colour=(255, 255, 255), center=False, bold=False):
    font = pg.font.SysFont("arial", size, bold=bold)
    picture = font.render(words, True, colour)
    rect = picture.get_rect(center=(x, y)) if center else picture.get_rect(topleft=(x, y))
    surface.blit(picture, rect)
    return rect


def arrow(surface, start, end, colour=(255, 200, 0), width=3):
    start, end = pg.Vector2(start), pg.Vector2(end)
    pg.draw.line(surface, colour, start, end, width)
    d = (end - start).normalize() * 12
    side = pg.Vector2(-d.y, d.x) * 0.6
    pg.draw.polygon(surface, colour, [end, end - d + side, end - d - side])


def shot(name, width, height, bg=GAME_BG):
    """Decorator: run the drawing function on a fresh surface and save it."""
    def wrap(draw):
        try:
            g.Style().reset()
            g.Debug.on = False
            g.Path.show_all = True
            g.Particles.clear()
            g.Menu.close_all()
            mouse_pos[0] = (-100, -100)
            surface = pg.Surface((width, height))
            surface.fill(bg)
            draw(surface)
            pg.image.save(surface, os.path.join(OUT, name + ".png"))
            made.append(name)
        except Exception:
            failed.append(name)
            print("FAILED:", name)
            traceback.print_exc()
        return draw
    return wrap


# ======================================================================
# Diagrams
# ======================================================================
@shot("diagram_game_loop", 900, 420, bg=(255, 255, 255))
def _(s):
    boxes = [("init_pygame()", "Make the window and\nall your objects", (90, 170, 90), (40, 40)),
             ("handle_inputs()", "Keys, mouse, clicks\nobj.handle_event(event)", (70, 130, 220), (40, 230)),
             ("update(tick)", "Move and animate\nobj.update(tick)", (230, 140, 40), (340, 230)),
             ("draw_game()", "Draw everything\nobj.draw(screen)", (150, 90, 200), (640, 230))]
    for title, words, colour, (x, y) in boxes:
        r = pg.Rect(x, y, 230, 140)
        pg.draw.rect(s, colour, r, border_radius=14)
        text(s, title, r.centerx, r.y + 30, 26, center=True, bold=True)
        for i, line in enumerate(words.split("\n")):
            text(s, line, r.centerx, r.y + 72 + i * 26, 19, center=True)
    text(s, "once, at the start", 290, 95, 20, (60, 60, 60))
    arrow(s, (155, 180), (155, 225), (90, 90, 90))
    arrow(s, (270, 300), (335, 300), (90, 90, 90))
    arrow(s, (570, 300), (635, 300), (90, 90, 90))
    pg.draw.lines(s, (90, 90, 90), False, [(755, 370), (755, 400), (155, 400), (155, 375)], 3)
    arrow(s, (155, 400), (155, 374), (90, 90, 90))
    text(s, "repeat about 60 times a second (while True:)", 450, 383, 20, (60, 60, 60), center=True)


@shot("diagram_pressed_held", 900, 330, bg=(255, 255, 255))
def _(s):
    left, frame_w = 170, 60
    frames = 11
    down, up = 2, 8
    text(s, "frame:", 20, 20, 20, (60, 60, 60))
    for f in range(frames):
        text(s, str(f + 1), left + f * frame_w + frame_w // 2, 30, 20, (60, 60, 60), center=True)
    rows = [("Key held down", lambda f: down <= f < up, (90, 90, 90)),
            ("was_pressed", lambda f: f == down, (70, 130, 220)),
            ("is_pressed", lambda f: down <= f < up, (90, 170, 90)),
            ("was_released", lambda f: f == up, (230, 140, 40))]
    for i, (name, on, colour) in enumerate(rows):
        y = 70 + i * 62
        text(s, name, 20, y + 12, 22, (30, 30, 30), bold=True)
        for f in range(frames):
            r = pg.Rect(left + f * frame_w + 3, y, frame_w - 6, 40)
            pg.draw.rect(s, colour if on(f) else (225, 225, 225), r, border_radius=6)
            if on(f) and i > 0:
                text(s, "True", r.centerx, r.centery, 16, center=True)
    text(s, "was_pressed = ONE frame (jump, shoot once, play a sound)      "
            "is_pressed = EVERY frame (walking)", 20, 305, 17, (60, 60, 60))


@shot("diagram_sprite_sheet", 760, 450, bg=(255, 255, 255))
def _(s):
    sheet = pg.image.load(asset("player_sheet.png")).convert_alpha()
    big = pg.transform.scale(sheet, (sheet.get_width() * 4, sheet.get_height() * 4))
    x0, y0 = 140, 40
    s.fill((60, 60, 70), (x0, y0, big.get_width(), big.get_height()))
    s.blit(big, (x0, y0))
    for c in range(5):
        pg.draw.line(s, (255, 200, 0), (x0 + c * 128, y0), (x0 + c * 128, y0 + 384 - 1), 2)
    for r in range(4):
        pg.draw.line(s, (255, 200, 0), (x0, y0 + r * 128 - (1 if r == 3 else 0)),
                     (x0 + 512, y0 + r * 128 - (1 if r == 3 else 0)), 2)
    for c in range(4):
        text(s, f"col {c}", x0 + c * 128 + 64, y0 - 22, 18, (30, 30, 30), center=True)
    names = ["row 0  idle", "row 1  walk", "row 2  jump"]
    for r in range(3):
        text(s, names[r].split("  ")[0], 20, y0 + r * 128 + 45, 20, (30, 30, 30), bold=True)
        text(s, names[r].split("  ")[1], 20, y0 + r * 128 + 70, 18, (90, 90, 90))
    text(s, "(1, 2) = row 1, col 2", x0 + 2 * 128 + 6, y0 + 128 + 4, 15, (255, 255, 255))


def fake_tiled(s, title):
    """A simplified Tiled window to draw steps on."""
    s.fill((235, 235, 240))
    pg.draw.rect(s, (60, 63, 70), (0, 0, s.get_width(), 34))
    text(s, title, 12, 6, 20, (255, 255, 255), bold=True)
    tools = ["Select", "Rectangle (R)", "Point (I)", "Polygon (P)", "Polyline (L)"]
    x = 10
    rects = {}
    for t in tools:
        w = text(s, t, -500, -500, 16).width + 20
        r = pg.Rect(x, 42, w, 30)
        pg.draw.rect(s, (255, 255, 255), r, border_radius=4)
        pg.draw.rect(s, (160, 160, 170), r, 1, border_radius=4)
        text(s, t, r.centerx, r.centery, 16, (40, 40, 40), center=True)
        rects[t] = r
        x += w + 6
    mapr = pg.Rect(10, 82, 560, 330)
    pg.draw.rect(s, (110, 170, 90), mapr)
    for gx in range(mapr.x, mapr.right, 32):
        pg.draw.line(s, (95, 150, 80), (gx, mapr.y), (gx, mapr.bottom))
    for gy in range(mapr.y, mapr.bottom, 32):
        pg.draw.line(s, (95, 150, 80), (mapr.x, gy), (mapr.right, gy))
    panel = pg.Rect(585, 42, s.get_width() - 595, 370)
    pg.draw.rect(s, (255, 255, 255), panel)
    pg.draw.rect(s, (160, 160, 170), panel, 1)
    text(s, "Properties", panel.x + 10, panel.y + 8, 18, (40, 40, 40), bold=True)
    return rects, mapr, panel


def prop_row(s, panel, n, name, value, highlight=False):
    y = panel.y + 40 + n * 30
    r = pg.Rect(panel.x + 6, y, panel.width - 12, 26)
    pg.draw.rect(s, (255, 240, 170) if highlight else (245, 245, 248), r)
    text(s, name, r.x + 6, r.y + 4, 16, (60, 60, 60))
    text(s, value, r.x + 120, r.y + 4, 16, (0, 0, 0), bold=highlight)
    return r


def step_badge(s, n, pos):
    pg.draw.circle(s, (220, 50, 50), pos, 15)
    text(s, str(n), pos[0], pos[1], 18, center=True, bold=True)


@shot("tiled_draw_path", 900, 460)
def _(s):
    rects, mapr, panel = fake_tiled(s, "Tiled - drawing a path")
    pg.draw.rect(s, (255, 220, 120), rects["Polyline (L)"], 3, border_radius=4)
    step_badge(s, 1, (rects["Polyline (L)"].right + 14, rects["Polyline (L)"].centery))
    pts = [(80, 360), (230, 160), (400, 200), (520, 330)]
    pg.draw.lines(s, (250, 250, 250), False, pts, 3)
    for i, p in enumerate(pts):
        pg.draw.circle(s, (255, 255, 255), p, 7)
        pg.draw.circle(s, (40, 40, 40), p, 7, 2)
        label = "double-click" if i == len(pts) - 1 else "click"
        text(s, label, p[0] + 10, p[1] - 26, 16, (20, 20, 20), bold=True)
    step_badge(s, 2, (60, 335))
    prop_row(s, panel, 0, "Name", "guard_route", True)
    prop_row(s, panel, 1, "Class", "")
    prop_row(s, panel, 2, "mode", "ping_pong")
    text(s, "(optional custom property)", panel.x + 10, panel.y + 136, 14, (110, 110, 110))
    step_badge(s, 3, (panel.x - 18, panel.y + 52))
    text(s, "1 Choose Polyline (L) - or Polygon (P) for a loop   2 Click each point, "
            "double-click the last   3 Type its Name", 10, 428, 16, (40, 40, 40))


@shot("tiled_object_class", 900, 460)
def _(s):
    rects, mapr, panel = fake_tiled(s, "Tiled - walls, platforms and ladders")
    pg.draw.rect(s, (255, 220, 120), rects["Rectangle (R)"], 3, border_radius=4)
    step_badge(s, 1, (rects["Rectangle (R)"].right + 14, rects["Rectangle (R)"].centery))
    wall = pg.Rect(60, 330, 460, 50)
    shade = pg.Surface(wall.size, pg.SRCALPHA)
    shade.fill((80, 140, 255, 110))
    s.blit(shade, wall)
    pg.draw.rect(s, (40, 90, 220), wall, 2)
    text(s, "drag a box over the wall", wall.x + 10, wall.y - 26, 16, (20, 20, 20), bold=True)
    step_badge(s, 2, (wall.x - 2, wall.y + 10))
    prop_row(s, panel, 0, "Name", "")
    prop_row(s, panel, 1, "Class", "collision", True)
    step_badge(s, 3, (panel.x - 18, panel.y + 82))
    text(s, "Other Classes: platform  ladder  trigger  enemy", panel.x + 10, panel.y + 120, 14,
         (80, 80, 80))
    text(s, "1 Choose Rectangle (R)   2 Drag a box over the wall   3 Type its Class",
         10, 428, 16, (40, 40, 40))


@shot("tiled_custom_property", 900, 460)
def _(s):
    rects, mapr, panel = fake_tiled(s, "Tiled - linking an enemy to a path")
    pts = [(120, 300), (300, 150), (480, 300)]
    pg.draw.lines(s, (250, 250, 250), False, pts, 3)
    text(s, "guard_route", 280, 120, 16, (20, 20, 20), bold=True)
    enemy = pg.Rect(105, 285, 32, 32)
    pg.draw.rect(s, (230, 80, 80), enemy)
    pg.draw.rect(s, (40, 40, 40), enemy, 2)
    step_badge(s, 1, (enemy.x - 14, enemy.y - 10))
    prop_row(s, panel, 0, "Name", "guard")
    prop_row(s, panel, 1, "Class", "enemy", True)
    text(s, "Custom Properties  ( + button )", panel.x + 10, panel.y + 112, 15, (40, 40, 40), bold=True)
    prop_row(s, panel, 3, "ai", "path", True)
    prop_row(s, panel, 4, "path", "guard_route", True)
    step_badge(s, 2, (panel.x - 18, panel.y + 172))
    text(s, "1 Make the enemy (a Rectangle)   2 Add custom properties with the + button. "
            "In Python: info[\"properties\"][\"path\"]", 10, 428, 16, (40, 40, 40))


# ======================================================================
# Widgets
# ======================================================================
@shot("label", 520, 150)
def _(s):
    g.Label(20, 20, "Score: 0").draw(s)
    g.Label(20, 55, "Big yellow title", fg=(255, 220, 0), font_size=44).draw(s)
    g.Label(20, 105, "With a background", fg=(0, 0, 0), bg=(200, 200, 200)).draw(s)


@shot("button", 560, 110)
def _(s):
    g.Button(20, 25, 150, 55, "Play").draw(s)
    g.Button(195, 25, 160, 55, "Rounded", bg=(250, 200, 60), hover_bg=(255, 230, 120),
             border_radius=15, border_color=(0, 0, 0), border_width=3, shadow=True).draw(s)
    g.Button(385, 25, 150, 55, "Quit", bg=(220, 70, 70), fg=(255, 255, 255)).draw(s)


@shot("button_hover", 400, 110)
def _(s):
    b1 = g.Button(20, 25, 160, 55, "Normal")
    b2 = g.Button(215, 25, 160, 55, "Hovered")
    b1.draw(s)
    mouse_pos[0] = (295, 50)
    b2.draw(s)
    pg.draw.polygon(s, (255, 255, 255), [(300, 55), (300, 80), (306, 74), (312, 86), (316, 84),
                                         (310, 72), (318, 72)])


@shot("textbox", 520, 160)
def _(s):
    box = g.TextBox(20, 25, max_chars=12, label="Name:", text="Sam")
    box.typing = True
    box.draw(s)
    g.TextBox(20, 85, max_chars=6, label="Age (label on top)", label_position="top",
              text="14").draw(s)


@shot("check_radio", 480, 230)
def _(s):
    music = g.BooleanVar(True)
    level = g.StringVar("Normal")
    g.Checkbutton(20, 20, "Music", variable=music).draw(s)
    g.Checkbutton(20, 55, "Show FPS", variable=g.BooleanVar(False)).draw(s)
    g.Label(240, 20, "Difficulty").draw(s)
    for i, name in enumerate(["Easy", "Normal", "Hard"]):
        g.Radiobutton(240, 55 + i * 35, name, variable=level, value=name).draw(s)


@shot("scale_spinbox", 560, 190)
def _(s):
    g.Scale(20, 20, from_=0, to=100, length=300, variable=g.IntVar(65), label="Volume").draw(s)
    g.Spinbox(20, 110, from_=1, to=4, variable=g.IntVar(2)).draw(s)
    g.Spinbox(140, 110, values=["Red", "Green", "Blue"]).draw(s)
    g.Scale(400, 20, from_=1, to=10, length=140, orient="vertical",
            variable=g.IntVar(4), label="Speed").draw(s)


@shot("listbox_combobox", 560, 260)
def _(s):
    lb = g.Listbox(20, 20, 200, rows=6, items=[f"Level {n}" for n in range(1, 10)])
    lb.selection_set(2)
    lb.draw(s)
    cb = g.Combobox(260, 20, 220, values=["Knight", "Wizard", "Archer", "Rogue"])
    cb.is_open = True
    cb.highlight = 1
    cb.draw(s)


@shot("message", 520, 180)
def _(s):
    g.Message(20, 20, "Welcome, traveller! A Message wraps long text onto new lines by "
              "itself - great for dialogue and instructions.", width=470, bg=(20, 20, 60),
              padding=14, font_size=26).draw(s)


@shot("progressbar", 560, 200)
def _(s):
    g.Label(20, 15, "Health").draw(s)
    g.Progressbar(20, 40, 300, thickness=26, value=70, bar_color=(80, 200, 120),
                  show_text=True, border_radius=6).draw(s)
    g.Progressbar(20, 85, 300, thickness=26, value=25, bar_color=(230, 60, 60),
                  border_radius=6).draw(s)
    g.Progressbar(20, 130, 270, thickness=48, maximum=5, value=3,
                  bar_image=asset("hearts_full.png"), trough_image=asset("hearts_empty.png")).draw(s)
    g.Label(400, 15, "Energy").draw(s)
    g.Progressbar(420, 45, 140, thickness=24, orient="vertical", value=60,
                  bar_color=(250, 200, 60)).draw(s)


@shot("frame", 420, 320)
def _(s):
    menu = g.Frame(20, 20, 300, 270, bg=(50, 50, 80), border_color=(200, 200, 255))
    menu.add(g.Label(140, 20, "Main Menu", font_size=40, center=True),
             g.Button(40, 60, 200, 50, "Start"),
             g.Button(40, 125, 200, 50, "Options"),
             g.Button(40, 190, 200, 50, "Quit"))
    menu.draw(s)


@shot("labelframe_notebook", 760, 300)
def _(s):
    lf = g.LabelFrame(20, 20, 220, 170, "Difficulty")
    level = g.StringVar("Normal")
    for i, n in enumerate(["Easy", "Normal", "Hard"]):
        lf.add(g.Radiobutton(0, i * 35, n, variable=level, value=n))
    lf.draw(s)
    nb = g.Notebook(280, 20, 450, 250)
    sound = nb.new_tab("Sound")
    sound.add(g.Scale(10, 10, length=380, variable=g.IntVar(70), label="Volume"),
              g.Checkbutton(10, 90, "Music", variable=g.BooleanVar(True)))
    nb.new_tab("Controls")
    nb.new_tab("Player")
    nb.draw(s)


@shot("popup", 640, 420)
def _(s):
    for i in range(12):
        pg.draw.circle(s, (60 + i * 10, 120, 200), (random.randint(0, 640), random.randint(0, 420)), 30)
    pop = g.Popup(320, 210, 340, 210, "Game Over", center=True, visible=True)
    pop.add(g.Label(160, 30, "You scored 42!", fg=(0, 0, 0), font_size=36, center=True),
            g.Button(85, 80, 160, 50, "Play again"))
    pop.draw(s)


@shot("scrolledframe", 320, 330)
def _(s):
    sf = g.ScrolledFrame(20, 20, width=260, height=290)
    for n in range(1, 16):
        g.Button(sf, text=f"Level {n}", width=190, font_size=24).grid(row=n, column=0, pady=3)
    sf.draw(s)
    sf.scroll_to(y=120)
    sf.draw(s)


def build_form(root, gap=6):
    form = g.LabelFrame(root, text="Your player")
    form.grid(row=0, column=0)
    g.Label(form, text="Name:").grid(row=0, column=0, sticky="e", padx=8 + gap, pady=gap)
    g.TextBox(form, max_chars=10, text="Sam").grid(row=0, column=1, sticky="w", pady=gap)
    g.Label(form, text="Hero:").grid(row=1, column=0, sticky="e", padx=8 + gap, pady=gap)
    g.Combobox(form, width=180, values=["Knight", "Wizard"]).grid(row=1, column=1, sticky="w",
                                                                 pady=gap)
    g.Checkbutton(form, text="Show hints", variable=g.BooleanVar(True)).grid(
        row=2, column=0, columnspan=2, pady=gap)
    return form


@shot("grid_layout", 520, 260)
def _(s):
    root = g.Root(s, padding=40)
    build_form(root)
    root.draw(s)


@shot("grid_debug", 640, 360)
def _(s):
    root = g.Root(s, padding=60)
    form = build_form(root, gap=14)
    g.Label(form, text="Forgot to grid me")
    g.Debug.on = True
    root.draw(s)


@shot("menu_bar", 560, 300)
def _(s):
    root = g.Root(s)
    menubar = g.Menu(root)
    file_menu = g.Menu(menubar)
    file_menu.add_command(label="New game", accelerator="Ctrl+N")
    file_menu.add_command(label="Save", accelerator="Ctrl+S")
    file_menu.add_command(label="Export", state="disabled")
    file_menu.add_separator()
    file_menu.add_checkbutton(label="Music", variable=g.BooleanVar(True))
    file_menu.add_command(label="Quit", accelerator="Ctrl+Q")
    menubar.add_cascade(label="File", menu=file_menu)
    menubar.add_cascade(label="Edit", menu=g.Menu(menubar))
    menubar.add_cascade(label="View", menu=g.Menu(menubar))
    root.config(menu=menubar)
    menubar.bar_width = 560
    menubar._open_bar_item(0)
    menubar._chain[0]["hover"] = 1
    root.draw(s)


@shot("table", 520, 300)
def _(s):
    t = g.Table(20, 20, columns=["Item", "Type", "Damage", "Price"], rows=7, editable=["Price"])
    t.column("Damage", anchor="e")
    t.column("Price", anchor="e")
    for row in [["Iron sword", "weapon", 7, 45], ["Oak shield", "shield", 0, 30],
                ["Fire staff", "weapon", 12, 120], ["Red potion", "potion", 0, 15],
                ["Bow", "weapon", 5, 35], ["Steel helm", "armour", 0, 75]]:
        t.insert(row)
    t.sort_by("Damage", reverse=True)
    t.selection_set(t.get_children()[1])
    t.start_edit(t.get_children()[0], "Price")
    t.editing["text"] = "50"
    t.draw(s)


@shot("table_tree", 420, 300)
def _(s):
    t = g.Table(20, 20, columns=["Level", "Stars"], rows=8, tree=True)
    for w in range(1, 4):
        world = t.insert([f"World {w}", ""], open=(w == 1))
        for n in range(1, 5):
            t.insert([f"Level {w}-{n}", "*" * ((w + n) % 4)], parent=world)
    t.draw(s)


def theme_panel(s, theme):
    g.Style().theme_use(theme)
    s.fill({"light": (30, 30, 40), "dark": (20, 20, 25), "retro": (0, 0, 0),
            "high_contrast": (0, 0, 0)}[theme])
    f = g.Frame(15, 15, 270, 260)
    f.add(g.Label(0, 0, theme.replace("_", " ").title() + " theme", font_size=30),
          g.Button(0, 40, 200, 45, "Play"),
          g.Checkbutton(0, 100, "Music", variable=g.BooleanVar(True)),
          g.Scale(0, 140, length=230, variable=g.IntVar(60)),
          g.TextBox(0, 195, max_chars=10, text="Sam"))
    f.draw(s)


for _theme in ("light", "dark", "retro", "high_contrast"):
    shot("theme_" + _theme, 300, 290)(lambda s, t=_theme: theme_panel(s, t))


@shot("tooltip", 460, 220)
def _(s):
    sword = g.DragObject(40, 40, 64, 64, image=asset("item_sword.png"), name="Iron Sword",
                         kind="weapon", stats={"damage": 7, "weight": 3})
    sword.draw(s)
    tips = g.Tooltip(delay=0)
    tips.attach(sword, lambda i: f"{i.name}\nDamage: {i.stats['damage']}\nWeight: {i.stats['weight']}")
    mouse_pos[0] = (80, 80)
    tips.update(10)
    tips.draw(s)


# ======================================================================
# Game objects
# ======================================================================
@shot("sprites", 560, 200)
def _(s):
    anim = g.Animator(asset("player_sheet.png"), from_sheet=True, tile_width=32, tile_height=32,
                      rows=3, cols=4, scale=3)
    for i, (row, col) in enumerate([(0, 0), (1, 0), (1, 2), (2, 2)]):
        frame = anim.frames[row * 4 + col]
        s.blit(frame, (20 + i * 130, 30))
        text(s, f"({row}, {col})", 68 + i * 130, 150, 18, (200, 200, 200), center=True)
    coin = g.SpriteObject(500, 60, image=asset("coin.png"), width=40, height=40)
    coin.draw(s)


def level_view(s, filename, focus, debug=False):
    level = g.TiledMap(asset(filename))
    camera = g.Camera(level.width, level.height, s.get_size(), smooth=1)
    target = g.SpriteObject(focus[0], focus[1], 28, 28, bg=(70, 160, 230))
    camera.follow(target)
    camera.update()
    world = g.World(level, camera)
    return level, camera, world


@shot("tiled_level", 640, 400)
def _(s):
    level, camera, world = level_view(s, "level1.tmx", (300, 330))
    anim = g.Animator(asset("player_sheet.png"), from_sheet=True, tile_width=32, tile_height=32,
                      rows=3, cols=4)
    player = g.SpriteObject(*level.spawn_points["player_spawn"], animator=anim)
    world.add_sprite(player)
    for info in level.custom_objects:
        if info["type"] == "coin":
            world.add_sprite(g.SpriteObject(info["x"], info["y"], image=asset("coin.png")))
    world.draw(s)


@shot("platformer", 700, 420)
def _(s):
    level, camera, world = level_view(s, "platformer.tmx", (700, 420))
    s.fill((120, 180, 230))
    anim = g.Animator(asset("player_sheet.png"), from_sheet=True, tile_width=32, tile_height=32,
                      rows=3, cols=4)
    world.add_sprite(g.SpriteObject(600, 512, animator=anim))
    slime = g.Animator(asset("slime_sheet.png"), from_sheet=True, tile_width=32, tile_height=32,
                       rows=1, cols=2)
    world.add_sprite(g.SpriteObject(17 * 32, 16 * 32, animator=slime))
    world.draw(s)


@shot("platformer_debug", 700, 420)
def _(s):
    level, camera, world = level_view(s, "platformer.tmx", (900, 330))
    s.fill((120, 180, 230))
    world.draw(s)
    for o in level.collision_objects:
        pg.draw.rect(s, (255, 0, 0), camera.apply(o["rect"]), 2)
    for r in level.rects_of_type("platform"):
        pg.draw.rect(s, (255, 200, 0), camera.apply(r), 2)
    for r in level.rects_of_type("ladder"):
        pg.draw.rect(s, (0, 255, 255), camera.apply(r), 2)
    for p in level.paths:
        g.Path.from_tiled(p).draw(s, camera)


@shot("topdown_ai", 700, 420)
def _(s):
    level, camera, world = level_view(s, "level1.tmx", (650, 300))
    walls = [o["rect"] for o in level.collision_objects]
    player = g.SpriteObject(560, 330, 28, 28, bg=(70, 160, 230))
    ghost = g.SpriteObject(700, 330, 28, 28, bg=(230, 230, 250))
    world.add_sprite(player, ghost)
    world.draw(s)
    brain = g.Chaser(ghost, player, detect_range=220, solids=walls)
    brain.update(16)
    brain.draw_debug(s, camera)
    level.get_path("guard_route").draw(s, camera)


@shot("inventory", 680, 360)
def _(s):
    bag = g.Grid(20, 50, cols=5, rows=3, cell_size=72, bg=(50, 45, 40))
    gear = g.Grid(440, 50, cols=2, rows=2, cell_size=72, bg=(40, 50, 70))
    for (c, r), (kind, label) in {(0, 0): ("weapon", "Weapon"), (1, 0): ("shield", "Shield"),
                                  (0, 1): ("potion", "Potion"), (1, 1): ("trinket", "Trinket")}.items():
        gear.set_slot(c, r, accepts=kind, label=label)
    items = []
    for i, name in enumerate(["sword", "shield", "potion", "gem", "key"]):
        item = g.DragObject(0, 0, 56, 56, image=asset(f"item_{name}.png"), grid=[bag, gear],
                            kind={"sword": "weapon", "gem": "trinket", "key": "trinket"}.get(name, name))
        bag.place(item, i, 0)
        items.append(item)
    bag.remove(items[1])
    gear.place(items[1], 1, 0)
    text(s, "Backpack", 20, 15, 24)
    text(s, "Equipment", 440, 15, 24)
    sword = items[0]
    gear.hover_cell, gear.hover_item = (0, 0), sword
    bag.draw(s)
    gear.draw(s)
    for item in items:
        item.draw(s)
    sword.rect.center = (476, 86)
    sword.dragging = True
    sword.draw(s)


@shot("particles", 840, 300, bg=(15, 15, 30))
def _(s):
    presets = [("explosion", lambda p: g.Particles.explosion(p, scale=1.3), 5),
               ("sparks", lambda p: g.Particles.sparks(p, count=40), 4),
               ("smoke", lambda p: g.Particles.smoke(pos=(p[0], p[1] + 70), rate=25), 90),
               ("fire", lambda p: g.Particles.fire(pos=(p[0], p[1] + 60), size=1.4), 40),
               ("magic", lambda p: g.Particles.magic(pos=p, rate=80), 40),
               ("confetti", lambda p: g.Particles.confetti((p[0], p[1] + 70)), 18)]
    for i, (name, make, frames) in enumerate(presets):
        g.Particles.clear()
        make((70 + i * 140, 130))
        for _ in range(frames):
            g.Particles.update(16)
        g.Particles.draw(s)
        text(s, name, 70 + i * 140, 270, 20, center=True)


@shot("chain", 700, 300)
def _(s):
    import math
    head = g.SpriteObject(0, 0, 34, 34, bg=(230, 130, 90))
    worm = g.Chain(head, count=16, spacing=22, size=32, color=(200, 110, 70), shrink=True)
    for t in range(200):
        head.rect.center = (40 + t * 3.1, 150 + math.sin(t / 14) * 70)
        worm.update(16)
    worm.draw(s)
    head.draw(s)
    text(s, "Chain: the links follow the head along its path", 20, 268, 20)


@shot("snake", 480, 330)
def _(s):
    board = g.Grid(0, 0, cols=15, rows=10, cell_size=32, show_lines=False)
    grass = pg.image.load(asset("snake_grass.png")).convert_alpha()
    for c, r in board.all_cells():
        s.blit(grass, board.cell_rect(c, r), area=pg.Rect(((c + r) % 2) * 32, 0, 32, 32))
    snake = g.Chain(mode="grid", grid=board, head_cell=(6, 5), length=6,
                    images=asset("snake_sheet.png"))
    for d in ("up", "up", "right", "right", "right", "down"):
        snake.turn(d)
        snake.step()
    snake.draw(s)
    apple = pg.transform.scale(pg.image.load(asset("apple.png")).convert_alpha(), (32, 32))
    s.blit(apple, board.cell_rect(12, 7))


@shot("shooter", 640, 360)
def _(s):
    player = g.SpriteObject(120, 160, 32, 32, bg=(70, 160, 230))
    enemy = g.SpriteObject(470, 150, 34, 34, bg=(220, 70, 70))
    bullets = g.ProjectileGroup()
    gun = g.Shooter(bullets, cooldown=0, speed=600)
    for i in range(5):
        gun.fire(player.rect.center, target=enemy.rect.center)
        bullets.update(90 - i * 15)
    g.flash(enemy, 10000)
    player.draw(s)
    enemy.draw(s)
    bullets.draw(s)
    g.Particles.sparks(enemy.rect.midleft, count=20)
    for _ in range(6):
        g.Particles.update(16)
    g.Particles.draw(s)
    bar = g.Progressbar(20, 20, 220, thickness=20, bar_color=(80, 200, 120), show_text=True)
    hp = g.Health(100, bar=bar)
    hp.damage(35)
    bar.draw(s)
    text(s, "Health bar, bullets, hit flash and sparks", 20, 320, 20)


# ---------------------------------------------------------------- v1.1
@shot("messagebox", 560, 300)
def _(s):
    for i in range(8):                                  # something "game-like" behind
        pg.draw.circle(s, (70, 90, 160), (40 + i * 70, 60 + (i % 3) * 90), 24)
    box = g.MessageBox("Quit?", "Save the game before you quit?",
                       buttons=("Yes", "No", "Cancel"), x=280, y=150, width=400)
    box.show()
    box.draw(s)


@shot("table_spreadsheet", 520, 260)
def _(s):
    t = g.Table(20, 20, columns=["Item", "Price", "Qty"], rows=6, width=360,
                editable=["Price", "Qty"], edit_mode="spreadsheet", border_color=(255, 200, 0))
    t.column("Price", type=int, anchor="e")
    t.column("Qty", type=int, anchor="e")
    for row in [["Iron sword", 45, 1], ["Bow", 35, 2], ["Oak shield", 30, 1],
                ["Red potion", 15, 5], ["Steel helm", 75, 1]]:
        t.insert(row)
    rows = t.get_children()
    t._pick_cell(rows[2], "Price")
    t.draw(s)
    text(s, "Click a cell, then just type", 400, 40, 18)
    text(s, "Enter = down   Tab = right", 400, 70, 18)
    text(s, "Arrows move around", 400, 100, 18)


@shot("fps_debug", 640, 400)
def _(s):
    level, camera, world = level_view(s, "level1.tmx", (300, 330))
    g.Debug.on = True
    now = pg.time.get_ticks()
    world._frame_times = [now - i * 16 for i in range(59, 0, -1)]   # pretend 60 frames ran
    world.draw(s)
    g.Debug.on = False


@shot("typewriter", 560, 200)
def _(s):
    talk = g.Message(20, 60, "Hello there! Welcome to the world of pygame!", width=520,
                     bg=(250, 250, 250), fg=(30, 30, 30), padding=18, font_size=28,
                     type_speed=20)
    talk.update(1100)                                   # part-way through typing
    talk.draw(s)
    text(s, "The letters appear one at a time...", 20, 20, 20)
    text(s, "Click or press SPACE to see the rest straight away", 20, 135, 18,
         colour=(255, 200, 0))


@shot("hearts", 560, 200)
def _(s):
    health = g.Health(10)
    health.damage(3)                                    # 7 HP left = 3.5 hearts
    text(s, "Drawn hearts (no pictures needed)", 20, 12, 16)
    g.HeartsBar(20, 40, health=health, hearts=5, heart_size=40, gap=6).draw(s)
    text(s, "Your own pictures", 290, 12, 16)
    g.HeartsBar(290, 40, health=health, hearts=5, heart_size=(45, 40), gap=6,
                full_image=asset("heart_full.png"), half_image=asset("heart_half.png"),
                empty_image=asset("heart_empty.png")).draw(s)
    arrow(s, (175, 120), (160, 88))
    text(s, "half a heart = 1 HP", 150, 122, 18, colour=(255, 200, 0))
    text(s, "One heart per HP, per_row=5", 20, 150, 18)
    g.HeartsBar(290, 140, health=health, heart_size=20, per_row=5).draw(s)

@shot("floating_text", 560, 240)
def _(s):
    text(s, "Damage numbers", 20, 12, 18)
    dummy = g.SpriteObject(50, 90, 90, 100, bg=(150, 110, 70))
    dummy.draw(s)
    g.FloatingText(80, 72, 12, color="red", font_size=32).draw(s)
    g.FloatingText(125, 50, "18!", color="yellow", font_size=44).draw(s)
    coin = pg.transform.scale(pg.image.load(asset("coin.png")).convert_alpha(), (40, 40))
    s.blit(coin, (330, 150))
    for age in (0, 650, 850):                           # the same "+10" at 3 moments
        pop = g.FloatingText(350, 135, "+10", color="gold", font_size=32, speed=110)
        pop.update(age)
        pop.draw(s)
    arrow(s, (420, 140), (420, 40))
    text(s, "floats up...", 430, 100, 18, colour=(255, 200, 0))
    text(s, "...then fades out", 430, 32, 18, colour=(255, 200, 0))
    text(s, "A text particle: it needs Particles.update(tick) and Particles.draw(screen)",
         20, 210, 16)

# ======================================================================
# Newer widget options (v1.1)
# ======================================================================
# Fades, slides and animated bars use the clock. This pretend clock lets a
# picture freeze them half way.
real_get_ticks = pg.time.get_ticks
fake_clock = [0]


def use_fake_clock(on=True):
    pg.time.get_ticks = (lambda: fake_clock[0]) if on else real_get_ticks


def stripes(s, colour=(230, 230, 180), bg=(40, 90, 60)):
    """A busy background, so outlines and shadows have something to beat."""
    s.fill(bg)
    for x in range(0, s.get_width(), 60):
        pg.draw.rect(s, colour, (x, 0, 30, s.get_height()))


@shot("label_outline", 560, 220)
def _(s):
    stripes(s)
    g.Label(20, 15, "Plain: hard to read", font_size=30).draw(s)
    g.Label(20, 60, "outline=2", font_size=30, outline=2).draw(s)
    g.Label(300, 60, "shadow=True", font_size=30, fg=(255, 220, 0), shadow=True,
            shadow_offset=(3, 3)).draw(s)
    g.Label(280, 165, "Arrows move   Space jumps\nEscape = pause", font_size=24,
            outline=2, justify="center", center=True).draw(s)
    g.Label(20, 110, '"\\n" starts a new line, justify="center":', font_size=20,
            outline=2).draw(s)


@shot("textbox_extras", 560, 200)
def _(s):
    g.TextBox(20, 20, max_chars=12, label="Name:", placeholder="Your hero").draw(s)
    g.TextBox(20, 75, max_chars=12, label="Password:", show="*", text="dragon").draw(s)
    g.TextBox(20, 130, max_chars=3, label="Lucky number:", allowed="digits", text="42").draw(s)
    text(s, 'placeholder="Your hero"', 330, 28, 18, colour=(255, 200, 0))
    text(s, 'show="*"', 330, 83, 18, colour=(255, 200, 0))
    text(s, 'allowed="digits"', 330, 138, 18, colour=(255, 200, 0))


@shot("list_extras", 560, 250)
def _(s):
    text(s, 'selectmode="multiple"', 20, 10, 18, colour=(255, 200, 0))
    skills = g.Listbox(20, 40, 200, rows=6, selectmode="multiple",
                       items=["Climbing", "Cooking", "Fishing", "Magic", "Sneaking", "Swimming"])
    for i in (1, 3, 4):
        skills.selection_set(i)
    skills.draw(s)
    text(s, "editable=True (typed: wi)", 270, 10, 18, colour=(255, 200, 0))
    hero = g.Combobox(270, 40, 220, editable=True,
                      values=["Archer", "Knight", "Rogue", "Wizard", "Witch"])
    hero._open()
    for letter in "wi":
        hero._type_key(pg.event.Event(pg.KEYDOWN, key=ord(letter), unicode=letter, mod=0))
    hero.draw(s)
    hero.draw_overlay(s)


@shot("askstring", 640, 360)
def _(s):
    for i in range(12):
        pg.draw.circle(s, (60 + i * 10, 120, 200), (random.randint(0, 640), random.randint(0, 360)), 30)
    box = g.askstring("High score!", "Type your name:", initialvalue="Sam", x=320, y=180)
    box.draw(s)


@shot("progressbar_extras", 560, 190)
def _(s):
    use_fake_clock()
    try:
        g.Label(20, 10, 'low_color: red when nearly empty').draw(s)
        g.Progressbar(20, 40, 300, thickness=26, value=20, show_text=True,
                      low_color=(230, 50, 50), low_at=0.25).draw(s)
        g.Label(20, 95, 'animate=True: the lost part fades away').draw(s)
        bar = g.Progressbar(20, 125, 300, thickness=26, value=80, animate=True)
        fake_clock[0] = 1000
        bar.draw(s)
        bar.config(value=45)                         # ouch!
        fake_clock[0] = 1100
        bar.draw(s)
        arrow(s, (420, 165), (275, 140))
        text(s, '"ghost" of the', 425, 140, 18, colour=(255, 200, 0))
        text(s, "health you lost", 425, 160, 18, colour=(255, 200, 0))
    finally:
        use_fake_clock(False)


@shot("fade_slide", 600, 300)
def _(s):
    use_fake_clock()
    try:
        stripes(s, colour=(60, 120, 80))
        fake_clock[0] = 0
        title = g.Label(-300, 20, "Level 1", font_size=56, outline=3, fg=(255, 220, 0))
        title.slide_to(330, 20, ms=900)
        menu = g.Frame(150, 100, 300, 170, bg=(50, 50, 80), border_color=(200, 200, 255),
                       visible=False)
        menu.add(g.Label(150, 20, "Paused", font_size=40, center=True),
                 g.Button(50, 60, 200, 50, "Resume"))
        fake_clock[0] = 300
        menu.show(fade_ms=400)
        fake_clock[0] = 500            # the fade is half way, the slide is part way
        title.draw(s)
        arrow(s, (10, 50), (title.x - 10, 50))
        menu.draw(s)
        text(s, "slide_to(330, 20, ms=900)", 20, 80, 18, colour=(255, 255, 255), bold=True)
        text(s, "show(fade_ms=400): half way", 160, 275, 18, colour=(255, 255, 255), bold=True)
    finally:
        use_fake_clock(False)


@shot("enemy_bars", 560, 230)
def _(s):
    use_fake_clock()
    try:
        s.fill((60, 100, 60))
        fake_clock[0] = 1000
        enemies = []
        for i, hp in enumerate((30, 18, 6)):
            enemy = g.SpriteObject(60 + i * 170, 110, 60, 60, bg=(220, 70, 70))
            enemy.health = g.Health(30)
            enemy.health.draw_bar(s.copy(), enemy, low_color=(230, 50, 50), animate=True)
            enemy.health.damage(30 - hp)
            enemies.append(enemy)
        fake_clock[0] = 1100
        for enemy in enemies:
            enemy.draw(s)
            enemy.health.draw_bar(s, enemy, low_color=(230, 50, 50), animate=True)
        text(s, "health.draw_bar(screen, enemy, camera)", 20, 15, 20, bold=True)
        text(s, "full", 75, 185, 18)
        text(s, "hurt (the ghost fades)", 190, 185, 18)
        text(s, "nearly dead: red", 400, 185, 18)
    finally:
        use_fake_clock(False)


print()
print(f"Made {len(made)} pictures in {OUT}")
if failed:
    print(f"{len(failed)} FAILED: {', '.join(failed)}  (send these errors to Claude)")
pg.quit()
