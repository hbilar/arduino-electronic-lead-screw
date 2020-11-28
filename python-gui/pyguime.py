import pygame
import attr

import enum


WIDTH = 640
HEIGHT = 480

C_WHITE = (255, 255, 255)
DEFAULT_BG_COLOUR = (255, 255, 255)

COL_TRANSPARENT = (1, 2, 3)

class KeypadFunction(enum.Enum):
    Clear = 1
    Backspace = 2


class TextAlign(enum.Enum):
    CENTER = 1
    RIGHT = 2
    LEFT = 3
    TOP = 4
    BOTTOM = 5


image_data = {}

@attr.s
class PyguimeEvent(object):
    # pygame.events
    pygame_events = attr.ib(default=None)
    pyguime_events = attr.ib(default=None)


@attr.s
class PyguimeBaseWidget(object):
    """ base class for pyguime widgets """
    name = attr.ib(default=None)

    # dict to hold user defined info about the widget
    data = attr.ib(default=None)

    parent = attr.ib(default=None)


@attr.s
class PyguimeClickable(PyguimeBaseWidget):
    pos = attr.ib(default=(0,0))
    size = attr.ib(default=(0,0))
    background = attr.ib(default=(0,0,0))

    # propagate clicks to parent instead of handling locally
    propagate_click = attr.ib(default=True)

    # Is the mouse down on this widget at the moment?
    _mouse_is_down = attr.ib(default=False)
    _mouse_down_pos = attr.ib(default=(0,0))

    children = attr.ib(default=None)

    def add(self, widget):
        if self.children is None:
            self.children = []

        widget.parent = self
        self.children.append(widget)
        return self

    def _default_click_callback(self, pos):
        """
        Default click callback - simply propagate click up to parent
        if parent is defined, and widget has "click_propagate = True
        :param pos: position of click (x, y)
        :return: None
        """

        print(f"DEFAULT CLICK CALLBACK: {self}")

        if self.propagate_click and self.parent:
            if self.parent.click_callback:
                self.parent.click_callback(pos)

    def determine_background(self):
        """ Find the background colour to use for this object. Checks if
            current object has a background defined, and uses it, otherwise
            checks parent """

        if hasattr(self, 'background') and self.background:
            return self.background

        if self.parent:
            return self.parent._determine_background
        else:
            return DEFAULT_BG_COLOUR


    click_callback = attr.ib(default=_default_click_callback)


@attr.s
class PyguimeContainer(PyguimeClickable):
    """ A container has other widgets inside it """

    def add_object(self, obj):
        obj.pos = (obj.pos[0], obj.pos[1] + self.cur_y)
        obj.parent = self

        self.add(obj)

        self.cur_y = self.cur_y + obj.size[1]
        return self

    def add_object_linear(self, obj, vertical=True):
        """ Add a widget to the container in either a horizontal
            or vertical fashion """
        obj.pos = (obj.pos[0], obj.pos[1] + self.cur_y)
        obj.parent = self
        self.add(obj)

        self.cur_y = self.cur_y + obj.size[1]
        return self

    def draw(self):
        """ produce a surface with image data on it, in (0,0) """
        surface = pygame.Surface(self.size)
        pygame.draw.rect(surface, self.background, pygame.Rect((0, 0), self.size))

        if self._mouse_is_down:
            mouse_down_widget = self.get_widget_at_position(self._mouse_down_pos)
            if mouse_down_widget:
                m_down_pos = self._mouse_down_pos
                w_pos = mouse_down_widget.pos
                rel_pos = (m_down_pos[0] - w_pos[0],
                           m_down_pos[1] - w_pos[1])
                mouse_down_widget._mouse_is_down = True
                mouse_down_widget._mouse_down_pos = rel_pos

        if self.children:
            for c in self.children:
                s = c.draw()
                surface.blit(s, c.pos, (0, 0, c.size[0], c.size[1]))

        return surface

    def get_widget_at_position(self, pos):
        """ Return the widget that is at position pos """

        cur_widget = None
        for w in self.children:
            if (w.pos[0] <= pos[0] and w.pos[0] + w.size[0] > pos[0] and
                    w.pos[1] <= pos[1] and w.pos[1] + w.size[1] > pos[1]):
                # Inside bounding box
                # note - not returning at first hit, in case we have overlapping
                # widgets we want to pick the last one ("last in stack"), as that
                # mirrors what is seen on screen
                cur_widget = w

        return cur_widget

    def get_widget_by_name(self, name):
        """ Find a widget named 'name' and return it """

        for w in self.children:
            if w.name == name:
                return w

        return None


    def container_handle_mouseclick(self, pos):
        """ Process a mouse click in the container"""

        print(f"CONTAINER click at {pos[0]} x {pos[1]}")
        w = self.get_widget_at_position(pos)
        print(f"Widget: {w}")

        if w and w.click_callback:
            rel_pos = (pos[0] - w.pos[0], pos[1] - w.pos[1])
            w.click_callback(w, rel_pos)


    def generate(self):
        if self.auto_size:
            # calculate bounding box for all the children in the container

            cur_max = [ 0, 0]
            for w in self.children:
                size = w.draw().get_size()

                if w.pos[0] + size[0] > cur_max[0]:
                    cur_max[0] = w.pos[0] + size[0]
                if w.pos[1] + size[1] > cur_max[1]:
                    cur_max[1] = w.pos[1] + size[1]

            self.size=(cur_max[0], cur_max[1])

        return self

    cur_y = attr.ib(default=0)
    auto_size = attr.ib(default=True)
    click_callback = attr.ib(default=container_handle_mouseclick)


