"""
Snake example - a complete small game using Chain in grid mode.

Shows: Chain(mode="grid") with a sprite sheet (head, body, corner and tail
pieces turn automatically), queued turns (quick key presses aren't lost),
growing, speeding up, hits_self / hits_wall, free_cells() for placing food,
particles and a sound when eating, and a saved high score.

Arrow keys / WASD to steer. ENTER to play again. TAB = wrap-around on / off.

Snake sheet layout (assets/snake_sheet.png), 4 pieces in a row:
    head (facing right) | body (left-right) | corner (joins left and bottom) | tail (joins right)
Draw your own pieces the same way and pass images="your_sheet.png".
"""
import os
import sys
import pygame as pg

# Lets this example find the library one folder up.
# In your own game, just put PygameTkinterGUITools.py next to your game file.
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import random
from PygameTkinterGUITools import (Grid, Chain, KeyboardInput, Label, Particles, SoundEffect,
                                   init_audio, HighScores, load_image)

# ---------- Settings ----------
CELL = 32
COLS, ROWS = 20, 15
WIDTH, HEIGHT = COLS * CELL, ROWS * CELL + 40
FPS = 60
ASSETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")


def new_game():
    global snake, food, score, game_over
    snake = Chain(mode="grid", grid=board, head_cell=(5, 7), length=4, direction="right",
                  move_every=150, wrap=wrap, images=os.path.join(ASSETS, "snake_sheet.png"))
    score = 0
    game_over = False
    food = random.choice(snake.free_cells())


def init_pygame():
    """Set up pygame, the window, the clock and all game objects."""
    global screen, clock, board, keys, wrap, eat_sound, crash_sound, best, info, apple, grass
    init_audio()
    pg.init()
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    pg.display.set_caption("Snake")
    clock = pg.time.Clock()

    # >>> Create objects here (after pg.init and set_mode)
    board = Grid(0, 40, cols=COLS, rows=ROWS, cell_size=CELL, show_lines=False)
    keys = KeyboardInput()
    keys.bind("up", "up", "w")
    keys.bind("down", "down", "s")
    keys.bind("left", "left", "a")
    keys.bind("right", "right", "d")
    keys.bind("restart", "return")
    keys.bind("wrap", "tab")
    eat_sound = SoundEffect(os.path.join(ASSETS, "sounds", "coin.wav"))
    crash_sound = SoundEffect(os.path.join(ASSETS, "sounds", "explosion.wav"))
    best = HighScores("snake_scores.json", keep=1)
    apple = load_image(os.path.join(ASSETS, "apple.png"), (CELL, CELL))
    grass = load_image(os.path.join(ASSETS, "snake_grass.png"))
    info = Label(10, 8, "", font_size=30)
    wrap = False
    new_game()


def handle_inputs():
    """Check every event: quitting, keys, mouse, controllers."""
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            sys.exit()

        # >>> Objects that react to events go here
        keys.handle_event(event)


def update(tick):
    """Move, animate and check things."""
    global food, score, game_over, wrap
    # >>> Objects with update(tick) go here
    keys.update(tick)
    Particles.update(tick)
    if keys.was_pressed("wrap"):
        wrap = not wrap
        snake.wrap = wrap
    if game_over:
        if keys.was_pressed("restart"):
            new_game()
        return

    # Turning: was_pressed = one turn per key press (turns are queued)
    for direction in ("up", "down", "left", "right"):
        if keys.was_pressed(direction):
            snake.turn(direction)

    snake.update(tick)                       # moves one cell every move_every ms
    if not snake.moved:
        return

    if snake.hits_self() or snake.hits_wall():
        game_over = True
        crash_sound.play()
        Particles.explosion(board.cell_rect(*snake.cells[1]).center, scale=0.8)
        best.add("You", score)
        return

    if snake.head_cell == food:
        snake.grow()
        score += 1
        eat_sound.play()
        Particles.sparks(board.cell_rect(*food).center, count=15, color=(255, 120, 120))
        snake.move_every = max(60, 150 - score * 4)     # faster as it grows
        food = random.choice(snake.free_cells())

    best_score = best.best()[1] if best.best() else 0
    info.config(text=f"Score: {score}    Best: {best_score}    Wrap (Tab): {'on' if wrap else 'off'}")


def draw_game():
    """Draw everything, then show it."""
    screen.fill((40, 70, 40))

    # >>> Objects with draw(screen) go here
    for col, row in board.all_cells():                        # checkerboard grass
        tile = pg.Rect(((col + row) % 2) * CELL, 0, CELL, CELL)
        screen.blit(grass, board.cell_rect(col, row), area=tile)
    screen.blit(apple, board.cell_rect(*food))
    snake.draw(screen)
    Particles.draw(screen)
    info.draw(screen)
    if game_over:
        Label(WIDTH // 2, HEIGHT // 2, "Game over - press Enter", font_size=48,
              bg=(0, 0, 0), center=True).draw(screen)

    pg.display.flip()


# ---------- Main program ----------
init_pygame()
while True:
    tick = clock.tick(FPS)   # tick = milliseconds since the last frame (used for animation)
    handle_inputs()
    update(tick)
    draw_game()
