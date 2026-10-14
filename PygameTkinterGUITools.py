"""
PygameTkinterGUITools
=====================
Helper objects for making games and GUIs in pygame.

GUI widgets work like tkinter: Label, Button, TextBox, Frame, Popup.
Game helpers: Animator, SpriteObject, Camera, ZoomCamera, TiledMap, World,
JoystickManager.

Every object uses the same methods, so they all go in the same place in
your game loop:
    obj.handle_event(event)   -> in handle_inputs()
    obj.update(tick)          -> in update(tick)
    obj.draw(screen)          -> in draw_game()

Option names follow tkinter:
    text, fg (text colour), bg (background colour), command (function to run),
    font_name, font_size, border_color, border_width
Colour options use the US spelling "color" but "colour" also works,
e.g. border_color= or border_colour=.
"""
import pygame as pg

# Some common colours
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)


# ================================
# Helper functions
# ================================

_font_cache = {}


def get_font(font_name=None, font_size=24):
    """
    Return a pygame font. Fonts are made once and then reused,
    because making a new font every frame is slow.
    """
    if not pg.font.get_init():
        pg.font.init()          # works even if pg.init() was forgotten
    key = (font_name, font_size)
    if key not in _font_cache:
        _font_cache[key] = pg.font.SysFont(font_name, font_size)
    return _font_cache[key]


def _pick(*values):
    """Return the first value that is not None (used for color / colour)."""
    for value in values:
        if value is not None:
            return value
    return None


def draw_text(screen, text, x, y, fg=WHITE, font_size=24, font_name=None,
              center=False):
    """
    Draw text on the screen in one line of code.

    Parameters:
        screen    - the pygame Surface to draw on
        text      - the words to show (string)
        x, y      - position (top-left, or the centre if center=True)
        fg        - text colour, e.g. (255, 255, 255)
        font_size - size of the text (int)
        font_name - optional font name, e.g. "Arial"
        center    - if True, the text is centred on (x, y)
    """
    surface = get_font(font_name, font_size).render(str(text), True, fg)
    rect = surface.get_rect()
    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)
    screen.blit(surface, rect)


# ================================
# Widget base class
# ================================

class Widget:
    """
    The base for every GUI object. You don't make a Widget yourself -
    Label, Button, TextBox, Frame and Popup are all built on it, so they
    all share these methods:

        draw(screen, offset=(0, 0))          draw it
        handle_event(event, offset=(0, 0))   react to mouse / keys
        update(tick)                         animate it
        config(option=value, ...)            change options (like tkinter)
        show(), hide(), toggle_visibility()

    offset is added to the position. Frames and Popups use it to move
    their children; you normally leave it out.
    """

    # Other names allowed in config(), e.g. "border_colour" -> "border_color"
    _aliases = {}

    def __init__(self, x, y, width=0, height=0, center=False, visible=True):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.center = center
        self.visible = visible

    @property
    def rect(self):
        """The widget's rectangle (without any offset)."""
        return self.get_rect()

    def get_rect(self, offset=(0, 0)):
        """The widget's rectangle on screen, after adding offset."""
        r = pg.Rect(0, 0, self.width, self.height)
        position = (self.x + offset[0], self.y + offset[1])
        if self.center:
            r.center = position
        else:
            r.topleft = position
        return r

    def show(self):
        self.visible = True

    def hide(self):
        self.visible = False

    def toggle_visibility(self):
        self.visible = not self.visible

    def config(self, **options):
        """
        Change options after the widget is made, like tkinter.
        Example: score_label.config(text="Score: 10", fg=(255, 0, 0))
        """
        for name, value in options.items():
            name = self._aliases.get(name, name)
            if not hasattr(self, name):
                raise ValueError(f"{type(self).__name__} has no option '{name}'")
            setattr(self, name, value)
        self._refresh()

    configure = config      # tkinter has both names

    def _refresh(self):
        """Recalculate sizes after config(). Widgets override this."""
        pass

    def draw(self, screen, offset=(0, 0)):
        pass

    def handle_event(self, event, offset=(0, 0)):
        pass

    def update(self, tick):
        pass


# ================================
# Label Class
# ================================

class Label(Widget):
    """
    Shows text on the screen (like tkinter's Label).

    Parameters:
        x, y      - position (top-left, or centre if center=True)
        text      - the words to show
        fg        - text colour
        bg        - background colour behind the text (None = no background)
        font_name - optional font name, e.g. "Arial"
        font_size - size of the text
        center    - if True, (x, y) is the centre of the label
        visible   - False to start hidden

    Example:
        score = Label(20, 20, "Score: 0", fg=(255, 255, 0))
        score.config(text="Score: 10")
    """

    def __init__(self, x, y, text="", fg=WHITE, bg=None,
                 font_name=None, font_size=24, center=False, visible=True):
        super().__init__(x, y, center=center, visible=visible)
        self.text = text
        self.fg = fg
        self.bg = bg
        self.font_name = font_name
        self.font_size = font_size
        self._refresh()

    def _refresh(self):
        self.font = get_font(self.font_name, self.font_size)
        self.width, self.height = self.font.size(str(self.text))

    def draw(self, screen, offset=(0, 0)):
        if not self.visible:
            return
        self._refresh()                      # text may have been changed directly
        r = self.get_rect(offset)
        if self.bg is not None:
            pg.draw.rect(screen, self.bg, r)
        screen.blit(self.font.render(str(self.text), True, self.fg), r)


# ================================
# Button Class
# ================================

