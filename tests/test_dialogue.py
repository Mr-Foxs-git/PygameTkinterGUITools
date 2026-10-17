"""
Automatic checks for Dialogue (conversations with names, portraits and choices).

Run this file in Visual Studio (right-click > Start without Debugging).
"""
import io
import json
import os
import sys
import tempfile
from contextlib import redirect_stdout

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"          # no sound plays while testing
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))

import pygame as pg
pg.init()
screen = pg.display.set_mode((800, 600))

import PygameTkinterGUITools as g

results = []


def check(name, condition):
    results.append(bool(condition))
    print(("PASS  " if condition else "FAIL  ") + name)


def click(pos=(400, 500), button=1):
    return pg.event.Event(pg.MOUSEBUTTONDOWN, button=button, pos=pos)


def key(k):
    return pg.event.Event(pg.KEYDOWN, key=k, unicode="", mod=0)


def warnings_from(make):
    """Run make() and return everything it printed (the warnings)."""
    printed = io.StringIO()
    with redirect_stdout(printed):
        result = make()
    return result, printed.getvalue()


def finish(talk):
    """Show the rest of the line straight away (like a first click)."""
    if talk.text.typing:
        talk.next()


WIZARD = {
    "start": [
        {"speaker": "Wizard", "text": "Hello, traveller!"},
        "Will you take this sword?",
        {"text": "Well?", "choices": [["Yes please", "take"],
                                      ["No thanks", "refuse"],
                                      ["Show me magic", "magic", {"if": "knows_magic"}]]},
    ],
    "take": [
        {"text": "Use it wisely!", "set": {"has_sword": True}, "do": "give_sword"},
    ],
    "refuse": [
        {"speaker": None, "text": "The wizard looks sad.", "goto": "again"},
    ],
    "again": [
        {"speaker": "Wizard", "text": "Come back any time."},
    ],
    "magic": ["Ta-da!"],
}

given = []
ended = []
talk = g.Dialogue(20, 400, 760, 180, script=WIZARD, type_speed=10,
                  actions={"give_sword": lambda: given.append("sword")},
                  on_end=lambda: ended.append(True))

# ---------- Starting ----------
check("starts hidden (not talking)", not talk.talking and not talk.visible)
check("handle_event does nothing while hidden", talk.handle_event(click()) is False)
talk.start()
check("start() opens the 'start' part", talk.talking and talk.part == "start"
      and talk.line == 0)
check("the first line has its speaker", talk._speaker == "Wizard")
talk.update(500)
check("text types out (10 letters per second, 500 ms = 5 letters)",
      talk.text._letters_shown() == 5 and talk.text.typing)

# ---------- Clicks and keys ----------
check("first click is used and finishes the typing",
      talk.handle_event(click()) is True and not talk.text.typing and talk.line == 0)
check("second click goes to the next line", talk.handle_event(click()) and talk.line == 1)
check("a plain string line keeps the speaker", talk._speaker == "Wizard"
      and talk.text.text == "Will you take this sword?")
check("Space also works (finish typing)", talk.handle_event(key(pg.K_SPACE))
      and not talk.text.typing)
check("other keys are left for the game", talk.handle_event(key(pg.K_ESCAPE)) is False
      and talk.handle_event(key(pg.K_a)) is False)
check("right clicks are used up but don't move on",
      talk.handle_event(click(button=3)) is True and talk.line == 1)
talk.handle_event(key(pg.K_RETURN))
check("Enter goes to the next line", talk.line == 2)

# ---------- Choices ----------
check("choices hide until the line has typed out", not talk._choices_showing())
finish(talk)
talk.draw(screen)
check("choices show once typed", talk._choices_showing())
check("'if' hides a choice until its flag is True",
      [b.text for b in talk._buttons] == ["Yes please", "No thanks"])
check("all choice buttons are the same width",
      len({b.width for b in talk._buttons}) == 1)
check("choices sit above the box", all(b.rect.bottom <= talk.rect.top
                                       for b in talk._buttons))
talk.next()
check("next() doesn't skip past the choices", talk.line == 2 and talk.talking)
check("a click away from the choices is used up but does nothing",
      talk.handle_event(click((5, 5))) and talk.part == "start")
