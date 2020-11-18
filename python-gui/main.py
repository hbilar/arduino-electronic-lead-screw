import sys
import attr
import pygame

import pyguime

import logic


@attr.s
class MachineState(object):
    # Steps from zero of machine
    global_step_counter = attr.ib(default=0)
    
    # current z position
    z = attr.ib(default=0)

    # z screw pitch (mm)
    z_pitch = attr.ib(default=1)

    # z steps per 1 revolution of screw
    z_steps_per_rev = attr.ib(default=1)

    # current RPM of spindle
    rpm = attr.ib(default=100)

    # If movement is happening
    moving = attr.ib(default=False)

    # steps left until movement is finished
    steps_left = attr.ib(default=0)


def cached(func):
    cache = dict()

    def wrapper(*args):
        cache_key = repr(*args)
        if cache_key in cache:
            return cache[cache_key]
        result = func(*args)
        cache[cache_key] = result
        return result

    return wrapper


def cached_keypad(func):
    cache = dict()

    def wrapper(*args):
        cache_key = repr(*args) + repr(logic.textbox_values)
        if cache_key in cache:
            return cache[cache_key]
        result = func(*args)
        cache[cache_key] = result
        return result

    return wrapper


@cached
def sprite_func_text(widget):
    """ Draw a piece of text (widget.data['text]) on a surface """

    surface = pygame.Surface(widget.size)

    # sane defaults
    default_font_name = 'Comic Sans MS'
    default_font_size = 15
    default_colour = (255, 0, 0)

    font_name = widget.data.get('font', default_font_name) if widget.data else default_font_name
    font_size = widget.data.get('fontsize', default_font_size) if widget.data else default_font_size
    widget_font = pygame.font.SysFont(font_name, font_size)

    font_colour = widget.data.get('font_colour', default_colour) if widget.data else default_colour

    text = widget.data['text'] if widget.data and widget.data.get('text', None) else widget.name
    surface.blit(widget_font.render(text, False, font_colour), (0, 0))

    return surface


@cached_keypad
def sprite_func_keypad(widget):
    """ Draw a piece of text (widget.data['text]) on a surface """

    surface = pygame.Surface(widget.size)

    # sane defaults
    default_font_name = 'Comic Sans MS'
    default_font_size = 15
    default_colour = (255, 0, 0)

    font_name = widget.data.get('font', default_font_name) if widget.data else default_font_name
    font_size = widget.data.get('fontsize', default_font_size) if widget.data else default_font_size
    widget_font = pygame.font.SysFont(font_name, font_size)

    font_colour = widget.data.get('font_colour', default_colour) if widget.data else default_colour

    value = logic.textbox_values.get(widget.data.get('textbox_id'), "")
    surface.blit(widget_font.render(value, False, font_colour), (0, 0))

#    text = widget.data['text'] if widget.data and widget.data.get('text', None) else widget.name
#    surface.blit(widget_font.render(text, False, font_colour), (0, 0))

    return surface


def main_loop(pyguime_screen, widgets):

    gui_surface = pygame.Surface((pyguime.WIDTH, pyguime.HEIGHT)).convert()

    running = True


    while running:
        gui_surface.fill((0, 0, 128))
        gui_surface = pyguime.draw_widgets(gui_surface, widgets)


        # Handle pygame events (button presses etc)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # Check keyboard presses
            if event.type in [ pygame.KEYDOWN, pygame.KEYUP ]:
                print(f"event.key:  {event.key}")

                if event.key == pygame.K_ESCAPE:
                    print("Quitting...")
                    running = False

            if event.type == pygame.MOUSEBUTTONUP:
                pyguime.handle_mouseclick(widgets, pygame.mouse.get_pos())


        # scale and blit to screen
        pyguime_screen.screen.blit(gui_surface, (0, 0))
        pygame.display.flip()

 
# define a main function
def main():
     
    # create a screen to draw on
    pyguime_screen = pyguime.setup_screen(width=1024, height=600)

    # widgets

    keypad_widgets = [ ]
    key_size = (30, 30)
    key_space = (10, 5)

    # Set up a keypad
    for n in range (0,10):
        print(f'n = {n}')

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

        print(f"  n = {n},   col = {col},  row = {row}")

        number = pyguime.PyguimeWidget(name=f'num_{n}',
                                       pos=(col * (key_size[0] + key_space[0]),
                                            row * (key_size[1] + key_space[1])),
                                       size=key_size,
                                       background=(0,20*n,0),
                                       data={'character': str(n), 'textbox_id': 'test'},
                                       click_callback=logic.keypad_button_callback
                                            )
        keypad_widgets.append(number)

    widgets = [ pyguime.PyguimeWidget(name="rect1", pos=(100,100), size=(50, 100), click_callback=logic.sample_button_callback),
                pyguime.PyguimeWidget(name="rect2", pos=(10,10), size=(10, 10), background=(128, 0, 0)),
                pyguime.PyguimeWidget(name="image", pos=(200, 200), size=(50, 50), image="images/ball.png"),
                pyguime.PyguimeWidget(name="imgfunc", pos=(300, 30), size=(100, 100), image_function=sprite_func_text, data={'text': 'sample'}, click_callback=logic.sample_button_callback),
                pyguime.PyguimeWidget(name="keypad_text", pos=(300, 230), size=(100, 100), image_function=sprite_func_keypad, data={'textbox_id': 'test'}),
                ] + keypad_widgets


    main_loop(pyguime_screen, widgets)
     
     
if __name__=="__main__":
    main()