class Button(Widget):
    """
    A clickable button (like tkinter's Button).

    Parameters:
        x, y, width, height - position and size
        text          - the words on the button
        command       - function to run when clicked (no brackets!)
        fg            - text colour
        bg            - button colour
        hover_bg      - button colour when the mouse is over it
        font_name, font_size
        border_color  - border colour (border_colour also works)
        border_width  - border thickness (0 = no border)
        border_radius - roundness of the corners
        shadow        - True to draw a shadow
        shadow_offset - (x, y) distance of the shadow
        shadow_color  - shadow colour, can include transparency (R, G, B, A)
        center        - if True, (x, y) is the centre of the button
        visible       - False to start hidden

    Example:
        def start_game():
            print("Starting!")
        start = Button(100, 100, 150, 50, "Start", command=start_game)
    """

    _aliases = {"border_colour": "border_color", "shadow_colour": "shadow_color"}

    def __init__(self, x, y, width, height, text="", command=None,
                 fg=BLACK, bg=(100, 150, 255), hover_bg=(150, 200, 255),
                 font_name=None, font_size=30,
                 border_color=None, border_colour=None, border_width=0,
                 border_radius=0,
                 shadow=False, shadow_offset=(3, 3),
                 shadow_color=None, shadow_colour=None,
                 center=False, visible=True):
        super().__init__(x, y, width, height, center, visible)
        self.text = text
        self.command = command
        self.fg = fg
        self.bg = bg
        self.hover_bg = hover_bg
        self.font_name = font_name
        self.font_size = font_size
        self.border_color = _pick(border_color, border_colour)
        self.border_width = border_width
        self.border_radius = border_radius
        self.shadow = shadow
        self.shadow_offset = shadow_offset
        self.shadow_color = _pick(shadow_color, shadow_colour, (0, 0, 0, 100))
        self._refresh()

    def _refresh(self):
        self.font = get_font(self.font_name, self.font_size)

    def is_hovered(self, offset=(0, 0)):
        """True if the mouse is over the button."""
        return self.get_rect(offset).collidepoint(pg.mouse.get_pos())

    def draw(self, screen, offset=(0, 0)):
        if not self.visible:
            return
        r = self.get_rect(offset)

        # Shadow
        if self.shadow:
            shadow_surface = pg.Surface(r.size, pg.SRCALPHA)
            pg.draw.rect(shadow_surface, self.shadow_color,
                         shadow_surface.get_rect(), border_radius=self.border_radius)
            screen.blit(shadow_surface, r.move(self.shadow_offset))

        # Button
        colour = self.hover_bg if self.is_hovered(offset) else self.bg
        pg.draw.rect(screen, colour, r, border_radius=self.border_radius)

        # Border
        if self.border_color and self.border_width > 0:
            pg.draw.rect(screen, self.border_color, r,
                         width=self.border_width, border_radius=self.border_radius)

        # Text
        text_surface = self.font.render(str(self.text), True, self.fg)
        screen.blit(text_surface, text_surface.get_rect(center=r.center))

    def handle_event(self, event, offset=(0, 0)):
        if not self.visible:
            return
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            if self.get_rect(offset).collidepoint(event.pos) and self.command:
                self.command()


# ================================
# TextBox Class
# ================================

class TextBox(Widget):
    """
    A box the player can type into (like tkinter's Entry).
    Click it to start typing. Supports arrow keys, Home, End,
    Backspace and Delete.

    Parameters:
        x, y           - position (top-left, or centre if center=True)
        max_chars      - most letters allowed (also sets the box width)
        text           - starting text
        fg             - text colour
        bg             - box colour
        border_color   - border colour (border_colour also works)
        font_name, font_size
        padding        - space inside the box around the text
        label          - optional words shown next to the box, e.g. "Name:"
        label_fg       - label colour
        label_gap      - space between label and box
        label_position - "left", "right", "top" or "bottom"
        on_enter       - function to run when Enter is pressed
        center         - if True, (x, y) is the centre of box + label
        visible        - False to start hidden

    Example:
        def submit():
            print("Hello", name_box.get())
        name_box = TextBox(100, 100, label="Name:", on_enter=submit)
    """

    _aliases = {"border_colour": "border_color"}

    def __init__(self, x, y, max_chars=20, text="",
                 fg=BLACK, bg=(230, 230, 230),
                 border_color=None, border_colour=None,
                 font_name=None, font_size=24, padding=6,
                 label=None, label_fg=WHITE, label_gap=10, label_position="left",
                 on_enter=None, center=False, visible=True):
        super().__init__(x, y, center=center, visible=visible)
        self.max_chars = max_chars
        self.fg = fg
        self.bg = bg
        self.border_color = _pick(border_color, border_colour, (100, 100, 100))
        self.font_name = font_name
        self.font_size = font_size
        self.padding = padding
        self.label = label
        self.label_fg = label_fg
        self.label_gap = label_gap
        self.label_position = label_position.lower()
        self.on_enter = on_enter

        self.text = str(text)[:max_chars]
        self.cursor_pos = len(self.text)
        self.cursor_visible = True
        self.cursor_timer = 0
        self.active = False
        self._refresh()

    def _refresh(self):
        """Work out where the box and label go (relative to the top-left)."""
        self.font = get_font(self.font_name, self.font_size)
        self.text = str(self.text)[:self.max_chars]
        self.cursor_pos = min(self.cursor_pos, len(self.text))

        box_w = self.max_chars * self.font.size("M")[0] + self.padding * 2
        box_h = self.font.get_height() + self.padding * 2

        if not self.label:
            self.box_rect = pg.Rect(0, 0, box_w, box_h)
            self.label_rect = None
            self.width, self.height = box_w, box_h
            return

        label_w, label_h = self.font.size(self.label)
        gap = self.label_gap
        if self.label_position in ("left", "right"):
            self.width = label_w + gap + box_w
            self.height = max(box_h, label_h)
            box_y = (self.height - box_h) // 2
            label_y = (self.height - label_h) // 2
            if self.label_position == "left":
                self.label_rect = pg.Rect(0, label_y, label_w, label_h)
                self.box_rect = pg.Rect(label_w + gap, box_y, box_w, box_h)
            else:
                self.box_rect = pg.Rect(0, box_y, box_w, box_h)
                self.label_rect = pg.Rect(box_w + gap, label_y, label_w, label_h)
        else:   # "top" or "bottom"
            self.width = max(box_w, label_w)
            self.height = label_h + gap + box_h
            box_x = (self.width - box_w) // 2
            label_x = (self.width - label_w) // 2
            if self.label_position == "top":
                self.label_rect = pg.Rect(label_x, 0, label_w, label_h)
                self.box_rect = pg.Rect(box_x, label_h + gap, box_w, box_h)
            else:
                self.box_rect = pg.Rect(box_x, 0, box_w, box_h)
                self.label_rect = pg.Rect(label_x, box_h + gap, label_w, label_h)

    # ---- text methods (get / set like tkinter) ----
    def get(self):
        """Return the text typed in the box."""
        return self.text

    get_text = get

    def set_text(self, new_text):
        """Replace the text in the box."""
        self.text = str(new_text)[:self.max_chars]
        self.cursor_pos = len(self.text)

    def clear(self):
        """Empty the box."""
        self.set_text("")

    def insert_text(self, characters):
        """Type characters at the cursor (stops at max_chars)."""
        for ch in characters:
            if len(self.text) >= self.max_chars:
                break
            self.text = self.text[:self.cursor_pos] + ch + self.text[self.cursor_pos:]
            self.cursor_pos += 1

    # ---- game loop methods ----
    def handle_event(self, event, offset=(0, 0)):
        if not self.visible:
            return
        box_on_screen = self.box_rect.move(self.get_rect(offset).topleft)

        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            self.active = box_on_screen.collidepoint(event.pos)

        if not self.active or event.type != pg.KEYDOWN:
            return

        if event.key in (pg.K_RETURN, pg.K_KP_ENTER):
            if self.on_enter:
                self.on_enter()
        elif event.key == pg.K_BACKSPACE:
            if self.cursor_pos > 0:
                self.text = self.text[:self.cursor_pos - 1] + self.text[self.cursor_pos:]
                self.cursor_pos -= 1
        elif event.key == pg.K_DELETE:
            self.text = self.text[:self.cursor_pos] + self.text[self.cursor_pos + 1:]
        elif event.key == pg.K_LEFT:
            self.cursor_pos = max(0, self.cursor_pos - 1)
        elif event.key == pg.K_RIGHT:
            self.cursor_pos = min(len(self.text), self.cursor_pos + 1)
        elif event.key == pg.K_HOME:
            self.cursor_pos = 0
        elif event.key == pg.K_END:
            self.cursor_pos = len(self.text)
        elif event.unicode and event.unicode.isprintable():
            self.insert_text(event.unicode)

    def update(self, tick):
        """Make the cursor blink."""
        self.cursor_timer += tick
        if self.cursor_timer >= 400:
            self.cursor_timer = 0
            self.cursor_visible = not self.cursor_visible

    def draw(self, screen, offset=(0, 0)):
        if not self.visible:
            return
        top_left = self.get_rect(offset).topleft

        # Label
        if self.label_rect:
            screen.blit(self.font.render(self.label, True, self.label_fg),
                        self.label_rect.move(top_left))

        # Box
        box = self.box_rect.move(top_left)
        pg.draw.rect(screen, self.bg, box)
        pg.draw.rect(screen, self.border_color, box, 2)

        # Text
        text_surface = self.font.render(self.text, True, self.fg)
        text_x = box.x + self.padding
        text_y = box.y + (box.height - text_surface.get_height()) // 2
        screen.blit(text_surface, (text_x, text_y))

        # Cursor
        if self.active and self.cursor_visible:
            cursor_x = text_x + self.font.size(self.text[:self.cursor_pos])[0]
            pg.draw.line(screen, self.fg, (cursor_x, text_y),
                         (cursor_x, text_y + self.font.get_height()), 2)


