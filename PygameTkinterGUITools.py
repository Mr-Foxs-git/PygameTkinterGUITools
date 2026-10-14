"""
PygameTkinterGUITools
=====================
Helper objects for making games and GUIs in pygame.

GUI widgets work like tkinter / ttk:
    Label, Button, TextBox, Checkbutton, Radiobutton, Scale, Spinbox,
    Listbox, Message, Progressbar, Combobox, Separator,
    Frame, LabelFrame, Notebook, Popup
    IntVar, StringVar, BooleanVar, DoubleVar   (shared values)
    Style                                      (colours and fonts for everything)
Game helpers: Animator, SpriteObject, Camera, ZoomCamera, TiledMap, World,
JoystickManager, KeyboardInput, MouseInput, Grid, DragObject, DragGroup,
Tooltip.
Movement: Path, PathFollower, Patrol, NavGrid, Chaser, line_of_sight,
TopDownBody, PlatformerBody, MovingPlatform.
Sound: init_audio, Audio, SoundEffect, Music.

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
Options you leave out come from the Style (see the Style class).
"""
import pygame as pg

# Some common colours
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)


# ================================
# Helper functions
# ================================

_font_cache = {}
_image_cache = {}


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


def load_image(image, size=None):
    """
    Return a Surface from a filename or Surface, scaled to size if given.
    Images are loaded once and then reused.
    """
    if image is None:
        return None
    key = (image if isinstance(image, str) else id(image), size)
    if key not in _image_cache:
        surface = pg.image.load(image).convert_alpha() if isinstance(image, str) else image
        if size and surface.get_size() != tuple(size):
            surface = pg.transform.scale(surface, (int(size[0]), int(size[1])))
        _image_cache[key] = surface
    return _image_cache[key]


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
# Variables (like tkinter IntVar, StringVar...)
# ================================

class Variable:
    """
    A value that widgets can share, like tkinter's variables.
    When one widget changes it, every widget using it shows the new value.

        volume = IntVar(50)
        Scale(50, 100, variable=volume)
        Label(50, 150, textvariable=volume)
        print(volume.get())
        volume.set(75)

    trace_add("write", function) runs function() whenever the value changes.
    """

    def __init__(self, value=None):
        self._value = self._convert(value if value is not None else self._default)
        self._callbacks = []

    _default = ""

    def _convert(self, value):
        return value

    def get(self):
        return self._value

    def set(self, value):
        value = self._convert(value)
        if value != self._value:
            self._value = value
            for callback in self._callbacks:
                callback()

    def trace_add(self, mode, callback):
        """Run callback() whenever the value is changed (mode is "write")."""
        self._callbacks.append(callback)

    def __str__(self):
        return str(self._value)


class StringVar(Variable):
    """Holds text."""
    _default = ""

    def _convert(self, value):
        return str(value)


class IntVar(Variable):
    """Holds a whole number."""
    _default = 0

    def _convert(self, value):
        return int(round(float(value)))


class DoubleVar(Variable):
    """Holds a decimal number."""
    _default = 0.0

    def _convert(self, value):
        return float(value)


class BooleanVar(Variable):
    """Holds True or False."""
    _default = False

    def _convert(self, value):
        return bool(value)


# ================================
# Style (like ttk.Style)
# ================================

# Built-in looks. "." means every widget.
THEMES = {
    "light": {
        ".": {"fg": WHITE, "bg": (60, 60, 60), "font_name": None, "font_size": 24,
              "border_color": (200, 200, 200), "border_width": 0, "border_radius": 0,
              "accent": (100, 150, 255), "trough_color": (90, 90, 90),
              "focus_color": (255, 200, 0), "select_bg": (100, 150, 255),
              "select_fg": WHITE, "disabled_fg": (140, 140, 140)},
        "Label": {"bg": None},
        "Message": {"bg": None},
        "Button": {"fg": BLACK, "bg": (100, 150, 255), "hover_bg": (150, 200, 255),
                   "font_size": 30, "border_color": None,
                   "shadow_color": (0, 0, 0, 100)},
        "TextBox": {"fg": BLACK, "bg": (230, 230, 230), "border_color": (100, 100, 100),
                    "label_fg": WHITE},
        "Checkbutton": {"bg": None, "box_bg": WHITE, "check_color": (40, 120, 220)},
        "Radiobutton": {"bg": None, "box_bg": WHITE, "check_color": (40, 120, 220)},
        "Scale": {"bg": None},
        "Spinbox": {"fg": BLACK, "bg": (230, 230, 230), "border_color": (100, 100, 100),
                    "button_bg": (190, 190, 200)},
        "Listbox": {"fg": BLACK, "bg": (230, 230, 230), "border_color": (100, 100, 100)},
        "Combobox": {"fg": BLACK, "bg": (230, 230, 230), "border_color": (100, 100, 100)},
        "Progressbar": {"bar_color": (80, 200, 120), "border_color": (200, 200, 200),
                        "border_width": 2},
        "Separator": {"fg": (150, 150, 150)},
        "Frame": {"bg": (60, 60, 60), "border_width": 2},
        "LabelFrame": {"bg": None, "border_width": 2},
        "Notebook": {"bg": (60, 60, 60), "tab_bg": (90, 90, 90), "border_width": 2},
        "Popup": {"fg": BLACK, "bg": (240, 240, 240), "border_color": BLACK,
                  "border_width": 2},
    },
    "dark": {
        ".": {"fg": (230, 230, 240), "bg": (40, 40, 50), "border_color": (90, 90, 110),
              "accent": (110, 140, 255), "trough_color": (25, 25, 32),
              "select_bg": (80, 100, 200)},
        "Button": {"fg": (230, 230, 240), "bg": (60, 70, 110), "hover_bg": (85, 100, 160),
                   "border_radius": 6},
        "TextBox": {"fg": (230, 230, 240), "bg": (25, 25, 32), "border_color": (90, 90, 110),
                    "label_fg": (230, 230, 240)},
        "Checkbutton": {"box_bg": (25, 25, 32), "check_color": (110, 140, 255)},
        "Radiobutton": {"box_bg": (25, 25, 32), "check_color": (110, 140, 255)},
        "Spinbox": {"fg": (230, 230, 240), "bg": (25, 25, 32), "button_bg": (60, 70, 110)},
        "Listbox": {"fg": (230, 230, 240), "bg": (25, 25, 32)},
        "Combobox": {"fg": (230, 230, 240), "bg": (25, 25, 32)},
        "Frame": {"bg": (40, 40, 50)},
        "Notebook": {"bg": (40, 40, 50), "tab_bg": (60, 60, 80)},
        "Popup": {"fg": (230, 230, 240), "bg": (50, 50, 64), "border_color": (110, 140, 255)},
    },
    "retro": {
        ".": {"fg": (255, 255, 255), "bg": (0, 0, 0), "border_color": (255, 255, 255),
              "border_width": 2, "border_radius": 0, "accent": (255, 60, 160),
              "trough_color": (40, 40, 40), "focus_color": (0, 255, 255),
              "select_bg": (255, 60, 160)},
        "Button": {"fg": (255, 255, 255), "bg": (0, 0, 0), "hover_bg": (255, 60, 160),
                   "border_color": (255, 255, 255), "border_width": 3},
        "TextBox": {"fg": (0, 255, 0), "bg": (0, 0, 0), "border_color": (255, 255, 255),
                    "label_fg": (255, 255, 255)},
        "Checkbutton": {"box_bg": (0, 0, 0), "check_color": (0, 255, 0)},
        "Radiobutton": {"box_bg": (0, 0, 0), "check_color": (0, 255, 0)},
        "Spinbox": {"fg": (0, 255, 0), "bg": (0, 0, 0), "button_bg": (255, 60, 160)},
        "Listbox": {"fg": (0, 255, 0), "bg": (0, 0, 0)},
        "Combobox": {"fg": (0, 255, 0), "bg": (0, 0, 0)},
        "Progressbar": {"bar_color": (255, 60, 160), "border_color": (255, 255, 255)},
        "Frame": {"bg": (0, 0, 0)},
        "Notebook": {"bg": (0, 0, 0), "tab_bg": (40, 40, 40)},
        "Popup": {"fg": (255, 255, 255), "bg": (0, 0, 0), "border_color": (255, 60, 160)},
    },
}


class Style:
    """
    Sets the colours and fonts of every widget in one place (like ttk.Style).

        style = Style()
        style.theme_use("dark")                          # "light", "dark", "retro"
        style.configure("Button", bg=(200, 50, 50), border_radius=10)
        style.configure(".", font_name="Arial")          # "." = every widget
        style.configure("Danger.Button", bg=(255, 0, 0)) # a named style...
        Button(10, 10, 100, 40, "Quit", style="Danger.Button")   # ...used here

    ttk names like "TButton" also work. Options given to a widget itself
    always win over the Style. Changes show straight away, even on widgets
    that already exist.
    """

    _theme = "light"
    _settings = {}        # shared by every Style object, like ttk

    @staticmethod
    def _name(name):
        """'TButton' -> 'Button', 'Danger.TButton' -> 'Danger.Button'."""
        parts = name.split(".")
        last = parts[-1]
        if len(last) > 1 and last[0] == "T" and last[1].isupper():
            parts[-1] = last[1:]
        return ".".join(parts) if name != "." else "."

    def configure(self, style_name, **options):
        """Set options for a widget type, e.g. configure("Button", bg=(0, 0, 0))."""
        options = {k.replace("colour", "color"): v for k, v in options.items()}
        Style._settings.setdefault(self._name(style_name), {}).update(options)

    def theme_use(self, theme_name=None):
        """Switch to a built-in theme, or return the current theme's name."""
        if theme_name is None:
            return Style._theme
        if theme_name not in THEMES:
            raise ValueError(f"No theme called '{theme_name}'. "
                             f"Choose from: {', '.join(THEMES)}")
        Style._theme = theme_name

    def theme_names(self):
        return list(THEMES)

    def reset(self):
        """Forget every configure() and go back to the light theme."""
        Style._settings = {}
        Style._theme = "light"

    @classmethod
    def lookup(cls, style_names, option):
        """Find an option: your configure() first, then the theme, then "light"."""
        theme_order = [THEMES[cls._theme]]
        if cls._theme != "light":
            theme_order.append(THEMES["light"])
        # The most specific name wins (e.g. "Label" before "." for every widget)
        for name in list(style_names) + ["."]:
            for source in [cls._settings] + theme_order:
                if option in source.get(name, {}):
                    return source[name][option]
        return None


# ================================
# Widget base class
# ================================

class Widget:
    """
    The base for every GUI object. You don't make a Widget yourself -
    every widget is built on it, so they all share these methods:

        draw(screen, offset=(0, 0))          draw it
        handle_event(event, offset=(0, 0))   react to the mouse (returns True if used)
        update(tick)                         animate it
        config(option=value, ...)            change options (like tkinter)
        cget("option")                       read an option (including Style values)
        show(), hide(), toggle_visibility()

    Options you leave out (None) come from the Style.
    offset is added to the position. Frames and Popups use it to move
    their children; you normally leave it out.
    state="disabled" greys the widget out and stops it reacting.
    """

    def __init__(self, x, y, width=0, height=0, center=False, visible=True,
                 style=None, state="normal"):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.center = center
        self.visible = visible
        self.style = style
        self.state = state
        self.focused = False        # set by FocusGroup
        self.parent = None          # the Frame / Notebook / Popup it is in
        self._last_offset = (0, 0)  # where it was last drawn (used by FocusGroup)

    # ---- position ----
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

    # ---- showing and hiding ----
    def show(self):
        self.visible = True

    def hide(self):
        self.visible = False

    def toggle_visibility(self):
        self.visible = not self.visible

    @property
    def showing(self):
        """True if the widget and everything it is inside are visible."""
        if not self.visible:
            return False
        return self.parent is None or self.parent._child_showing(self)

    def _child_showing(self, child):
        return self.showing

    @property
    def active(self):
        """True if the widget can be used (showing and not disabled)."""
        return self.showing and self.state != "disabled"

    # ---- options ----
    def _style_names(self):
        """Style names to look in, e.g. ["Danger.Button", "Button"]."""
        names = []
        if self.style:
            names.append(Style._name(self.style))
        for cls in type(self).__mro__:
            if cls is Widget:
                break
            names.append(cls.__name__)
        return names

    def cget(self, option):
        """Return an option's value: the widget's own, or else the Style's."""
        option = option.replace("colour", "color")
        value = getattr(self, option, None)
        if value is not None:
            return value
        return Style.lookup(self._style_names(), option)

    def config(self, **options):
        """
        Change options after the widget is made, like tkinter.
        Example: score_label.config(text="Score: 10", fg=(255, 0, 0))
        Set an option to None to go back to the Style's value.
        """
        for name, value in options.items():
            name = name.replace("colour", "color")
            if not hasattr(self, name):
                raise ValueError(f"{type(self).__name__} has no option '{name}'")
            setattr(self, name, value)
        self._refresh()

    configure = config      # tkinter has both names

    def _refresh(self):
        """Recalculate sizes after config(). Widgets override this."""
        pass

    def _font(self):
        return get_font(self.cget("font_name"), self.cget("font_size"))

    def _text_colour(self):
        return self.cget("disabled_fg") if self.state == "disabled" else self.cget("fg")

    # ---- keyboard focus (see FocusGroup) ----
    takes_focus = False          # True for widgets you can use with keys

    def focus_action(self, action):
        """
        Called by FocusGroup. action is "activate", "up", "down", "left" or
        "right". Return True if the widget used it.
        """
        return False

    def _draw_focus(self, screen, r):
        if self.focused:
            pg.draw.rect(screen, self.cget("focus_color"), r.inflate(8, 8), 3,
                         border_radius=6)

    # ---- game loop methods ----
    def draw(self, screen, offset=(0, 0)):
        pass

    def handle_event(self, event, offset=(0, 0)):
        return False

    def update(self, tick):
        pass


def _clicked(event, rect):
    """True if this event is a left click inside rect."""
    return (event.type == pg.MOUSEBUTTONDOWN and event.button == 1
            and rect.collidepoint(event.pos))


# ================================
# Label Class
# ================================

class Label(Widget):
    """
    Shows text on the screen (like tkinter's Label).

    Parameters:
        x, y         - position (top-left, or centre if center=True)
        text         - the words to show
        textvariable - a StringVar / IntVar to show instead of text
        fg           - text colour
        bg           - background colour behind the text (None = see-through)
        image        - optional picture (filename or Surface) shown instead of text
        font_name, font_size
        center       - if True, (x, y) is the centre of the label
        style        - a named Style, e.g. "Title.Label"

    Example:
        score = Label(20, 20, "Score: 0", fg=(255, 255, 0))
        score.config(text="Score: 10")
    """

    def __init__(self, x, y, text="", textvariable=None, fg=None, bg=None,
                 image=None, font_name=None, font_size=None,
                 center=False, visible=True, style=None):
        super().__init__(x, y, center=center, visible=visible, style=style)
        self.text = text
        self.textvariable = textvariable
        self.fg = fg
        self.bg = bg
        self.image = image
        self.font_name = font_name
        self.font_size = font_size
        self._refresh()

    def _get_text(self):
        return str(self.textvariable.get() if self.textvariable else self.text)

    def _refresh(self):
        if self.image is not None:
            self.width, self.height = load_image(self.image).get_size()
        else:
            self.width, self.height = self._font().size(self._get_text())

    def draw(self, screen, offset=(0, 0)):
        if not self.visible:
            return
        self._refresh()                      # text may have been changed directly
        r = self.get_rect(offset)
        if self.cget("bg") is not None:
            pg.draw.rect(screen, self.cget("bg"), r)
        if self.image is not None:
            screen.blit(load_image(self.image), r)
        else:
            screen.blit(self._font().render(self._get_text(), True, self.cget("fg")), r)


# ================================
# Message Class
# ================================