talk.handle_event(key(pg.K_DOWN))
check("Down moves to the second choice", talk._buttons[1].focused)
talk.handle_event(key(pg.K_RETURN))
check("Enter picks it and jumps to that part", talk.part == "refuse")
check("speaker None = no name (narrator)", talk._speaker is None)
finish(talk)
talk.next()
check("goto jumps to another part", talk.part == "again" and talk._speaker == "Wizard")
finish(talk)
talk.next()
check("running out of lines ends it", not talk.talking and talk.part is None)
check("on_end runs once", ended == [True])
talk.stop()
check("stop() when already stopped doesn't run on_end again", ended == [True])

# Clicking a choice, set and do
talk.start()
for _ in range(4):
    finish(talk)
    talk.next()
finish(talk)
talk.draw(screen)
first = talk._buttons[0].rect
check("clicking a choice button picks it", talk.handle_event(click(first.center))
      and talk.part == "take")
check("'set' sets a flag", talk.flags == {"has_sword": True})
check("'do' runs the action", given == ["sword"])

# choose(), "end" and flags shown by "if"
talk.flags["knows_magic"] = True
talk.start()
talk.line = 2
talk._show_line()
check("a choice with a True 'if' flag shows", len(talk._choices()) == 3)
talk.choose(2)
check("choose(2) picks the third choice", talk.part == "magic")
talk.choose(5)
check("choose() with no such choice does nothing", talk.part == "magic")
ended.clear()
talk.start()
talk.line = 2
talk._show_line()
talk._current = {"text": "?", "choices": [["Bye", "end"]]}
talk._make_buttons()
talk.choose(0)
check("a choice that jumps to 'end' ends it", not talk.talking and ended == [True])

# ---------- type_speed=0 and type_sound ----------
quick = g.Dialogue(0, 0, 400, 150, script={"start": ["One", "Two"]}, type_speed=0)
quick.start()
check("type_speed=0 shows the line at once", not quick.text.typing)
quick.handle_event(click())
check("...so one click goes to the next line", quick.line == 1)


class FakeSound:
    def __init__(self):
        self.plays = 0

    def play(self):
        self.plays += 1


sound = FakeSound()
noisy = g.Dialogue(0, 0, 400, 150, script={"start": ["Hello"]}, type_speed=20,
                   type_sound=sound)
noisy.start()
noisy.update(200)
check("type_sound plays while typing", sound.plays == 1)
real = g.Dialogue(0, 0, 400, 150, script={"start": ["Hi"]},
                  type_sound=g.SoundEffect(os.path.join(HERE, "..", "examples", "assets",
                                                        "sounds", "click.wav")))
real.start()
real.update(100)
check("a real SoundEffect with no audio device doesn't crash", True)

# ---------- say() ----------
sign = g.Dialogue(0, 0, 400, 150)
sign.say("Sign", "Danger! Keep out.")
check("say() shows one line with a name", sign.talking and sign._speaker == "Sign"
      and sign.text.text == "Danger! Keep out.")
sign.say("The door is locked.")
check("say(text) shows it with no name", sign._speaker is None
      and sign.text.text == "The door is locked.")
finish(sign)
sign.next()
check("say() ends after its line", not sign.talking)

# ---------- JSON scripts ----------
folder = tempfile.mkdtemp()
json_path = os.path.join(folder, "shop.json")
with open(json_path, "w") as f:
    json.dump({"start": [{"speaker": "Shopkeeper", "text": "Buy something?",
                          "choices": [["Yes", "buy"], ["No", "end"]]}],
               "buy": ["Thanks!"]}, f)
shop = g.Dialogue(0, 0, 400, 150, script=json_path)
shop.start()
check("a script loads from a JSON file", shop._speaker == "Shopkeeper")
finish(shop)
shop.choose(0)
check("JSON choices (lists) work", shop.part == "buy")

missing, printed = warnings_from(lambda: g.Dialogue(0, 0, 400, 150,
                                                    script="no_such_file.json"))
check("a missing JSON file doesn't crash (warning printed)",
      "couldn't load no_such_file.json" in printed)
missing.start()
check("...and the box says what went wrong", missing.talking
      and "Couldn't load" in missing.text.text)
broken_path = os.path.join(folder, "broken.json")
with open(broken_path, "w") as f:
    f.write("{ this is not json")
broken, printed = warnings_from(lambda: g.Dialogue(0, 0, 400, 150, script=broken_path))
check("a broken JSON file doesn't crash", "couldn't load" in printed)

