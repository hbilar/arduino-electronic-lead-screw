import pygame
import attr

import enum


WIDTH = 640
HEIGHT = 480

C_WHITE = (255, 255, 255)

class TextboxType(enum.Enum):
    NineAndTextbox = 1


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


@attr.s
class PyguimeContainer(PyguimeClickable):
    """ A container has other widgets inside it """

    def draw(self):
        """ produce a surface with image data on it, in (0,0) """
        surface = pygame.Surface(self.size)
        pygame.draw.rect(surface, self.background, pygame.Rect((0, 0), self.size))

        if self.children:
            for c in self.children:
                s = c.draw()
                surface.blit(s, c.pos, (0, 0, c.size[0], c.size[1]))

        return surface

    def add(self, widget):
        if self.children is None:
            self.children = []
        self.children.append(widget)

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

    children = attr.ib(default=None)
    click_callback = attr.ib(default=container_handle_mouseclick)


@attr.s
class PyguimeWidget(PyguimeClickable):
    """ Class to hold a widget. Widgets are objects that can be drawn on screen.
        A widget is a container that can contain other widgets """

    click_callback = attr.ib(default=None)

    image = attr.ib(default=None)

    # The image function is used to draw the widget, if defined
    image_function = attr.ib(default=None)

    _image_data = attr.ib(default=None)

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


@attr.s
class PyguimeTextbox(PyguimeWidget):
    """ Class to hold textbox data """

    text = attr.ib(default="default text")
    font = attr.ib(default="Comic Sans MS")

    font_size = attr.ib(default=15)
    font_colour = attr.ib(default=(255,0,0))

    align = attr.ib(default=TextAlign.LEFT)
    valign = attr.ib(default=TextAlign.TOP)


    def get_text(self):
        return self.text

    def set_text(self, text):
        self.text = text

    def draw(self):
        """ Draw a piece of text (widget.data['text]) on a surface """

        surface = pygame.Surface(self.size)

        # draw background first
        pygame.draw.rect(surface, self.background, pygame.Rect((0, 0), self.size))

        widget_font = pygame.font.SysFont(self.font, self.font_size)

        # draw the text onto a surface and get the bounding rect
        font_surface = widget_font.render(self.text, False, self.font_colour)
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

        # finally draw the font image onto the right place in the surface
        surface.blit(font_surface, align_pos)
        return surface


@attr.s
class PyguimeKeypad(PyguimeContainer):
    """ Keypad type object """

    children = attr.ib(default=None)
    layout = attr.ib(default=TextboxType.NineAndTextbox)


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

        cur_val = textbox.text
        cur_val = cur_val + widget.data.get('character', '')
        print(f"Updating textbox to {cur_val}")

        textbox.text = cur_val


    def add_keypad(self, pos=(0,30), key_size=(30, 30), key_space=(10, 10),
                   background=(100, 100, 100)):

        # Set up a keypad
        for n in range(0, 10):
            if n == 0:
                row = 3
            elif n <= 3:
                row = 2
            elif n <= 6:
                row = 1
            else:
                row = 0

            if n == 0:
                col = 1
            else:
                col = (n - 1) % 3

            number=PyguimeTextbox(name=f'num_{n}',
                                  text=str(n),
                                  pos=(pos[0] + col * (key_size[0] + key_space[0]),
                                       pos[1] + row * (key_size[1] + key_space[1])),
                                  size=key_size,
                                  font_size=key_size[1],
                                  valign=TextAlign.CENTER,
                                  align=TextAlign.CENTER,
                                  background=background,
                                  click_callback=PyguimeKeypad._key_callback,
                                  parent=self,
                                  data={'character': str(n)}
            )
            self.add(number)
        return self



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


def handle_mouseclick(widgets, pos):
    """ Process a mouse click """

    print(f"Mouse click at {pos[0]} x {pos[1]}")
    w = get_widget_at_position(widgets, pos)
    print(f"Widget: {w}")

    if w and w.click_callback:
        rel_pos = (pos[0] - w.pos[0], pos[1] - w.pos[1])
        w.click_callback(w, rel_pos)


def setup_screen(width=WIDTH, height=HEIGHT):
    pygame.init()

    return PyguimeScreen(screen=pygame.display.set_mode((width, height)),
                         width=width,
                         height=height)

