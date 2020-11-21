import pygame
import attr


WIDTH = 640
HEIGHT = 480

C_WHITE = (255, 255, 255)

image_data = {}

@attr.s
class PyguimeEvent(object):
    # pygame.events
    pygame_events = attr.ib(default=None)
    pyguime_events = attr.ib(default=None)


@attr.s
class PyguimeWidget(object):
    """ Class to hold a widget. Widgets are objects that can be drawn on screen.
        A widget is a container that can contain other widgets """

    name = attr.ib(default=None)
    click_callback = attr.ib(default=None)

    children = attr.ib(default=None)

    background = attr.ib(default=None)
    image = attr.ib(default=None)
    pos = attr.ib(default=(0,0))
    size = attr.ib(default=(0,0))

    # The image function is used to draw the widget, if defined
    image_function = attr.ib(default=None)

    # dict to hold user defined info about the widget
    data = attr.ib(default=None)

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

    def get_text(self):
        return self.text

    def set_text(self, text):
        self.text = text

    def draw(self):
        """ Draw a piece of text (widget.data['text]) on a surface """

        surface = pygame.Surface(self.size)

        font_name = self.font
        font_size = self.font_size
        font_colour = self.font_colour

        widget_font = pygame.font.SysFont(font_name, font_size)

        text = self.text
        surface.blit(widget_font.render(text, False, font_colour), (0, 0))

        return surface

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

