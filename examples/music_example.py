"""
Music and Audio example - background music and volume controls.

Shows: Music.switch() with fades, a playlist, pause, and volume Scales /
a mute Checkbutton linked with Audio.link() - no extra code needed.
"""
import os
import sys
import pygame as pg

# Lets this example find the library one folder up.
# In your own game, just put PygameTkinterGUITools.py next to your game file.
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from PygameTkinterGUITools import (Music, Audio, SoundEffect, init_audio, Button, Scale,
                                   Checkbutton, Label, IntVar, BooleanVar)

# ---------- Settings ----------
WIDTH, HEIGHT = 800, 600
FPS = 60
SOUNDS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "sounds")
MENU_MUSIC = os.path.join(SOUNDS, "music_menu.wav")
LEVEL_MUSIC = os.path.join(SOUNDS, "music_level.wav")


def menu_music():
    Music.switch(MENU_MUSIC, fade_ms=800)      # fade out the old track, fade in this one


def level_music():
    Music.switch(LEVEL_MUSIC, fade_ms=800)


def play_list():
    Music.playlist([MENU_MUSIC, LEVEL_MUSIC])  # one after the other, forever


def pause_or_play():
    if Music.is_playing():
        Music.pause()
        pause_button.config(text="Unpause")
    else:
        Music.unpause()
        pause_button.config(text="Pause")


def init_pygame():
    """Set up pygame, the window, the clock and all game objects."""
    global screen, clock, widgets, pause_button, now_playing, click_sound
    init_audio()                         # BEFORE pg.init()
    pg.init()
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    pg.display.set_caption("Music example")
    clock = pg.time.Clock()

    # >>> Create objects here (after pg.init)
    music_volume = IntVar(70)
    sfx_volume = IntVar(80)
    muted = BooleanVar(False)
    Audio.link(music_volume=music_volume, sfx_volume=sfx_volume, muted=muted)

    click_sound = SoundEffect(os.path.join(SOUNDS, "coin.wav"))
    pause_button = Button(50, 260, 200, 45, "Pause", command=pause_or_play, font_size=26)
    widgets = [
        Button(50, 50, 200, 45, "Menu music", command=menu_music, font_size=26),
        Button(50, 120, 200, 45, "Level music", command=level_music, font_size=26),
        Button(50, 190, 200, 45, "Playlist", command=play_list, font_size=26),
        pause_button,
        Button(50, 330, 200, 45, "Stop", command=lambda: Music.stop(fade_ms=500), font_size=26),
        Scale(350, 50, from_=0, to=100, length=300, variable=music_volume, label="Music"),
        Scale(350, 130, from_=0, to=100, length=300, variable=sfx_volume, label="Effects"),
        Checkbutton(350, 210, "Mute everything", variable=muted),
        Button(350, 260, 200, 45, "Test effect", command=click_sound.play, font_size=26),
    ]
    now_playing = Label(50, 450, "")
    menu_music()


def handle_inputs():
    """Check every event: quitting, keys, mouse, controllers."""
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            sys.exit()

        # >>> Objects that react to events go here
        for widget in widgets:
            widget.handle_event(event)


def update(tick):
    """Move, animate and check things."""
    # >>> Objects with update(tick) go here
    Music.update(tick)                   # needed for switch() and playlist()
    track = os.path.basename(Music.current) if Music.current else "nothing"
    now_playing.config(text=f"Now playing: {track}")


def draw_game():
    """Draw everything, then show it."""
    screen.fill((30, 30, 40))

    # >>> Objects with draw(screen) go here
    for widget in widgets:
        widget.draw(screen)
    now_playing.draw(screen)
    if not Audio.available:
        Label(50, 500, "No sound output found on this computer", fg=(255, 120, 120)).draw(screen)

    pg.display.flip()


# ---------- Main program ----------
init_pygame()
while True:
    tick = clock.tick(FPS)   # tick = milliseconds since the last frame (used for animation)
    handle_inputs()
    update(tick)
    draw_game()