@attr.s
class PyguimeWidget(PyguimeClickable):
    """ Class to hold a widget. Widgets are objects that can be drawn on screen.
        A widget is a container that can contain other widgets """

    def draw(self):
        """ produce a surface with image data on it, in (0,0) """
        surface = pygame.Surface(self.size)

        if self.image:
            #if not image_data.get(self.image, None):
            if not self._image_data:
                print("loading")
                self._image_data = pygame.image.load(self.image)
            surface.blit(self._image_data, (0, 0), (0, 0, self.size[0], self.size[1]))
        elif self.image_function:
            # A function to draw the image exists
            surface.blit(self.image_function(), (0,0), (0, 0, self.size[0], self.size[1]))
        elif self.background:
            # simple background
            pygame.draw.rect(surface, self.background, pygame.Rect((0, 0), self.size))
        else:
            # default to just an outline
            pygame.draw.rect(surface, C_WHITE, pygame.Rect((0,0), self.size), 1)

        return surface

    click_callback = attr.ib(default=None)
    image = attr.ib(default=None)

    # The image function is used to draw the widget, if defined
    image_function = attr.ib(default=None)
    _image_data = attr.ib(default=None)


@attr.s
class PyguimeButton(PyguimeClickable):
    """ A single, clickable button """



    def draw(self):
        """ produce a surface with image data on it, in (0,0) """
        surface = pygame.Surface(self.size)
        pygame.draw.rect(surface, self.background, pygame.Rect((0, 0), self.size))

        # simple background

        if self._mouse_is_down:
            pygame.draw.rect(surface, self.background_mouse_down,
                             pygame.Rect((0, 0), self.size))
        else:
            sticky_bg = self.background_selected if self.is_down else self.background
            bg = sticky_bg if self.sticky else self.background
            pygame.draw.rect(surface, bg, pygame.Rect((0, 0), self.size))

        # top line
        pygame.draw.line(surface, self.top_shading_colour, (0, 0),
                         (self.size[0], 0), self.outline_line_width)
        # left line
        pygame.draw.line(surface, self.top_shading_colour, (0, 0),
                         (0, self.size[1]), self.outline_line_width)
        # right line
        pygame.draw.line(surface, self.bottom_shading_colour,
                         (self.size[0] - self.outline_line_width + 1, self.outline_line_width),
                         (self.size[0] - self.outline_line_width + 1, self.size[1]),
                         self.outline_line_width)
        # bottom line
        pygame.draw.line(surface, self.bottom_shading_colour,
                         (0, self.size[1] - self.outline_line_width + 1),
                         (self.size[0], self.size[1] - self.outline_line_width + 1),
                         self.outline_line_width)

        # add any text or other child objects
        if self.children:
            for c in self.children:
                s = c.draw()
                surface.blit(s, c.pos, (0, 0, c.size[0], c.size[1]))

        return surface


    def button_handle_mouseclick(self, pos):
        """ Process a mouse click in the container"""

        print(f"BUTTON {self.name} click at {pos[0]} x {pos[1]}")
        if self.sticky:
            self.is_down = not self.is_down



    def generate(self):
        self.add(PyguimeTextbox(name=f"textbox_{self.name}", size=self.size,
                                text=self.text, font_size=self.font_size,
                                font_colour=self.font_colour, align=self.align,
                                valign=self.valign,
                                click_callback=self.click_callback,
                                transparent_background=True))
        return self


    text = attr.ib(default="button")

    # Is the button sticky (does it stay selected)?
    sticky = attr.ib(default=False)
    # If the button is sticky, is it currently down?
    is_down = attr.ib(default=False)

    # fixme: all this should really be a style type object...
    font = attr.ib(default="Comic Sans MS")
    font_size = attr.ib(default=15)
    font_colour = attr.ib(default=(0, 0, 0))
    align = attr.ib(default=TextAlign.CENTER)
    valign = attr.ib(default=TextAlign.CENTER)
    background = attr.ib(default=(200, 200, 200))
    background_mouse_down = attr.ib(default=(255, 0, 0))
    background_selected = attr.ib(default=(100, 100, 100))
    bottom_shading_colour = attr.ib(default=(60, 60, 60))
    top_shading_colour = attr.ib(default=(255, 255, 255))
    outline_line_width = attr.ib(default=3)

    size = attr.ib(default=(100, 50))

    # colour to make transparent in the blit (used for the textbox we use
    # for the text of the button
    colour_key = attr.ib(default=(1, 2, 3))

    click_callback = attr.ib(default=button_handle_mouseclick)


