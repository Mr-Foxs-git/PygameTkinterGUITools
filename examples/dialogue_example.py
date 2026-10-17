"""
Dialogue example - talk to people, like in Zelda or Pokemon.

Shows: Dialogue with a script written as a dict (the wizard) and a script
loaded from a JSON file (the shopkeeper), speakers with portraits, choices,
"set" flags, "do" actions, an "if" choice, say() and saving the flags.
Arrow keys = walk. E = talk to whoever you are standing next to.
SPACE / ENTER / click = show the rest of the line, then the next line.
Choices: click one, or Up / Down and ENTER.
The wizard remembers giving you the sword, even after you close the game
(delete dialogue_save.json to forget).
"""
import os
import sys
import pygame as pg

# Lets this example find the library one folder up.
# In your own game, just put PygameTkinterGUITools.py next to your game file.
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from PygameTkinterGUITools import (Dialogue, KeyboardInput, Label, SoundEffect,
                                   init_audio, load_image, save_data, load_data)

# Folders with the images and sounds for the examples
HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(HERE, "assets")
SOUNDS = os.path.join(ASSETS, "sounds")
SAVE_FILE = os.path.join(HERE, "dialogue_save.json")

# ---------- Settings ----------
WIDTH, HEIGHT = 800, 600
FPS = 60
PLAYER_SPEED = 200            # pixels per second

# The wizard's script. Each part is a list of lines; choices jump to parts.
WIZARD_TALK = {
    "start": [
        {"speaker": "Wizard", "text": "Ah, a traveller! It's dangerous to go alone."},
        "Will you take this sword?",              # a string = same speaker again
        {"text": "Well?", "choices": [["Yes please", "take"],
                                      ["No thanks", "refuse"]]},
    ],
    "take": [
        {"text": "Use it wisely!", "set": {"has_sword": True}, "do": "give_sword"},
    ],
    "refuse": [
        "Come back if you change your mind.",
    ],
    "again": [
        {"speaker": "Wizard", "text": "How is that sword working out?"},
        {"speaker": None, "text": "The wizard smiles and goes back to his book."},
    ],
}


def give_sword():
    """Runs from "do": "give_sword" in the script."""
    save_data(SAVE_FILE, flags=dialogue.flags)     # remember it next time


def buy_potion():
    """Runs from "do": "buy_potion" in the shopkeeper's JSON script."""
    global coins, potions
    coins -= 5
    potions += 1


def talk_to(person):
    """Start the right conversation for the person we are next to."""
    if person == "wizard":
        dialogue.load(WIZARD_TALK)
        # Plain Python decides where to start: has the wizard met us before?
        if dialogue.flags.get("has_sword"):
            dialogue.start("again")
        else:
            dialogue.start()
    else:
        dialogue.load(os.path.join(ASSETS, "shop_talk.json"))
        # The "Buy" choice has {"if": "can_afford"}, so it only shows with 5 coins
        dialogue.flags["can_afford"] = coins >= 5
        dialogue.start()


def person_nearby():
    """Return "wizard", "shopkeeper" or None, depending on who is close."""
    for name, rect in people.items():
        if player.colliderect(rect.inflate(40, 40)):
            return name
    return None


def init_pygame():
    """Set up pygame, the window, the clock and all game objects."""
    global screen, clock, keys, player, people, pictures, dialogue, coins, potions
    global status, hint
    init_audio()                         # BEFORE pg.init(): sounds play with less delay
    pg.init()
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    pg.display.set_caption("Dialogue example")
    clock = pg.time.Clock()

    # >>> Create objects here (after pg.init)
    keys = KeyboardInput()
    keys.bind("left", "left")
    keys.bind("right", "right")
    keys.bind("up", "up")
    keys.bind("down", "down")
    keys.bind("talk", "e")

    player = pg.Rect(380, 300, 32, 32)
    people = {"wizard": pg.Rect(180, 150, 48, 48),
              "shopkeeper": pg.Rect(570, 150, 48, 48)}
    pictures = {"wizard": os.path.join(ASSETS, "portrait_wizard.png"),
                "shopkeeper": os.path.join(ASSETS, "portrait_shopkeeper.png")}
    coins = 12
    potions = 0

    # Saved flags from last time (or none). The game never crashes on a bad file.
    saved = load_data(SAVE_FILE, default={"flags": {}})

    click = SoundEffect(os.path.join(SOUNDS, "click.wav"), volume=0.3, cooldown=60)
    dialogue = Dialogue(20, 410, 760, 170,
                        speakers={"Wizard": {"portrait": pictures["wizard"]},
                                  "Shopkeeper": {"portrait": pictures["shopkeeper"],
                                                 "name_fg": (120, 230, 140),
                                                 "side": "right"}},
                        actions={"give_sword": give_sword, "buy_potion": buy_potion},
                        flags=saved["flags"], type_speed=40, type_sound=click)
    # One line with no script - good for signs and tips
    dialogue.say("Use the arrow keys to walk. Press E next to someone to talk.")

    status = Label(20, 20, "")
    hint = Label(0, 0, "E: talk", font_size=22, outline=2, visible=False)


def handle_inputs():
    """Check every event: quitting, keys, mouse, controllers."""
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            sys.exit()

        # >>> Objects that react to events go here
        # The Dialogue goes FIRST: True = it used the click / key,
        # so the same press doesn't also do something in the game
        if dialogue.handle_event(event):
            continue
        keys.handle_event(event)


def update(tick):
    """Move, animate and check things."""
    # >>> Objects with update(tick) go here
    keys.update(tick)                    # always first: works out pressed / held / released
    dialogue.update(tick)                # types the text out

    # Only walk and start talking when no one is already talking
    nearby = person_nearby()
    if not dialogue.talking:
        step = round(PLAYER_SPEED * tick / 1000)
        if keys.is_pressed("left"):
            player.x -= step
        if keys.is_pressed("right"):
            player.x += step
        if keys.is_pressed("up"):
            player.y -= step
        if keys.is_pressed("down"):
            player.y += step
        player.clamp_ip(screen.get_rect())
        if keys.was_pressed("talk") and nearby:
            talk_to(nearby)

    # Show "E: talk" above whoever is close
    hint.visible = nearby is not None and not dialogue.talking
    if nearby:
        hint.x, hint.y = people[nearby].x - 10, people[nearby].y - 30
    sword = "yes" if dialogue.flags.get("has_sword") else "no"
    status.config(text=f"Coins: {coins}    Potions: {potions}    Sword: {sword}")


def draw_game():
    """Draw everything, then show it."""
    screen.fill((70, 140, 80))

    # >>> Objects with draw(screen) go here
    for name, rect in people.items():
        screen.blit(load_image(pictures[name], rect.size), rect)
    pg.draw.rect(screen, (60, 120, 230), player)
    status.draw(screen)
    hint.draw(screen)
    dialogue.draw(screen)                # LAST, so it is on top

    pg.display.flip()


# ---------- Main program ----------
init_pygame()
while True:
    tick = clock.tick(FPS)   # tick = milliseconds since the last frame (used for animation)
    handle_inputs()
    update(tick)
    draw_game()