# ================================
# Container base class (Frame and Popup)
# ================================

class Container(Widget):
    """
    The base for Frame and Popup: a box that holds other widgets.
    Children's x, y are measured from the inside top-left corner
    (after the padding), and they move when the container moves.
    """

    _aliases = {"border_colour": "border_color"}

    def __init__(self, x, y, width, height, bg, border_color, border_width,
                 pad_x, pad_y, center, visible):
        super().__init__(x, y, width, height, center, visible)
        self.bg = bg
        self.border_color = border_color
        self.border_width = border_width
        self.pad_x = pad_x
        self.pad_y = pad_y
        self.children = []
        self.top_space = 0          # extra space at the top (Popup title bar)

    def add(self, *widgets):
        """Add one or more widgets, e.g. frame.add(label, button)."""
        for widget in widgets:
            self.children.append(widget)

    def child_offset(self, offset=(0, 0)):
        """Where the children's (0, 0) is on screen."""
        r = self.get_rect(offset)
        return (r.x + self.pad_x, r.y + self.pad_y + self.top_space)

    def draw_children(self, screen, offset=(0, 0)):
        inside = self.child_offset(offset)
        for child in self.children:
            child.draw(screen, inside)

    def handle_event(self, event, offset=(0, 0)):
        if not self.visible:
            return
        inside = self.child_offset(offset)
        for child in self.children:
            child.handle_event(event, inside)

    def update(self, tick):
        if not self.visible:
            return
        for child in self.children:
            child.update(tick)


# ================================
# Frame Class
# ================================

class Frame(Container):
    """
    A box that holds other widgets (like tkinter's Frame).
    Widgets added to a Frame are positioned from the Frame's inside corner,
    and are drawn, updated and hidden together with it.

    Parameters:
        x, y, width, height - position and size
        bg            - background colour (None = see-through)
        border_color  - border colour (border_colour also works)
        border_width  - border thickness (0 = no border)
        pad_x, pad_y  - space between the edge and the children
        center        - if True, (x, y) is the centre of the frame
        visible       - False to start hidden

    Example:
        menu = Frame(50, 50, 300, 200)
        menu.add(Label(0, 0, "Menu"), Button(0, 40, 120, 40, "Play"))
    """

    def __init__(self, x, y, width, height, bg=(60, 60, 60),
                 border_color=None, border_colour=None, border_width=2,
                 pad_x=10, pad_y=10, center=False, visible=True):
        super().__init__(x, y, width, height, bg,
                         _pick(border_color, border_colour, (200, 200, 200)),
                         border_width, pad_x, pad_y, center, visible)

    def draw(self, screen, offset=(0, 0)):
        if not self.visible:
            return
        r = self.get_rect(offset)
        if self.bg is not None:
            pg.draw.rect(screen, self.bg, r)
        if self.border_width > 0 and self.border_color:
            pg.draw.rect(screen, self.border_color, r, self.border_width)
        self.draw_children(screen, offset)


# ================================
# Popup Class
# ================================