class Message(Widget):
    """
    Text that wraps onto several lines (like tkinter's Message).
    Good for instructions, story text and dialogue. "\\n" starts a new line.

    Parameters:
        x, y         - position
        text         - the words to show
        width        - how wide the text can be before it wraps (pixels)
        textvariable - a StringVar to show instead of text
        fg, bg       - text and background colours
        font_name, font_size
        justify      - "left", "center" or "right"
        padding      - space around the text (when there is a bg)
        center       - if True, (x, y) is the centre

    Example:
        story = Message(50, 50, "A long time ago...", width=400)
    """

    def __init__(self, x, y, text="", width=300, textvariable=None, fg=None, bg=None,
                 font_name=None, font_size=None, justify="left", padding=8,
                 line_spacing=4, center=False, visible=True, style=None):
        super().__init__(x, y, width, 0, center, visible, style)
        self.text = text
        self.textvariable = textvariable
        self.fg = fg
        self.bg = bg
        self.font_name = font_name
        self.font_size = font_size
        self.justify = justify
        self.padding = padding
        self.line_spacing = line_spacing
        self._refresh()

    def _lines(self):
        """Split the text into lines that fit inside the width."""
        font = self._font()
        text = str(self.textvariable.get() if self.textvariable else self.text)
        max_width = self.width - self.padding * 2
        lines = []
        for paragraph in text.split("\n"):
            line = ""
            for word in paragraph.split(" "):
                attempt = word if not line else line + " " + word
                if font.size(attempt)[0] <= max_width or not line:
                    line = attempt
                else:
                    lines.append(line)
                    line = word
            lines.append(line)
        return lines

    def _refresh(self):
        font = self._font()
        n = len(self._lines())
        self.height = n * font.get_height() + (n - 1) * self.line_spacing + self.padding * 2

    def draw(self, screen, offset=(0, 0)):
        if not self.visible:
            return
        self._refresh()
        r = self.get_rect(offset)
        if self.cget("bg") is not None:
            pg.draw.rect(screen, self.cget("bg"), r)
        font = self._font()
        y = r.y + self.padding
        for line in self._lines():
            surface = font.render(line, True, self.cget("fg"))
            if self.justify == "center":
                x = r.centerx - surface.get_width() // 2
            elif self.justify == "right":
                x = r.right - self.padding - surface.get_width()
            else:
                x = r.x + self.padding
            screen.blit(surface, (x, y))
            y += font.get_height() + self.line_spacing


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
        image         - picture for the button (filename or Surface), scaled to fit
        hover_image   - picture when the mouse is over it
        font_name, font_size
        border_color  - border colour (border_colour also works)
        border_width  - border thickness (0 = no border)
        border_radius - roundness of the corners
        shadow        - True to draw a shadow
        shadow_offset - (x, y) distance of the shadow
        shadow_color  - shadow colour, can include transparency (R, G, B, A)
        center        - if True, (x, y) is the centre of the button
        state         - "disabled" to grey it out
        style         - a named Style, e.g. "Danger.Button"

    Example:
        def start_game():
            print("Starting!")
        start = Button(100, 100, 150, 50, "Start", command=start_game)
    """

    takes_focus = True

    def __init__(self, x, y, width, height, text="", command=None,
                 fg=None, bg=None, hover_bg=None, image=None, hover_image=None,
                 font_name=None, font_size=None,
                 border_color=None, border_colour=None, border_width=None,
                 border_radius=None,
                 shadow=False, shadow_offset=(3, 3),
                 shadow_color=None, shadow_colour=None,
                 center=False, visible=True, state="normal", style=None):
        super().__init__(x, y, width, height, center, visible, style, state)
        self.text = text
        self.command = command
        self.fg = fg
        self.bg = bg
        self.hover_bg = hover_bg
        self.image = image
        self.hover_image = hover_image
        self.font_name = font_name
        self.font_size = font_size
        self.border_color = _pick(border_color, border_colour)
        self.border_width = border_width
        self.border_radius = border_radius
        self.shadow = shadow
        self.shadow_offset = shadow_offset
        self.shadow_color = _pick(shadow_color, shadow_colour)

    def is_hovered(self, offset=(0, 0)):
        """True if the mouse is over the button."""
        return self.active and self.get_rect(offset).collidepoint(pg.mouse.get_pos())

    def invoke(self):
        """Run the command, as if the button was clicked."""
        if self.command and self.state != "disabled":
            self.command()

    def focus_action(self, action):
        if action == "activate":
            self.invoke()
            return True
        return False

    def draw(self, screen, offset=(0, 0)):
        if not self.visible:
            return
        self._last_offset = offset
        r = self.get_rect(offset)
        hovered = self.is_hovered(offset) or self.focused
        radius = self.cget("border_radius") or 0

        if self.image is not None:
            picture = self.hover_image if hovered and self.hover_image is not None else self.image
            screen.blit(load_image(picture, r.size), r)
        else:
            # Shadow
            if self.shadow:
                shadow_surface = pg.Surface(r.size, pg.SRCALPHA)
                pg.draw.rect(shadow_surface, self.cget("shadow_color"),
                             shadow_surface.get_rect(), border_radius=radius)
                screen.blit(shadow_surface, r.move(self.shadow_offset))

            # Button
            colour = self.cget("hover_bg") if hovered else self.cget("bg")
            pg.draw.rect(screen, colour, r, border_radius=radius)

            # Border
            border_width = self.cget("border_width") or 0
            if self.cget("border_color") and border_width > 0:
                pg.draw.rect(screen, self.cget("border_color"), r,
                             width=border_width, border_radius=radius)

        # Text
        if self.text:
            text_surface = self._font().render(str(self.text), True, self._text_colour())
            screen.blit(text_surface, text_surface.get_rect(center=r.center))
        self._draw_focus(screen, r)

    def handle_event(self, event, offset=(0, 0)):
        if self.active and _clicked(event, self.get_rect(offset)):
            self.invoke()
            return True
        return False


# ================================
# Separator Class
# ================================

class Separator(Widget):
    """
    A dividing line (like ttk.Separator).

    Parameters:
        x, y    - start of the line
        length  - how long the line is
        orient  - "horizontal" or "vertical"
        fg      - line colour
        thickness - line thickness
    """

    def __init__(self, x, y, length=200, orient="horizontal", fg=None, thickness=2,
                 center=False, visible=True, style=None):
        super().__init__(x, y, center=center, visible=visible, style=style)
        self.length = length
        self.orient = orient
        self.fg = fg
        self.thickness = thickness
        self._refresh()

    def _refresh(self):
        if self.orient == "vertical":
            self.width, self.height = self.thickness, self.length
        else:
            self.width, self.height = self.length, self.thickness

    def draw(self, screen, offset=(0, 0)):
        if self.visible:
            pg.draw.rect(screen, self.cget("fg"), self.get_rect(offset))


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
        textvariable   - a StringVar that always holds the typed text
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
        state          - "disabled" to stop typing

    Example:
        def submit():
            print("Hello", name_box.get())
        name_box = TextBox(100, 100, label="Name:", on_enter=submit)
    """

    takes_focus = True

    def __init__(self, x, y, max_chars=20, text="", textvariable=None,
                 fg=None, bg=None, border_color=None, border_colour=None,
                 font_name=None, font_size=None, padding=6,
                 label=None, label_fg=None, label_gap=10, label_position="left",
                 on_enter=None, center=False, visible=True, state="normal", style=None):
        super().__init__(x, y, center=center, visible=visible, style=style, state=state)
        self.max_chars = max_chars
        self.textvariable = textvariable
        self.fg = fg
        self.bg = bg
        self.border_color = _pick(border_color, border_colour)
        self.font_name = font_name
        self.font_size = font_size
        self.padding = padding
        self.label = label
        self.label_fg = label_fg
        self.label_gap = label_gap
        self.label_position = label_position.lower()
        self.on_enter = on_enter

        self._text = ""
        self.cursor_pos = 0
        self.set_text(textvariable.get() if textvariable else text)
        self.cursor_visible = True
        self.cursor_timer = 0
        self.typing = False         # True after clicking the box
        self._refresh()

    # The text is kept in the textvariable too, if there is one
    @property
    def text(self):
        if self.textvariable is not None and self.textvariable.get() != self._text:
            self._text = str(self.textvariable.get())[:self.max_chars]
            self.cursor_pos = min(self.cursor_pos, len(self._text))
        return self._text

    @text.setter
    def text(self, value):
        self._text = str(value)[:self.max_chars]
        self.cursor_pos = min(self.cursor_pos, len(self._text))
        if self.textvariable is not None:
            self.textvariable.set(self._text)

    def _refresh(self):
        """Work out where the box and label go (relative to the top-left)."""
        font = self._font()
        box_w = self.max_chars * font.size("M")[0] + self.padding * 2
        box_h = font.get_height() + self.padding * 2

        if not self.label:
            self.box_rect = pg.Rect(0, 0, box_w, box_h)
            self.label_rect = None
            self.width, self.height = box_w, box_h
            return

        label_w, label_h = font.size(self.label)
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
        self.text = new_text
        self.cursor_pos = len(self.text)

    def clear(self):
        """Empty the box."""
        self.set_text("")

    def insert_text(self, characters):
        """Type characters at the cursor (stops at max_chars)."""
        for ch in characters:
            text = self.text
            if len(text) >= self.max_chars:
                break
            pos = self.cursor_pos
            self.text = text[:pos] + ch + text[pos:]
            self.cursor_pos = pos + 1

    # ---- keyboard ----
    def _key(self, event):
        text, pos = self.text, self.cursor_pos
        if event.key in (pg.K_RETURN, pg.K_KP_ENTER):
            if self.on_enter:
                self.on_enter()
        elif event.key == pg.K_BACKSPACE:
            if pos > 0:
                self.text = text[:pos - 1] + text[pos:]
                self.cursor_pos = pos - 1
        elif event.key == pg.K_DELETE:
            self.text = text[:pos] + text[pos + 1:]
        elif event.key == pg.K_LEFT:
            self.cursor_pos = max(0, pos - 1)
        elif event.key == pg.K_RIGHT:
            self.cursor_pos = min(len(text), pos + 1)
        elif event.key == pg.K_HOME:
            self.cursor_pos = 0
        elif event.key == pg.K_END:
            self.cursor_pos = len(text)
        elif event.key == pg.K_ESCAPE:
            self.typing = False
        elif event.unicode and event.unicode.isprintable():
            self.insert_text(event.unicode)
        else:
            return False
        return True

    def focus_action(self, action):
        if action == "activate":
            self.typing = True       # Enter / Space starts typing
            return True
        return False

    # ---- game loop methods ----
    def handle_event(self, event, offset=(0, 0)):
        if not self.active:
            self.typing = False
            return False
        box_on_screen = self.box_rect.move(self.get_rect(offset).topleft)

        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            self.typing = box_on_screen.collidepoint(event.pos)
            return self.typing

        if self.typing and event.type == pg.KEYDOWN:
            return self._key(event)
        return False

    def update(self, tick):
        """Make the cursor blink."""
        self.cursor_timer += tick
        if self.cursor_timer >= 400:
            self.cursor_timer = 0
            self.cursor_visible = not self.cursor_visible

    def draw(self, screen, offset=(0, 0)):
        if not self.visible:
            return
        self._last_offset = offset
        self._refresh()
        font = self._font()
        top_left = self.get_rect(offset).topleft

        # Label
        if self.label_rect:
            screen.blit(font.render(self.label, True, self.cget("label_fg")),
                        self.label_rect.move(top_left))

        # Box
        box = self.box_rect.move(top_left)
        pg.draw.rect(screen, self.cget("bg"), box)
        pg.draw.rect(screen, self.cget("border_color"), box, 2)

        # Text
        text_surface = font.render(self.text, True, self._text_colour())
        text_x = box.x + self.padding
        text_y = box.y + (box.height - text_surface.get_height()) // 2
        screen.blit(text_surface, (text_x, text_y))

        # Cursor
        if self.typing and self.cursor_visible:
            cursor_x = text_x + font.size(self.text[:self.cursor_pos])[0]
            pg.draw.line(screen, self.cget("fg"), (cursor_x, text_y),
                         (cursor_x, text_y + font.get_height()), 2)
        self._draw_focus(screen, box)


# ================================
# Checkbutton Class
# ================================

