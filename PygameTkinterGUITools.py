import pygame as pg
from typing import List, Tuple, Optional, Callable
from pytmx.util_pygame import load_pygame

# ================================
# Base Frame Class
# ================================

class Frame:
    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        background: Optional[Tuple[int, int, int]] = None,
        bg: Optional[Tuple[int, int, int]] = None,
        border_color: Optional[Tuple[int, int, int]] = None,
        border_colour: Optional[Tuple[int, int, int]] = None,
        border_width: Optional[int] = None,
        border: Optional[int] = None,
        visible: bool = True,
        pad_x:int = 10,
        pad_y:int = 10
    ):
        """
        A container for visual elements (similar to a Tkinter Frame).
        """
        self.rect = pg.Rect(x, y, width, height)
        self.pad_x = pad_x
        self.pad_y = pad_y

        # Either spelling can be used (e.g. bg= or background=).
        # If neither is given, use the default value.
        if background is not None:
            self.background = background
        elif bg is not None:
            self.background = bg
        else:
            self.background = (60, 60, 60)

        if border_color is not None:
            self.border_color = border_color
        elif border_colour is not None:
            self.border_color = border_colour
        else:
            self.border_color = (200, 200, 200)

        if border_width is not None:
            self.border_width = border_width
        elif border is not None:
            self.border_width = border
        else:
            self.border_width = 2

        self.children: List[object] = []
        self.visible = visible

    def add(self, element):
        """Add a visual element (Label, Button, etc.) to this Frame."""
        self.children.append(element)

    def _child_offset(self, offset):
        """Where the children's (0, 0) is on screen: frame position + padding."""
        ox, oy = offset
        return (ox + self.rect.x + self.pad_x, oy + self.rect.y + self.pad_y)

    def draw(self, surface, offset=(0, 0)):
        if not self.visible:
            return

        ox, oy = offset
        my_off = self._child_offset(offset)

        # Draw frame background
        if self.background:
            pg.draw.rect(surface, self.background,
                (self.rect.x + ox, self.rect.y + oy, self.rect.width, self.rect.height))

        # Draw border
        if self.border_width > 0:
            pg.draw.rect(surface, self.border_color,
                (self.rect.x + ox, self.rect.y + oy, self.rect.width, self.rect.height),
                self.border_width)

        # Draw children with updated offset
        for child in self.children:
            child.draw(surface, my_off)

    def handle_event(self, event, offset=(0,0)):
        if not self.visible:
            return

        # Use the same offset as draw() so clicks line up with what is drawn
        my_off = self._child_offset(offset)

        # Send event to children
        for child in self.children:
            if hasattr(child, "handle_event"):
                child.handle_event(event, my_off)

    def update(self, tick):
        """Pass the tick on to children that animate (e.g. TextBox cursor)."""
        if not self.visible:
            return
        for child in self.children:
            if hasattr(child, "update"):
                child.update(tick)

    def toggle_visibility(self):
        """Show or hide the frame."""
        self.visible = not self.visible

# ================================
# Label Class
# ================================

class Label:
    def __init__(
        self,
        text: str,
        x: int=10,
        y: int=10,
        font_size: int = 24,
        colour: Tuple[int, int, int] = (255, 255, 255),
        fontfamily: Optional[str] = None,
        center: bool = False,
    ):
        """
        Simple text label that can be added to a Frame.
        """
        self.text = text
        self.x = x
        self.y = y
        self.font = pg.font.SysFont(fontfamily, font_size)
        self.colour = colour
        self.center = center

    def draw(self, screen: pg.Surface, offset: Tuple[int, int] = (0, 0)):
        text_surface = self.font.render(self.text, True, self.colour)
        rect = text_surface.get_rect()

        if self.center:
            rect.center = (self.x + offset[0], self.y + offset[1])
        else:
            rect.topleft = (self.x + offset[0], self.y + offset[1])

        screen.blit(text_surface, rect)

    def handle_event(self, event, offset=(0,0)):
        pass
    