class Popup(Container):
    """
    A pop-up window with a title bar and a close (X) button.
    It starts hidden: call show() to open it. Widgets added to it appear
    below the title bar.

    Parameters:
        x, y, width, height - position and size
        title         - words in the title bar
        fg            - title colour
        bg            - window colour
        border_color  - border colour (border_colour also works)
        border_width  - border thickness
        dim           - if True, darken the rest of the screen when open
        pad_x, pad_y  - space between the edge and the children
        center        - if True, (x, y) is the centre of the popup
        visible       - True to start open

    Example:
        message = Popup(200, 150, 300, 200, "Game Over")
        message.add(Label(0, 0, "You win!", fg=(0, 0, 0)))
        message.show()
    """

    TITLE_HEIGHT = 40

    def __init__(self, x, y, width, height, title="Popup",
                 fg=BLACK, bg=(240, 240, 240),
                 border_color=None, border_colour=None, border_width=2,
                 dim=True, pad_x=10, pad_y=0, center=False, visible=False):
        super().__init__(x, y, width, height, bg,
                         _pick(border_color, border_colour, BLACK),
                         border_width, pad_x, pad_y, center, visible)
        self.title = title
        self.fg = fg
        self.dim = dim
        self.top_space = self.TITLE_HEIGHT
        self.close_button = Button(width - 30, 10, 20, 20, "X", command=self.hide,
                                   bg=(200, 60, 60), hover_bg=(255, 80, 80),
                                   font_size=22)

    def handle_event(self, event, offset=(0, 0)):
        if not self.visible:
            return
        super().handle_event(event, offset)
        self.close_button.handle_event(event, self.get_rect(offset).topleft)

    def draw(self, screen, offset=(0, 0)):
        if not self.visible:
            return

        # Darken everything behind the popup
        if self.dim:
            overlay = pg.Surface(screen.get_size(), pg.SRCALPHA)
            overlay.fill((0, 0, 0, 120))
            screen.blit(overlay, (0, 0))

        r = self.get_rect(offset)
        pg.draw.rect(screen, self.bg, r, border_radius=10)
        if self.border_width > 0:
            pg.draw.rect(screen, self.border_color, r, self.border_width,
                         border_radius=10)

        draw_text(screen, self.title, r.x + 10, r.y + 10, fg=self.fg)
        self.draw_children(screen, offset)
        self.close_button.draw(screen, r.topleft)


# ================================
# Camera Class
# ================================

class Camera:
    """
    Scrolls the world so it follows a target (e.g. the player).

    Parameters:
        width, height - size of the whole world / map in pixels
        screen_size   - (width, height) of the window
        smooth        - how quickly it catches up each frame (0.1 = smooth,
                        1.0 = instant)

    Use camera.follow(player), call camera.update(tick) every frame, and draw
    things at camera.apply(thing.rect).
    """

    def __init__(self, width, height, screen_size, smooth=0.1):
        self.width = width
        self.height = height
        self.screen_w, self.screen_h = screen_size   # area of the world shown
        self.offset = pg.Vector2(0, 0)
        self.target = None
        self.smooth = smooth

    def follow(self, target):
        """Follow an object that has a .rect (e.g. a SpriteObject)."""
        self.target = target

    def update(self, tick=None):
        """
        Move towards the target. Pass tick so the smoothing is the same
        speed at any frame rate.
        """
        if not self.target:
            return

        # Where the camera wants to be: target in the middle of the view
        wanted = pg.Vector2(self.target.rect.centerx - self.screen_w / 2,
                            self.target.rect.centery - self.screen_h / 2)

        # Don't show past the edges of the map
        wanted.x = max(0, min(wanted.x, self.width - self.screen_w))
        wanted.y = max(0, min(wanted.y, self.height - self.screen_h))

        # Smooth follow (60 frames per second is the "normal" speed)
        amount = self.smooth
        if tick is not None:
            amount = 1 - (1 - self.smooth) ** (tick / (1000 / 60))
        self.offset += (wanted - self.offset) * min(1, amount)

    def apply(self, rect):
        """Return where a world rect appears on screen."""
        return rect.move(-self.offset.x, -self.offset.y)

    def apply_pos(self, pos):
        """Return where a world (x, y) appears on screen."""
        return (pos[0] - self.offset.x, pos[1] - self.offset.y)

    def screen_to_world(self, pos):
        """Turn a screen position (e.g. the mouse) into a world position."""
        return (pos[0] + self.offset.x, pos[1] + self.offset.y)


# ================================
# Zoom Camera Class
# ================================

class ZoomCamera:
    """
    Adds zoom to a Camera. zoom=2.0 shows things twice as big,
    zoom=0.5 shows twice as much of the world.

    Parameters:
        base_camera - the Camera to zoom
        screen_size - (width, height) of the window
        zoom        - starting zoom
        smooth      - False = crisp pixels (best for pixel art),
                      True = smooth scaling

    Use zoom_camera.update(tick) and zoom_camera.draw_world(world, screen)
    instead of the base camera's.
    """

    MIN_ZOOM = 0.3
    MAX_ZOOM = 6.0

    def __init__(self, base_camera, screen_size, zoom=2.0, smooth=False):
        self.base = base_camera
        self.screen_w, self.screen_h = screen_size
        self.smooth = smooth
        self.render = None
        self.set_zoom(zoom)

    def set_zoom(self, z):
        """Change the zoom (kept between MIN_ZOOM and MAX_ZOOM)."""
        self.zoom = max(self.MIN_ZOOM, min(self.MAX_ZOOM, z))
        # The base camera now shows a bigger or smaller part of the world
        self.base.screen_w = self.screen_w / self.zoom
        self.base.screen_h = self.screen_h / self.zoom

    def update(self, tick=None):
        self.base.update(tick)

    def screen_to_world(self, pos):
        """Turn a screen position (e.g. the mouse) into a world position."""
        return self.base.screen_to_world((pos[0] / self.zoom, pos[1] / self.zoom))

    def draw_world(self, world, screen):
        """Draw the world at the current zoom onto the screen."""
        view_size = (max(1, int(self.base.screen_w)), max(1, int(self.base.screen_h)))
        if self.render is None or self.render.get_size() != view_size:
            self.render = pg.Surface(view_size, pg.SRCALPHA)

        # Draw the visible part of the world, then scale it to fill the screen
        self.render.fill((0, 0, 0, 0))
        world.draw(self.render)
        if self.smooth:
            zoomed = pg.transform.smoothscale(self.render, (self.screen_w, self.screen_h))
        else:
            zoomed = pg.transform.scale(self.render, (self.screen_w, self.screen_h))
        screen.blit(zoomed, (0, 0))



# ================================
# Animator Class
# ================================

