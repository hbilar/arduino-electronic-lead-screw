import pygame
import attr


WIDTH = 640
HEIGHT = 480

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

    background = attr.ib(default=(0,0,0))
    pos = attr.ib(default=(0,0))
    size = attr.ib(default=(0,0))


def draw_widgets(surface, widgets):
    """ Draw the pyguime widgets onto the surface"""

    for w in widgets:
        pygame.draw.rect(surface, w.background, pygame.Rect(w.pos, w.size))

    return surface


def setup_screen(width=WIDTH, height=HEIGHT):
    pygame.init()
    return pygame.display.set_mode((width, height))

