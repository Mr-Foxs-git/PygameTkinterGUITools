"""
Scenes example - menu -> game -> game over, with timers and high scores.

Shows: Scenes with fade / slide transitions, scenes written as FUNCTIONS
(menu, game) and as a CLASS (game over), passing data to the next scene,
after_repeat() to spawn targets, Countdown for a 20 second timer, and a
saved HighScores table (scores.json is saved next to this file).

Click the targets before the time runs out!
"""
import os
import sys
import pygame as pg

# Lets this example find the library one folder up.
# In your own game, just put PygameTkinterGUITools.py next to your game file.
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import random
from PygameTkinterGUITools import (Scenes, Scene, Root, Label, Button, TextBox, Message,
                                   after, after_repeat, Countdown, HighScores, Debug)

# ---------- Settings ----------
WIDTH, HEIGHT = 800, 600
FPS = 60


# ================= MENU scene (written as functions) =================
def menu_start():
    global menu
    menu = Root(screen, padding=40)
    menu.columnconfigure(0, weight=1)
    Label(menu, text="Target Clicker", font_size=64).grid(row=0, column=0, pady=30)
    Button(menu, text="Play", command=lambda: scenes.switch("game", transition="fade",
                                                            ms=600)).grid(row=1, column=0, pady=8)
    Button(menu, text="High scores", command=lambda: scenes.switch(
        "scores", transition="slide_left", ms=500)).grid(row=2, column=0, pady=8)


def menu_event(event):
    menu.handle_event(event)


def menu_draw(screen):
    screen.fill((25, 30, 50))
    menu.draw(screen)


# ================= GAME scene (written as functions) =================
def game_start():
    global targets, score, timer, hud
    targets = []
    score = 0
    timer = Countdown(20000, on_finish=lambda: scenes.switch(
        "game_over", transition="fade", ms=800, score=score))
    after_repeat(700, spawn_target)          # stops by itself when the scene ends
    hud = Label(10, 10, "")


def spawn_target():
    size = random.randint(30, 60)
    targets.append(pg.Rect(random.randint(0, WIDTH - size), random.randint(60, HEIGHT - size),
                           size, size))
    after(1800, remove_target, targets[-1])  # each target disappears after 1.8 s


def remove_target(target):
    if target in targets:
        targets.remove(target)


def game_event(event):
    global score
    if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
        for target in targets[:]:
            if target.collidepoint(event.pos):
                targets.remove(target)
                score += 1


def game_update(tick):
    hud.config(text=f"Score: {score}     Time: {timer.text()}")


def game_draw(screen):
    screen.fill((30, 60, 40))
    for target in targets:
        pg.draw.circle(screen, (240, 80, 80), target.center, target.width // 2)
        pg.draw.circle(screen, WHITE, target.center, target.width // 4)
    hud.draw(screen)


# ================= GAME OVER scene (written as a class) =================
class GameOver(Scene):
    def start(self, score=0):
        self.score = score
        self.root = Root(screen, padding=40)
        self.root.columnconfigure(0, weight=1)
        Label(self.root, text="Time's up!", font_size=60).grid(row=0, column=0, pady=20)
        Label(self.root, text=f"You scored {score}").grid(row=1, column=0)
        if high_scores.is_high_score(score) and score > 0:
            Label(self.root, text="New high score! Type your name, press Enter:",
                  fg=(255, 220, 0)).grid(row=2, column=0, pady=(20, 5))
            self.name_box = TextBox(self.root, max_chars=12, on_enter=self.save_score)
            self.name_box.grid(row=3, column=0)
            self.name_box.typing = True
        Button(self.root, text="Menu", command=lambda: self.scenes.switch(
            "menu", transition="fade")).grid(row=4, column=0, pady=20)

    def save_score(self):
        high_scores.add(self.name_box.get() or "???", self.score)
        self.scenes.switch("scores", transition="slide_left", ms=500)

    def handle_event(self, event):
        self.root.handle_event(event)

    def update(self, tick):
        self.root.update(tick)

    def draw(self, screen):
        screen.fill((50, 25, 30))
        self.root.draw(screen)


# ================= HIGH SCORES scene (a class too) =================
class ScoresScreen(Scene):
    def start(self):
        self.root = Root(screen, padding=40)
        self.root.columnconfigure(0, weight=1)
        Label(self.root, text="High scores", font_size=56).grid(row=0, column=0, pady=20)
        lines = high_scores.table() or ["No scores yet!"]
        Message(self.root, text="\n".join(lines), width=300, justify="center").grid(
            row=1, column=0)
        Button(self.root, text="Back", command=lambda: self.scenes.switch(
            "menu", transition="slide_right", ms=500)).grid(row=2, column=0, pady=20)

    def handle_event(self, event):
        self.root.handle_event(event)

    def draw(self, screen):
        screen.fill((25, 30, 50))
        self.root.draw(screen)


WHITE = (255, 255, 255)


def init_pygame():
    """Set up pygame, the window, the clock and all game objects."""
    global screen, clock, scenes, high_scores
    pg.init()
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    pg.display.set_caption("Scenes example")
    clock = pg.time.Clock()

    # >>> Create objects here (after pg.init)
    high_scores = HighScores("scores.json", keep=5)
    scenes = Scenes()
    scenes.add("menu", start=menu_start, handle_event=menu_event, draw=menu_draw)
    scenes.add("game", start=game_start, handle_event=game_event, update=game_update,
               draw=game_draw)
    scenes.add("game_over", GameOver())
    scenes.add("scores", ScoresScreen())


def handle_inputs():
    """Check every event: quitting, keys, mouse, controllers."""
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            sys.exit()

        # >>> Objects that react to events go here
        Debug.handle_event(event)            # F1 shows the layout debug view
        scenes.handle_event(event)           # the current scene gets it


def update(tick):
    """Move, animate and check things."""
    # >>> Objects with update(tick) go here
    scenes.update(tick)                      # also runs the after() timers


def draw_game():
    """Draw everything, then show it."""
    # >>> Objects with draw(screen) go here
    scenes.draw(screen)                      # the current scene draws itself

    pg.display.flip()


# ---------- Main program ----------
init_pygame()
while True:
    tick = clock.tick(FPS)   # tick = milliseconds since the last frame (used for animation)
    handle_inputs()
    update(tick)
    draw_game()