# ---------- Warnings for script mistakes ----------
bad_script = {
    "start": [
        {"speeker": "Bob", "text": "Typo in a key"},
        {"text": "Jump", "goto": "nowhere"},
        {"text": "Pick", "choices": [["A", "missing_part"], "not a list"]},
        {"text": "Do it", "do": "dance"},
        {"text": "Face", "portrait": "no_such_picture.png"},
        {"speaker": "Ann"},
    ],
}
bad, printed = warnings_from(lambda: g.Dialogue(0, 0, 400, 150, script=bad_script))
check("warns about an unknown key", "'speeker'" in printed)
check("warns about a goto to a missing part", "'nowhere'" in printed)
check("warns about a choice to a missing part", "'missing_part'" in printed)
check("warns about a badly written choice", "'not a list'" in printed)
check("warns about a 'do' not in actions", "'dance'" in printed)
check("warns about a missing portrait file", "no_such_picture.png" in printed)
check("warns about a line with no text", "has no \"text\"" in printed)
_, printed = warnings_from(lambda: bad.start("shop"))
check("start() with no such part warns and shows it in the box",
      "no part called 'shop'" in printed and "shop" in bad.text.text)
bad.start()
bad.draw(screen)               # a missing portrait is skipped, not a crash
check("drawing with a missing portrait doesn't crash", True)

# ---------- Saving flags ----------
save_file = os.path.join(folder, "save.json")
g.save_data(save_file, flags=talk.flags)
loaded = g.load_data(save_file, default={"flags": {}})["flags"]
again = g.Dialogue(0, 0, 400, 150, script=WIZARD, flags=loaded,
                   actions={"give_sword": lambda: None})
check("flags round-trip through save_data / load_data",
      again.flags == {"has_sword": True, "knows_magic": True})
again.start("take")
check("flags= keeps the same dict, so the game sees changes", again.flags is loaded)

# ---------- Drawing ----------
art = pg.Surface((40, 40))
art.fill((200, 50, 50))
with_face = g.Dialogue(0, 400, 800, 200, script={"start": ["Hi"]},
                       speakers={None: {}}, type_speed=0)
with_face.start()
with_face._current = {"speaker": "Ann", "text": "Hi", "portrait": art}
with_face._speaker = "Ann"
_, portrait_rect, name_pos, text_rect = with_face._areas(with_face.rect)
check("a portrait fills the box height", portrait_rect.size == (176, 176))
check("the text starts to the right of the portrait", text_rect.x > portrait_rect.right)
with_face.speakers = {"Ann": {"side": "right"}}
_, portrait_rect, _, text_rect = with_face._areas(with_face.rect)
check("side='right' puts the portrait on the right", portrait_rect.right == 800 - 12
      and text_rect.right < portrait_rect.x)
with_face._current = {"speaker": "Ann", "text": "Hi"}
_, portrait_rect, _, text_rect = with_face._areas(with_face.rect)
check("no portrait = the text uses the full width", portrait_rect is None
      and text_rect.width == 800 - 24)
surface = pg.Surface((800, 600))
with_face.speakers = {}
with_face._current = {"speaker": "Ann", "text": "Hi", "portrait": art}
with_face.draw(surface)
check("the portrait is drawn", surface.get_at((30, 430))[:3] == (200, 50, 50))
g.Debug.on = True
with_face.draw(surface)
g.Debug.on = False
check("draws with Debug on (F1)", True)
long_box = g.Dialogue(0, 0, 300, 80, script={"start": ["word " * 60]}, type_speed=0)
long_box.start()
_, printed = warnings_from(lambda: long_box.draw(screen))
check("warns when a line is too long for the box", "too long for the box" in printed)
for theme in ("dark", "retro", "high_contrast"):
    g.Style().theme_use(theme)
    with_face.draw(surface)
g.Style().reset()
check("draws in every theme", True)

# ---------- config, keys=None and parent first ----------
talk.config(bg=(10, 20, 30), type_speed=99)
talk.start()
talk.update(10)
check("config() changes options", talk.cget("bg") == (10, 20, 30)
      and talk.text.type_speed == 99)
mouse_only = g.Dialogue(0, 400, 400, 150, keys=None, type_speed=0, script={
    "start": [{"text": "?", "choices": [["A", "end"], ["B", "end"]]}]})
mouse_only.start()
check("keys=None: no key choosing", mouse_only._focus is None
      and mouse_only.handle_event(key(pg.K_DOWN)) is False)
frame = g.Frame(0, 0, 800, 600)
in_frame = g.Dialogue(frame, width=400, height=150, script={"start": ["Hi"]})
in_frame.place(x=10, y=400)
check("Dialogue(frame, ...) goes in the frame", in_frame.parent is frame)

print()
print("ALL TESTS PASS" if all(results) else f"{results.count(False)} TEST(S) FAILED")
pg.quit()
