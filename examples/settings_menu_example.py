"""
Settings menu example - a game with a pause menu.

Shows: Notebook (tabs), LabelFrame, Separator, Variables shared between the
menu and the game, FocusGroup for keyboard control of the menu, and the
Volume slider / sound tick box really controlling the music (Audio.link).

Arrow keys move the player. ESCAPE opens / closes the menu.
While the menu is open, the arrow keys move between widgets instead
(Enter / Space to press) - the FocusGroup only uses keys while it is active,
so it never fights with the game's controls.
"""
import os
import sys
import pygame as pg

# Lets this example find the library one folder up.
# In your own game, just put PygameTkinterGUITools.py next to your game file.
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from PygameTkinterGUITools import (Notebook, LabelFrame, Separator, Label, Button,
                                   Checkbutton, Radiobutton, Scale, Spinbox, Combobox,
                                   TextBox, FocusGroup, IntVar, StringVar, BooleanVar,
                                   Audio, Music, init_audio)

# ---------- Settings ----------
MUSIC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "sounds",
                     "music_menu.wav")
WIDTH, HEIGHT = 800, 600
FPS = 60
SPEEDS = {"Slow": 150, "Normal": 300, "Fast": 500}
COLOURS = {"Blue": (70, 160, 230), "Red": (230, 70, 70), "Green": (70, 200, 100)}


def toggle_menu():
    menu.toggle_visibility()
    menu_focus.active = menu.visible        # keyboard focus only while the menu is open


def init_pygame():
    """Set up pygame, the window, the clock and all game objects."""
    global screen, clock, player, menu, menu_focus, hint
    global volume, show_trail, speed, size, colour, name, trail, sound_on
    init_audio()                         # BEFORE pg.init()
    pg.init()
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    pg.display.set_caption("Settings menu example")
    clock = pg.time.Clock()

    # >>> Create objects here (after pg.init)
    # Variables shared by the menu and the game
    volume = IntVar(70)
    show_trail = BooleanVar(True)
    speed = StringVar("Normal")
    size = IntVar(40)
    colour = StringVar("Blue")
    name = StringVar("Player 1")
    sound_on = BooleanVar(True)

    # The volume slider and sound tick box control the real volume
    Audio.link(music_volume=volume)
    sound_on.trace_add("write", lambda: Audio.set_muted(not sound_on.get()))
    Music.play(MUSIC)

    player = pg.Rect(380, 280, 40, 40)
    trail = []
    hint = Label(10, 10, "Arrows = move   ESC = menu")

    # The menu: a Notebook with three tabs
    menu = Notebook(WIDTH // 2, HEIGHT // 2, 460, 380, center=True, visible=False)

    sound = menu.new_tab("Sound")
    volume_slider = Scale(10, 10, from_=0, to=100, length=400, variable=volume,
                          label="Volume")
    trail_check = Checkbutton(10, 90, "Show trail", variable=show_trail)
    sound_check = Checkbutton(10, 160, "Sound on", variable=sound_on)
    sound.add(volume_slider, trail_check, Separator(10, 140, length=400), sound_check)

    game = menu.new_tab("Game")
    speed_group = LabelFrame(10, 10, 200, 160, "Speed")
    slow = Radiobutton(0, 0, "Slow", variable=speed, value="Slow")
    normal = Radiobutton(0, 35, "Normal", variable=speed, value="Normal")
    fast = Radiobutton(0, 70, "Fast", variable=speed, value="Fast")
    speed_group.add(slow, normal, fast)
    size_box = Spinbox(240, 40, from_=20, to=80, increment=10, variable=size)
    game.add(speed_group, Label(240, 10, "Size"), size_box)

    player_tab = menu.new_tab("Player")
    name_box = TextBox(10, 10, max_chars=14, label="Name:", textvariable=name)
    colour_box = Combobox(10, 70, 200, values=list(COLOURS), textvariable=colour)
    player_tab.add(name_box, colour_box)

    close = Button(330, 290, 100, 40, "Close", command=toggle_menu, font_size=24)
    sound.add(close)

    # Keyboard control: the widgets in the order the arrow keys move through them.
    # Widgets on hidden tabs are skipped automatically.
    menu_focus = FocusGroup(menu, volume_slider, trail_check, sound_check, close,
                            slow, normal, fast, size_box, name_box, colour_box,
                            keys="arrows")


def handle_inputs():
    """Check every event: quitting, keys, mouse, controllers."""
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            sys.exit()

        if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
            toggle_menu()
            continue

        # >>> Objects that react to events go here
        # The menu gets the event first. If it used it, the game doesn't.
        if menu_focus.handle_event(event):
            continue
        menu.handle_event(event)


def update(tick):
    """Move, animate and check things."""
    # >>> Objects with update(tick) go here
    menu.update(tick)
    if menu.visible:
        return                          # game is paused while the menu is open

    keys = pg.key.get_pressed()         # game controls only run when the menu is closed
    step = SPEEDS[speed.get()] * tick / 1000
    player.x += int((keys[pg.K_RIGHT] - keys[pg.K_LEFT]) * step)
    player.y += int((keys[pg.K_DOWN] - keys[pg.K_UP]) * step)
    player.size = (size.get(), size.get())
    player.clamp_ip(screen.get_rect())

    trail.append(player.center)
    del trail[:-30]


def draw_game():
    """Draw everything, then show it."""
    screen.fill((30, 30, 30))

    # >>> Objects with draw(screen) go here
    if show_trail.get() and len(trail) > 1:
        pg.draw.lines(screen, (90, 90, 90), False, trail, 4)
    pg.draw.rect(screen, COLOURS[colour.get()], player, border_radius=8)
    Label(player.x, player.y - 26, name.get(), font_size=22).draw(screen)
    hint.draw(screen)
    Label(10, 40, f"Volume: {volume.get()}").draw(screen)
    menu.draw(screen)

    pg.display.flip()


# ---------- Main program ----------
init_pygame()
while True:
    tick = clock.tick(FPS)   # tick = milliseconds since the last frame (used for animation)
    handle_inputs()
    update(tick)
    draw_game()
