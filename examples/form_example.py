"""
Form example - a "make your character" form.

Shows the newer form options:
  TextBox    placeholder=, show="*" (password), allowed="digits", on_change=
  Combobox   editable=True (type to search the list)
  Listbox    selectmode="multiple" (choose several)
  Button     active_bg= (pressed colour), sound=, repeatdelay= / repeatinterval=
             (hold + or - to keep counting)
  askstring() / askinteger() - question boxes the player types into
"""
import os
import sys
import pygame as pg

# Lets this example find the library one folder up.
# In your own game, just put PygameTkinterGUITools.py next to your game file.
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from PygameTkinterGUITools import (TextBox, Button, Label, Combobox, Listbox,
                                   askstring, askinteger, init_audio)

# ---------- Settings ----------
WIDTH, HEIGHT = 800, 600
FPS = 60
HERE = os.path.dirname(os.path.abspath(__file__))
CLICK = os.path.join(HERE, "assets", "sounds", "click.wav")

HEROES = ["Archer", "Bard", "Cleric", "Druid", "Knight", "Monk", "Paladin",
          "Ranger", "Rogue", "Wizard", "Witch"]
SKILLS = ["Climbing", "Cooking", "Fishing", "Magic", "Sneaking", "Swimming"]

level = 1
question = None          # the question box that is open (or None)


# ---------- Button and box functions ----------
def name_changed():
    """Runs every time the name changes (on_change)."""
    letters_left = name_box.max_chars - len(name_box.get())
    name_help.config(text=f"{letters_left} letters left")


def level_up():
    global level
    level = min(99, level + 1)
    level_label.config(text=f"Level: {level}")


def level_down():
    global level
    level = max(1, level - 1)
    level_label.config(text=f"Level: {level}")


def got_nickname(nickname):              # the typed text, or None for Cancel
    if nickname:
        result.config(text=f"Nickname: {nickname}")


def got_age(age):                        # a whole number, or None for Cancel
    if age is not None:
        result.config(text=f"Age: {age}")


def ask_nickname():
    global question
    question = askstring("Nickname", "What do your friends call you?",
                         command=got_nickname, max_chars=12)


def ask_age():
    global question
    question = askinteger("Age", "How old is your hero?", command=got_age,
                          minvalue=10, maxvalue=500)


def show_summary():
    skills = ", ".join(skills_list.get_all_selected()) or "no skills"
    result.config(text=f"{name_box.get() or '???'} the {hero_box.get()}, "
                       f"level {level}, {skills}")


def init_pygame():
    """Set up pygame, the window, the clock and all game objects."""
    global screen, clock, name_box, name_help, password_box, age_box, hero_box
    global hero_title, skills_title, skills_list, level_label, plus_button, minus_button, buttons, result
    init_audio()                       # sound setup - BEFORE pg.init()
    pg.init()
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    pg.display.set_caption("Form example")
    clock = pg.time.Clock()

    # >>> Create objects here (after pg.init)
    name_box = TextBox(30, 30, max_chars=12, label="Name:", placeholder="Your hero",
                       on_change=name_changed)
    name_help = Label(140, 75, "12 letters left", font_size=20)
    password_box = TextBox(30, 110, max_chars=12, label="Password:", show="*",
                           placeholder="secret")
    age_box = TextBox(30, 170, max_chars=3, label="Lucky number:", allowed="digits",
                      placeholder="0-999")

    hero_title = Label(480, 10, "Hero (type to search):", font_size=22)
    hero_box = Combobox(480, 40, 220, values=HEROES, editable=True)
    skills_title = Label(480, 95, "Skills (choose several):", font_size=22)
    skills_list = Listbox(480, 120, 220, rows=6, items=SKILLS, selectmode="multiple")

    level_label = Label(30, 250, "Level: 1", font_size=32)
    minus_button = Button(200, 245, 50, 45, "-", command=level_down, sound=CLICK,
                          active_bg=(40, 80, 180), repeatdelay=400, repeatinterval=80)
    plus_button = Button(260, 245, 50, 45, "+", command=level_up, sound=CLICK,
                         active_bg=(40, 80, 180), repeatdelay=400, repeatinterval=80)

    buttons = [minus_button, plus_button,
               Button(30, 330, 200, 45, "Ask nickname", command=ask_nickname,
                      active_bg=(40, 80, 180)),
               Button(250, 330, 200, 45, "Ask age", command=ask_age,
                      active_bg=(40, 80, 180)),
               Button(470, 330, 200, 45, "Done", command=show_summary,
                      active_bg=(40, 80, 180), sound=CLICK)]
    result = Label(30, 420, "Fill in the form, then press Done", font_size=26,
                   outline=2)


def handle_inputs():
    """Check every event: quitting, keys, mouse, controllers."""
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            sys.exit()

        # >>> Objects that react to events go here
        # An open question box goes FIRST and takes every key and click
        if question is not None and question.visible:
            question.handle_event(event)
            continue
        # An open drop-down list is on top, so it gets events first too
        if hero_box.handle_event(event):
            continue
        name_box.handle_event(event)
        password_box.handle_event(event)
        age_box.handle_event(event)
        skills_list.handle_event(event)
        for button in buttons:
            button.handle_event(event)


def update(tick):
    """Move, animate and check things."""
    # >>> Objects with update(tick) go here
    name_box.update(tick)              # makes the cursor blink
    password_box.update(tick)
    age_box.update(tick)
    plus_button.update(tick)           # repeats while + is held down
    minus_button.update(tick)
    if question is not None:
        question.update(tick)


def draw_game():
    """Draw everything, then show it."""
    screen.fill((30, 30, 40))

    # >>> Objects with draw(screen) go here
    name_box.draw(screen)
    name_help.draw(screen)
    password_box.draw(screen)
    age_box.draw(screen)
    hero_title.draw(screen)
    skills_title.draw(screen)
    skills_list.draw(screen)
    level_label.draw(screen)
    for button in buttons:
        button.draw(screen)
    result.draw(screen)
    hero_box.draw(screen)              # after the widgets below it, so its list is on top
    if question is not None:
        question.draw(screen)          # question boxes LAST, so they are on top

    pg.display.flip()


# ---------- Main program ----------
init_pygame()
while True:
    tick = clock.tick(FPS)   # tick = milliseconds since the last frame (used for animation)
    handle_inputs()
    update(tick)
    draw_game()
