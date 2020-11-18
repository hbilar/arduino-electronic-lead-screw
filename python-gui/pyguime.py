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

@attr.s
class PyguimeScreen(object):
    """ Class to hold pygame stuff etc """
    screen = attr.ib(default=None)
    width = attr.ib(default=WIDTH)
    height = attr.ib(default=HEIGHT)



def draw_widgets(surface, widgets):
    """ Draw the pyguime widgets onto the surface"""

    for w in widgets:
        if w.background:
            pygame.draw.rect(surface, w.background, pygame.Rect(w.pos, w.size))
        elif w.image:
            if not image_data.get(w.image, None):
                image_data[w.image] = pygame.image.load(w.image)
            surface.blit(image_data[w.image], w.pos, (0, 0, w.size[0], w.size[1]))
        elif w.image_function:
            # A function to draw the image exists
            surface.blit(w.image_function(w), w.pos, (0, 0, w.size[0], w.size[1]))
        else:
            # default to just an outline
            pygame.draw.rect(surface, C_WHITE, pygame.Rect(w.pos, w.size), 1)

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