class Animator:
    """
    Plays animations from:
      - A list of individual images, OR
      - A sprite sheet divided into tiles.

    Supports:
      - Multiple named animations with custom frame ranges
      - Delta time frame advancement
      - Play once or looped animations
      - Flipping/inverting animations horizontally or vertically

    Parameters:
        source      - a list of image files (or Surfaces), or one sprite sheet file
        from_sheet  - True if source is a sprite sheet
        tile_width, tile_height - size of one frame on the sprite sheet
        rows, cols  - how many frames down and across the sprite sheet
        frame_rate  - frames per second
        scale       - make every frame bigger (2 = double size)

    Call animator.update(tick) every frame; it returns the image to draw.
    """

    def __init__(self, source, from_sheet=False,
                 tile_width=0, tile_height=0, rows=1, cols=1,
                 frame_rate=8, scale=1):
        self.from_sheet = from_sheet
        self.frame_rate = frame_rate
        self.scale = scale

        self.frames = []
        self.flipped_cache = {}
        self.animations = {}
        self.current_animation = None
        self.current_frame_index = 0
        self.timer = 0

        # New playback control variables
        self.playing = True
        self.loop = True
        self.image = None

        if from_sheet:
            self._load_from_sheet(source, tile_width, tile_height, rows, cols)
        else:
            self._load_from_files(source)

    # -----------------------------
    # Loading methods
    # -----------------------------
    def _load_from_files(self, file_list):
        """Load individual frame images (filenames or ready-made Surfaces)."""
        for item in file_list:
            if isinstance(item, pg.Surface):
                img = item
            else:
                img = pg.image.load(item).convert_alpha()
            if self.scale != 1:
                w, h = img.get_size()
                img = pg.transform.scale(img, (int(w * self.scale), int(h * self.scale)))
            self.frames.append(img)

        self.sheet_cols = None   # no sprite sheet: frames are numbered 0, 1, 2...
        self.animations["default"] = {"frames": list(range(len(self.frames))),
                                      "invert": (False, False)}
        self.current_animation = "default"

    def _load_from_sheet(self, filename, tile_width, tile_height, rows, cols):
        """Slice up the sprite sheet into frames."""
        sheet = pg.image.load(filename).convert_alpha()
        for row in range(rows):
            for col in range(cols):
                x, y = col * tile_width, row * tile_height
                frame = sheet.subsurface(pg.Rect(x, y, tile_width, tile_height))
                if self.scale != 1:
                    frame = pg.transform.scale(
                        frame, (int(tile_width * self.scale), int(tile_height * self.scale))
                    )
                self.frames.append(frame)

        self.sheet_cols = cols
        self.animations["default"] = {"frames": list(range(len(self.frames))),
                                      "invert": (False, False)}
        self.current_animation = "default"

    # -----------------------------
    # Animation controls
    # -----------------------------
    def add_animation(self, name, frames, invert=(False, False)):
        """
        Define an animation sequence and optional flipping.
        frames: a list of (row, col) positions on a sprite sheet,
                or a list of frame numbers, e.g. [0, 1, 2]
        invert: (flip_x, flip_y)
        """
        indices = []
        for f in frames:
            if isinstance(f, int):
                index = f
            else:
                row, col = f
                if self.sheet_cols is None:
                    raise ValueError("(row, col) frames need a sprite sheet; "
                                     "use frame numbers like [0, 1, 2] instead")
                index = row * self.sheet_cols + col
            if 0 <= index < len(self.frames):
                indices.append(index)
        self.animations[name] = {"frames": indices, "invert": invert}

    def play(self, name, reset=False):
        """
        Switch to a different animation by name.
        If reset is True, restart from frame 0.
        If reset is False and the requested animation is already current,
          do NOT reset the frame index (important for held-keys).
        """
        if name not in self.animations:
            return

        # if switching to a new animation, always reset to start
        if name != self.current_animation:
            self.current_animation = name
            self.current_frame_index = 0
            self.timer = 0
            # Switching animation always plays it looping
            # (play_once() turns looping off again straight after)
            self.playing = True
            self.loop = True
        else:
            # same animation requested; only reset if caller asked for it
            if reset:
                self.current_frame_index = 0
                self.timer = 0

    def play_once(self, name):
        """
        Play the named animation once (non-looping) from the start.
        Useful for attacks/jumps triggered by single KEYDOWN events.
        """
        if name not in self.animations:
            return
        self.play(name, reset=True)
        self.start(loop=False)

    def start(self, loop=True):
        """Begin playing the current animation."""
        self.playing = True
        self.loop = loop
        self.current_frame_index = 0
        self.timer = 0

    def stop(self):
        """Stop animation playback."""
        self.playing = False

    def update(self, tick, flip_x=False, flip_y=False):
        """
        Advance the animation and return the current frame surface.
        tick: time since last frame (e.g. from clock.tick(FPS))
        flip_x/flip_y: temporary real-time flipping override
        """
        if not self.current_animation:
            return None

        anim = self.animations[self.current_animation]
        frame_list = anim["frames"]

        if self.playing:
            # Timer counts whole milliseconds (decimals of seconds add up
            # with tiny rounding errors)
            self.timer += tick
            frame_time = 1000 / self.frame_rate
            # Keep the leftover time so the speed matches frame_rate exactly
            while self.playing and self.timer >= frame_time:
                self.timer -= frame_time
                self.current_frame_index += 1

                # Handle looping or stopping at the end
                if self.current_frame_index >= len(frame_list):
                    if self.loop:
                        self.current_frame_index = 0
                    else:
                        self.current_frame_index = len(frame_list) - 1
                        self.playing = False

        frame_index = frame_list[self.current_frame_index]
        invert_x, invert_y = anim["invert"]
        total_flip_x = invert_x ^ flip_x
        total_flip_y = invert_y ^ flip_y

        key = (frame_index, total_flip_x, total_flip_y)
        if key not in self.flipped_cache:
            frame = self.frames[frame_index]
            if total_flip_x or total_flip_y:
                frame = pg.transform.flip(frame, total_flip_x, total_flip_y)
            self.flipped_cache[key] = frame

        self.image = self.flipped_cache[key]
        return self.image

    def reset(self):
        """Restart the current animation."""
        self.current_frame_index = 0
        self.timer = 0



# ================================
# Tile Classes (made by TiledMap)
# ================================

class Tile(pg.sprite.Sprite):
    """One still map tile. TiledMap makes these for you."""

    def __init__(self, pos, image):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect(topleft=pos)

    def update(self, tick):
        pass    # still tiles don't change

    def draw(self, screen, camera=None):
        """Draw the tile. Pass the camera if the world scrolls."""
        r = camera.apply(self.rect) if camera else self.rect
        screen.blit(self.image, r)