@attr.s
class PyguimeCheckbox(PyguimeButton):
    """ Class to handle a single checkbox """

    def draw(self):
        """ produce a surface with image data on it, in (0,0) """
        surface = pygame.Surface(self.size)
        pygame.draw.rect(surface, self.background, pygame.Rect((0, 0), self.size))

        # simple background
        if self._mouse_is_down:
            pygame.draw.rect(surface, self.background_mouse_down,
                             pygame.Rect((0, 0), self.size))
        else:
            bg = self.background_selected if self.is_down else self.background
            pygame.draw.rect(surface, bg,
                             pygame.Rect(self.checkbox_offset, self.checkbox_size))

        # rect around the checkbox
        pygame.draw.rect(surface, (0, 0, 0),
                         pygame.Rect(self.checkbox_offset, self.checkbox_size), 1)

        # add any text or other child objects
        if self.children:
            for c in self.children:
                s = c.draw()
                surface.blit(s, c.pos, (0, 0, c.size[0], c.size[1]))

        return surface

    def generate(self):
        self.sticky = True

        self.checkbox_offset = (self.checkbox_offset[0],
                                (self.size[1]-self.checkbox_size[1])/2)

        self.add(PyguimeTextbox(name=f"textbox_{self.name}", size=self.size,
                                text=self.text, font_size=self.font_size,
                                font_colour=self.font_colour, align=TextAlign.LEFT,
                                valign=self.valign,
                                click_callback=self.click_callback,
                                transparent_background=True,
                                offset=(self.checkbox_size[0] + self.checkbox_offset[0] + self.text_offset[0], self.text_offset[1])))
        return self

    checkbox_size = attr.ib(default=(20, 20))
    checkbox_offset = attr.ib(default=(5, 10))
    # How much to offset the text label from the button rect
    text_offset = attr.ib(default=(5, 0))

    sticky = attr.ib(default=True)


@attr.s
class PyguimeCheckboxes(PyguimeContainer):
    """ Class to handle a several checkboxes """

    def add_object_linear(self, obj, vertical=True):
        """ Add a widget to the container in either a horizontal
            or vertical fashion """
        obj.pos = (obj.pos[0], obj.pos[1] + self.cur_y)
        self.add(obj)

        self.cur_y = self.cur_y + obj.size[1]
        return self

    def generate(self):
        """ Method to finalize the checkboxes. At the moment all it
            does is resize the container for the checkboxes... """
        if self.auto_size:
            self.size=(self.size[0], self.cur_y)
        return self

    cur_y = attr.ib(default=0)