def draw_text(screen, text: str, x: int, y: int, fontsize: int,
              colour: tuple, fontfamily: str = None, center: bool = False):
    """
        Draw Text to the 
        Parameters:
        screen - pygame.Surface object to draw on (object)
        text - string of text to display (string)
        fontsize - size of font (int)
        colour - RGB tuple for text colour (Red (0-255), Green (0-255), Blue (0-255))
        fontfamily - optional font name (e.g. "Arial")
        center - if True, the text is centred on (x,y) (boolean)
    """

    
    font = pg.font.SysFont(fontfamily, fontsize)
    text_surface = font.render(text, True, colour)
    text_rect = text_surface.get_rect()
    
    if center:
        text_rect.center = (x, y)
    else:
        text_rect.topleft = (x, y)
    
    screen.blit(text_surface, text_rect)

# ================================
# Camera Class
# ================================

class Camera:
    """
    Handles world-to-screen offset based on a target (e.g., player).
    Supports bounds limiting and smooth following.
    """
    def __init__(self, width, height, screen_size):
        self.width = width
        self.height = height
        self.screen_w, self.screen_h = screen_size
        self.offset = pg.Vector2(0, 0)
        self.target = None
        self.smooth_factor = 0.1  # smaller = smoother follow

    def follow(self, target):
        """Assign a target object with a .rect attribute."""
        self.target = target

    def update(self):
        """Move camera to follow the target."""
        if not self.target:
            return

        # Desired camera center
        target_center = pg.Vector2(
            self.target.rect.centerx - self.screen_w / 2,
            self.target.rect.centery - self.screen_h / 2
        )

        # Clamp to map bounds
        target_center.x = max(0, min(target_center.x, self.width - self.screen_w))
        target_center.y = max(0, min(target_center.y, self.height - self.screen_h))

        # Smooth follow
        self.offset += (target_center - self.offset) * self.smooth_factor

    def apply(self, rect):
        """Return a rect adjusted for camera offset."""
        return rect.move(-self.offset.x, -self.offset.y)

    def apply_pos(self, pos):
        """Return a position tuple adjusted for camera offset."""
        return (pos[0] - self.offset.x, pos[1] - self.offset.y)


# ================================
# Zoom Camera Class
# ================================