class AnimatedTile(Tile):
    """
    A map tile that loops an Animator (water, torches, machinery...).
    TiledMap makes these for tiles animated in Tiled.
    """

    def __init__(self, pos, animator, default_animation="default"):
        self.animator = animator
        self.animator.play(default_animation)
        self.animator.start(loop=True)
        super().__init__(pos, self.animator.update(0))

    def update(self, tick):
        self.image = self.animator.update(tick)


# ================================
# TiledMap Class
# ================================

class TiledMap:
    """
    Loads a map made in Tiled (a .tmx file). Needs: pip install pytmx

    Tile layers go into map.background, or map.foreground if the layer's
    name contains "foreground" (drawn in front of sprites).
    Object layers are sorted into:
        map.spawn_points      {"player_spawn": (x, y)}  - name contains "spawn"
        map.collision_objects [{"rect": Rect, "properties": {...}}] - class "collision"
        map.triggers          [{"rect", "name", "properties"}] - class "trigger"
        map.paths             [{"points", "name", "properties"}] - polygons / polylines
        map.custom_objects    everything else
    """

    def __init__(self, filename):
        # Imported here so the rest of the library works without pytmx
        from pytmx.util_pygame import load_pygame
        self._object_classes = self._read_object_classes(filename)
        self.tmx = load_pygame(filename)

        self.tilewidth = self.tmx.tilewidth
        self.tileheight = self.tmx.tileheight

        self.width = self.tmx.width * self.tmx.tilewidth
        self.height = self.tmx.height * self.tmx.tileheight
        self.objects = list(self.tmx.objects)

        # Things found in object layers (filled in by _load_object_layers)
        self.spawn_points = {}
        self.collision_objects = []
        self.triggers = []
        self.paths = []
        self.custom_objects = []

        # Layer groups
        self.background = pg.sprite.Group()
        self.foreground = pg.sprite.Group()
        self._load_tile_layers()
        self._load_object_layers()

    # --------------------------------------------------------------
    @staticmethod
    def _read_object_classes(filename):
        """
        Read each object's "class" straight from the .tmx file, because
        some pytmx versions don't load it.
        """
        import xml.etree.ElementTree as ET
        classes = {}
        for element in ET.parse(filename).getroot().iter("object"):
            if element.get("class"):
                classes[int(element.get("id"))] = element.get("class")
        return classes

    def get_objects(self):
        return list(self.tmx.objects)

    def _load_tile_layers(self):
        for layer in self.tmx.visible_layers:
            if hasattr(layer, "tiles"):

                for x, y, surf in layer.tiles():
                    gid = layer.data[y][x]

                    # IMPORTANT: use pytmx API, never self.tmx.tiles
                    tile_props = self.tmx.get_tile_properties_by_gid(gid) or {}

                    world_pos = (x * self.tilewidth, y * self.tileheight)

                    # ----------------------------
                    # Animated tile detection
                    # ----------------------------
                    # pytmx stores Tiled animations under "frames"
                    anim = tile_props.get("frames")
                    if anim:

                        frames = []
                        durations = []

                        for f in anim:
                            frame_img = self.tmx.get_tile_image_by_gid(f.gid)
                            frames.append(frame_img)
                            durations.append(f.duration)

                        avg_duration = sum(durations) / len(durations)  # ms
                        frame_rate = 1000 / avg_duration                 # fps

                        animator = Animator(frames, from_sheet=False, frame_rate=frame_rate)
                        anim_tile = AnimatedTile(world_pos, animator)

                        if "foreground" in layer.name.lower():
                            self.foreground.add(anim_tile)
                        else:
                            self.background.add(anim_tile)

                        continue

                    # ----------------------------
                    # Static tile
                    # ----------------------------
                    tile = Tile(world_pos, surf)

                    if "foreground" in layer.name.lower():
                        self.foreground.add(tile)
                    else:
                        self.background.add(tile)

    def _load_object_layers(self):
        """Loads all objects from Tiled object layers."""
        for obj in self.objects:

            ox, oy = obj.x, obj.y
            ow, oh = getattr(obj, "width", 0), getattr(obj, "height", 0)
            props = dict(obj.properties)

            name = obj.name or ""
            # Older Tiled saves "type", Tiled 1.9+ saves "class"
            obj_type = getattr(obj, "type", None) or self._object_classes.get(obj.id, "")
            obj_type = str(obj_type).lower()
            shape = getattr(obj, "shape", None)

            # ------------- Spawn Points -------------
            if "spawn" in name.lower():
                self.spawn_points[name] = (ox, oy)
                continue

            # ------------- Collision -------------
            if obj_type == "collision":
                rect = pg.Rect(ox, oy, ow, oh)
                self.collision_objects.append({"rect": rect, "properties": props})
                continue

            # ------------- Trigger Zones -------------
            if obj_type == "trigger":
                rect = pg.Rect(ox, oy, ow, oh)
                self.triggers.append({
                    "rect": rect,
                    "name": name,
                    "properties": props
                })
                continue

            # ------------- Ellipse -------------
            if shape == "ellipse" or getattr(obj, "ellipse", False):
                self.collision_objects.append({
                    "ellipse": (ox, oy, ow, oh),
                    "properties": props
                })
                continue

            # ------------- Polygon / Polyline -------------
            # pytmx gives these a .points list (not a .shape), and the
            # points are already in map coordinates
            if shape in ("polygon", "polyline") or hasattr(obj, "points"):
                points = [(p.x, p.y) for p in obj.points]
                self.paths.append({
                    "points": points,
                    "name": name,
                    "properties": props
                })
                continue

            # ------------- Generic Custom Object -------------
            self.custom_objects.append({
                "name": name,
                "type": obj_type,
                "x": ox,
                "y": oy,
                "width": ow,
                "height": oh,
                "properties": props
            })





# ================================
# SpriteObject Class
# ================================

