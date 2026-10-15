"""
Automatic checks for ScrolledFrame, Table, Menu, particles and Chain.

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


def click(pos, button=1):
    return pg.event.Event(pg.MOUSEBUTTONDOWN, button=button, pos=pos)


def key(k, mod=0, unicode=""):
    return pg.event.Event(pg.KEYDOWN, key=k, mod=mod, unicode=unicode)


clock_ms = [50000]
real_ticks = pg.time.get_ticks
pg.time.get_ticks = lambda: clock_ms[0]
real_mouse = pg.mouse.get_pos

# ---------- ScrolledFrame ----------
sf = g.ScrolledFrame(100, 100, width=200, height=150, pad_x=0, pad_y=0)
hits = []
buttons = [g.Button(sf, text=f"B{n}", width=150, height=30,
                    command=lambda n=n: hits.append(n)).grid(row=n, column=0) for n in range(20)]
sf.draw(screen)
check("Content is taller than the frame", sf.content_h == 600)
check("Starts at the top", sf.scroll_y == 0)
pg.mouse.get_pos = lambda: (150, 150)
sf.handle_event(pg.event.Event(pg.MOUSEWHEEL, x=0, y=-1))
check("Mouse wheel scrolls down", sf.scroll_y == 40)
sf.scroll_to_bottom()
check("Can't scroll past the end", sf.scroll_y == sf.content_h - sf._viewport().height)
sf.scroll_to_top()
inside = sf.child_offset()
b5 = buttons[5].get_rect(inside)
sf.handle_event(click(b5.center))
check("Widgets below the visible part can't be clicked", hits == [])
sf.see(buttons[5])
sf.draw(screen)
b5 = buttons[5].get_rect(sf.child_offset())
sf.handle_event(click(b5.center))
check("see() scrolls to a widget, which can then be clicked", hits == [5])
(track, thumb), _ = sf._bars()
before = sf.scroll_y
sf.handle_event(click(thumb.center))
sf.handle_event(pg.event.Event(pg.MOUSEMOTION, pos=(thumb.centerx, thumb.centery + 40),
                               rel=(0, 40), buttons=(1, 0, 0)))
sf.handle_event(pg.event.Event(pg.MOUSEBUTTONUP, button=1, pos=(thumb.centerx, thumb.centery + 40)))
check("Dragging the scroll bar scrolls", sf.scroll_y > before)
focus = g.FocusGroup(*buttons, active=True)
for _ in range(15):
    focus.handle_event(key(pg.K_DOWN))
check("Keyboard focus scrolls to the focused widget",
      sf.scroll_y >= buttons[15].get_rect().bottom - sf._viewport().height)
g.Debug.on = True
sf.draw(screen)
g.Debug.on = False

# ---------- Table ----------
t = g.Table(0, 0, columns=["Name", "Score"], rows=4, editable=["Score"])
t.column("Score", type=int, anchor="e")
for name, score in [("Cat", 30), ("Ann", 120), ("Bob", 5), ("Dee", 70), ("Eve", 50)]:
    t.insert([name, score])
t.draw(screen)
check("insert / all_rows", len(t.all_rows()) == 5)
t.sort_by("Score", reverse=True)
check("sort_by numbers", [r[1] for r in t.all_rows()] == [120, 70, 50, 30, 5])
t.sort_by("Name")
check("sort_by text", [r[0] for r in t.all_rows()] == ["Ann", "Bob", "Cat", "Dee", "Eve"])
r, widths, xs = t._table_layout()
row_h = t._row_height()
heading_score = (xs[1] + 10, r.y + 2 + row_h // 2)
t.handle_event(click(heading_score))
check("Clicking a heading sorts by it", t.sorted_by == ("Score", False))
t.handle_event(click(heading_score))
check("Clicking again reverses", t.sorted_by == ("Score", True))
chosen = []
t.command = lambda: chosen.append(t.get_selected())
first_row = (xs[0] + 10, r.y + 2 + row_h + row_h // 2)
t.handle_event(click(first_row))
check("Click a row to select it", t.get_selected() == ["Ann", 120] and chosen)
score_cell = (xs[1] + 10, first_row[1])
t.handle_event(click(score_cell))
clock_ms[0] += 200
t.handle_event(click(score_cell))
check("Double-click an editable cell starts editing", t.editing is not None)
t.handle_event(key(pg.K_BACKSPACE)); t.handle_event(key(pg.K_BACKSPACE)); t.handle_event(key(pg.K_BACKSPACE))
for ch in "99":
    t.handle_event(key(ord(ch), unicode=ch))
edits = []
t.on_edit = lambda: edits.append(t.last_edit)
t.handle_event(key(pg.K_RETURN))
check("Enter saves the edit (as an int)", t.get_selected() == ["Ann", 99] and edits)
t.start_edit(t.selection(), "Score")
for ch in "x":
    t.handle_event(key(ord(ch), unicode=ch))
t.handle_event(key(pg.K_RETURN))
check("type=int refuses letters (stays editing with an error)", t.editing and t.edit_error)
t.handle_event(key(pg.K_ESCAPE))
check("Escape cancels", t.editing is None and t.get_selected()[1] == 99)
check("Non-editable column can't be edited", not t.start_edit(t.selection(), "Name"))
clock_ms[0] += 1000
t.handle_event(click((xs[0] + 10, first_row[1])))
clock_ms[0] += 100
t.handle_event(click((xs[0] + 10, first_row[1])))
check("Double-click on a non-editable cell doesn't edit", t.editing is None)
t.delete(t.selection())
check("delete()", len(t.all_rows()) == 4)

tree = g.Table(0, 0, columns=["Level", "Done"], rows=6, tree=True)
w1 = tree.insert(["World 1", ""], open=True)
w2 = tree.insert(["World 2", ""])
for n in range(3):
    tree.insert([f"1-{n}", "yes"], parent=w1)
    tree.insert([f"2-{n}", ""], parent=w2)
check("Tree: closed folders hide their rows", len(tree._visible_rows()) == 5)
tree.draw(screen)
r, widths, xs = tree._table_layout()
rows = tree._visible_rows()
w2_line = rows.index((w2, 0))
arrow = (xs[0] + 8, r.y + 2 + (w2_line + 1) * tree._row_height() + tree._row_height() // 2)
tree.handle_event(click(arrow))
check("Tree: clicking the arrow opens a folder", tree.items[w2]["open"]
      and len(tree._visible_rows()) == 8)
tree.selection_set(tree.get_children(w2)[0])
tree.focus_action("left")
check("Tree: keyboard down / left / right work", True)
long_table = g.Table(0, 0, columns=["N"], rows=4)
for n in range(20):
    long_table.insert([n])
long_table.draw(screen)
track, thumb = long_table._table_scrollbar(long_table.get_rect())
long_table.handle_event(click((track.centerx, track.bottom - 3)))
check("Table: clicking the scroll bar below the handle jumps down", long_table.scroll == 4)
track, thumb = long_table._table_scrollbar(long_table.get_rect())
long_table.handle_event(click(thumb.center))
long_table.handle_event(pg.event.Event(pg.MOUSEMOTION, pos=(thumb.centerx, track.bottom),
                                       rel=(0, 0), buttons=(1, 0, 0)))
long_table.handle_event(pg.event.Event(pg.MOUSEBUTTONUP, button=1, pos=(thumb.centerx, track.bottom)))
check("Table: dragging the scroll bar handle scrolls", long_table.scroll == 16)
lb = g.Listbox(0, 0, 200, rows=3, items=list(range(12)))
lb.draw(screen)
track, thumb = lb._list_scrollbar(lb.get_rect())
lb.handle_event(click(thumb.center))
lb.handle_event(pg.event.Event(pg.MOUSEMOTION, pos=(thumb.centerx, track.bottom),
                               rel=(0, 0), buttons=(1, 0, 0)))
lb.handle_event(pg.event.Event(pg.MOUSEBUTTONUP, button=1, pos=(thumb.centerx, track.bottom)))
check("Listbox: dragging the scroll bar handle scrolls", lb.scroll == 9 and lb.selected is None)
tree.load([["a", 1], ["b", 2]])
check("load() replaces everything", len(tree.all_rows()) == 2)

# ---------- Menu ----------
screen_root = g.Root(screen)
did = []
music = g.BooleanVar(False)
level = g.StringVar("Easy")
menubar = g.Menu(screen_root)
file_menu = g.Menu(menubar)
file_menu.add_command(label="New", command=lambda: did.append("new"), accelerator="Ctrl+N")
file_menu.add_command(label="Export", command=lambda: did.append("export"), state="disabled")
file_menu.add_separator()
options = g.Menu(file_menu)
options.add_checkbutton(label="Music", variable=music)
options.add_radiobutton(label="Hard", variable=level, value="Hard")
file_menu.add_cascade(label="Options", menu=options)
menubar.add_cascade(label="File", menu=file_menu)
screen_root.config(menu=menubar)
check("root.config(menu=) makes a menu bar and leaves room for it",
      menubar.is_bar and screen_root.top_space == menubar.bar_height())
under = []
b = g.Button(screen_root, text="Under", width=200, height=200, command=lambda: under.append(1))
b.place(x=0, y=0)
screen_root.draw(screen)
file_item = menubar._bar_items()[0]
screen_root.handle_event(click(file_item.center))
check("Clicking a bar item opens its menu", menubar.is_open)
screen_root.draw(screen)
rect = menubar._chain[0]["rect"]
items = file_menu._item_rects(rect)
screen_root.handle_event(click(items[1].center))
check("Disabled items do nothing", "export" not in did and menubar.is_open)
screen_root.handle_event(click(items[0].center))
check("Clicking an item runs it and closes the menu", did == ["new"] and not menubar.is_open)
check("...and the click didn't reach the button underneath", under == [])
screen_root.handle_event(key(pg.K_n, mod=pg.KMOD_CTRL))
check("Accelerator Ctrl+N works", did == ["new", "new"])
screen_root.handle_event(key(pg.K_n))
check("N without Ctrl doesn't", did == ["new", "new"])
screen_root.handle_event(click(file_item.center))
rect = menubar._chain[0]["rect"]
items = file_menu._item_rects(rect)
screen_root.handle_event(pg.event.Event(pg.MOUSEMOTION, pos=items[3].center, rel=(0, 0),
                                        buttons=(0, 0, 0)))
check("Hovering a cascade opens the sub-menu", len(menubar._chain) == 2)
sub_items = options._item_rects(menubar._chain[1]["rect"])
screen_root.handle_event(click(sub_items[0].center))
check("Check item toggles its variable", music.get() is True)
screen_root.handle_event(click(file_item.center))
screen_root.handle_event(click((700, 500)))
check("Clicking elsewhere closes the menu (and doesn't click the game)", not menubar.is_open)
screen_root.draw(screen)

context = g.Menu()
context.add_command(label="Delete", command=lambda: did.append("delete"))
context.post(300, 300)
context.draw(screen)
check("post() opens a right-click menu", context.is_open)
context.handle_event(key(pg.K_ESCAPE))
check("Escape closes it", not context.is_open)
context.post(300, 300)
context.handle_event(key(pg.K_DOWN))
context.handle_event(key(pg.K_RETURN))
check("Keyboard: down + Enter chooses", did[-1] == "delete")

# ---------- Particles ----------
g.Particles.clear()
e = g.ParticleEmitter((100, 100), rate=100, lifetime=500, speed=50)
for _ in range(10):
    g.Particles.update(16)
check("Emitter makes particles at its rate (~16)", 12 <= e.count <= 18)
e.stop()
for _ in range(40):
    g.Particles.update(16)
check("Particles disappear after their lifetime", e.count == 0)
check("A stopped emitter stays until removed", e in g.Particles.emitters)
e.remove()
boom = g.Particles.explosion((300, 300))
check("explosion makes particles", g.Particles.count() > 30)
for _ in range(120):
    g.Particles.update(16)
check("One-off effects remove themselves when done", g.Particles.count() == 0
      and not g.Particles.emitters)
grav = g.ParticleEmitter((0, 0), rate=0, lifetime=2000, speed=0, gravity=500)
grav.burst(1)
grav.update(500)
check("Gravity pulls particles down", grav.particles[0][1] > 0)
floor = g.ParticleEmitter((0, 0), rate=0, lifetime=5000, speed=0, gravity=1000, floor=50)
floor.burst(1)
for _ in range(30):
    floor.update(16)
check("Particles bounce on a floor", floor.particles[0][1] <= 50)
cap = g.ParticleEmitter((0, 0), rate=0, max_particles=20)
cap.burst(100)
check("max_particles limits the count", cap.count == 20)
target = g.SpriteObject(400, 400, 10, 10)
follow = g.ParticleEmitter(follow=target, rate=0, speed=0, lifetime=1000)
follow.burst(1)
check("follow= starts particles at the sprite", abs(follow.particles[0][0] - 405) < 1)
g.Debug.on = True
for preset in (lambda: g.Particles.sparks((50, 50)), lambda: g.Particles.dust((50, 50)),
               lambda: g.Particles.confetti((50, 50)), lambda: g.Particles.smoke((50, 50)),
               lambda: g.Particles.fire((50, 50)), lambda: g.Particles.rain(screen.get_rect()),
               lambda: g.Particles.snow(screen.get_rect()), lambda: g.Particles.magic((50, 50)),
               lambda: g.Particles.trail(target)):
    preset()
for _ in range(20):
    g.Particles.update(16)
g.Particles.draw(screen)
img = g.ParticleEmitter((10, 10), rate=0, shape=os.path.join(ASSETS, "coin.png"), spin=90)
img.burst(5)
img.update(16)
img.draw(screen)
check("Every preset (and image particles) updates and draws", True)
g.Debug.on = False
g.Particles.clear()

# ---------- Chain: path mode ----------
leader = g.SpriteObject(400, 300, 20, 20)
worm = g.Chain(leader, count=5, spacing=20)
for _ in range(60):
    leader.move(3, 0)
    worm.update(16)
gaps = [abs(worm.segments[i].rect.centerx - worm.segments[i + 1].rect.centerx)
        for i in range(4)]
check("Links stay 'spacing' apart along the path", all(abs(gap - 20) <= 2 for gap in gaps))
check("First link is behind the leader", leader.rect.centerx - worm.segments[0].rect.centerx in range(18, 23))
for _ in range(30):
    leader.move(0, 3)
    worm.update(16)
check("Links follow the path round a corner",
      worm.segments[0].rect.centerx == leader.rect.centerx and
      worm.segments[-1].rect.centery < worm.segments[0].rect.centery)
sprite = g.SpriteObject(0, 0, 16, 16)
worm.attach(sprite)
worm.update(16)
check("attach() adds any sprite to the end", worm.segments[-1] is sprite and len(worm) == 6)
worm.detach(sprite)
worm.shrink_by(2)
check("detach() / shrink_by()", len(worm) == 3)
check("touching()", worm.touching(worm.segments[1].rect) is worm.segments[1])

slow = g.Chain(leader, count=2, delay_ms=200)
start = pg.Vector2(leader.rect.center)
for _ in range(30):
    clock_ms[0] += 16
    leader.move(2, 0)
    slow.update(16)
check("delay_ms: follows behind by time", slow.segments[0].rect.centerx < leader.rect.centerx)
worm.draw(screen)
g.Chain(leader, count=4, image=os.path.join(ASSETS, "coin.png"), fade=True, shrink=True).draw(screen)

# ---------- Chain: grid mode (Snake) ----------
board = g.Grid(0, 0, cols=10, rows=8, cell_size=20)
snake = g.Chain(mode="grid", grid=board, head_cell=(4, 4), length=3, move_every=100)
check("Grid chain starts with its length", snake.cells == [(4, 4), (3, 4), (2, 4)])
snake.update(100)
check("Moves one cell every move_every ms", snake.head_cell == (5, 4) and snake.moved)
snake.update(50)
check("...and not before", snake.head_cell == (5, 4) and not snake.moved)
snake.turn("left")
check("Can't turn straight back into itself", snake._queue == [])
snake.turn("up")
snake.turn("left")
snake.update(50); snake.update(100)
check("Quick turns are queued (both count)", snake.head_cell == (4, 3))
snake.grow(2)
snake.update(100); snake.update(100)
check("grow() adds cells as it moves", len(snake) == 5)
check("free_cells / occupies", snake.occupies(snake.head_cell)
      and snake.head_cell not in snake.free_cells())
loop = g.Chain(mode="grid", grid=board, head_cell=(5, 5), length=5)
for d in ("up", "left", "down"):
    loop.turn(d)
    loop.step()
check("hits_self()", loop.hits_self())
edge = g.Chain(mode="grid", grid=board, head_cell=(9, 0), length=2)
edge.step()
check("hits_wall() when it leaves the grid", edge.hits_wall())
wrap = g.Chain(mode="grid", grid=board, head_cell=(9, 0), length=2, wrap=True)
wrap.step()
check("wrap=True comes out the other side", wrap.head_cell == (0, 0) and not wrap.hits_wall())
pretty = g.Chain(mode="grid", grid=board, head_cell=(5, 5), length=4,
                 images=os.path.join(ASSETS, "snake_sheet.png"))
pretty.turn("up"); pretty.step(); pretty.turn("left"); pretty.step()
pretty.draw(screen)
snake.draw(screen)
check("Grid chain draws with images and with colours", pretty.pieces is not None)

pg.time.get_ticks = real_ticks
pg.mouse.get_pos = real_mouse
print()
print("ALL TESTS PASS" if all(results) else f"{results.count(False)} TEST(S) FAILED")
pg.quit()