@attr.s
class PyguimeTextbox(PyguimeWidget):
    """ Class to hold textbox data (like a label etc) """

    def generate(self):
        """ clean up class data """

        if self.auto_size and self.size == (0, 0):
                font_surface = self.get_text_surface()
                font_rect =font_surface.get_rect()
                self.size = (font_rect[2], font_rect[3])

        return self

    def get_text(self):
        return self.text

    def set_text(self, text):
        self.text = text

    def get_text_surface(self):
        """ make a surface with the text of the widget """
        widget_font = pygame.font.SysFont(self.font, self.font_size)

        # draw the text onto a surface and get the bounding rect
        font_surface = widget_font.render(self.text, False, self.font_colour)

        return font_surface

    def draw(self):
        """ Draw a piece of text (widget.data['text]) on a surface """

        surface = pygame.Surface(self.size)

        # draw background first
        if self.transparent_background:
            pygame.draw.rect(surface, self.transparent_colour,
                             pygame.Rect((0, 0), self.size))
            surface.set_colorkey(self.transparent_colour)
        else:
            bg = self.determine_background()
            pygame.draw.rect(surface, bg, pygame.Rect((0, 0), self.size))

        # draw the text onto a surface and get the bounding rect
        font_surface = self.get_text_surface()
        font_rect = font_surface.get_rect()

        align_pos = (0, 0) # default:  align = LEFT, valign = TOP
        # horizontal alignment
        if self.align == TextAlign.RIGHT:
            align_pos = (self.size[0] - font_rect[2], align_pos[1])
        elif self.align == TextAlign.CENTER:
            align_pos = ((self.size[0] - font_rect[2])/2, align_pos[1])

        # vertical
        if self.valign == TextAlign.BOTTOM:
            align_pos = (align_pos[0], self.size[1] - font_rect[3])
        elif self.valign == TextAlign.CENTER:
            align_pos = (align_pos[0], (self.size[1] - font_rect[3])/2)

        # add any offset
        align_pos = (align_pos[0] + self.offset[0],
                     align_pos[1] + self.offset[1])

        # finally draw the font image onto the right place in the surface
        surface.blit(font_surface, align_pos)
        return surface

    text = attr.ib(default="default text")
    font = attr.ib(default="Comic Sans MS")

    font_size = attr.ib(default=15)
    font_colour = attr.ib(default=(0,0,0))

    align = attr.ib(default=TextAlign.LEFT)
    valign = attr.ib(default=TextAlign.TOP)

    offset = attr.ib(default=(0, 0))

    transparent_background = attr.ib(default=False)
    transparent_colour = attr.ib(default=COL_TRANSPARENT)

    auto_size = attr.ib(default=True)


@attr.s
class PyguimeKeypadKey(object):
    """ Define a key """

    display = attr.ib(default=None)
    value = attr.ib(default=None)
    function = attr.ib(default=None)

    def __attrs_post_init__(self):
        if not self.value:
            self.value = self.display


@attr.s
class PyguimeKeypadLayout(object):
    """ Define a keypad layout """

    keys = attr.ib(default=[
        [PyguimeKeypadKey(display='7'),
         PyguimeKeypadKey(display='8'),
         PyguimeKeypadKey(display='9'),
         ],
        [PyguimeKeypadKey(display='4'),
         PyguimeKeypadKey(display='5'),
         PyguimeKeypadKey(display='6'),
         ],
        [PyguimeKeypadKey(display='1'),
         PyguimeKeypadKey(display='2'),
         PyguimeKeypadKey(display='3'),
         ],
        [PyguimeKeypadKey(display='Clr', function=KeypadFunction.Clear),
         PyguimeKeypadKey(display='0'),
         PyguimeKeypadKey(display='.'),
        ],
        ])