class SpriteObject(pg.sprite.Sprite):
    """
    A simple game object (player, enemy, coin...) with an image or Animator.

    Parameters:
        x, y          - position (top-left)
        width, height - optional size; the image is scaled to fit
        image         - a Surface or an image filename, e.g. "player.png"
        animator      - an Animator (used instead of image)
        bg            - colour of the plain box used when there is no image

    Example:
        player = SpriteObject(100, 100, image="player.png")
        player.move(5, 0)
        if player.collides_with(enemy): ...
    """

    def __init__(self, x, y, width=None, height=None, image=None, animator=None,
                 bg=(255, 0, 255)):
        super().__init__()
        self.animator = animator

        if isinstance(image, str):
            image = pg.image.load(image).convert_alpha()
        if animator:
            image = animator.frames[0]
        if image is None:
            image = pg.Surface((width or 32, height or 32))
            image.fill(bg)

        self.size = (width, height) if width and height else None
        self.image = self._fit(image)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.visible = True

    def _fit(self, image):
        """Scale the image to the size given when the sprite was made."""
        if self.size and image.get_size() != self.size:
            return pg.transform.scale(image, self.size)
        return image

    def move(self, dx, dy):
        """Move the sprite by dx, dy pixels."""
        self.rect.x += dx
        self.rect.y += dy

    def collides_with(self, other):
        """True if this sprite touches another (anything with a .rect)."""
        return self.rect.colliderect(other.rect)

    def handle_event(self, event, offset=(0, 0)):
        pass

    def update(self, tick):
        """Play the animation (if there is an Animator)."""
        if self.animator:
            self.image = self._fit(self.animator.update(tick))

    def draw(self, screen, camera=None):
        """Draw the sprite. Pass the camera if the world scrolls."""
        if not self.visible:
            return
        r = camera.apply(self.rect) if camera else self.rect
        screen.blit(self.image, r)


# ================================
# World Class
# ================================

class World:
    """
    Puts a TiledMap, a Camera and your sprites together and draws them in
    the right order: background tiles, sprites, then foreground tiles.

    Parameters:
        tiled_map - a TiledMap
        camera    - a Camera (if you use a ZoomCamera, give World the base Camera)

    Example:
        world = World(TiledMap("level1.tmx"), camera)
        world.add_sprite(player)
        world.update(tick)        # in update(tick)
        world.draw(screen)        # in draw_game()
    """

    def __init__(self, tiled_map, camera):
        self.map = tiled_map
        self.camera = camera
        self.sprites = pg.sprite.Group()

    def add_sprite(self, *sprites):
        """Add one or more sprites (player, enemies...)."""
        self.sprites.add(*sprites)

    def update(self, tick):
        """Animate tiles and sprites."""
        for tile in self.map.background:
            tile.update(tick)
        for tile in self.map.foreground:
            tile.update(tick)
        for sprite in self.sprites:
            sprite.update(tick)

    def _draw_tiles(self, screen, tiles, view):
        for tile in tiles:
            if tile.rect.colliderect(view):      # skip tiles off screen
                tile.draw(screen, self.camera)

    def draw(self, screen):
        """Draw background tiles, then sprites, then foreground tiles."""
        # The part of the world that is on screen
        view = pg.Rect(int(self.camera.offset.x), int(self.camera.offset.y),
                       screen.get_width() + 1, screen.get_height() + 1)

        self._draw_tiles(screen, self.map.background, view)
        for sprite in self.sprites:
            if hasattr(sprite, "draw"):
                sprite.draw(screen, self.camera)
            else:
                screen.blit(sprite.image, self.camera.apply(sprite.rect))
        self._draw_tiles(screen, self.map.foreground, view)


# ================================
# Joystick Manager Class
# ================================