class Checkbutton(Widget):
    """
    A tick box with text (like tkinter's Checkbutton). Click to tick / untick.

    Parameters:
        x, y        - position
        text        - words next to the box
        variable    - a BooleanVar (or IntVar / StringVar) holding the value
        onvalue     - value when ticked (default True)
        offvalue    - value when not ticked (default False)
        command     - function to run when clicked
        fg, bg      - text colour, background behind the whole widget
        box_bg      - colour inside the box
        check_color - colour of the tick
        image, selected_image - pictures for the box (unticked / ticked)
        box_size    - size of the box (default: height of the text)
        font_name, font_size, state, style

    Example:
        music_on = BooleanVar(True)
        Checkbutton(50, 50, "Music", variable=music_on)
        if music_on.get(): ...
    """

    takes_focus = True
    _shape = "box"

    def __init__(self, x, y, text="", variable=None, onvalue=True, offvalue=False,
                 command=None, fg=None, bg=None, box_bg=None,
                 check_color=None, check_colour=None, image=None, selected_image=None,
                 box_size=None, font_name=None, font_size=None,
                 center=False, visible=True, state="normal", style=None):
        super().__init__(x, y, center=center, visible=visible, style=style, state=state)
        self.text = text
        self.variable = variable if variable is not None else BooleanVar(False)
        self.onvalue = onvalue
        self.offvalue = offvalue
        self.command = command
        self.fg = fg
        self.bg = bg
        self.box_bg = box_bg
        self.check_color = _pick(check_color, check_colour)
        self.image = image
        self.selected_image = selected_image
        self.box_size = box_size
        self.font_name = font_name
        self.font_size = font_size
        self._refresh()

    def _box(self):
        return self.box_size or self._font().get_height()

    def _refresh(self):
        box = self._box()
        text_w, text_h = self._font().size(str(self.text)) if self.text else (0, 0)
        gap = 8 if self.text else 0
        self.width = box + gap + text_w
        self.height = max(box, text_h)

    def is_selected(self):
        return self.variable.get() == self.onvalue

    def get(self):
        return self.variable.get()

    def select(self):
        self.variable.set(self.onvalue)

    def deselect(self):
        self.variable.set(self.offvalue)

    def toggle(self):
        if self.is_selected():
            self.deselect()
        else:
            self.select()

    def invoke(self):
        """Click it from code."""
        if self.state == "disabled":
            return
        self.toggle()
        if self.command:
            self.command()

    def focus_action(self, action):
        if action == "activate":
            self.invoke()
            return True
        return False

    def handle_event(self, event, offset=(0, 0)):
        if self.active and _clicked(event, self.get_rect(offset)):
            self.invoke()
            return True
        return False

    def _draw_mark(self, screen, box_rect):
        """Draw the empty box and the tick."""
        selected = self.is_selected()
        if self.image is not None:
            picture = self.selected_image if selected and self.selected_image is not None else self.image
            screen.blit(load_image(picture, box_rect.size), box_rect)
            return
        pg.draw.rect(screen, self.cget("box_bg"), box_rect, border_radius=3)
        pg.draw.rect(screen, self.cget("border_color"), box_rect, 2, border_radius=3)
        if selected:
            s = box_rect.width
            points = [(box_rect.x + s * 0.2, box_rect.y + s * 0.55),
                      (box_rect.x + s * 0.42, box_rect.y + s * 0.75),
                      (box_rect.x + s * 0.8, box_rect.y + s * 0.25)]
            pg.draw.lines(screen, self.cget("check_color"), False, points, max(2, s // 7))

    def draw(self, screen, offset=(0, 0)):
        if not self.visible:
            return
        self._last_offset = offset
        self._refresh()
        r = self.get_rect(offset)
        if self.cget("bg") is not None:
            pg.draw.rect(screen, self.cget("bg"), r)
        box = self._box()
        box_rect = pg.Rect(r.x, r.y + (r.height - box) // 2, box, box)
        self._draw_mark(screen, box_rect)
        if self.text:
            surface = self._font().render(str(self.text), True, self._text_colour())
            screen.blit(surface, (box_rect.right + 8, r.centery - surface.get_height() // 2))
        self._draw_focus(screen, r)


# ================================
# Radiobutton Class
# ================================

class Radiobutton(Checkbutton):
    """
    One choice from a group (like tkinter's Radiobutton).
    Give every Radiobutton in a group the SAME variable and a different value.

    Parameters:
        x, y      - position
        text      - words next to the circle
        variable  - the shared StringVar / IntVar
        value     - the value this button sets
        command   - function to run when chosen
        (other options are the same as Checkbutton)

    Example:
        difficulty = StringVar("Normal")
        Radiobutton(50, 50, "Easy", variable=difficulty, value="Easy")
        Radiobutton(50, 80, "Normal", variable=difficulty, value="Normal")
        Radiobutton(50, 110, "Hard", variable=difficulty, value="Hard")
    """

    def __init__(self, x, y, text="", variable=None, value=None, command=None, **options):
        if variable is None:
            variable = StringVar("")
        super().__init__(x, y, text, variable=variable, onvalue=value, command=command,
                         **options)
        self.value = value

    def is_selected(self):
        return self.variable.get() == self.value

    def invoke(self):
        if self.state == "disabled":
            return
        self.variable.set(self.value)
        if self.command:
            self.command()

    def _draw_mark(self, screen, box_rect):
        selected = self.is_selected()
        if self.image is not None:
            picture = self.selected_image if selected and self.selected_image is not None else self.image
            screen.blit(load_image(picture, box_rect.size), box_rect)
            return
        radius = box_rect.width // 2
        pg.draw.circle(screen, self.cget("box_bg"), box_rect.center, radius)
        pg.draw.circle(screen, self.cget("border_color"), box_rect.center, radius, 2)
        if selected:
            pg.draw.circle(screen, self.cget("check_color"), box_rect.center,
                           max(2, radius - 5))


# ================================
# Scale Class
# ================================

class Scale(Widget):
    """
    A slider for choosing a number (like tkinter's Scale).
    Drag the handle, or click anywhere on the bar.

    Parameters:
        x, y        - position
        from_, to   - lowest and highest values
        length      - length of the slider in pixels
        orient      - "horizontal" or "vertical"
        variable    - an IntVar / DoubleVar holding the value
        resolution  - step size (1 = whole numbers, 0.1 = one decimal place)
        command     - function to run when the value changes
        label       - optional words shown above the slider
        showvalue   - True to show the number
        fg          - text colour
        accent      - handle colour
        trough_color - colour of the bar
        thickness   - thickness of the bar
        handle_image - optional picture for the handle

    Example:
        volume = IntVar(50)
        Scale(50, 100, from_=0, to=100, variable=volume, label="Volume")
    """

    takes_focus = True

    def __init__(self, x, y, from_=0, to=100, length=200, orient="horizontal",
                 variable=None, resolution=1, command=None, label=None, showvalue=True,
                 fg=None, accent=None, trough_color=None, trough_colour=None,
                 thickness=8, handle_image=None, font_name=None, font_size=None,
                 center=False, visible=True, state="normal", style=None):
        super().__init__(x, y, center=center, visible=visible, style=style, state=state)
        self.from_ = from_
        self.to = to
        self.length = length
        self.orient = orient
        self.resolution = resolution
        if variable is None:
            whole = float(resolution or 1).is_integer()
            variable = IntVar(from_) if whole else DoubleVar(from_)
        self.variable = variable
        self.command = command
        self.label = label
        self.showvalue = showvalue
        self.fg = fg
        self.accent = accent
        self.trough_color = _pick(trough_color, trough_colour)
        self.thickness = thickness
        self.handle_image = handle_image
        self.font_name = font_name
        self.font_size = font_size
        self.dragging = False
        self._refresh()

    def _handle_radius(self):
        return self.thickness + 4

    def _text_height(self):
        return self._font().get_height() if (self.label or self.showvalue) else 0

    def _refresh(self):
        h = self._handle_radius() * 2
        if self.orient == "vertical":
            self.width = h + 60
            self.height = self.length + self._text_height() + 4
        else:
            self.width = self.length
            self.height = self._text_height() + h

    def _bar(self, r):
        """The bar's rectangle on screen."""
        top = r.y + self._text_height()
        radius = self._handle_radius()
        if self.orient == "vertical":
            return pg.Rect(r.x + radius - self.thickness // 2, top + 4,
                           self.thickness, self.length)
        return pg.Rect(r.x, top + radius - self.thickness // 2, self.length, self.thickness)

    def get(self):
        return self.variable.get()

    def set(self, value):
        """Set the value (kept between from_ and to, rounded to resolution)."""
        low, high = min(self.from_, self.to), max(self.from_, self.to)
        value = max(low, min(high, value))
        if self.resolution:
            value = round(round(value / self.resolution) * self.resolution, 10)
            if float(self.resolution).is_integer():
                value = int(value)
        old = self.variable.get()
        self.variable.set(value)
        if self.command and self.variable.get() != old:
            self.command()

    def _fraction(self):
        span = self.to - self.from_
        return 0 if span == 0 else (self.get() - self.from_) / span

    def _set_from_mouse(self, pos, offset):
        bar = self._bar(self.get_rect(offset))
        if self.orient == "vertical":
            fraction = (pos[1] - bar.y) / bar.height
        else:
            fraction = (pos[0] - bar.x) / bar.width
        fraction = max(0, min(1, fraction))
        self.set(self.from_ + fraction * (self.to - self.from_))

    def focus_action(self, action):
        step = self.resolution or (self.to - self.from_) / 20
        direction = 1 if self.to >= self.from_ else -1
        if action in ("right", "up") and self.orient == "horizontal" or \
                action == "down" and self.orient == "vertical":
            self.set(self.get() + step * direction)
            return True
        if action in ("left", "down") and self.orient == "horizontal" or \
                action == "up" and self.orient == "vertical":
            self.set(self.get() - step * direction)
            return True
        return False

    def handle_event(self, event, offset=(0, 0)):
        if not self.active:
            self.dragging = False
            return False
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            hit_area = self._bar(self.get_rect(offset)).inflate(
                self._handle_radius() * 2, self._handle_radius() * 2)
            if hit_area.collidepoint(event.pos):
                self.dragging = True
                self._set_from_mouse(event.pos, offset)
                return True
        elif event.type == pg.MOUSEMOTION and self.dragging:
            self._set_from_mouse(event.pos, offset)
            return True
        elif event.type == pg.MOUSEBUTTONUP and event.button == 1 and self.dragging:
            self.dragging = False
            return True
        return False

    def draw(self, screen, offset=(0, 0)):
        if not self.visible:
            return
        self._last_offset = offset
        self._refresh()
        r = self.get_rect(offset)
        font = self._font()
        bar = self._bar(r)

        # Label and value
        words = []
        if self.label:
            words.append(str(self.label))
        if self.showvalue:
            words.append(str(self.get()))
        if words:
            screen.blit(font.render("  ".join(words), True, self._text_colour()), r.topleft)

        # Bar, filled part and handle
        pg.draw.rect(screen, self.cget("trough_color"), bar, border_radius=self.thickness // 2)
        fraction = self._fraction()
        if self.orient == "vertical":
            filled = pg.Rect(bar.x, bar.y, bar.width, int(bar.height * fraction))
            handle = (bar.centerx, bar.y + int(bar.height * fraction))
        else:
            filled = pg.Rect(bar.x, bar.y, int(bar.width * fraction), bar.height)
            handle = (bar.x + int(bar.width * fraction), bar.centery)
        pg.draw.rect(screen, self.cget("accent"), filled, border_radius=self.thickness // 2)
        radius = self._handle_radius()
        if self.handle_image is not None:
            picture = load_image(self.handle_image, (radius * 2, radius * 2))
            screen.blit(picture, picture.get_rect(center=handle))
        else:
            pg.draw.circle(screen, self.cget("accent"), handle, radius)
            pg.draw.circle(screen, WHITE, handle, radius, 2)
        self._draw_focus(screen, bar.inflate(radius * 2, radius))


# ================================
# Spinbox Class
# ================================

class Spinbox(Widget):
    """
    A number (or choice) with up / down arrows (like tkinter's Spinbox).
    Click the arrows or scroll the mouse wheel over it.

    Parameters:
        x, y        - position
        from_, to   - lowest and highest numbers
        increment   - how much each click changes it
        values      - a list of choices to use instead of numbers,
                      e.g. ["Red", "Green", "Blue"]
        variable    - an IntVar / StringVar holding the value
        wrap        - True to go back to the start after the end
        width_chars - width of the box in letters
        command     - function to run when the value changes
        fg, bg, button_bg, border_color, font_name, font_size, state, style

    Example:
        players = IntVar(2)
        Spinbox(50, 50, from_=1, to=4, variable=players)
    """

    takes_focus = True

    def __init__(self, x, y, from_=0, to=10, increment=1, values=None, variable=None,
                 wrap=False, width_chars=4, command=None,
                 fg=None, bg=None, button_bg=None, border_color=None, border_colour=None,
                 font_name=None, font_size=None,
                 center=False, visible=True, state="normal", style=None):
        super().__init__(x, y, center=center, visible=visible, style=style, state=state)
        self.from_ = from_
        self.to = to
        self.increment = increment
        self.values = list(values) if values else None
        if variable is None:
            variable = StringVar(self.values[0]) if self.values else IntVar(from_)
        self.variable = variable
        self.wrap = wrap
        self.width_chars = width_chars
        self.command = command
        self.fg = fg
        self.bg = bg
        self.button_bg = button_bg
        self.border_color = _pick(border_color, border_colour)
        self.font_name = font_name
        self.font_size = font_size
        self._refresh()

    def _refresh(self):
        font = self._font()
        chars = self.width_chars
        if self.values:
            chars = max(chars, max(len(str(v)) for v in self.values))
        self.height = font.get_height() + 12
        self.button_w = self.height // 2 + 8
        self.width = chars * font.size("M")[0] + 12 + self.button_w

    def get(self):
        return self.variable.get()

    def set(self, value):
        old = self.variable.get()
        self.variable.set(value)
        if self.command and self.variable.get() != old:
            self.command()

    def step(self, direction):
        """Go up (direction=1) or down (direction=-1) one step."""
        if self.state == "disabled":
            return
        if self.values:
            current = str(self.get())
            index = self.values.index(current) if current in self.values else 0
            index += direction
            if self.wrap:
                index %= len(self.values)
            index = max(0, min(len(self.values) - 1, index))
            self.set(self.values[index])
        else:
            value = self.get() + direction * self.increment
            if self.wrap and value > self.to:
                value = self.from_
            elif self.wrap and value < self.from_:
                value = self.to
            self.set(max(self.from_, min(self.to, value)))

    def _buttons(self, r):
        half = r.height // 2
        up = pg.Rect(r.right - self.button_w, r.y, self.button_w, half)
        down = pg.Rect(r.right - self.button_w, r.y + half, self.button_w, r.height - half)
        return up, down

    def focus_action(self, action):
        if action in ("up", "right"):
            self.step(1)
            return True
        if action in ("down", "left"):
            self.step(-1)
            return True
        return False

    def handle_event(self, event, offset=(0, 0)):
        if not self.active:
            return False
        r = self.get_rect(offset)
        up, down = self._buttons(r)
        if _clicked(event, up):
            self.step(1)
            return True
        if _clicked(event, down):
            self.step(-1)
            return True
        if event.type == pg.MOUSEWHEEL and r.collidepoint(pg.mouse.get_pos()):
            self.step(1 if event.y > 0 else -1)
            return True
        return False

    def draw(self, screen, offset=(0, 0)):
        if not self.visible:
            return
        self._last_offset = offset
        self._refresh()
        r = self.get_rect(offset)
        pg.draw.rect(screen, self.cget("bg"), r)
        pg.draw.rect(screen, self.cget("border_color"), r, 2)
        surface = self._font().render(str(self.get()), True, self._text_colour())
        screen.blit(surface, (r.x + 6, r.centery - surface.get_height() // 2))
        for button, pointing_up in zip(self._buttons(r), (True, False)):
            pg.draw.rect(screen, self.cget("button_bg"), button)
            pg.draw.rect(screen, self.cget("border_color"), button, 1)
            cx, cy, s = button.centerx, button.centery, button.height // 4
            if pointing_up:
                points = [(cx - s, cy + s // 2), (cx + s, cy + s // 2), (cx, cy - s // 2 - 1)]
            else:
                points = [(cx - s, cy - s // 2), (cx + s, cy - s // 2), (cx, cy + s // 2 + 1)]
            pg.draw.polygon(screen, self._text_colour(), points)
        self._draw_focus(screen, r)


# ================================
# Listbox Class
# ================================

class Listbox(Widget):
    """
    A list of items you can click to choose (like tkinter's Listbox).
    Scroll with the mouse wheel when there are more items than rows.

    Parameters:
        x, y      - position
        width     - width in pixels
        rows      - how many items show at once (tkinter calls this height)
        items     - starting list of items
        command   - function to run when an item is chosen
        fg, bg, select_fg, select_bg, border_color, font_name, font_size, style

    Methods (like tkinter):
        insert("end", "Level 4")   delete(0)    get(2)    size()
        curselection()  -> (index,) of the chosen item, or ()
        selection_set(1)

    Example:
        levels = Listbox(50, 50, 200, rows=5, items=["Level 1", "Level 2"])
        chosen = levels.get_selected()      # "Level 1" or None
    """

    takes_focus = True

    def __init__(self, x, y, width=200, rows=5, items=None, command=None,
                 fg=None, bg=None, select_fg=None, select_bg=None,
                 border_color=None, border_colour=None, font_name=None, font_size=None,
                 center=False, visible=True, state="normal", style=None):
        super().__init__(x, y, width, 0, center, visible, style, state)
        self.rows = rows
        self.items = list(items) if items else []
        self.command = command
        self.fg = fg
        self.bg = bg
        self.select_fg = select_fg
        self.select_bg = select_bg
        self.border_color = _pick(border_color, border_colour)
        self.font_name = font_name
        self.font_size = font_size
        self.selected = None        # index of the chosen item
        self.scroll = 0             # index of the top item showing
        self._refresh()

    def _row_height(self):
        return self._font().get_height() + 6

    def _refresh(self):
        self.height = self.rows * self._row_height() + 4

    # ---- tkinter-style methods ----
    def insert(self, index, *items):
        """Add items. index can be a number or "end"."""
        if index == "end":
            index = len(self.items)
        for i, item in enumerate(items):
            self.items.insert(index + i, item)

    def delete(self, first, last=None):
        """Remove item first (or items first..last). "end" means the last item."""
        if first == "end":
            first = len(self.items) - 1
        if last is None:
            last = first
        elif last == "end":
            last = len(self.items) - 1
        del self.items[first:last + 1]
        if self.selected is not None and self.selected >= len(self.items):
            self.selected = None
        self.scroll = max(0, min(self.scroll, len(self.items) - self.rows))

    def get(self, index):
        return self.items[index]

    def size(self):
        return len(self.items)

    def curselection(self):
        return () if self.selected is None else (self.selected,)

    def get_selected(self):
        """The chosen item, or None."""
        return None if self.selected is None else self.items[self.selected]

    def selection_set(self, index):
        self.selected = index
        self.see(index)

    def selection_clear(self):
        self.selected = None

    def see(self, index):
        """Scroll so item index can be seen."""
        if index < self.scroll:
            self.scroll = index
        elif index >= self.scroll + self.rows:
            self.scroll = index - self.rows + 1

    def _choose(self, index):
        if 0 <= index < len(self.items):
            self.selection_set(index)
            if self.command:
                self.command()

    def focus_action(self, action):
        if not self.items:
            return False
        current = -1 if self.selected is None else self.selected
        if action == "down":
            self._choose(min(len(self.items) - 1, current + 1))
            return True
        if action == "up":
            self._choose(max(0, current - 1))
            return True
        if action == "activate" and self.selected is not None and self.command:
            self.command()
            return True
        return False

    def handle_event(self, event, offset=(0, 0)):
        if not self.active:
            return False
        r = self.get_rect(offset)
        if _clicked(event, r):
            index = self.scroll + (event.pos[1] - r.y - 2) // self._row_height()
            self._choose(index)
            return True
        if event.type == pg.MOUSEWHEEL and r.collidepoint(pg.mouse.get_pos()):
            most = max(0, len(self.items) - self.rows)
            self.scroll = max(0, min(most, self.scroll - event.y))
            return True
        return False

    def draw(self, screen, offset=(0, 0)):
        if not self.visible:
            return
        self._last_offset = offset
        self._refresh()
        r = self.get_rect(offset)
        font = self._font()
        row_h = self._row_height()
        pg.draw.rect(screen, self.cget("bg"), r)

        for row in range(self.rows):
            index = self.scroll + row
            if index >= len(self.items):
                break
            row_rect = pg.Rect(r.x + 2, r.y + 2 + row * row_h, r.width - 4, row_h)
            colour = self._text_colour()
            if index == self.selected:
                pg.draw.rect(screen, self.cget("select_bg"), row_rect)
                colour = self.cget("select_fg")
            surface = font.render(str(self.items[index]), True, colour)
            screen.blit(surface, (row_rect.x + 4, row_rect.y + 3))

        # Scroll bar (only if there are more items than rows)
        if len(self.items) > self.rows:
            track = pg.Rect(r.right - 8, r.y + 2, 6, r.height - 4)
            pg.draw.rect(screen, self.cget("trough_color"), track)
            thumb_h = max(10, track.height * self.rows // len(self.items))
            most = len(self.items) - self.rows
            thumb_y = track.y + (track.height - thumb_h) * self.scroll // most
            pg.draw.rect(screen, self.cget("accent"), (track.x, thumb_y, 6, thumb_h))

        pg.draw.rect(screen, self.cget("border_color"), r, 2)
        self._draw_focus(screen, r)


# ================================
# Combobox Class
# ================================

class Combobox(Widget):
    """
    A drop-down list (like ttk.Combobox). Click to open, click a choice.

    Draw it AFTER the widgets below it, so the open list is on top
    (inside a Frame or Notebook this is done for you).

    Parameters:
        x, y         - position
        width        - width in pixels
        values       - the choices, e.g. ["Knight", "Wizard", "Archer"]
        textvariable - a StringVar holding the chosen value
        command      - function to run when a choice is made
        max_rows     - most choices shown at once when open
        fg, bg, select_fg, select_bg, border_color, font_name, font_size, style

    Example:
        hero = StringVar("Knight")
        Combobox(50, 50, 200, values=["Knight", "Wizard", "Archer"], textvariable=hero)
    """

    takes_focus = True

    def __init__(self, x, y, width=200, values=None, textvariable=None, command=None,
                 max_rows=6, fg=None, bg=None, select_fg=None, select_bg=None,
                 border_color=None, border_colour=None, font_name=None, font_size=None,
                 center=False, visible=True, state="normal", style=None):
        super().__init__(x, y, width, 0, center, visible, style, state)
        self.values = list(values) if values else []
        if textvariable is None:
            textvariable = StringVar(self.values[0] if self.values else "")
        self.textvariable = textvariable
        self.command = command
        self.max_rows = max_rows
        self.fg = fg
        self.bg = bg
        self.select_fg = select_fg
        self.select_bg = select_bg
        self.border_color = _pick(border_color, border_colour)
        self.font_name = font_name
        self.font_size = font_size
        self.is_open = False
        self.scroll = 0
        self.highlight = 0           # choice under the mouse / arrow keys
        self._refresh()

    def _row_height(self):
        return self._font().get_height() + 8

    def _refresh(self):
        self.height = self._row_height() + 4

    def get(self):
        return self.textvariable.get()

    def set(self, value):
        self.textvariable.set(value)

    def current(self, index=None):
        """current() returns the chosen index; current(2) chooses item 2."""
        if index is None:
            value = self.get()
            return self.values.index(value) if value in self.values else -1
        self.set(self.values[index])

    def _choose(self, index):
        old = self.get()
        self.current(index)
        self.is_open = False
        if self.command and self.get() != old:
            self.command()

    def _list_rect(self, r):
        rows = min(self.max_rows, len(self.values))
        return pg.Rect(r.x, r.bottom, r.width, rows * self._row_height() + 4)

    def focus_action(self, action):
        if not self.values:
            return False
        if action == "activate":
            if self.is_open:
                self._choose(self.highlight)
            else:
                self.is_open = True
                self.highlight = max(0, self.current())
            return True
        if action in ("down", "up"):
            direction = 1 if action == "down" else -1
            if self.is_open:
                self.highlight = max(0, min(len(self.values) - 1, self.highlight + direction))
                if self.highlight < self.scroll:
                    self.scroll = self.highlight
                elif self.highlight >= self.scroll + self.max_rows:
                    self.scroll = self.highlight - self.max_rows + 1
            else:
                index = max(0, min(len(self.values) - 1, self.current() + direction))
                self._choose(index)
            return True
        return False

    def handle_event(self, event, offset=(0, 0)):
        if not self.active:
            self.is_open = False
            return False
        r = self.get_rect(offset)
        if self.is_open:
            lst = self._list_rect(r)
            if event.type == pg.MOUSEMOTION and lst.collidepoint(event.pos):
                self.highlight = self.scroll + (event.pos[1] - lst.y - 2) // self._row_height()
                return True
            if event.type == pg.MOUSEWHEEL:
                most = max(0, len(self.values) - self.max_rows)
                self.scroll = max(0, min(most, self.scroll - event.y))
                return True
            if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                if lst.collidepoint(event.pos):
                    index = self.scroll + (event.pos[1] - lst.y - 2) // self._row_height()
                    if 0 <= index < len(self.values):
                        self._choose(index)
                else:
                    self.is_open = False
                return True            # clicks while open never reach other widgets
            return False
        if _clicked(event, r) and self.values:
            self.is_open = True
            self.highlight = max(0, self.current())
            return True
        return False

    def draw(self, screen, offset=(0, 0)):
        if not self.visible:
            return
        self._last_offset = offset
        r = self.get_rect(offset)
        font = self._font()
        pg.draw.rect(screen, self.cget("bg"), r)
        pg.draw.rect(screen, self.cget("border_color"), r, 2)
        surface = font.render(str(self.get()), True, self._text_colour())
        screen.blit(surface, (r.x + 6, r.centery - surface.get_height() // 2))
        # Arrow
        cx, cy = r.right - 14, r.centery
        pg.draw.polygon(screen, self._text_colour(),
                        [(cx - 6, cy - 3), (cx + 6, cy - 3), (cx, cy + 4)])
        self._draw_focus(screen, r)
        if self.is_open:
            self.draw_overlay(screen, offset)

    def draw_overlay(self, screen, offset=(0, 0)):
        """Draw the open list (Frames call this last so it is on top)."""
        if not (self.visible and self.is_open):
            return
        r = self.get_rect(offset)
        lst = self._list_rect(r)
        font = self._font()
        row_h = self._row_height()
        pg.draw.rect(screen, self.cget("bg"), lst)
        for row in range(min(self.max_rows, len(self.values))):
            index = self.scroll + row
            if index >= len(self.values):
                break
            row_rect = pg.Rect(lst.x + 2, lst.y + 2 + row * row_h, lst.width - 4, row_h)
            colour = self.cget("fg")
            if index == self.highlight:
                pg.draw.rect(screen, self.cget("select_bg"), row_rect)
                colour = self.cget("select_fg")
            surface = font.render(str(self.values[index]), True, colour)
            screen.blit(surface, (row_rect.x + 4, row_rect.centery - surface.get_height() // 2))
        pg.draw.rect(screen, self.cget("border_color"), lst, 2)


# ================================
# Progressbar Class
# ================================

class Progressbar(Widget):
    """
    A bar that fills up (like ttk.Progressbar). Great for health, energy,
    timers and loading screens.

    Parameters:
        x, y        - position
        length      - length of the bar
        thickness   - thickness of the bar
        orient      - "horizontal" or "vertical" (vertical fills from the bottom)
        maximum     - the value that means "full"
        value       - starting value
        variable    - an IntVar / DoubleVar holding the value
        mode        - "determinate" (shows the value) or "indeterminate"
                      (a block that moves back and forth, for "loading...")
        bar_color   - colour of the filled part
        trough_color - colour of the empty part
        border_color, border_width, border_radius
        show_text   - True to show the percentage in the bar
        bar_image, trough_image - optional pictures for the full and empty parts

    Example:
        health = Progressbar(20, 20, 200, maximum=100, value=100, bar_color=(220, 50, 50))
        health.config(value=health.value - 10)     # or health.step(-10)
    """

    def __init__(self, x, y, length=200, thickness=20, orient="horizontal",
                 maximum=100, value=0, variable=None, mode="determinate",
                 bar_color=None, bar_colour=None, trough_color=None, trough_colour=None,
                 border_color=None, border_colour=None, border_width=None,
                 border_radius=None, show_text=False, fg=None,
                 bar_image=None, trough_image=None, font_name=None, font_size=None,
                 center=False, visible=True, style=None):
        super().__init__(x, y, center=center, visible=visible, style=style)
        self.length = length
        self.thickness = thickness
        self.orient = orient
        self.maximum = maximum
        self.variable = variable if variable is not None else DoubleVar(value)
        self.mode = mode
        self.bar_color = _pick(bar_color, bar_colour)
        self.trough_color = _pick(trough_color, trough_colour)
        self.border_color = _pick(border_color, border_colour)
        self.border_width = border_width
        self.border_radius = border_radius
        self.show_text = show_text
        self.fg = fg
        self.bar_image = bar_image
        self.trough_image = trough_image
        self.font_name = font_name
        self.font_size = font_size
        self.running = mode == "indeterminate"
        self._bounce = 0.0           # position of the moving block (indeterminate)
        self._refresh()

    def _refresh(self):
        if self.orient == "vertical":
            self.width, self.height = self.thickness, self.length
        else:
            self.width, self.height = self.length, self.thickness

    # value works like an option: bar.value, bar.config(value=50)
    @property
    def value(self):
        return self.variable.get()

    @value.setter
    def value(self, new_value):
        self.variable.set(max(0, min(self.maximum, new_value)))

    def step(self, amount=1):
        """Add amount to the value (use a negative number to go down)."""
        self.value = self.value + amount

    def fraction(self):
        """How full the bar is, from 0.0 to 1.0."""
        return 0 if not self.maximum else self.value / self.maximum

    def start(self):
        """Start the moving block (indeterminate mode)."""
        self.running = True

    def stop(self):
        self.running = False

    def update(self, tick):
        if self.mode == "indeterminate" and self.running:
            self._bounce = (self._bounce + tick / 1500) % 2      # 1.5 s each way

    def draw(self, screen, offset=(0, 0)):
        if not self.visible:
            return
        self._refresh()
        r = self.get_rect(offset)
        radius = self.cget("border_radius") or 0
        vertical = self.orient == "vertical"

        # Empty part
        if self.trough_image is not None:
            screen.blit(load_image(self.trough_image, r.size), r)
        else:
            pg.draw.rect(screen, self.cget("trough_color"), r, border_radius=radius)

        # Filled part
        if self.mode == "indeterminate":
            block = 0.3
            position = self._bounce if self._bounce <= 1 else 2 - self._bounce
            start, size = position * (1 - block), block
        else:
            start, size = 0, self.fraction()
        if vertical:
            fill = pg.Rect(r.x, r.bottom - int(r.height * (start + size)),
                           r.width, int(r.height * size))
        else:
            fill = pg.Rect(r.x + int(r.width * start), r.y, int(r.width * size), r.height)
        if fill.width > 0 and fill.height > 0:
            if self.bar_image is not None:
                full = load_image(self.bar_image, r.size)
                screen.blit(full, fill, area=fill.move(-r.x, -r.y))
            else:
                pg.draw.rect(screen, self.cget("bar_color"), fill, border_radius=radius)

        # Border and text
        border_width = self.cget("border_width") or 0
        if border_width and self.trough_image is None:
            pg.draw.rect(screen, self.cget("border_color"), r, border_width,
                         border_radius=radius)
        if self.show_text and self.mode == "determinate":
            font = get_font(self.cget("font_name"), max(12, min(self.cget("font_size"),
                                                                 self.thickness)))
            words = font.render(f"{int(self.fraction() * 100)}%", True, self.cget("fg"))
            screen.blit(words, words.get_rect(center=r.center))


# ================================
# Container base class (Frame, LabelFrame, Notebook, Popup)
# ================================

class Container(Widget):
    """
    The base for widgets that hold other widgets.
    Children's x, y are measured from the inside top-left corner
    (after the padding), and they move, hide and update with the container.
    """

    def __init__(self, x, y, width, height, bg=None, border_color=None, border_width=None,
                 pad_x=10, pad_y=10, center=False, visible=True, style=None):
        super().__init__(x, y, width, height, center, visible, style)
        self.bg = bg
        self.border_color = border_color
        self.border_width = border_width
        self.pad_x = pad_x
        self.pad_y = pad_y
        self.children = []
        self.top_space = 0          # extra space at the top (title bars, tabs)

    def add(self, *widgets):
        """Add one or more widgets, e.g. frame.add(label, button)."""
        for widget in widgets:
            self.children.append(widget)
            widget.parent = self
        return widgets[0] if len(widgets) == 1 else widgets

    def child_offset(self, offset=(0, 0)):
        """Where the children's (0, 0) is on screen."""
        r = self.get_rect(offset)
        return (r.x + self.pad_x, r.y + self.pad_y + self.top_space)

    def _visible_children(self):
        return self.children

    def has_open_popup(self):
        """True if a drop-down inside is open (it gets the mouse first)."""
        for child in self._visible_children():
            if getattr(child, "is_open", False):
                return True
            if isinstance(child, Container) and child.has_open_popup():
                return True
        return False

    def draw_children(self, screen, offset=(0, 0)):
        inside = self.child_offset(offset)
        children = self._visible_children()
        for child in children:
            child.draw(screen, inside)
        # Open drop-down lists are drawn last so they are on top
        for child in children:
            if hasattr(child, "draw_overlay"):
                child.draw_overlay(screen, inside)

    def draw_overlay(self, screen, offset=(0, 0)):
        if self.visible:
            inside = self.child_offset(offset)
            for child in self._visible_children():
                if hasattr(child, "draw_overlay"):
                    child.draw_overlay(screen, inside)

    def handle_event(self, event, offset=(0, 0)):
        """Pass the event to the children. Returns True if one of them used it."""
        if not self.visible:
            return False
        self._last_offset = offset
        inside = self.child_offset(offset)
        children = self._visible_children()
        # An open drop-down gets the event first
        for child in children:
            if getattr(child, "is_open", False) or \
                    (isinstance(child, Container) and child.has_open_popup()):
                return bool(child.handle_event(event, inside))
        for child in children:
            if child.handle_event(event, inside):
                return True
        return False

    def update(self, tick):
        if not self.visible:
            return
        for child in self._visible_children():
            child.update(tick)

    def _draw_box(self, screen, r, radius=0):
        if self.cget("bg") is not None:
            pg.draw.rect(screen, self.cget("bg"), r, border_radius=radius)
        border_width = self.cget("border_width") or 0
        if border_width > 0 and self.cget("border_color"):
            pg.draw.rect(screen, self.cget("border_color"), r, border_width,
                         border_radius=radius)


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
        bg            - background colour
        border_color  - border colour (border_colour also works)
        border_width  - border thickness (0 = no border)
        pad_x, pad_y  - space between the edge and the children
        center        - if True, (x, y) is the centre of the frame
        style         - a named Style, e.g. "Menu.Frame"

    Example:
        menu = Frame(50, 50, 300, 200)
        menu.add(Label(0, 0, "Menu"), Button(0, 40, 120, 40, "Play"))
    """

    def __init__(self, x, y, width, height, bg=None,
                 border_color=None, border_colour=None, border_width=None,
                 pad_x=10, pad_y=10, center=False, visible=True, style=None):
        super().__init__(x, y, width, height, bg, _pick(border_color, border_colour),
                         border_width, pad_x, pad_y, center, visible, style)

    def draw(self, screen, offset=(0, 0)):
        if not self.visible:
            return
        self._last_offset = offset
        self._draw_box(screen, self.get_rect(offset))
        self.draw_children(screen, offset)


# ================================
# LabelFrame Class
# ================================

class LabelFrame(Frame):
    """
    A Frame with a title on its border (like tkinter's LabelFrame).
    Good for grouping options, e.g. "Sound" or "Difficulty".

    Parameters: the same as Frame, plus
        text - the title
        fg   - title colour
        font_name, font_size

    Example:
        group = LabelFrame(50, 50, 250, 150, "Difficulty")
        group.add(Radiobutton(0, 0, "Easy", variable=level, value="Easy"))
    """

    def __init__(self, x, y, width, height, text="", fg=None, font_name=None,
                 font_size=None, **options):
        super().__init__(x, y, width, height, **options)
        self.text = text
        self.fg = fg
        self.font_name = font_name
        self.font_size = font_size

    def child_offset(self, offset=(0, 0)):
        x, y = super().child_offset(offset)
        return (x, y + self._font().get_height() // 2)

    def draw(self, screen, offset=(0, 0)):
        if not self.visible:
            return
        self._last_offset = offset
        r = self.get_rect(offset)
        font = self._font()
        title = font.render(str(self.text), True, self.cget("fg"))
        box = pg.Rect(r.x, r.y + title.get_height() // 2, r.width,
                      r.height - title.get_height() // 2)
        if self.cget("bg") is not None:
            pg.draw.rect(screen, self.cget("bg"), box)
        border = self.cget("border_width") or 0
        colour = self.cget("border_color")
        gap_left, gap_right = box.x + 10, box.x + 18 + title.get_width()
        if border and colour:
            # Draw the border in pieces, leaving a gap in the top line for the title
            pg.draw.line(screen, colour, box.topleft, (gap_left, box.top), border)
            if self.text:
                pg.draw.line(screen, colour, (gap_right, box.top), box.topright, border)
            else:
                pg.draw.line(screen, colour, box.topleft, box.topright, border)
            pg.draw.line(screen, colour, box.topleft, box.bottomleft, border)
            pg.draw.line(screen, colour, box.topright, box.bottomright, border)
            pg.draw.line(screen, colour, box.bottomleft, box.bottomright, border)
        if self.text:
            screen.blit(title, (gap_left + 4, r.y))
        self.draw_children(screen, offset)


# ================================
# Notebook Class
# ================================

class Notebook(Container):
    """
    Tabs, each showing a different page (like ttk.Notebook).

    Parameters:
        x, y, width, height - position and size (including the tabs)
        tab_height    - height of the tabs
        command       - function to run when the tab changes
        fg, bg, tab_bg, select_bg, border_color, border_width, font_name, font_size

    Example:
        settings = Notebook(100, 50, 400, 300)
        sound = settings.new_tab("Sound")          # returns a Frame for that tab
        sound.add(Checkbutton(0, 0, "Music", variable=music_on))
        controls = settings.new_tab("Controls")
    """

    takes_focus = True

    def __init__(self, x, y, width, height, tab_height=36, command=None,
                 fg=None, bg=None, tab_bg=None, select_bg=None,
                 border_color=None, border_colour=None, border_width=None,
                 font_name=None, font_size=None, center=False, visible=True, style=None):
        super().__init__(x, y, width, height, bg, _pick(border_color, border_colour),
                         border_width, 0, 0, center, visible, style)
        self.tab_height = tab_height
        self.command = command
        self.fg = fg
        self.tab_bg = tab_bg
        self.select_bg = select_bg
        self.font_name = font_name
        self.font_size = font_size
        self.tabs = []              # list of (text, page)
        self.selected = 0
        self.top_space = tab_height

    # ---- tkinter-style methods ----
    def add(self, page, text="Tab"):
        """Add a page (usually a Frame) as a new tab."""
        self.tabs.append((text, page))
        page.parent = self
        return page

    def _child_showing(self, child):
        return self.showing and bool(self.tabs) and self.tabs[self.selected][1] is child

    def new_tab(self, text, **frame_options):
        """Make a new tab with an empty Frame that fills it, and return the Frame."""
        frame_options.setdefault("border_width", 0)
        frame_options.setdefault("bg", None)
        page = Frame(0, 0, self.width, self.height - self.tab_height, **frame_options)
        return self.add(page, text)

    def select(self, index=None):
        """select() returns the current tab number; select(1) shows tab 1."""
        if index is None:
            return self.selected
        if 0 <= index < len(self.tabs) and index != self.selected:
            self.selected = index
            if self.command:
                self.command()

    def tab_text(self, index=None):
        return self.tabs[self.selected if index is None else index][0]

    def _visible_children(self):
        return [self.tabs[self.selected][1]] if self.tabs else []

    def _tab_rects(self, r):
        if not self.tabs:
            return []
        width = r.width // len(self.tabs)
        return [pg.Rect(r.x + i * width, r.y, width, self.tab_height)
                for i in range(len(self.tabs))]

    def focus_action(self, action):
        if action == "right":
            self.select((self.selected + 1) % len(self.tabs))
            return True
        if action == "left":
            self.select((self.selected - 1) % len(self.tabs))
            return True
        return False

    def handle_event(self, event, offset=(0, 0)):
        if not self.visible:
            return False
        if not self.has_open_popup():
            for i, tab in enumerate(self._tab_rects(self.get_rect(offset))):
                if _clicked(event, tab):
                    self.select(i)
                    return True
        return super().handle_event(event, offset)

    def draw(self, screen, offset=(0, 0)):
        if not self.visible:
            return
        self._last_offset = offset
        r = self.get_rect(offset)
        page = pg.Rect(r.x, r.y + self.tab_height, r.width, r.height - self.tab_height)
        self._draw_box(screen, page)
        font = self._font()
        for i, tab in enumerate(self._tab_rects(r)):
            colour = self.cget("bg") if i == self.selected else self.cget("tab_bg")
            pg.draw.rect(screen, colour, tab, border_top_left_radius=8,
                         border_top_right_radius=8)
            if self.cget("border_color"):
                pg.draw.rect(screen, self.cget("border_color"), tab, 1,
                             border_top_left_radius=8, border_top_right_radius=8)
            words = font.render(str(self.tabs[i][0]), True, self.cget("fg"))
            screen.blit(words, words.get_rect(center=tab.center))
        if self.focused and self.tabs:
            self._draw_focus(screen, self._tab_rects(r)[self.selected])
        self.draw_children(screen, offset)


# ================================
# Popup Class
# ================================

class Popup(Container):
    """
    A pop-up window with a title bar and a close (X) button.
    It starts hidden: call show() to open it. Widgets added to it appear
    below the title bar. Draw it last so it is on top of everything.

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

    def __init__(self, x, y, width, height, title="Popup", fg=None, bg=None,
                 border_color=None, border_colour=None, border_width=None,
                 dim=True, pad_x=10, pad_y=0, center=False, visible=False, style=None):
        super().__init__(x, y, width, height, bg, _pick(border_color, border_colour),
                         border_width, pad_x, pad_y, center, visible, style)
        self.title = title
        self.fg = fg
        self.dim = dim
        self.top_space = self.TITLE_HEIGHT
        self.close_button = Button(width - 30, 10, 20, 20, "X", command=self.hide,
                                   fg=WHITE, bg=(200, 60, 60), hover_bg=(255, 80, 80),
                                   font_size=22)

    def handle_event(self, event, offset=(0, 0)):
        if not self.visible:
            return False
        if self.close_button.handle_event(event, self.get_rect(offset).topleft):
            return True
        return super().handle_event(event, offset)

    def draw(self, screen, offset=(0, 0)):
        if not self.visible:
            return
        self._last_offset = offset

        # Darken everything behind the popup
        if self.dim:
            overlay = pg.Surface(screen.get_size(), pg.SRCALPHA)
            overlay.fill((0, 0, 0, 120))
            screen.blit(overlay, (0, 0))

        r = self.get_rect(offset)
        self._draw_box(screen, r, radius=10)
        draw_text(screen, self.title, r.x + 10, r.y + 10, fg=self.cget("fg"))
        self.draw_children(screen, offset)
        self.close_button.draw(screen, r.topleft)


# ================================
# FocusGroup Class (keyboard / controller control of widgets)
# ================================

class FocusGroup:
    """
    Lets the player use widgets with the keyboard or a controller.
    It is OFF until you set active = True, and only uses the keys you choose,
    so it won't fight with your game's controls.

    Parameters:
        *widgets - the widgets to move between, in order
        keys     - which keys to use:
                   "arrows" - arrow keys move, Enter / Space press
                   "tab"    - Tab / Shift+Tab move, Enter / Space press,
                              arrow keys only change sliders, lists etc.
                   "wasd"   - W A S D move, Enter / Space press
                   or a dict, e.g. {"next": [pg.K_DOWN], "previous": [pg.K_UP],
                   "activate": [pg.K_RETURN], "left": [pg.K_LEFT], "right": [pg.K_RIGHT]}
        active   - True to start switched on

    handle_event(event) returns True if it used the event, so you can do:
        if not menu_focus.handle_event(event):
            ...your game's own key handling...

    Example:
        menu_focus = FocusGroup(play_button, volume_slider, music_check)
        menu_focus.active = True        # e.g. only while the menu is open
    """

    KEY_SETS = {
        "arrows": {"next": [pg.K_DOWN], "previous": [pg.K_UP],
                   "left": [pg.K_LEFT], "right": [pg.K_RIGHT],
                   "activate": [pg.K_RETURN, pg.K_KP_ENTER, pg.K_SPACE]},
        "tab": {"next": [pg.K_TAB], "previous": [],          # Shift+Tab handled below
                "up": [pg.K_UP], "down": [pg.K_DOWN],
                "left": [pg.K_LEFT], "right": [pg.K_RIGHT],
                "activate": [pg.K_RETURN, pg.K_KP_ENTER, pg.K_SPACE]},
        "wasd": {"next": [pg.K_s], "previous": [pg.K_w],
                 "left": [pg.K_a], "right": [pg.K_d],
                 "activate": [pg.K_RETURN, pg.K_KP_ENTER, pg.K_SPACE]},
    }

    def __init__(self, *widgets, keys="arrows", active=False):
        self.widgets = list(widgets)
        self.keys = self.KEY_SETS[keys] if isinstance(keys, str) else keys
        self.tab_mode = keys == "tab"
        self.index = 0
        self.joystick = None
        self._active = False
        self.active = active

    # Turning it on shows the highlight; off hides it
    @property
    def active(self):
        return self._active

    @active.setter
    def active(self, on):
        self._active = on
        self._show_focus()

    def add(self, *widgets):
        self.widgets.extend(widgets)
        self._show_focus()

    def focused_widget(self):
        usable = [w for w in self.widgets if w.active]
        if not self._active or not usable:
            return None
        if not self.widgets[self.index].active:
            self.move(1)
        return self.widgets[self.index]

    def _show_focus(self):
        for i, widget in enumerate(self.widgets):
            widget.focused = self._active and i == self.index

    def focus_on(self, widget):
        """Move the highlight to this widget."""
        self.index = self.widgets.index(widget)
        self._show_focus()

    def move(self, direction):
        """Move to the next (1) or previous (-1) usable widget."""
        if not any(w.active for w in self.widgets):
            return
        for _ in range(len(self.widgets)):
            self.index = (self.index + direction) % len(self.widgets)
            if self.widgets[self.index].active:
                break
        self._show_focus()

    def use_joystick(self, joystick, hat="dpad", press_button=None, axis_x=None, axis_y=None):
        """
        Also move with a controller. hat / press_button / axis names are ones
        you bound on the JoystickManager (or raw numbers).
        Call focus.update(tick) every frame when using a joystick.
        """
        self.joystick = joystick
        self._joy = {"hat": hat, "press": press_button, "x": axis_x, "y": axis_y}
        self._joy_last = (0, 0)
        self._joy_timer = 0

    def _do(self, action):
        """Do an action: next / previous move focus, the rest go to the widget."""
        widget = self.focused_widget()
        if widget is None:
            return False
        if action in ("next", "previous"):
            direction = 1 if action == "next" else -1
            item_action = "down" if direction == 1 else "up"
            # An open drop-down: move through its choices
            if isinstance(widget, Combobox) and widget.is_open:
                return widget.focus_action(item_action)
            # A Listbox (arrows / wasd keys): move through the items, and
            # only leave the list at its first / last item
            if isinstance(widget, Listbox) and widget.items and not self.tab_mode:
                current = widget.selected
                at_edge = (current is None and direction == -1) or \
                    (current is not None and
                     (current + direction < 0 or current + direction >= len(widget.items)))
                if not at_edge:
                    return widget.focus_action(item_action)
            self.move(direction)
            return True
        return widget.focus_action(action)

    def _action_for_key(self, event):
        if self.tab_mode and event.key == pg.K_TAB and event.mod & pg.KMOD_SHIFT:
            return "previous"
        for action, key_list in self.keys.items():
            if event.key in key_list:
                return action
        return None

    def handle_event(self, event):
        """Use the event if it is one of our keys. Returns True if used."""
        if not self._active:
            return False
        widget = self.focused_widget()
        # A TextBox that is being typed in gets every key (Enter / Escape finish)
        if isinstance(widget, TextBox) and widget.typing and event.type == pg.KEYDOWN:
            widget._key(event)
            if event.key in (pg.K_RETURN, pg.K_KP_ENTER, pg.K_ESCAPE):
                widget.typing = False
            return True
        if event.type != pg.KEYDOWN:
            return False
        action = self._action_for_key(event)
        if action is None:
            return False            # not one of our keys: the game can use it
        self._do(action)
        return True

    def update(self, tick):
        """Only needed when using a joystick: reads the D-pad / stick."""
        if not (self._active and self.joystick):
            return
        joy = self._joy
        dx, dy = 0, 0
        if joy["hat"] is not None:
            try:
                dx, dy = self.joystick.get_hat(joy["hat"])
                dy = -dy                       # hat up is +1
            except ValueError:
                pass
        if joy["x"] is not None and abs(self.joystick.get_axis(joy["x"])) > 0.5:
            dx = 1 if self.joystick.get_axis(joy["x"]) > 0 else -1
        if joy["y"] is not None and abs(self.joystick.get_axis(joy["y"])) > 0.5:
            dy = 1 if self.joystick.get_axis(joy["y"]) > 0 else -1

        # Repeat while held: first move straight away, then every 200 ms
        self._joy_timer -= tick
        if (dx, dy) != self._joy_last or ((dx or dy) and self._joy_timer <= 0):
            self._joy_timer = 400 if (dx, dy) != self._joy_last else 200
            if dy > 0:
                self._do("next")
            elif dy < 0:
                self._do("previous")
            elif dx > 0:
                self._do("right")
            elif dx < 0:
                self._do("left")
        self._joy_last = (dx, dy)

        if joy["press"] is not None and self.joystick.was_pressed(joy["press"]):
            self._do("activate")


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
            if element.find("polygon") is not None:     # closed shape -> looping path
                classes.setdefault("_closed", set()).add(int(element.get("id")))
        return classes

    def get_objects(self):
        return list(self.tmx.objects)

    def get_path(self, name):
        """Return a Path drawn in Tiled, found by its name (see the Path class)."""
        for path in self.paths:
            if path["name"] == name:
                return Path.from_tiled(path)
        names = ", ".join(p["name"] or "(no name)" for p in self.paths) or "none"
        raise ValueError(f"No path called '{name}' in the map. Paths found: {names}")

    def objects_of_type(self, obj_type):
        """Every custom object with this Class / type, e.g. "enemy"."""
        return [o for o in self.custom_objects if o["type"] == obj_type.lower()]

    def rects_of_type(self, obj_type):
        """The rectangles of every object with this Class, e.g. "platform" or "ladder"."""
        return [o["rect"] for o in self.objects_of_type(obj_type)]

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
                    "type": obj_type,
                    "closed": obj.id in self._object_classes.get("_closed", set()),
                    "properties": props
                })
                continue

            # ------------- Generic Custom Object -------------
            self.custom_objects.append({
                "rect": pg.Rect(ox, oy, ow, oh),
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
        self.flip_x = False          # True = face the other way (mirror left / right)
        self.flip_y = False

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
            self.image = self._fit(self.animator.update(tick, self.flip_x, self.flip_y))

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


# ================================
# KeyboardInput Class
# ================================

class KeyboardInput:
    """
    Tells you if a key was just pressed, is being held, or was just let go.

        keys = KeyboardInput()
        keys.bind("jump", "space", "w")       # names for keys (several allowed)

        keys.handle_event(event)              # in handle_inputs()
        keys.update(tick)                     # at the START of update(tick)

        keys.was_pressed("jump")   # True for ONE frame when pressed (jump, shoot once)
        keys.is_pressed("jump")    # True EVERY frame while held (move, engine sound)
        keys.was_released("jump")  # True for ONE frame when let go
        keys.held_time("jump")     # milliseconds it has been held

    You can also use key names ("space", "a", "left", "return") or pygame keys
    (pg.K_SPACE) without binding them.
    """

    def __init__(self):
        self.binds = {}
        self._held = set()
        self._pressed = set()        # pressed this frame
        self._released = set()       # released this frame
        self._new_pressed = set()    # collected by handle_event, used next update
        self._new_released = set()
        self._held_ms = {}

    def bind(self, name, *keys):
        """Give one or more keys a name, e.g. bind("left", "a", pg.K_LEFT)."""
        self.binds[name] = [self._key_code(k) for k in keys]

    @staticmethod
    def _key_code(key):
        if isinstance(key, str):
            try:
                return pg.key.key_code(key)
            except ValueError:
                raise ValueError(f"'{key}' is not a key name. Try names like "
                                 f"'space', 'a', 'left', 'return'.") from None
        return key

    def _codes(self, key):
        if isinstance(key, str) and key in self.binds:
            return self.binds[key]
        if isinstance(key, str) and key not in self.binds and len(key) > 1 \
                and key.replace("_", "").isalpha():
            try:
                return [pg.key.key_code(key)]
            except ValueError:
                raise ValueError(f"No key called '{key}'. Use bind('{key}', key) "
                                 f"first, or a key name like 'space'.") from None
        return [self._key_code(key)]

    def handle_event(self, event):
        """Call this for every event in handle_inputs()."""
        if event.type == pg.KEYDOWN:
            self._new_pressed.add(event.key)
            self._held.add(event.key)
            self._held_ms[event.key] = 0
        elif event.type == pg.KEYUP:
            self._new_released.add(event.key)
            self._held.discard(event.key)
        elif event.type in (getattr(pg, "WINDOWFOCUSLOST", -1),):
            # Window lost focus: let go of everything so keys don't get "stuck"
            self._new_released |= self._held
            self._held = set()
        return False

    def update(self, tick=0):
        """Call this once per frame, at the START of update(tick)."""
        self._pressed, self._new_pressed = self._new_pressed, set()
        self._released, self._new_released = self._new_released, set()
        for key in self._held:
            if key not in self._pressed:
                self._held_ms[key] = self._held_ms.get(key, 0) + tick

    def is_pressed(self, key):
        """True every frame while the key (or any key with that name) is held."""
        return any(code in self._held for code in self._codes(key))

    def was_pressed(self, key):
        """True for one frame only, when the key goes down."""
        return any(code in self._pressed for code in self._codes(key))

    def was_released(self, key):
        """True for one frame only, when the key comes up."""
        return any(code in self._released for code in self._codes(key))

    def held_time(self, key):
        """How long (milliseconds) the key has been held, or 0."""
        return max([self._held_ms.get(c, 0) for c in self._codes(key) if c in self._held] or [0])

    def any_pressed(self):
        """True on the frame any key is pressed ("Press any key to start")."""
        return bool(self._pressed)


# ================================
# MouseInput Class
# ================================

class MouseInput:
    """
    Mouse buttons, position and scroll wheel - like KeyboardInput.

        mouse = MouseInput()
        mouse.bind("shoot", "left")           # "left", "middle", "right"

        mouse.handle_event(event)             # in handle_inputs()
        mouse.update(tick)                    # at the START of update(tick)

        mouse.was_pressed("shoot")  mouse.is_pressed("left")  mouse.was_released("right")
        mouse.pos       # (x, y)
        mouse.moved     # True if it moved this frame
        mouse.wheel     # scroll this frame: +1 up, -1 down, 0 none
    """

    BUTTONS = {"left": 1, "middle": 2, "right": 3}

    def __init__(self):
        self.binds = {}
        self._held = set()
        self._pressed, self._released = set(), set()
        self._new_pressed, self._new_released = set(), set()
        self._new_wheel = 0
        self._new_moved = False
        self.wheel = 0
        self.moved = False
        self._held_ms = {}

    def bind(self, name, *buttons):
        self.binds[name] = [self._code(b) for b in buttons]

    def _code(self, button):
        if isinstance(button, str):
            if button not in self.BUTTONS:
                raise ValueError(f"Mouse button must be 'left', 'middle' or 'right', "
                                 f"not '{button}'")
            return self.BUTTONS[button]
        return button

    def _codes(self, button):
        if isinstance(button, str) and button in self.binds:
            return self.binds[button]
        return [self._code(button)]

    @property
    def pos(self):
        return pg.mouse.get_pos()

    def world_pos(self, camera):
        """The mouse position in the world (when using a Camera)."""
        return camera.screen_to_world(self.pos)

    def handle_event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN and event.button in (1, 2, 3):
            self._new_pressed.add(event.button)
            self._held.add(event.button)
            self._held_ms[event.button] = 0
        elif event.type == pg.MOUSEBUTTONUP and event.button in (1, 2, 3):
            self._new_released.add(event.button)
            self._held.discard(event.button)
        elif event.type == pg.MOUSEWHEEL:
            self._new_wheel += event.y
        elif event.type == pg.MOUSEMOTION:
            self._new_moved = True
        return False

    def update(self, tick=0):
        self._pressed, self._new_pressed = self._new_pressed, set()
        self._released, self._new_released = self._new_released, set()
        self.wheel, self._new_wheel = self._new_wheel, 0
        self.moved, self._new_moved = self._new_moved, False
        for b in self._held:
            if b not in self._pressed:
                self._held_ms[b] = self._held_ms.get(b, 0) + tick

    def is_pressed(self, button):
        return any(b in self._held for b in self._codes(button))

    def was_pressed(self, button):
        return any(b in self._pressed for b in self._codes(button))

    def was_released(self, button):
        return any(b in self._released for b in self._codes(button))

    def held_time(self, button):
        return max([self._held_ms.get(b, 0) for b in self._codes(button) if b in self._held] or [0])


# ================================
# Audio (sound setup and volume)
# ================================

class Audio:
    """
    Sound setup and the volume of everything.
    Volumes are 0 - 100. If the computer has no sound output, sounds are
    simply skipped - the game still runs.

        init_audio()                     # in init_pygame(), BEFORE pg.init()
        Audio.set_music_volume(50)
        Audio.set_sfx_volume(80)
        Audio.toggle_mute()

    Link volumes to widgets (e.g. a Scale and a Checkbutton in a settings menu):
        Audio.link(music_volume=music_var, sfx_volume=sfx_var, muted=mute_var)
    """

    available = None          # None = not checked yet, then True / False
    music_volume = 70
    sfx_volume = 80
    muted = False
    _sounds = []              # every SoundEffect, so volume changes reach them
    _warned = False

    @classmethod
    def check(cls):
        """Start the mixer if needed. Returns True if sound works."""
        if cls.available is None or (cls.available and not pg.mixer.get_init()):
            try:
                if not pg.mixer.get_init():
                    pg.mixer.init()
                cls.available = True
            except pg.error as error:
                cls.available = False
                if not cls._warned:
                    print("No sound output found - sounds are turned off.", error)
                    cls._warned = True
        return cls.available

    @classmethod
    def sfx_factor(cls):
        return 0 if cls.muted else cls.sfx_volume / 100

    @classmethod
    def music_factor(cls):
        return 0 if cls.muted else cls.music_volume / 100

    @classmethod
    def _apply(cls):
        """Send the current volumes to the music and every sound effect."""
        if not cls.check():
            return
        pg.mixer.music.set_volume(Music.volume * cls.music_factor())
        for sound in cls._sounds:
            sound._apply_volume()

    @classmethod
    def set_music_volume(cls, volume):
        cls.music_volume = max(0, min(100, volume))
        cls._apply()

    @classmethod
    def set_sfx_volume(cls, volume):
        cls.sfx_volume = max(0, min(100, volume))
        cls._apply()

    @classmethod
    def set_muted(cls, muted=True):
        cls.muted = bool(muted)
        cls._apply()

    @classmethod
    def toggle_mute(cls):
        cls.set_muted(not cls.muted)

    @classmethod
    def link(cls, music_volume=None, sfx_volume=None, muted=None):
        """Link volumes to IntVars / a BooleanVar, so widgets control them."""
        if music_volume is not None:
            music_volume.trace_add("write", lambda: cls.set_music_volume(music_volume.get()))
            cls.set_music_volume(music_volume.get())
        if sfx_volume is not None:
            sfx_volume.trace_add("write", lambda: cls.set_sfx_volume(sfx_volume.get()))
            cls.set_sfx_volume(sfx_volume.get())
        if muted is not None:
            muted.trace_add("write", lambda: cls.set_muted(muted.get()))
            cls.set_muted(muted.get())


def init_audio(frequency=44100, buffer=512):
    """
    Set up sound with a short delay (so sounds play straight away when a
    key is pressed). Call it in init_pygame() BEFORE pg.init().
    """
    try:
        if pg.mixer.get_init():
            pg.mixer.quit()
        pg.mixer.pre_init(frequency, -16, 2, buffer)
        pg.mixer.init(frequency, -16, 2, buffer)
        pg.mixer.set_num_channels(32)
        Audio.available = True
    except pg.error as error:
        Audio.available = False
        print("No sound output found - sounds are turned off.", error)
        Audio._warned = True


# ================================
# SoundEffect Class
# ================================

class SoundEffect:
    """
    A short sound (jump, coin, laser...). Safe to use inside your game loop.

    Parameters:
        files       - a sound file, or a list of files (one is picked at random,
                      good for footsteps)
        volume      - 0.0 to 1.0
        cooldown    - smallest time between plays in milliseconds
                      (e.g. 150 for a laser that is held down)
        max_playing - most copies playing at once (stops sounds piling up)

    Ways to play it:
        jump.play()                        play now (respects cooldown / max_playing)
        coin.play_on(touching_coin)        play only when the True/False value
                                           CHANGES to True - safe to call every frame
        engine.play_while(thrust_held)     loop while True, stop when False -
                                           safe to call every frame

    Example:
        jump = SoundEffect("jump.wav")
        if keys.was_pressed("jump"):
            jump.play()
    """

    def __init__(self, files, volume=1.0, cooldown=0, max_playing=None):
        self.files = [files] if isinstance(files, str) else list(files)
        self.volume = volume
        self.cooldown = cooldown
        self.max_playing = max_playing
        self._sounds = []
        self._channels = []
        self._last_play = -10 ** 9
        self._last_condition = False
        self._loop_channel = None
        if Audio.check():
            for f in self.files:
                self._sounds.append(pg.mixer.Sound(f))
        Audio._sounds.append(self)
        self._apply_volume()

    def _apply_volume(self):
        for sound in self._sounds:
            sound.set_volume(self.volume * Audio.sfx_factor())

    def set_volume(self, volume):
        """Change this sound's volume (0.0 to 1.0)."""
        self.volume = max(0.0, min(1.0, volume))
        self._apply_volume()

    def _playing_channels(self):
        self._channels = [c for c in self._channels if c is not None and c.get_busy()]
        return self._channels

    def is_playing(self):
        return bool(self._playing_channels())

    def play(self, loops=0):
        """Play the sound. Returns False if it was skipped (cooldown / limit / no sound)."""
        if not self._sounds:
            return False
        now = pg.time.get_ticks()
        if now - self._last_play < self.cooldown:
            return False
        if self.max_playing is not None and len(self._playing_channels()) >= self.max_playing:
            return False
        import random
        channel = random.choice(self._sounds).play(loops)
        if channel is None:              # every channel busy
            return False
        self._channels.append(channel)
        self._last_play = now
        return True

    def play_on(self, condition):
        """
        Play once each time condition changes from False to True.
        Call it every frame, e.g. coin_sound.play_on(player.collides_with(coin)).
        """
        played = False
        if condition and not self._last_condition:
            played = self.play()
        self._last_condition = bool(condition)
        return played

    def play_while(self, condition, fade_ms=60):
        """
        Loop the sound while condition is True and stop it when False.
        Call it every frame, e.g. engine.play_while(keys.is_pressed("thrust")).
        """
        looping = self._loop_channel is not None and self._loop_channel.get_busy()
        if condition and not looping and self._sounds:
            self._loop_channel = self._sounds[0].play(-1)
        elif not condition and looping:
            self._loop_channel.fadeout(fade_ms)
            self._loop_channel = None

    def stop(self):
        """Stop every copy of this sound."""
        for channel in self._playing_channels():
            channel.stop()
        if self._loop_channel is not None:
            self._loop_channel.stop()
            self._loop_channel = None

    def fadeout(self, ms=300):
        for channel in self._playing_channels():
            channel.fadeout(ms)
        if self._loop_channel is not None:
            self._loop_channel.fadeout(ms)
            self._loop_channel = None


# ================================
# Music Class (background music)
# ================================

class Music:
    """
    Background music. Plays one track at a time, streamed from the file
    (so long songs don't use much memory). Use it straight from the class:

        Music.play("menu.wav", fade_ms=1000)    # loops forever by default
        Music.switch("level1.wav", fade_ms=800) # fade out, then the new track
        Music.pause()   Music.unpause()   Music.stop(fade_ms=500)
        Music.playlist(["track1.wav", "track2.wav"], shuffle=True)

    Call Music.update(tick) in update(tick) when you use switch() or playlist().
    """

    volume = 1.0          # this track's volume (0.0 - 1.0), Audio sets the overall level
    current = None
    _next = None          # (file, loops, fade_in) waiting for a fade out to finish
    _fade_left = 0
    _playlist = []
    _playlist_index = 0
    _shuffle = False
    _paused = False

    @classmethod
    def play(cls, file, loops=-1, fade_ms=0, volume=None):
        """Play a track. loops=-1 repeats forever, 0 plays once."""
        if volume is not None:
            cls.volume = volume
        cls._next = None
        if not Audio.check():
            cls.current = file
            return
        pg.mixer.music.load(file)
        pg.mixer.music.set_volume(cls.volume * Audio.music_factor())
        pg.mixer.music.play(loops, fade_ms=fade_ms)
        cls.current = file
        cls._paused = False

    @classmethod
    def switch(cls, file, fade_ms=800, loops=-1):
        """Fade out the current track, then fade in a new one."""
        if file == cls.current and cls.is_playing():
            return
        cls._playlist = []
        if not (Audio.check() and pg.mixer.music.get_busy()):
            cls.play(file, loops, fade_ms)
            return
        pg.mixer.music.fadeout(fade_ms)
        cls._next = (file, loops, fade_ms)
        cls._fade_left = fade_ms

    @classmethod
    def playlist(cls, files, shuffle=False):
        """Play a list of tracks one after another (forever)."""
        import random
        cls._playlist = list(files)
        cls._shuffle = shuffle
        if shuffle:
            random.shuffle(cls._playlist)
        cls._playlist_index = 0
        cls.play(cls._playlist[0], loops=0)
        cls._playlist = list(cls._playlist)

    @classmethod
    def update(cls, tick=0):
        """Needed for switch() and playlist(): starts the next track at the right time."""
        if not Audio.check():
            return
        if cls._next is not None:
            cls._fade_left -= tick
            if cls._fade_left <= 0 or not pg.mixer.music.get_busy():
                file, loops, fade_ms = cls._next
                cls.play(file, loops, fade_ms)
        elif cls._playlist and not cls._paused and not pg.mixer.music.get_busy():
            import random
            cls._playlist_index += 1
            if cls._playlist_index >= len(cls._playlist):
                cls._playlist_index = 0
                if cls._shuffle:
                    random.shuffle(cls._playlist)
            playlist = cls._playlist
            cls.play(playlist[cls._playlist_index], loops=0)
            cls._playlist = playlist

    @classmethod
    def pause(cls):
        if Audio.check():
            pg.mixer.music.pause()
        cls._paused = True

    @classmethod
    def unpause(cls):
        if Audio.check():
            pg.mixer.music.unpause()
        cls._paused = False

    @classmethod
    def stop(cls, fade_ms=0):
        cls._next = None
        cls._playlist = []
        cls.current = None
        if Audio.check():
            if fade_ms:
                pg.mixer.music.fadeout(fade_ms)
            else:
                pg.mixer.music.stop()

    @classmethod
    def set_volume(cls, volume):
        """This track's volume, 0.0 - 1.0 (Audio.set_music_volume is the overall level)."""
        cls.volume = max(0.0, min(1.0, volume))
        Audio._apply()

    @classmethod
    def is_playing(cls):
        return bool(Audio.check() and pg.mixer.music.get_busy() and not cls._paused)


# ================================
# Grid Class
# ================================

class Grid:
    """
    A grid of cells for inventories, board games, puzzles and level editors.
    DragObjects given this grid snap into its cells when dropped.

    Parameters:
        x, y          - top-left corner
        cols, rows    - number of columns and rows
        cell_size     - size of each cell: 64, or (width, height)
        show_lines    - draw the grid lines
        line_color    - colour of the lines
        bg            - colour behind the grid (None = see-through)
        one_per_cell  - True: only one item can be in each cell
        snap          - True: dropped items snap to the middle of a cell
        highlight     - True: show the cell a dragged item will drop into
        good_color, bad_color - highlight colours (can drop / can't drop)
        accepts       - which items the whole grid takes: None (anything),
                        a kind ("potion"), a list of kinds, or a function
                        given the item that returns True / False

    Slots (one cell with its own rule, e.g. an equipment slot):
        equipment.set_slot(0, 0, accepts="sword", label="Sword")
        equipment.set_slot(0, 1, accepts=["helmet", "hat"], image="helmet_outline.png")

    Example:
        board = Grid(100, 100, cols=8, rows=8, cell_size=64)
        board.place(king, 4, 0)
        board.cell_at(mouse.pos)       # -> (col, row) or None
    """

    def __init__(self, x, y, cols, rows, cell_size=64, show_lines=True,
                 line_color=None, line_colour=None, bg=None, one_per_cell=True,
                 snap=True, highlight=True, good_color=(80, 220, 120, 90),
                 bad_color=(230, 70, 70, 90), accepts=None):
        self.x, self.y = x, y
        self.cols, self.rows = cols, rows
        if isinstance(cell_size, (int, float)):
            cell_size = (cell_size, cell_size)
        self.cell_w, self.cell_h = cell_size
        self.show_lines = show_lines
        self.line_color = _pick(line_color, line_colour, (120, 120, 140))
        self.bg = bg
        self.one_per_cell = one_per_cell
        self.snap = snap
        self.highlight = highlight
        self.good_color = good_color
        self.bad_color = bad_color
        self.accepts = accepts
        self.slots = {}            # (col, row) -> {"accepts", "label", "image"}
        self.items = {}            # (col, row) -> item
        self.hover_cell = None     # set by a DragObject while it is dragged
        self.hover_item = None

    @property
    def rect(self):
        return pg.Rect(self.x, self.y, self.cols * self.cell_w, self.rows * self.cell_h)

    # ---- cells ----
    def cell_at(self, pos):
        """The (col, row) at a screen position, or None if outside the grid."""
        col = int((pos[0] - self.x) // self.cell_w)
        row = int((pos[1] - self.y) // self.cell_h)
        if 0 <= col < self.cols and 0 <= row < self.rows:
            return (col, row)
        return None

    def cell_rect(self, col, row):
        return pg.Rect(self.x + col * self.cell_w, self.y + row * self.cell_h,
                       self.cell_w, self.cell_h)

    def cell_center(self, col, row):
        return self.cell_rect(col, row).center

    def all_cells(self):
        return [(c, r) for r in range(self.rows) for c in range(self.cols)]

    # ---- items ----
    def item_at(self, col, row):
        return self.items.get((col, row))

    def is_free(self, col, row):
        return (col, row) not in self.items

    def cell_of(self, item):
        """The cell an item is in, or None."""
        for cell, other in self.items.items():
            if other is item:
                return cell
        return None

    def set_slot(self, col, row, accepts=None, label=None, image=None):
        """
        Give one cell its own rule. label / image are shown (faded) while
        the slot is empty, so players know what goes there.
        """
        self.slots[(col, row)] = {"accepts": accepts, "label": label, "image": image}

    @staticmethod
    def _allowed(item, rule):
        """Check an item against an accepts rule (None, kind, list or function)."""
        if rule is None:
            return True
        if callable(rule):
            return bool(rule(item))
        kinds = getattr(item, "kinds", ())
        rules = [rule] if isinstance(rule, str) else list(rule)
        return any(r in kinds for r in rules)

    def accepts_item(self, item, col, row):
        """True if the grid and the slot both allow this item."""
        slot = self.slots.get((col, row))
        return self._allowed(item, self.accepts) and \
            (slot is None or self._allowed(item, slot["accepts"]))

    def can_place(self, item, col, row):
        """True if item is allowed in this cell (inside, right kind, and free)."""
        if not (0 <= col < self.cols and 0 <= row < self.rows):
            return False
        if item is not None and not self.accepts_item(item, col, row):
            return False
        other = self.items.get((col, row))
        return other is None or other is item or not self.one_per_cell

    def place(self, item, col, row):
        """Put an item in a cell (moving it there). Returns False if not allowed."""
        if not self.can_place(item, col, row):
            return False
        self.remove(item)
        if self.one_per_cell or (col, row) not in self.items:
            self.items[(col, row)] = item
        if self.snap and hasattr(item, "rect"):
            item.rect.center = self.cell_center(col, row)
        if hasattr(item, "cell"):
            item.cell = (col, row)
            item.grid = self
        return True

    def remove(self, item):
        """Take an item out of the grid (it stays where it is on screen)."""
        cell = self.cell_of(item)
        if cell is not None:
            del self.items[cell]
            if hasattr(item, "cell"):
                item.cell = None
                item.grid = None

    def clear(self):
        self.items = {}

    def first_free_cell(self):
        for cell in self.all_cells():
            if self.is_free(*cell):
                return cell
        return None

    # ---- drawing ----
    def draw(self, screen):
        r = self.rect
        if self.bg is not None:
            pg.draw.rect(screen, self.bg, r)
        # Empty slots show what goes in them (faded)
        for cell, slot in self.slots.items():
            if cell in self.items:
                continue
            cell_rect = self.cell_rect(*cell)
            if slot["image"] is not None:
                picture = load_image(slot["image"], (self.cell_w * 3 // 4, self.cell_h * 3 // 4)).copy()
                picture.set_alpha(90)
                screen.blit(picture, picture.get_rect(center=cell_rect.center))
            if slot["label"]:
                words = get_font(None, 18).render(str(slot["label"]), True, (170, 170, 170))
                screen.blit(words, words.get_rect(midbottom=(cell_rect.centerx, cell_rect.bottom - 3)))
        if self.highlight and self.hover_cell is not None:
            good = self.can_place(self.hover_item, *self.hover_cell)
            shade = pg.Surface((self.cell_w, self.cell_h), pg.SRCALPHA)
            shade.fill(self.good_color if good else self.bad_color)
            screen.blit(shade, self.cell_rect(*self.hover_cell))
        if self.show_lines:
            for c in range(self.cols + 1):
                x = self.x + c * self.cell_w
                pg.draw.line(screen, self.line_color, (x, r.top), (x, r.bottom))
            for row in range(self.rows + 1):
                y = self.y + row * self.cell_h
                pg.draw.line(screen, self.line_color, (r.left, y), (r.right, y))


# ================================
# DragObject Class
# ================================

class DragObject(SpriteObject):
    """
    A sprite you can pick up and move with the mouse.

    Parameters:
        x, y, width, height, image, animator, bg - the same as SpriteObject
        grid        - a Grid to snap into when dropped, or a list of Grids
                      (e.g. [inventory, equipment]) it can move between
        bounds      - a pg.Rect it must stay inside (optional)
        on_pick_up  - function to run when it is picked up
        on_drop     - function to run when it is dropped
        return_if_invalid - True: go back to where it started if dropped
                            outside the grid / on a taken cell
        button      - mouse button to drag with: "left" or "right"
        kind        - what sort of item it is, e.g. "sword", or a list like
                      ["armor", "helmet"]. Grids / slots use this in accepts=
        stats       - a dictionary of anything you like, e.g.
                      {"damage": 5, "weight": 2, "rarity": "rare"}
                      (also usable as item.stats["damage"])

    Attributes:
        dragging    - True while it is being held
        cell        - (col, row) in its grid, or None
        grid        - the Grid it is in now, or None

    Use a DragGroup when you have several, so only the top one is picked up.

    Example:
        sword = DragObject(50, 50, image="sword.png", grid=inventory)
        inventory.place(sword, 0, 0)
    """

    def __init__(self, x, y, width=None, height=None, image=None, animator=None,
                 bg=(255, 0, 255), grid=None, bounds=None, on_pick_up=None, on_drop=None,
                 return_if_invalid=True, button="left", enabled=True, kind=None,
                 stats=None, name=None):
        super().__init__(x, y, width, height, image, animator, bg)
        if kind is None:
            self.kinds = []
        elif isinstance(kind, str):
            self.kinds = [kind]
        else:
            self.kinds = list(kind)
        self.stats = dict(stats) if stats else {}
        self.name = name
        if grid is None:
            self.grids = []
        elif isinstance(grid, (list, tuple)):
            self.grids = list(grid)
        else:
            self.grids = [grid]
        self.grid = None            # the grid it is in (set by Grid.place)
        self.bounds = bounds
        self.on_pick_up = on_pick_up
        self.on_drop = on_drop
        self.return_if_invalid = return_if_invalid
        self.button = MouseInput.BUTTONS.get(button, button)
        self.enabled = enabled
        self.dragging = False
        self.cell = None
        self.start_pos = self.rect.topleft
        self._grab = (0, 0)

    @property
    def kind(self):
        """The first kind (or None)."""
        return self.kinds[0] if self.kinds else None

    def is_kind(self, kind):
        """True if the item is this kind, e.g. item.is_kind("weapon")."""
        return kind in self.kinds

    def pick_up(self, mouse_pos):
        self.dragging = True
        self.start_pos = self.rect.topleft
        self._start_cell = self.cell
        self._start_grid = self.grid
        self._grab = (mouse_pos[0] - self.rect.x, mouse_pos[1] - self.rect.y)
        if self.on_pick_up:
            self.on_pick_up()

    def return_to_start(self):
        """Go back to where it was picked up from."""
        self.rect.topleft = self.start_pos
        start_grid = getattr(self, "_start_grid", None)
        if start_grid is not None and self._start_cell is not None:
            start_grid.place(self, *self._start_cell)

    def _move_to_mouse(self, mouse_pos):
        self.rect.topleft = (mouse_pos[0] - self._grab[0], mouse_pos[1] - self._grab[1])
        if self.bounds is not None:
            self.rect.clamp_ip(self.bounds)
        for grid in self.grids:
            grid.hover_cell = grid.cell_at(self.rect.center)
            grid.hover_item = self

    def drop(self):
        self.dragging = False
        if self.grids:
            for grid in self.grids:
                grid.hover_cell = None
            # Find the grid (and cell) under the middle of the object
            target = None
            for grid in self.grids:
                cell = grid.cell_at(self.rect.center)
                if cell is not None:
                    target = (grid, cell)
                    break
            if target and target[0].can_place(self, *target[1]):
                if self.grid is not None and self.grid is not target[0]:
                    self.grid.remove(self)
                target[0].place(self, *target[1])
            elif self.return_if_invalid:
                self.return_to_start()
            elif self.grid is not None:
                self.grid.remove(self)      # left outside the grid
        if self.on_drop:
            self.on_drop()

    def handle_event(self, event, offset=(0, 0)):
        """Returns True if this object used the event."""
        if not (self.enabled and self.visible):
            return False
        if event.type == pg.MOUSEBUTTONDOWN and event.button == self.button \
                and self.rect.collidepoint(event.pos):
            self.pick_up(event.pos)
            return True
        if event.type == pg.MOUSEMOTION and self.dragging:
            self._move_to_mouse(event.pos)
            return True
        if event.type == pg.MOUSEBUTTONUP and event.button == self.button and self.dragging:
            self._move_to_mouse(event.pos)
            self.drop()
            return True
        return False

    def draw(self, screen, camera=None):
        if not self.visible:
            return
        if self.dragging:
            # A small shadow so it looks "picked up"
            shadow = pg.Surface(self.rect.size, pg.SRCALPHA)
            shadow.fill((0, 0, 0, 70))
            screen.blit(shadow, self.rect.move(5, 5))
        super().draw(screen, camera)


# ================================
# DragGroup Class
# ================================

class DragGroup:
    """
    Holds several DragObjects. Only the top one under the mouse is picked up,
    and the one being dragged is drawn on top.

        items = DragGroup(sword, shield, potion)
        items.handle_event(event)      # in handle_inputs()
        items.update(tick)             # in update(tick)
        items.draw(screen)             # in draw_game()
    """

    def __init__(self, *items):
        self.items = list(items)

    def add(self, *items):
        self.items.extend(items)

    def remove(self, item):
        if item in self.items:
            self.items.remove(item)
        if getattr(item, "grid", None) is not None:
            item.grid.remove(item)

    def __iter__(self):
        return iter(list(self.items))

    def __len__(self):
        return len(self.items)

    def dragged(self):
        """The object being dragged, or None."""
        for item in self.items:
            if item.dragging:
                return item
        return None

    def handle_event(self, event, offset=(0, 0)):
        # The top item (drawn last) gets the first chance
        for item in reversed(self.items):
            if item.handle_event(event, offset):
                if item.dragging and self.items[-1] is not item:
                    self.items.remove(item)
                    self.items.append(item)      # bring to the front
                return True
        return False

    def update(self, tick):
        for item in self.items:
            item.update(tick)

    def draw(self, screen, camera=None):
        for item in self.items:
            item.draw(screen, camera)


# ================================
# Path Class
# ================================

def _rect_of(thing):
    """Get a pg.Rect from a Rect, or anything with a .rect."""
    return thing if isinstance(thing, pg.Rect) else thing.rect


class Path:
    """
    A list of points for things to follow (enemy routes, moving platforms...).

    Parameters:
        points - [(x, y), (x, y), ...]
        mode   - "loop"      go back to the first point and repeat
                 "ping_pong" go to the end, then back again
                 "once"      stop at the last point
        color  - colour used when drawing it (for debugging)

    Draw it in Tiled with the Polyline tool and load it with
    level.get_path("guard_route")  (see the README: "Drawing a path in Tiled").

    path.draw(screen, camera) shows the path. Set Path.show_all = False to
    hide every path at once (e.g. when your game is finished).
    """

    show_all = True

    def __init__(self, points, mode="loop", color=(255, 200, 0), colour=None, visible=True):
        if len(points) < 1:
            raise ValueError("A Path needs at least one point")
        self.points = [pg.Vector2(p) for p in points]
        if mode not in ("loop", "ping_pong", "once"):
            raise ValueError("mode must be 'loop', 'ping_pong' or 'once'")
        self.mode = mode
        self.color = _pick(colour, color)
        self.visible = visible

    @classmethod
    def from_tiled(cls, tiled_path, mode=None):
        """
        Make a Path from one of TiledMap.paths. The mode comes from (in order):
        the mode given here, a custom property called "mode" in Tiled, then
        "loop" for a Polygon or "ping_pong" for a Polyline.
        """
        if mode is None:
            mode = tiled_path.get("properties", {}).get("mode")
        if mode is None:
            mode = "loop" if tiled_path.get("closed") else "ping_pong"
        return cls(tiled_path["points"], mode=mode)

    def __len__(self):
        return len(self.points)

    def length(self):
        """Total length in pixels."""
        total = sum(self.points[i].distance_to(self.points[i + 1])
                    for i in range(len(self.points) - 1))
        if self.mode == "loop" and len(self.points) > 2:
            total += self.points[-1].distance_to(self.points[0])
        return total

    def draw(self, screen, camera=None, show=None):
        """Draw the path for debugging (lines, numbered points, direction arrows)."""
        if show is None:
            show = Path.show_all and self.visible
        if not show:
            return
        points = [camera.apply_pos(p) if camera else (p.x, p.y) for p in self.points]
        if len(points) > 1:
            pg.draw.lines(screen, self.color, self.mode == "loop", points, 2)
            pairs = list(zip(points, points[1:]))
            if self.mode == "loop":
                pairs.append((points[-1], points[0]))
            for a, b in pairs:                       # small arrow in the middle
                a, b = pg.Vector2(a), pg.Vector2(b)
                if a == b:
                    continue
                mid = (a + b) / 2
                d = (b - a).normalize() * 7
                side = pg.Vector2(-d.y, d.x) * 0.6
                pg.draw.polygon(screen, self.color, [mid + d, mid - d + side, mid - d - side])
        font = get_font(None, 18)
        for i, p in enumerate(points):
            pg.draw.circle(screen, self.color, p, 6)
            pg.draw.circle(screen, BLACK, p, 6, 1)
            label = font.render(str(i), True, BLACK)
            screen.blit(label, label.get_rect(center=p))


# ================================
# PathFollower Class
# ================================

class PathFollower:
    """
    Moves a sprite along a Path.

    Parameters:
        sprite  - anything with a .rect (SpriteObject, enemy...)
        path    - a Path
        speed   - pixels per second
        wait    - milliseconds to wait at each point
        axis    - "both" (top-down games) or "x" (platformers: only follow left /
                  right, let gravity do up / down)
        body    - optional PlatformerBody / TopDownBody to move with, so walls
                  and gravity still work
        anchor  - which part of the sprite sits on the path: "center" or "midbottom"
        start   - index of the point to start at

    Attributes:
        facing   - "left", "right", "up" or "down"
        finished - True when a "once" path has ended
        active   - set False to pause

    Example:
        guard = PathFollower(enemy, level.get_path("guard_route"), speed=120, wait=500)
        guard.update(tick)      # in update(tick)
    """

    def __init__(self, sprite, path, speed=100, wait=0, axis="both", body=None,
                 anchor="center", start=0, snap_to_start=True):
        self.sprite = sprite
        self.path = path
        self.speed = speed
        self.wait = wait
        self.axis = axis
        self.body = body
        self.anchor = anchor
        self.index = start
        self.step_direction = 1          # +1 forwards, -1 backwards (ping_pong)
        self.finished = False
        self.active = True
        self.facing = "right"
        self._wait_left = 0
        if snap_to_start and body is None:
            setattr(sprite.rect, anchor, (round(path.points[start].x),
                                          round(path.points[start].y)))
        self._pos = pg.Vector2(getattr(sprite.rect, anchor))
        if self._pos.distance_to(path.points[start]) < 3:
            self._advance()          # already at the first point: head for the next

    @property
    def target(self):
        return self.path.points[self.index]

    def _advance(self):
        """Choose the next point."""
        n = len(self.path.points)
        if n == 1:
            return
        nxt = self.index + self.step_direction
        if self.path.mode == "loop":
            self.index = nxt % n
        elif self.path.mode == "ping_pong":
            if not 0 <= nxt < n:
                self.step_direction *= -1
                nxt = self.index + self.step_direction
            self.index = nxt
        else:   # once
            if nxt >= n:
                self.finished = True
            else:
                self.index = nxt

    def restart(self, index=0):
        self.index = index
        self.finished = False
        self.step_direction = 1

    def update(self, tick):
        if not self.active or self.finished:
            if self.body is not None:
                self.body.move(0)
            return
        if self._wait_left > 0:
            self._wait_left -= tick
            if self.body is not None:
                self.body.move(0)
            return

        here = pg.Vector2(getattr(self.sprite.rect, self.anchor))
        # Something else moved the sprite (a collision, a body): follow it
        if here.distance_to(self._pos) > 1.5:
            self._pos = here
        target = pg.Vector2(self.target)
        if self.axis == "x":
            target.y = self._pos.y
        to_target = target - self._pos
        distance = to_target.length()
        step = self.speed * tick / 1000

        if abs(to_target.x) >= abs(to_target.y):
            self.facing = "right" if to_target.x > 0 else "left" if to_target.x < 0 else self.facing
        else:
            self.facing = "down" if to_target.y > 0 else "up"

        if distance <= max(step, 2):
            # Reached the point
            if self.body is None:
                self._pos = target
                setattr(self.sprite.rect, self.anchor, (round(target.x), round(target.y)))
            else:
                self.body.move(0)
            self._wait_left = self.wait
            self._advance()
            return

        if self.body is not None:
            # Let the body move (so walls and gravity work)
            if self.axis == "x" or not hasattr(self.body, "move_towards"):
                self.body.move(1 if to_target.x > 0 else -1)
            else:
                self.body.move_towards(target)
        else:
            self._pos += to_target.normalize() * step
            setattr(self.sprite.rect, self.anchor, (round(self._pos.x), round(self._pos.y)))

    def draw(self, screen, camera=None):
        """Draw the path (debug)."""
        self.path.draw(screen, camera)


# ================================
# Patrol Class (simple left / right walking)
# ================================

class Patrol:
    """
    Walks a sprite left and right - the classic platformer enemy.

    Parameters:
        sprite      - anything with a .rect
        left, right - x limits (None = no limit, just turn at walls / edges)
        speed       - pixels per second
        body        - a PlatformerBody (recommended for platformers)
        turn_at_walls - turn around when bumping into a wall (needs a body)
        turn_at_edges - turn around instead of walking off a ledge (needs a body)

    Example:
        Patrol(slime, body=slime_body, turn_at_edges=True)
    """

    def __init__(self, sprite, left=None, right=None, speed=80, body=None,
                 turn_at_walls=True, turn_at_edges=True, start_direction=1):
        self.sprite = sprite
        self.left = left
        self.right = right
        self.speed = speed
        self.body = body
        self.turn_at_walls = turn_at_walls
        self.turn_at_edges = turn_at_edges
        self.direction = start_direction
        self.active = True
        self._x = float(sprite.rect.x)

    @property
    def facing(self):
        return "right" if self.direction > 0 else "left"

    def turn(self):
        self.direction *= -1

    def update(self, tick):
        if not self.active:
            if self.body is not None:
                self.body.move(0)
            return
        r = self.sprite.rect
        if self.left is not None and r.left <= self.left:
            self.direction = 1
        elif self.right is not None and r.right >= self.right:
            self.direction = -1

        if self.body is not None:
            touching = self.body.touching
            if self.turn_at_walls and (("right" in touching and self.direction > 0) or
                                       ("left" in touching and self.direction < 0)):
                self.turn()
            elif self.turn_at_edges and self.body.on_ground and \
                    not self.body.ground_ahead(self.direction):
                self.turn()
            self.body.move(self.direction, speed=self.speed)
        else:
            if abs(self._x - r.x) > 1.5:
                self._x = float(r.x)
            self._x += self.direction * self.speed * tick / 1000
            r.x = round(self._x)


# ================================
# Line of sight
# ================================

def line_of_sight(start, end, solids):
    """True if nothing in solids (Rects, or things with .rect) blocks the line."""
    for solid in solids:
        if _rect_of(solid).clipline(start, end):
            return False
    return True


# ================================
# NavGrid Class (path finding)
# ================================

class NavGrid:
    """
    Finds a way around walls (A* path finding) for top-down games.

    Parameters:
        width, height - size of the world in pixels
        cell_size     - size of each square (smaller = more accurate, slower)
        solids        - walls: a list of Rects (or things with .rect)
        diagonal      - True to allow diagonal moves
        agent_size    - size of the thing moving: walls are made this much
                        bigger so it doesn't clip corners

    Example:
        nav = NavGrid.from_tiled(level, agent_size=28)
        route = nav.find_path(enemy.rect.center, player.rect.center)   # a Path or None
        nav.draw(screen, camera)      # debug: shows blocked squares
    """

    def __init__(self, width, height, cell_size=32, solids=(), diagonal=True, agent_size=0):
        import math
        self.cell_size = cell_size
        self.cols = math.ceil(width / cell_size)       # only cells inside the world
        self.rows = math.ceil(height / cell_size)
        self.diagonal = diagonal
        self.blocked = set()
        grow = max(0, agent_size - 2)
        for solid in solids:
            r = _rect_of(solid).inflate(grow, grow)
            for c in range(max(0, r.left // cell_size), min(self.cols, r.right // cell_size + 1)):
                for row in range(max(0, r.top // cell_size), min(self.rows, r.bottom // cell_size + 1)):
                    cell = pg.Rect(c * cell_size, row * cell_size, cell_size, cell_size)
                    if cell.colliderect(r):
                        self.blocked.add((c, row))

    @classmethod
    def from_tiled(cls, tiled_map, cell_size=None, diagonal=True, agent_size=0, extra_solids=()):
        """Build a NavGrid from a TiledMap's "collision" objects."""
        solids = [o["rect"] for o in tiled_map.collision_objects] + list(extra_solids)
        return cls(tiled_map.width, tiled_map.height, cell_size or tiled_map.tilewidth,
                   solids, diagonal, agent_size)

    def cell_of(self, pos):
        return (int(pos[0] // self.cell_size), int(pos[1] // self.cell_size))

    def cell_center(self, cell):
        return ((cell[0] + 0.5) * self.cell_size, (cell[1] + 0.5) * self.cell_size)

    def is_blocked(self, cell):
        c, r = cell
        return not (0 <= c < self.cols and 0 <= r < self.rows) or cell in self.blocked

    def _nearest_open(self, cell):
        if not self.is_blocked(cell):
            return cell
        for radius in range(1, 4):
            for dc in range(-radius, radius + 1):
                for dr in range(-radius, radius + 1):
                    near = (cell[0] + dc, cell[1] + dr)
                    if not self.is_blocked(near):
                        return near
        return None

    def find_path(self, start, goal, max_steps=4000):
        """
        Find a route from start to goal (pixel positions).
        Returns a Path (mode "once") or None if there is no way through.
        """
        import heapq
        start_cell = self._nearest_open(self.cell_of(start))
        goal_cell = self._nearest_open(self.cell_of(goal))
        if start_cell is None or goal_cell is None:
            return None
        moves = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        if self.diagonal:
            moves += [(1, 1), (1, -1), (-1, 1), (-1, -1)]

        def guess(cell):
            """Estimated distance to the goal (A* needs this)."""
            dx, dy = abs(cell[0] - goal_cell[0]), abs(cell[1] - goal_cell[1])
            if self.diagonal:
                return max(dx, dy) + 0.41 * min(dx, dy)
            return dx + dy

        open_list = [(guess(start_cell), 0, start_cell)]
        came_from = {start_cell: None}
        cost = {start_cell: 0}
        steps = 0
        while open_list and steps < max_steps:
            steps += 1
            _, here_cost, here = heapq.heappop(open_list)
            if here == goal_cell:
                break
            for dc, dr in moves:
                nxt = (here[0] + dc, here[1] + dr)
                if self.is_blocked(nxt):
                    continue
                if dc and dr and (self.is_blocked((here[0] + dc, here[1])) or
                                  self.is_blocked((here[0], here[1] + dr))):
                    continue        # don't cut corners
                new_cost = here_cost + (1.41 if dc and dr else 1)
                if new_cost < cost.get(nxt, 10 ** 9):
                    cost[nxt] = new_cost
                    came_from[nxt] = here
                    heapq.heappush(open_list, (new_cost + guess(nxt), new_cost, nxt))
        if goal_cell not in came_from:
            return None

        cells = []
        cell = goal_cell
        while cell is not None:
            cells.append(cell)
            cell = came_from[cell]
        cells.reverse()
        points = [self.cell_center(c) for c in cells]
        points[-1] = goal
        if len(points) > 1:
            points[0] = start
        return Path(points, mode="once", color=(0, 220, 255))

    def draw(self, screen, camera=None):
        """Debug: shade the blocked squares."""
        if not Path.show_all:
            return
        shade = pg.Surface((self.cell_size, self.cell_size), pg.SRCALPHA)
        shade.fill((255, 0, 0, 60))
        for c, r in self.blocked:
            pos = (c * self.cell_size, r * self.cell_size)
            screen.blit(shade, camera.apply_pos(pos) if camera else pos)


# ================================
# Chaser Class (detect and chase a target)
# ================================

class Chaser:
    """
    Makes a sprite notice a target (usually the player) and chase it.
    When the target gets away, it goes back to what it was doing before.

    Parameters:
        sprite       - the enemy (anything with a .rect)
        target       - what to chase (anything with a .rect)
        speed        - chase speed in pixels per second
        detect_range - starts chasing when the target is this close
        lose_range   - stops chasing when the target is further than this
        solids       - walls, used for line of sight (and moving without a body)
        line_of_sight - True: only notice the target if no wall is in the way
        nav          - a NavGrid: find a way around walls (top-down games)
        body         - a PlatformerBody / TopDownBody to move with
        jump_when_blocked - platformers: jump when a wall is in the way
        idle         - what to do when not chasing: a PathFollower or Patrol
                       (or None to stand still)
        return_home  - True: walk back to where the chase started

    Attributes:
        state  - "idle", "chase" or "return"
        can_see_target

    Example:
        guard_ai = Chaser(guard, player, speed=150, detect_range=200,
                          nav=nav, solids=walls, idle=guard_path_follower)
        guard_ai.update(tick)
        guard_ai.draw_debug(screen, camera)
    """

    def __init__(self, sprite, target, speed=150, detect_range=200, lose_range=None,
                 solids=(), line_of_sight=True, nav=None, body=None,
                 jump_when_blocked=True, idle=None, return_home=True, repath_ms=400):
        self.sprite = sprite
        self.target = target
        self.speed = speed
        self.detect_range = detect_range
        self.lose_range = lose_range if lose_range is not None else detect_range * 1.5
        self.solids = solids
        self.use_line_of_sight = line_of_sight
        self.nav = nav
        self.body = body
        self.jump_when_blocked = jump_when_blocked
        self.idle = idle
        self.return_home = return_home
        self.repath_ms = repath_ms
        self.state = "idle"
        self.can_see_target = False
        self.active = True
        self.facing = "right"
        self._home = None
        self._route = None
        self._route_follower = None
        self._repath_timer = 0
        self._pos = pg.Vector2(sprite.rect.center)

    def distance(self):
        return pg.Vector2(self.sprite.rect.center).distance_to(self.target.rect.center)

    def _sees(self):
        if self.use_line_of_sight and self.solids:
            return line_of_sight(self.sprite.rect.center, self.target.rect.center, self.solids)
        return True

    def _move_towards(self, point, tick):
        """Move one step towards a point (with a body, nav route or straight)."""
        here = pg.Vector2(self.sprite.rect.center)
        point = pg.Vector2(point)
        self.facing = "right" if point.x > here.x else "left"
        platformer = isinstance(self.body, PlatformerBody)

        if self.nav is not None and not platformer:
            self._repath_timer -= tick
            if self._route_follower is None or self._repath_timer <= 0 or \
                    self._route_follower.finished:
                self._repath_timer = self.repath_ms
                route = self.nav.find_path(here, point)
                self._route = route
                self._route_follower = PathFollower(self.sprite, route, self.speed,
                                                    body=self.body, snap_to_start=False) \
                    if route is not None and len(route) > 1 else None
            if self._route_follower is not None:
                self._route_follower.update(tick)
                return

        if self.body is not None:
            if platformer:
                if abs(point.x - here.x) > 4:
                    direction = 1 if point.x > here.x else -1
                    self.body.move(direction, speed=self.speed)
                    blocked = ("right" if direction > 0 else "left") in self.body.touching
                    if self.jump_when_blocked and blocked and self.body.on_ground:
                        self.body.jump()
                else:
                    self.body.move(0)
            else:
                self.body.move_towards(point, speed=self.speed)
            return

        # No body: move straight, stopping at walls
        if here.distance_to(self._pos) > 1.5:
            self._pos = here
        if self._pos.distance_to(point) > 2:
            step = (point - self._pos).normalize() * self.speed * tick / 1000
            old = self.sprite.rect.copy()
            self._pos += step
            self.sprite.rect.center = (round(self._pos.x), round(self._pos.y))
            if any(self.sprite.rect.colliderect(_rect_of(s)) for s in self.solids):
                self.sprite.rect = old
                self._pos = pg.Vector2(old.center)

    def update(self, tick):
        if not self.active:
            return
        distance = self.distance()
        self.can_see_target = distance <= self.lose_range and self._sees()

        if self.state != "chase" and distance <= self.detect_range and self.can_see_target:
            if self.state == "idle":
                self._home = self.sprite.rect.center
            self.state = "chase"
            self._route_follower = None
        elif self.state == "chase" and (distance > self.lose_range or not self.can_see_target):
            self.state = "return" if (self.return_home and self._home) else "idle"
            self._route_follower = None
            if self.body is not None:
                self.body.move(0)

        if self.state == "chase":
            self._move_towards(self.target.rect.center, tick)
        elif self.state == "return":
            here = pg.Vector2(self.sprite.rect.center)
            close = abs(here.x - self._home[0]) < 6 if isinstance(self.body, PlatformerBody) \
                else here.distance_to(self._home) < 6
            if close:
                self.state = "idle"
                self._route_follower = None
                if self.body is not None:
                    self.body.move(0)
            else:
                self._move_towards(self._home, tick)
        else:
            if self.idle is not None:
                self.idle.update(tick)
                self.facing = getattr(self.idle, "facing", self.facing)
            elif self.body is not None:
                self.body.move(0)

    def draw_debug(self, screen, camera=None):
        """Show the detect / lose ranges, line of sight and the chase route."""
        if not Path.show_all:
            return
        centre = self.sprite.rect.center
        to_screen = (lambda p: camera.apply_pos(p)) if camera else (lambda p: p)
        c = to_screen(centre)
        pg.draw.circle(screen, (255, 200, 0), c, int(self.detect_range), 1)
        pg.draw.circle(screen, (120, 120, 120), c, int(self.lose_range), 1)
        colour = (80, 255, 120) if self.can_see_target else (255, 80, 80)
        pg.draw.line(screen, colour, c, to_screen(self.target.rect.center), 1)
        if self.state == "chase" and self._route is not None:
            self._route.draw(screen, camera, show=True)
        draw_text(screen, self.state, c[0], c[1] - self.sprite.rect.height, fg=(255, 255, 0),
                  font_size=18, center=True)


# ================================
# Body classes (movement with collisions)
# ================================

class Body:
    """
    The base for TopDownBody and PlatformerBody: moves a sprite and stops it
    going through solids. Movement is done one axis at a time, so things slide
    along walls instead of sticking.

    Attributes:
        velocity  - pg.Vector2 in pixels per second
        touching  - set of sides touching a solid: "left", "right", "top", "bottom"
        facing    - "left" / "right" (and "up" / "down" for top-down)
    """

    def __init__(self, sprite, solids=None, speed=200):
        self.sprite = sprite
        self.solids = solids if solids is not None else []
        self.speed = speed
        self.velocity = pg.Vector2(0, 0)
        self.touching = set()
        self.facing = "right"
        self._pos = pg.Vector2(sprite.rect.topleft)

    def _sync(self):
        """If something else moved the sprite (e.g. teleport), follow it."""
        if (round(self._pos.x), round(self._pos.y)) != self.sprite.rect.topleft:
            self._pos = pg.Vector2(self.sprite.rect.topleft)

    def set_position(self, x, y):
        self.sprite.rect.topleft = (x, y)
        self._pos = pg.Vector2(x, y)
        self.velocity.update(0, 0)

    def _solid_rects(self):
        return [_rect_of(s) for s in self.solids]

    def move_and_collide(self, dx, dy, extra_y_check=None):
        """Move by dx, dy pixels, stopping at solids. Fills in self.touching."""
        self.touching = set()
        r = self.sprite.rect
        solids = self._solid_rects()

        self._pos.x += dx
        r.x = round(self._pos.x)
        for s in solids:
            if r.colliderect(s):
                if dx > 0:
                    r.right = s.left
                    self.touching.add("right")
                elif dx < 0:
                    r.left = s.right
                    self.touching.add("left")
                self._pos.x = r.x
                self.velocity.x = 0

        old_bottom = r.bottom
        self._pos.y += dy
        r.y = round(self._pos.y)
        for s in solids:
            if r.colliderect(s):
                if dy > 0:
                    r.bottom = s.top
                    self.touching.add("bottom")
                elif dy < 0:
                    r.top = s.bottom
                    self.touching.add("top")
                self._pos.y = r.y
                self.velocity.y = 0
        if extra_y_check:
            extra_y_check(old_bottom, dy)


class TopDownBody(Body):
    """
    Movement with collisions for top-down games (RPGs, twin-stick shooters).

    Parameters:
        sprite  - anything with a .rect
        solids  - walls: Rects or things with .rect
        speed   - pixels per second
        normalize_diagonal - True: moving diagonally isn't faster

    Example:
        body = TopDownBody(player, solids=walls, speed=200)
        body.move(dx, dy)          # -1, 0 or 1 each, e.g. from KeyboardInput
        body.update(tick)
    """

    def __init__(self, sprite, solids=None, speed=200, normalize_diagonal=True):
        super().__init__(sprite, solids, speed)
        self.normalize_diagonal = normalize_diagonal
        self._direction = pg.Vector2(0, 0)
        self._speed_now = speed

    def move(self, dx, dy=0, speed=None):
        """Set the direction to move this frame (-1, 0 or 1 for each)."""
        self._direction = pg.Vector2(dx, dy)
        self._speed_now = speed if speed is not None else self.speed

    def move_towards(self, point, speed=None):
        """Head towards a point."""
        d = pg.Vector2(point) - pg.Vector2(self.sprite.rect.center)
        if d.length() < 2:
            self.move(0, 0)
        else:
            d = d.normalize()
            self.move(d.x, d.y, speed)

    def update(self, tick):
        self._sync()
        direction = pg.Vector2(self._direction)
        if self.normalize_diagonal and direction.length() > 1:
            direction = direction.normalize()
        self.velocity = direction * self._speed_now
        if direction.length():
            if abs(direction.x) >= abs(direction.y):
                self.facing = "right" if direction.x > 0 else "left"
            else:
                self.facing = "down" if direction.y > 0 else "up"
        dt = tick / 1000
        self.move_and_collide(self.velocity.x * dt, self.velocity.y * dt)


class PlatformerBody(Body):
    """
    Gravity, jumping, platforms and ladders for platform games.

    Parameters:
        sprite      - anything with a .rect
        solids      - walls and floors (Rects or things with .rect)
        platforms   - one-way platforms: jump up through them, stand on top,
                      press down to drop through. MovingPlatforms go here too.
        ladders     - Rects you can climb
        move_speed  - walking speed (pixels per second)
        gravity     - how fast you speed up when falling (pixels per second²)
        max_fall    - fastest falling speed
        jump_speed  - how hard you jump
        max_jumps   - 2 for a double jump
        coyote_ms   - you can still jump this long after walking off a ledge
        jump_buffer_ms - a jump pressed this long before landing still happens
        climb_speed - ladder speed
        acceleration - None = start / stop instantly, or e.g. 2000 for a slide

    Use (every frame):
        body.move(direction)        # -1 left, 0 stop, 1 right
        body.climb(direction)       # -1 up, 1 down (only on ladders)
        body.jump()                 # e.g. when keys.was_pressed("jump")
        body.release_jump()         # e.g. when keys.was_released("jump") - small hop
        body.drop_down()            # fall through a one-way platform
        body.update(tick)

    Attributes: on_ground, on_ladder, climbing, velocity, touching, facing
    """

    def __init__(self, sprite, solids=None, platforms=None, ladders=None,
                 move_speed=250, gravity=1800, max_fall=900, jump_speed=650,
                 max_jumps=1, coyote_ms=100, jump_buffer_ms=120, climb_speed=160,
                 acceleration=None):
        super().__init__(sprite, solids, move_speed)
        self.platforms = platforms if platforms is not None else []
        self.ladders = ladders if ladders is not None else []
        self.gravity = gravity
        self.max_fall = max_fall
        self.jump_speed = jump_speed
        self.max_jumps = max_jumps
        self.coyote_ms = coyote_ms
        self.jump_buffer_ms = jump_buffer_ms
        self.climb_speed = climb_speed
        self.acceleration = acceleration

        self.on_ground = False
        self.on_ladder = False
        self.climbing = False
        self.standing_on = None       # the platform / MovingPlatform underneath
        self._move_dir = 0
        self._move_speed_now = move_speed
        self._climb_dir = 0
        self._coyote = 0
        self._jump_buffer = 0
        self._jumps_used = 0
        self._drop_timer = 0

    # ---- controls ----
    def move(self, direction, speed=None):
        self._move_dir = max(-1, min(1, direction))
        self._move_speed_now = speed if speed is not None else self.speed

    def climb(self, direction):
        self._climb_dir = max(-1, min(1, direction))

    def jump(self):
        self._jump_buffer = self.jump_buffer_ms

    def release_jump(self, cut=0.45):
        """Let go of jump early for a smaller jump."""
        if self.velocity.y < 0:
            self.velocity.y *= cut

    def drop_down(self):
        if self.standing_on is not None and self.standing_on in self.platforms:
            self._drop_timer = 200

    # ---- checks ----
    def ground_ahead(self, direction, distance=4):
        """True if there is ground just ahead (used to stop at ledge edges)."""
        r = self.sprite.rect
        x = r.right + distance if direction > 0 else r.left - distance - 1
        probe = pg.Rect(x, r.bottom, 1, 4)
        return any(probe.colliderect(s) for s in self._solid_rects() + self._platform_rects())

    def _platform_rects(self):
        return [_rect_of(p) for p in self.platforms]

    def _ladder_here(self):
        r = self.sprite.rect
        middle = pg.Rect(r.centerx - 2, r.top, 4, r.height + 2)
        for ladder in self.ladders:
            lr = _rect_of(ladder)
            if middle.colliderect(lr):
                return lr
        return None

    def _land_on_platforms(self, old_bottom, dy):
        """One-way platforms: only stop when falling onto the top."""
        r = self.sprite.rect
        if dy < 0 or self._drop_timer > 0 or self.climbing:
            return
        for platform in self.platforms:
            pr = _rect_of(platform)
            if r.colliderect(pr) and old_bottom <= pr.top + 1:
                r.bottom = pr.top
                self._pos.y = r.y
                self.velocity.y = 0
                self.touching.add("bottom")
                self.standing_on = platform

    # ---- update ----
    def update(self, tick):
        self._sync()
        dt = tick / 1000
        self._jump_buffer -= tick
        self._coyote -= tick
        self._drop_timer -= tick

        # Ride moving platforms
        if self.standing_on is not None and hasattr(self.standing_on, "delta"):
            self._pos += self.standing_on.delta
            self.sprite.rect.topleft = (round(self._pos.x), round(self._pos.y))

        # Ladders
        ladder = self._ladder_here()
        self.on_ladder = ladder is not None
        if not self.on_ladder:
            self.climbing = False
        elif self._climb_dir != 0:
            self.climbing = True
            self.sprite.rect.centerx = ladder.centerx      # line up with the ladder
            self._pos.x = self.sprite.rect.x

        # Sideways
        target_vx = self._move_dir * self._move_speed_now
        if self.acceleration:
            change = self.acceleration * dt
            self.velocity.x += max(-change, min(change, target_vx - self.velocity.x))
        else:
            self.velocity.x = target_vx
        if self._move_dir:
            self.facing = "right" if self._move_dir > 0 else "left"

        # Up / down
        if self.climbing:
            self.velocity.y = self._climb_dir * self.climb_speed
            self._jumps_used = 0
        else:
            self.velocity.y = min(self.max_fall, self.velocity.y + self.gravity * dt)

        # Jumping (buffer + coyote time + extra jumps)
        if self._jump_buffer > 0:
            if self.on_ground or self._coyote > 0 or self.climbing:
                allowed = True
                self._jumps_used = 0
            else:
                # In the air: falling off a ledge uses up the first jump
                self._jumps_used = max(self._jumps_used, 1)
                allowed = self._jumps_used < self.max_jumps
            if allowed:
                self.velocity.y = -self.jump_speed
                self._jumps_used += 1
                self._jump_buffer = 0
                self._coyote = 0
                self.climbing = False

        was_on_ground = self.on_ground
        self.standing_on = None
        self.move_and_collide(self.velocity.x * dt, self.velocity.y * dt,
                              extra_y_check=self._land_on_platforms)
        # Standing still, gravity moves us less than a pixel each frame, so also
        # check the pixel just below our feet
        if "bottom" not in self.touching and self.velocity.y >= 0:
            feet = pg.Rect(self.sprite.rect.x, self.sprite.rect.bottom, self.sprite.rect.width, 1)
            for solid in self.solids:
                if feet.colliderect(_rect_of(solid)):
                    self.touching.add("bottom")
                    break
            else:
                if self._drop_timer <= 0 and not self.climbing:
                    for platform in self.platforms:
                        pr = _rect_of(platform)
                        if feet.colliderect(pr) and self.sprite.rect.bottom == pr.top:
                            self.touching.add("bottom")
                            self.standing_on = platform
                            break
        self.on_ground = "bottom" in self.touching
        if self.on_ground:
            if self.velocity.y > 0:
                self.velocity.y = 0          # don't build up falling speed while standing
            self._coyote = self.coyote_ms
            self._jumps_used = 0
            if self.standing_on is None:
                self.standing_on = next((s for s in self.solids
                                         if pg.Rect(self.sprite.rect.x, self.sprite.rect.bottom,
                                                    self.sprite.rect.width, 1)
                                         .colliderect(_rect_of(s))), None)
        elif was_on_ground and self.velocity.y >= 0:
            self._coyote = self.coyote_ms         # just walked off a ledge
        # Controls only last one frame: call move() / climb() every frame
        self._move_dir = 0
        self._climb_dir = 0


class MovingPlatform(SpriteObject):
    """
    A platform that follows a Path and carries anything standing on it.
    Put it in a PlatformerBody's platforms (one-way) or solids list, and
    update it BEFORE the bodies that stand on it. The middle of the
    platform follows the path.

        lift = MovingPlatform(300, 400, 96, 16, path=level.get_path("lift"), speed=80)
        lift.update(tick)
    """

    def __init__(self, x, y, width, height, path, speed=80, wait=300, image=None,
                 bg=(150, 110, 70)):
        super().__init__(x, y, width, height, image=image, bg=bg)
        self.follower = PathFollower(self, path, speed, wait)
        self.delta = pg.Vector2(0, 0)

    def update(self, tick):
        before = pg.Vector2(self.rect.topleft)
        self.follower.update(tick)
        super().update(tick)
        self.delta = pg.Vector2(self.rect.topleft) - before


# ================================
# Tooltip Class
# ================================

class Tooltip:
    """
    A small box of text that appears when the mouse rests on something.
    Works with anything that has a .rect (widgets, sprites, DragObjects...).

        tips = Tooltip()
        tips.attach(play_button, "Start a new game")
        tips.attach(sword, lambda item: f"{item.name}\\nDamage: {item.stats['damage']}")

        tips.update(tick)        # in update(tick)
        tips.draw(screen)        # LAST in draw_game(), so it is on top

    The text can be a string, or a function that is given the object and
    returns the text (so it can show stats that change).

    Parameters: delay (ms before it shows), width, fg, bg, border_color,
    font_name, font_size, padding
    """

    def __init__(self, delay=400, width=220, fg=WHITE, bg=(20, 20, 30),
                 border_color=(200, 200, 200), border_colour=None,
                 font_name=None, font_size=20, padding=8):
        self.delay = delay
        self.width = width
        self.fg = fg
        self.bg = bg
        self.border_color = _pick(border_colour, border_color)
        self.font_name = font_name
        self.font_size = font_size
        self.padding = padding
        self.targets = []           # list of (object, text or function)
        self.current = None
        self._timer = 0
        self._last_mouse = None

    def attach(self, target, text):
        """Show text when the mouse is over target."""
        self.targets.append((target, text))

    def detach(self, target):
        self.targets = [(t, x) for t, x in self.targets if t is not target]

    def _rect(self, target):
        if hasattr(target, "get_rect") and isinstance(target, Widget):
            return target.get_rect(target._last_offset)
        return _rect_of(target)

    def _text_for(self, target, text):
        return text(target) if callable(text) else str(text)

    def update(self, tick):
        mouse = pg.mouse.get_pos()
        hovered = None
        for target, text in reversed(self.targets):
            if getattr(target, "visible", True) and not getattr(target, "dragging", False) \
                    and self._rect(target).collidepoint(mouse):
                hovered = (target, text)
                break
        if hovered is None or (self.current and hovered[0] is not self.current[0]):
            self._timer = 0
        if hovered is not None:
            self._timer += tick
        self.current = hovered

    def draw(self, screen):
        if self.current is None or self._timer < self.delay:
            return
        target, text = self.current
        words = self._text_for(target, text)
        if not words:
            return
        box = Message(0, 0, words, width=self.width, fg=self.fg, bg=self.bg,
                      font_name=self.font_name, font_size=self.font_size,
                      padding=self.padding)
        # Fit the box to the text, and keep it on screen
        font = get_font(self.font_name, self.font_size)
        widest = max(font.size(line)[0] for line in box._lines())
        box.width = min(self.width, widest + self.padding * 2)
        box._refresh()
        mx, my = pg.mouse.get_pos()
        x, y = mx + 16, my + 16
        sw, sh = screen.get_size()
        if x + box.width > sw:
            x = mx - box.width - 8
        if y + box.height > sh:
            y = my - box.height - 8
        box.x, box.y = max(0, x), max(0, y)
        box.draw(screen)
        if self.border_color:
            pg.draw.rect(screen, self.border_color, box.get_rect(), 1)