class ZoomCamera:
    """
    Wraps your fox.Camera to add zooming.
    Zoom works by rendering the world to a temp surface, then scaling it.
    """
    def __init__(self, base_camera, screen_size, initial_zoom=2.0):
        self.base = base_camera
        self.zoom = initial_zoom
        self.screen_w, self.screen_h = screen_size

        # temporary render surface (world area as seen by camera)
        self.render = pg.Surface(screen_size, pg.SRCALPHA)

    def set_zoom(self, z):
        self.zoom = max(0.3, min(6.0, z))  # clamp zoom

    def apply_offset(self):
        """
        Return the camera offset (base camera already follows player).
        """
        return (self.base.offset.x, self.base.offset.y)

    def update(self):
        self.base.update()

    def draw_world(self, world, screen):
        """
        Draws the entire world to a temp surface, then scales it.
        """
        # Step 1 — draw to clean render surface
        self.render.fill((0,0,0,0))
        world.draw(self.render)

        # Step 2 — zoom by scaling
        zoomed_surface = pg.transform.smoothscale(
            self.render,
            (int(self.screen_w * self.zoom), int(self.screen_h * self.zoom))
        )

        # Step 3 — center the zoom on screen
        rect = zoomed_surface.get_rect(center=(self.screen_w//2, self.screen_h//2))

        screen.blit(zoomed_surface, rect)




class Animator:
    """
    Handles animation from:
      - A list of individual images, OR
      - A sprite sheet divided into tiles.

    Supports:
      - Multiple named animations with custom frame ranges
      - Delta time frame advancement
      - Play once or looped animations
      - Flipping/inverting animations horizontally or vertically
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
            dt = tick / 1000.0
            self.timer += dt
            if self.timer >= 1 / self.frame_rate:
                self.timer = 0
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

        return self.flipped_cache[key]

    def reset(self):
        """Restart the current animation."""
        self.current_frame_index = 0
        self.timer = 0

# ================================
# SpriteObject Class (Used with Animator)
# ================================

class Tile(pg.sprite.Sprite):
    """Basic static tile."""
    def __init__(self, pos, image):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect(topleft=pos)

    def update(self, tick):
        pass  # static tiles do nothing

    def draw(self, surface, offset=(0, 0)):
        ox, oy = offset
        surface.blit(self.image, (self.rect.x - ox, self.rect.y - oy))


# ================================
# Animated Tile Class
# ================================

class AnimatedTile(pg.sprite.Sprite):
    """
    Tile that uses the Animator class to loop an animation.
    Perfect for water, torches, lights, machinery, etc.
    """
    def __init__(self, pos, animator: Animator, default_animation="default"):
        super().__init__()
        self.animator = animator

        # Start animation looping
        self.animator.play(default_animation)
        self.animator.start(loop=True)

        # Initial image
        self.image = self.animator.update(0)
        self.rect = self.image.get_rect(topleft=pos)

    def update(self, tick):
        self.image = self.animator.update(tick)

    def draw(self, surface, offset=(0, 0)):
        ox, oy = offset
        surface.blit(self.image, (self.rect.x - ox, self.rect.y - oy))

# ================================
# TileMap Class
# ================================

class TiledMap:
    def __init__(self, filename):
        from pytmx.util_pygame import load_pygame
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
            obj_type = (obj.type or "").lower()
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
# Button Class
# ================================

class Button:
    """
    A simple, customizable button class that:
     - Draws a rectangle and text
     - Changes colour when hovered
     - Supports rounded corners, borders, shadows
     - Can be centered or positioned by top-left
     - Works both inside and outside of frames
    """

    def __init__(self, x, y, width, height, text,
                 colour=(100, 150, 255), hover_colour=(150, 200, 255),
                 text_colour=(0, 0, 0), font_size=30,
                 font_name=None, action=None,
                 border_radius=0, border_colour=None, border_thickness=0,
                 shadow=False, shadow_offset=(3, 3), shadow_colour=(0, 0, 0, 100),
                 center=False):
        # --- store logical (local) position ---
        self.local_x = x
        self.local_y = y
        self.center = center

        # --- visual setup ---
        self.rect = pg.Rect(0, 0, width, height)
        self.text = text
        self.colour = colour
        self.hover_colour = hover_colour
        self.text_colour = text_colour
        self.font = pg.font.SysFont(font_name, font_size)
        self.action = action

        # --- visual options ---
        self.border_radius = border_radius
        self.border_colour = border_colour
        self.border_thickness = border_thickness
        self.shadow = shadow
        self.shadow_offset = shadow_offset
        self.shadow_colour = shadow_colour

    def get_rect_with_offset(self, offset=(0, 0)):
        """Compute the button’s rect, applying offset and centering correctly."""
        # Create a copy to avoid mutating the original rect
        draw_rect = self.rect.copy()
        if self.center:
            draw_rect.center = (self.local_x + offset[0], self.local_y + offset[1])
        else:
            draw_rect.topleft = (self.local_x + offset[0], self.local_y + offset[1])
        return draw_rect

    def draw(self, screen, offset=(0, 0)):
        """Draws the button, handling hover, border, and shadow effects."""
        draw_rect = self.get_rect_with_offset(offset)
        mouse_pos = pg.mouse.get_pos()
        is_hovered = draw_rect.collidepoint(mouse_pos)
        current_colour = self.hover_colour if is_hovered else self.colour

        # --- Shadow ---
        if self.shadow:
            shadow_rect = draw_rect.move(self.shadow_offset)
            shadow_surface = pg.Surface(draw_rect.size, pg.SRCALPHA)
            pg.draw.rect(
                shadow_surface,
                self.shadow_colour,
                shadow_surface.get_rect(),
                border_radius=self.border_radius
            )
            screen.blit(shadow_surface, shadow_rect.topleft)

        # --- Main Button ---
        pg.draw.rect(screen, current_colour, draw_rect, border_radius=self.border_radius)

        # --- Border ---
        if self.border_colour and self.border_thickness > 0:
            pg.draw.rect(
                screen, self.border_colour, draw_rect,
                width=self.border_thickness, border_radius=self.border_radius
            )

        # --- Text ---
        text_surface = self.font.render(self.text, True, self.text_colour)
        text_rect = text_surface.get_rect(center=draw_rect.center)
        screen.blit(text_surface, text_rect)

    def handle_event(self, event, offset=(0,0)):
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            # Use the same rectangle that draw() uses
            if self.get_rect_with_offset(offset).collidepoint(event.pos):
                if self.action:
                    self.action()


# ================================
# Animator Class
# ================================



class SpriteObject(pg.sprite.Sprite):
    """
    A simplified sprite class for Year 10 students.

    Features:
    - Holds an image or an Animator
    - Tracks position with a rect
    - Supports movement
    - Simple collision detection
    """

    def __init__(self, x, y, width=None, height=None, image=None, animator=None):
        super().__init__()
        self.animator = animator
        self.image = image
        if self.animator:
            self.image = self.animator.frames[0]

        # No image or animator: use a plain coloured rectangle
        if self.image is None:
            self.image = pg.Surface((width or 32, height or 32))
            self.image.fill((255, 0, 255))

        # Use given size or image size
        self.size = None
        if width and height:
            self.size = (width, height)
            self.image = pg.transform.scale(self.image, self.size)
        self.rect = self.image.get_rect(topleft=(x, y))

        # Velocity
        self.dx = 0
        self.dy = 0

    def move(self, dx, dy):
        """Move the sprite by dx and dy."""
        self.rect.x += dx
        self.rect.y += dy

    def update(self, tick):
        """Update animator if exists, return current frame."""
        if self.animator:
            self.image = self.animator.update(tick)
            # Keep the size given when the sprite was made
            if self.size and self.image.get_size() != self.size:
                self.image = pg.transform.scale(self.image, self.size)

    def collides_with(self, other):
        """Check collision with another SpriteObject."""
        return self.rect.colliderect(other.rect)

    def handle_event(self, event, offset=(0,0)):
        pass

# ================================
# TextBox Class
# ================================

class TextBox:
    """
    A simple Pygame text input box for Year 10 students.

    Features:
    - Click to focus / type
    - Backspace, typing, and cursor blinking
    - get_text(), set_text(), insert_text()
    - Visual sunken textbox appearance
    - Character limit + auto-sizing from font width
    - Optional label positioned left, top, right, or bottom
    - Works inside Frames via offset support
    """

    def __init__(self, x, y,
                 max_chars=20, font_size=24,
                 text_color=(0, 0, 0),
                 box_color=(230, 230, 230),
                 border_color=(100, 100, 100),
                 padding=6,
                 label_text=None,
                 label_color=(255, 255, 255),
                 label_gap=10,
                 label_position="left"):
        self.font = pg.font.SysFont(None, font_size)
        self.text_color = text_color
        self.box_color = box_color
        self.border_color = border_color
        self.padding = padding
        self.label_text = label_text
        self.label_color = label_color
        self.label_gap = label_gap
        self.label_position = label_position.lower()

        # Estimate box size
        avg_char_width = self.font.size("M")[0]
        box_width = max_chars * avg_char_width + padding * 2
        box_height = font_size + padding * 2

        # Label surface
        if self.label_text:
            self.label_surface = self.font.render(self.label_text, True, self.label_color)
            self.label_rect = self.label_surface.get_rect()
        else:
            self.label_surface = None
            self.label_rect = None

        # Layout relative positions (local to this element)
        self._compute_layout(x, y, box_width, box_height)

        # Text state
        self.text = ""
        self.max_chars = max_chars
        self.cursor_pos = 0
        self.cursor_visible = True
        self.cursor_timer = 0
        self.active = False

    # ------------------------------------------------
    def _compute_layout(self, x, y, box_width, box_height):
        """Compute rects for label and box relative to (x, y) combined area."""
        if self.label_surface:
            if self.label_position == "left":
                total_width = self.label_rect.width + self.label_gap + box_width
                total_height = max(box_height, self.label_rect.height)
                self.rect = pg.Rect(self.label_rect.width + self.label_gap, 
                                    (total_height - box_height) // 2, 
                                    box_width, box_height)
                self.label_rect.topleft = (0, (total_height - self.label_rect.height) // 2)
                self.total_rect = pg.Rect(x, y, total_width, total_height)

            elif self.label_position == "right":
                total_width = self.label_rect.width + self.label_gap + box_width
                total_height = max(box_height, self.label_rect.height)
                self.rect = pg.Rect(0, (total_height - box_height) // 2,
                                    box_width, box_height)
                self.label_rect.topleft = (box_width + self.label_gap, (total_height - self.label_rect.height) // 2)
                self.total_rect = pg.Rect(x, y, total_width, total_height)

            elif self.label_position == "top":
                total_width = max(box_width, self.label_rect.width)
                total_height = self.label_rect.height + self.label_gap + box_height
                self.label_rect.midtop = (total_width // 2, 0)
                self.rect = pg.Rect((total_width - box_width) // 2,
                                    self.label_rect.height + self.label_gap,
                                    box_width, box_height)
                self.total_rect = pg.Rect(x, y, total_width, total_height)

            elif self.label_position == "bottom":
                total_width = max(box_width, self.label_rect.width)
                total_height = self.label_rect.height + self.label_gap + box_height
                self.rect = pg.Rect((total_width - box_width) // 2, 0,
                                    box_width, box_height)
                self.label_rect.midtop = (total_width // 2, box_height + self.label_gap)
                self.total_rect = pg.Rect(x, y, total_width, total_height)
        else:
            self.rect = pg.Rect(0, 0, box_width, box_height)
            self.total_rect = pg.Rect(x, y, box_width, box_height)

    # ------------------------------------------------
    def handle_event(self, event, offset=(0, 0)):
        """Handle key presses and mouse clicks, supporting offset."""
        # Get absolute rect for click detection
        abs_rect = self.rect.move(self.total_rect.x + offset[0],
                                  self.total_rect.y + offset[1])

        if event.type == pg.MOUSEBUTTONDOWN:
            self.active = abs_rect.collidepoint(event.pos)

        if self.active and event.type == pg.KEYDOWN:
            if event.key == pg.K_BACKSPACE:
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
            elif event.unicode.isprintable():
                self.insert_text(event.unicode)

    # ------------------------------------------------
    def update(self, tick):
        """Blinking cursor animation."""
        self.cursor_timer += tick
        if self.cursor_timer >= 400:
            self.cursor_timer = 0
            self.cursor_visible = not self.cursor_visible

    # ------------------------------------------------
    def draw(self, screen, offset=(0, 0)):
        """Draw the label and text box relative to an optional frame offset."""
        # Compute on-screen position
        ox, oy = self.total_rect.x + offset[0], self.total_rect.y + offset[1]

        # Label
        if self.label_surface:
            label_rect = self.label_rect.move(ox, oy)
            screen.blit(self.label_surface, label_rect)

        # Text box
        box_rect = self.rect.move(ox, oy)
        pg.draw.rect(screen, (255, 255, 255), box_rect)
        pg.draw.rect(screen, self.border_color, box_rect, 2)
        inner_rect = box_rect.inflate(-4, -4)
        pg.draw.rect(screen, self.box_color, inner_rect)

        # Text
        text_surface = self.font.render(self.text, True, self.text_color)
        text_x = inner_rect.x + self.padding
        text_y = inner_rect.y + (inner_rect.height - text_surface.get_height()) // 2
        screen.blit(text_surface, (text_x, text_y))

        # Cursor
        if self.active and self.cursor_visible:
            cursor_x = text_x + self.font.size(self.text[:self.cursor_pos])[0]
            cursor_y = text_y
            pg.draw.line(screen, (0, 0, 0),
                         (cursor_x, cursor_y),
                         (cursor_x, cursor_y + text_surface.get_height()), 2)

    # ------------------------------------------------
    def get_text(self):
        return self.text

    def set_text(self, new_text):
        self.text = new_text[:self.max_chars]
        self.cursor_pos = len(self.text)

    def insert_text(self, char):
        if len(self.text) < self.max_chars:
            self.text = self.text[:self.cursor_pos] + char + self.text[self.cursor_pos:]
            self.cursor_pos += 1

# ================================
# Popup Class
# ================================

class Popup:
    """
    A simple modal popup window that overlays the main screen or a frame.
    """
    def __init__(self, x, y, width, height, title="Popup", bg_color=(240, 240, 240)):
        self.rect = pg.Rect(x, y, width, height)
        self.bg_color = bg_color
        self.title = title
        self.visible = False
        self.children = []
        self.title_height = 40   # children are placed below the title bar
        self.close_button = Button(width - 30, 10, 20, 20, "X", colour=(200, 60, 60),
                                   hover_colour=(255, 80, 80), center=False,
                                   action=self.hide)
    
    def add(self, element):
        """Add child UI element."""
        self.children.append(element)

    def show(self):
        self.visible = True

    def hide(self):
        self.visible = False

    def _offsets(self, offset):
        """Return (popup top-left, children top-left) on screen."""
        px = self.rect.x + offset[0]
        py = self.rect.y + offset[1]
        return (px, py), (px, py + self.title_height)

    def handle_event(self, event, offset=(0, 0)):
        """Only handle events when visible."""
        if not self.visible:
            return

        popup_pos, child_pos = self._offsets(offset)
        for child in self.children:
            if hasattr(child, "handle_event"):
                child.handle_event(event, offset=child_pos)
        self.close_button.handle_event(event, offset=popup_pos)

    def update(self, tick):
        """Update animations or child widgets."""
        if not self.visible:
            return
        for child in self.children:
            if hasattr(child, "update"):
                child.update(tick)

    def draw(self, screen, offset=(0, 0)):
        if not self.visible:
            return

        popup_pos, child_pos = self._offsets(offset)
        box = pg.Rect(popup_pos, self.rect.size)

        # Dim background (optional)
        overlay = pg.Surface(screen.get_size(), pg.SRCALPHA)
        overlay.fill((0, 0, 0, 120))
        screen.blit(overlay, (0, 0))

        # Draw popup background
        pg.draw.rect(screen, self.bg_color, box, border_radius=10)
        pg.draw.rect(screen, (0, 0, 0), box, 2, border_radius=10)

        # Title
        font = pg.font.SysFont(None, 24)
        title_surface = font.render(self.title, True, (0, 0, 0))
        screen.blit(title_surface, (box.x + 10, box.y + 10))

        # Draw children (below the title bar)
        for child in self.children:
            if hasattr(child, "draw"):
                child.draw(screen, offset=child_pos)

        # Close button
        self.close_button.draw(screen, offset=popup_pos)

# ================================
# World Class
# ================================

class World:
    """
    A container for:
        • Tilemap background layers
        • Tilemap foreground layers
        • Dynamic sprite objects (player, enemies, NPC)
        • Camera-based drawing
    """

    def __init__(self, tiled_map, camera):
        self.map = tiled_map            # TiledMap instance
        self.camera = camera            # Camera instance

        # Sprite groups
        self.sprites = pg.sprite.Group()     # Player, enemies, etc.

    # ----------------------------------------------------------------------

    def add_sprite(self, sprite):
        """Add any dynamic object (player, enemy) to the world."""
        self.sprites.add(sprite)

    # ----------------------------------------------------------------------

    def update(self, dt):
        """Update tiles (animated), dynamic sprites, and camera logic."""
        
        # Update animated tiles
        for tile in self.map.background:
            if hasattr(tile, "update"):
                tile.update(dt)

        for tile in self.map.foreground:
            if hasattr(tile, "update"):
                tile.update(dt)

        # Update all sprites
        for spr in self.sprites:
            if hasattr(spr, "update"):
                spr.update(dt)

    # ----------------------------------------------------------------------

    def draw(self, surface):
        """
        Draw order:
            1. Background tile layers
            2. Sprite objects (player, enemies)
            3. Foreground tile layers (trees, roofs, top-layers etc)
        """

        # -----------------------------
        # Draw BACKGROUND tiles
        # -----------------------------
        for tile in self.map.background:
            tx = tile.rect.x - self.camera.offset.x
            ty = tile.rect.y - self.camera.offset.y
            surface.blit(tile.image, (tx, ty))

        # -----------------------------
        # Draw SPRITES
        # -----------------------------
        for spr in self.sprites:
            sx = spr.rect.x - self.camera.offset.x
            sy = spr.rect.y - self.camera.offset.y
            surface.blit(spr.image, (sx, sy))

        # -----------------------------
        # Draw FOREGROUND tiles
        # -----------------------------
        for tile in self.map.foreground:
            tx = tile.rect.x - self.camera.offset.x
            ty = tile.rect.y - self.camera.offset.y
            surface.blit(tile.image, (tx, ty))