class JoystickManager:
    """
    Reads any game controller pygame can see (Xbox, PlayStation, Switch,
    cheap USB pads, arcade sticks...).

    Every controller numbers its buttons, axes and hats differently, so:
      1. Turn on debug=True and press things to see pygame's numbers.
      2. Give those numbers names with bind_button / bind_axis / bind_hat.
      3. Read them with is_pressed("jump"), get_axis("move_x") etc.

    Parameters:
        index    - which controller to use (0 = first, 1 = second...)
        deadzone - small stick movements below this are ignored (0.0 - 1.0)
        debug    - if True, print every button / axis / hat change

    Put pad.handle_event(event) in handle_inputs()
    and pad.update(tick) at the start of update(tick).
    """

    def __init__(self, index=0, deadzone=0.15, debug=False):
        self.index = index
        self.deadzone = deadzone
        self.debug = debug
        self.joystick = None

        # Names the student gives to pygame's numbers
        self.button_binds = {}     # "jump"   -> 0
        self.axis_binds = {}       # "move_x" -> (0, invert)
        self.hat_binds = {}        # "dpad"   -> 0
        self.commands = {}         # button number -> list of functions

        # Buttons held this frame and last frame (for was_pressed)
        self._held = set()
        self._held_before = set()

        self._font = None

        if not pg.joystick.get_init():
            pg.joystick.init()
        self.connect_joystick()

    # -----------------------------
    # Connecting
    # -----------------------------
    def connect_joystick(self):
        """Connect to the controller number self.index (if plugged in)."""
        if pg.joystick.get_count() > self.index:
            self.joystick = pg.joystick.Joystick(self.index)
            self.joystick.init()
            print("Connected:", self.joystick.get_name())
        else:
            self.joystick = None
            print("No controller connected")

    @property
    def connected(self):
        """True if a controller is plugged in."""
        return self.joystick is not None

    def _is_mine(self, event):
        """True if this event came from our controller."""
        if self.joystick is None:
            return False
        if hasattr(event, "instance_id"):
            return event.instance_id == self.joystick.get_instance_id()
        return True

    # -----------------------------
    # Game loop methods
    # -----------------------------
    def handle_event(self, event):
        """Call this for every event in handle_inputs()."""
        # Controller plugged in while the game is running
        if event.type == pg.JOYDEVICEADDED:
            if self.joystick is None:
                self.connect_joystick()
            return

        # Controller unplugged
        if event.type == pg.JOYDEVICEREMOVED:
            if self.joystick is not None and \
                    event.instance_id == self.joystick.get_instance_id():
                self.joystick = None
                self._held = set()
                self._held_before = set()
                print("Controller disconnected")
            return

        if not self._is_mine(event):
            return

        if self.debug:
            self.debug_event(event)

        # Run any command= functions linked to this button
        if event.type == pg.JOYBUTTONDOWN:
            for command in self.commands.get(event.button, []):
                command()

    def update(self, tick=None):
        """Call this once per frame, at the start of update(tick)."""
        self._held_before = self._held
        self._held = set()
        if self.joystick is None:
            return
        for number in range(self.joystick.get_numbuttons()):
            if self.joystick.get_button(number):
                self._held.add(number)

    # -----------------------------
    # Linking names to numbers
    # -----------------------------
    def bind_button(self, name, number, command=None):
        """Give button `number` a name. Optional command runs when pressed."""
        self.button_binds[name] = number
        if command is not None:
            self.commands.setdefault(number, []).append(command)

    def bind_axis(self, name, number, invert=False):
        """Give axis `number` a name. invert=True flips the direction."""
        self.axis_binds[name] = (number, invert)

    def bind_hat(self, name, number):
        """Give hat (D-pad) `number` a name."""
        self.hat_binds[name] = number

    def _lookup(self, binds, name, kind):
        """Turn a name into a number. Numbers are passed straight through."""
        if isinstance(name, str):
            if name not in binds:
                raise ValueError(f"No {kind} called '{name}'. "
                                 f"Use bind_{kind}('{name}', number) first.")
            return binds[name]
        return name

    # -----------------------------
    # Reading buttons
    # -----------------------------
    def get_button(self, button):
        """True while the button is held. button can be a number or a name."""
        number = self._lookup(self.button_binds, button, "button")
        if self.joystick is None or not 0 <= number < self.joystick.get_numbuttons():
            return False
        return bool(self.joystick.get_button(number))

    def is_pressed(self, button):
        """True while the button is held down (same as get_button)."""
        return self.get_button(button)

    def was_pressed(self, button):
        """True only on the frame the button was pressed (like KEYDOWN)."""
        number = self._lookup(self.button_binds, button, "button")
        return number in self._held and number not in self._held_before

    def was_released(self, button):
        """True only on the frame the button was let go (like KEYUP)."""
        number = self._lookup(self.button_binds, button, "button")
        return number not in self._held and number in self._held_before

    # -----------------------------
    # Reading sticks and D-pads
    # -----------------------------
    def get_axis(self, axis):
        """
        Stick / trigger position from -1.0 to 1.0, with the deadzone applied.
        axis can be a number or a name.
        """
        if isinstance(axis, str):
            number, invert = self._lookup(self.axis_binds, axis, "axis")
        else:
            number, invert = axis, False

        if self.joystick is None or not 0 <= number < self.joystick.get_numaxes():
            return 0

        value = self.joystick.get_axis(number)

        # Apply deadzone, then stretch the rest so it still goes smoothly 0 -> 1
        if abs(value) < self.deadzone:
            value = 0
        else:
            sign = 1 if value > 0 else -1
            value = sign * (abs(value) - self.deadzone) / (1 - self.deadzone)
            value = max(-1.0, min(1.0, value))

        if invert:
            value = -value
        return value

    def get_hat(self, hat):
        """D-pad direction as (x, y), e.g. (-1, 0) = left. Number or name."""
        number = self._lookup(self.hat_binds, hat, "hat")
        if self.joystick is None or not 0 <= number < self.joystick.get_numhats():
            return (0, 0)
        return self.joystick.get_hat(number)

    # -----------------------------
    # Saving the student's controls
    # -----------------------------
    def save_bindings(self, filename):
        """Save the bound names to a JSON file (commands are not saved)."""
        import json
        data = {
            "buttons": self.button_binds,
            "axes": {name: list(v) for name, v in self.axis_binds.items()},
            "hats": self.hat_binds,
        }
        with open(filename, "w") as f:
            json.dump(data, f, indent=2)

    def load_bindings(self, filename):
        """Load names saved with save_bindings."""
        import json
        with open(filename) as f:
            data = json.load(f)
        self.button_binds.update(data.get("buttons", {}))
        for name, (number, invert) in data.get("axes", {}).items():
            self.axis_binds[name] = (number, invert)
        self.hat_binds.update(data.get("hats", {}))

    # -----------------------------
    # Debugging
    # -----------------------------
    def debug_event(self, event):
        """Print what pygame reports, so you can find the numbers to bind."""
        if event.type == pg.JOYBUTTONDOWN:
            print(f"Button PRESSED: {event.button}")

        elif event.type == pg.JOYBUTTONUP:
            print(f"Button RELEASED: {event.button}")

        elif event.type == pg.JOYAXISMOTION:
            # Only print significant axis movement
            if abs(event.value) > self.deadzone:
                print(f"Axis {event.axis}: {event.value:.2f}")

        elif event.type == pg.JOYHATMOTION:
            print(f"Hat {event.hat}: {event.value}")

    def draw_debug(self, screen, x=10, y=10):
        """Draw a live panel showing every button, axis and hat."""
        if self._font is None:
            self._font = get_font(None, 22)
        font = self._font
        white = (255, 255, 255)

        if self.joystick is None:
            screen.blit(font.render("No controller connected", True, white), (x, y))
            return

        js = self.joystick
        screen.blit(font.render(js.get_name(), True, white), (x, y))
        y += 28

        # Buttons: numbered circles, lit while held
        screen.blit(font.render("Buttons", True, white), (x, y))
        y += 20
        for n in range(js.get_numbuttons()):
            cx = x + 15 + (n % 8) * 36
            cy = y + 15 + (n // 8) * 36
            colour = (80, 220, 80) if js.get_button(n) else (70, 70, 70)
            pg.draw.circle(screen, colour, (cx, cy), 14)
            label = font.render(str(n), True, white)
            screen.blit(label, label.get_rect(center=(cx, cy)))
        y += ((js.get_numbuttons() + 7) // 8) * 36 + 10

        # Axes: bars from -1 to 1
        screen.blit(font.render("Axes", True, white), (x, y))
        y += 20
        for n in range(js.get_numaxes()):
            value = js.get_axis(n)
            screen.blit(font.render(f"{n}: {value:+.2f}", True, white), (x, y))
            bar = pg.Rect(x + 80, y + 2, 160, 12)
            pg.draw.rect(screen, (70, 70, 70), bar)
            mid = bar.centerx
            end = mid + int(value * bar.width / 2)
            pg.draw.rect(screen, (80, 160, 255),
                         pg.Rect(min(mid, end), bar.y, abs(end - mid) or 1, bar.height))
            y += 20
        y += 10

        # Hats (D-pads)
        screen.blit(font.render("Hats", True, white), (x, y))
        y += 20
        for n in range(js.get_numhats()):
            screen.blit(font.render(f"{n}: {js.get_hat(n)}", True, white), (x, y))
            y += 20