@attr.s
class PyguimeKeypad(PyguimeContainer):
    """ Keypad type object """

    def add_textbox(self, size=(100, 30), font_size=15,
                    font_colour=(255, 0, 0), pos=(0,0),
                    initial_text=""):
        self.add(PyguimeTextbox(name="textbox", size=size, pos=pos,
                                text=initial_text, font_size=font_size,
                                font_colour=font_colour, align=TextAlign.CENTER,
                                valign=TextAlign.CENTER))
        return self

    def _key_callback(widget, pos):
        print(f"Callback for widget {widget},   pos = {pos}")

        if not widget.parent:
            print(f"** ERROR: parent not defined for {widget}")
            return

        textbox = widget.parent.get_widget_by_name('textbox')
        if not textbox:
            print(f"** ERROR: No widget named 'textbox' could be found")
            return

        if widget.data.get('function', None) == KeypadFunction.Clear:
            textbox.text = ""
        elif widget.data.get('function', None) == KeypadFunction.Backspace:
            textbox.text = textbox.text[:-1]
        else:
            textbox.text = textbox.text + widget.data.get('character', '')
            print(f"Updating textbox to {textbox.text}")

    def generate(self, pos=(0, 30), key_size=(30, 30), key_space=(10, 10),
                 background=(100, 100, 100), font_colour=(255,255,0),
                 layout=PyguimeKeypadLayout()):
        """ Add a keypad (or other buttons) to a PyguimeKeypad. The
            layout of the keys is defined by the PyguimeKeypadLayout object
            passed in as the layout parameter """

        for r in range(0, len(layout.keys)):
            for c in range(0, len(layout.keys[r])):
                k = layout.keys[r][c]

                char = PyguimeTextbox(name=k.value, text=k.display,
                                      pos=(pos[0] + c * (key_size[0] + key_space[0]),
                                           pos[1] + r * (key_size[1] + key_space[1])),
                                      size=key_size,
                                      font_size=key_size[1],
                                      font_colour=font_colour,
                                      valign=TextAlign.CENTER,
                                      align=TextAlign.CENTER,
                                      background=background,
                                      click_callback=PyguimeKeypad._key_callback,
                                      parent=self,
                                      data={'character': k.value,
                                            'function': k.function}
                                      )
                self.add(char)
        return self

    children = attr.ib(default=None)


@attr.s
class PyguimeScreen(object):
    """ Class to hold pygame stuff etc """
    screen = attr.ib(default=None)
    width = attr.ib(default=WIDTH)
    height = attr.ib(default=HEIGHT)


def draw_widgets(surface, widgets):
    """ Draw the pyguime widgets onto the surface"""

    for w in widgets:
        w_surface = w.draw()
        if w_surface:
            surface.blit(w_surface, w.pos, (0, 0, w.size[0], w.size[1]))


    return surface


def get_widget_at_position(widgets, pos):
    """ Return the widget that is at position pos """

    cur_widget = None
    for w in widgets:
        if (w.pos[0] <= pos[0] and w.pos[0] + w.size[0] > pos[0] and
            w.pos[1] <= pos[1] and w.pos[1] + w.size[1] > pos[1]):
            # Inside bounding box
            cur_widget = w

    return cur_widget


# The last widget that was clicked on
_last_mouse_click_widget = None

def _clear_downclick_status(widgets):
    """ Set the down click property to False for all widgets that
        have the down click property """
    for w in widgets:
        # clear any child objects
        if hasattr(w, "children") and w.children:
            _clear_downclick_status(w.children)

        # clear this object
        if hasattr(w, "_mouse_is_down"):
            w._mouse_is_down = False


def handle_mouseclick_up(widgets, pos):
    """ Process a mouse click """

    print(f"Mouse UP at {pos[0]} x {pos[1]}")
    w = get_widget_at_position(widgets, pos)
    print(f"Widget: {w}")

    global _last_mouse_click_widget

    if _last_mouse_click_widget is w:
        # good - the widget we release the mouse on is the same as the one we
        # clicked on

        if w and w.click_callback:
            rel_pos = (pos[0] - w.pos[0], pos[1] - w.pos[1])
            w.click_callback(w, rel_pos)

    # As we have now released the mouse button, we should not have any
    # widgets that currently have the mouse down on them.
    _last_mouse_click_widget = None

    # finally, clear the downclick status of any widgets
    _clear_downclick_status(widgets)


def handle_mouseclick_down(widgets, pos):
    """ Process a mouse click """

    w = get_widget_at_position(widgets, pos)

    global _last_mouse_click_widget
    if _last_mouse_click_widget is not w:
        _last_mouse_click_widget = w

        # clear down click for any widgets
        _clear_downclick_status(widgets)

        # set the downclick status on the new widget
        if hasattr(w, "_mouse_is_down"):
            rel_pos = (pos[0] - w.pos[0], pos[1] - w.pos[1])
            w._mouse_is_down = True
            w._mouse_down_pos = rel_pos


def setup_screen(width=WIDTH, height=HEIGHT):
    pygame.init()

    return PyguimeScreen(screen=pygame.display.set_mode((width, height)),
                         width=width,
                         height=height)

