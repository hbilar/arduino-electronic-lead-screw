import logging
import sys

sys.path.insert(0, '../libraries/')

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



def example_button_callback(widget, pos):
    """ Example callback for buttons """
    print(f"EXAMPLE BUTTON PRESSED: {widget}")


def main_loop(pyguime_screen, widgets):

    gui_surface = pygame.Surface((pyguime_screen.width, pyguime_screen.height)).convert()
    running = True

    while running:

        # Buttons that are clicked
        # is_down_widgets = pyguime.find_widgets_by_name(widgets, 'c1')
        # is_down_widgets = pyguime.find_widgets_by_filter(widgets, lambda x: hasattr(x, 'is_down') and x.is_down)
        is_down_widgets = pyguime.find_widgets_that_are_down(widgets)
#        print("####")
#        for w in is_down_widgets:
#            print(f"    is_down_widget: {w}")


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
                pyguime.handle_mouseclick_up(widgets, pygame.mouse.get_pos())
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pyguime.handle_mouseclick_down(widgets, pygame.mouse.get_pos())


        # scale and blit to screen
        pyguime_screen.screen.blit(gui_surface, (0, 0))
        pygame.display.flip()

 
# define a main function
def main():
     
    # create a screen to draw on
    pyguime_screen = pyguime.setup_screen(width=1024, height=600)

    # widgets - define

    keypad_widgets = [ ]
    key_size = (30, 30)
    key_space = (10, 5)

    # Set up a textbox and some small squares in a 3x4 pattern
    keypad_widgets.append(pyguime.PyguimeTextbox(text="Random little widget",
                                                 pos=(10, 10), size=(100, 50),
                                                 font_colour=(255,0,0),
                                                 transparent_background=True))
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

        keypad_offset = (10, 30)
        number = pyguime.PyguimeWidget(name=f'num_{n}',
                                       pos=(keypad_offset[0] +
                                            col * (key_size[0] +key_space[0]),
                                            keypad_offset[1] +
                                            row * (key_size[1] + key_space[1])),
                                       size=key_size,
                                       background=(0,20*n,0),
                                       handle_click_callback=logic.keypad_button_callback
                                            )
        keypad_widgets.append(number)


    container = pyguime.PyguimeContainer(name="container", pos=(100,300), size=(200,200))
    container.add(pyguime.PyguimeWidget(name="c1", pos=(10, 20), size=(30, 50), background=(255,0,0)))
    container.add(pyguime.PyguimeTextbox(name="t1", pos=(50, 0), size=(50, 20), font_size=10, font_colour=(0,255,0)))

    container2 = pyguime.PyguimeContainer(name="container2", pos=(400,300), size=(200,200))
    container2.add(pyguime.PyguimeWidget(name="c1", pos=(10, 20), size=(30, 50), background=(128,255,0)))
    container2.add(pyguime.PyguimeTextbox(name="t1", pos=(50, 0), size=(50, 20), font_size=10, font_colour=(0,0, 255), text="test"))

    keypad = pyguime.PyguimeKeypad(name="keypad1", pos=(300, 0), size=(110, 200), background=(50, 50, 50))
    keypad.add_textbox(initial_text="textbox", size=(keypad.size[0], 30),
                       font_size=30, font_colour=(255, 0, 128)).\
        generate(pos=(0, 50), font_colour=(255, 0, 255))

    keypad2 = pyguime.PyguimeKeypad(name="keypad1", pos=(500, 0), size=(110, 200), background=(50, 50, 50))
    keypad2.add_textbox(initial_text="mytext", size=(keypad2.size[0], 30),
                        font_size=30). \
        generate(pos=(0, 50))


    button1 = pyguime.PyguimeButton(name="button1", pos=(600,200), click_callback=example_button_callback).generate()
    sticky_button1 = pyguime.PyguimeButton(name="sticky_button1", pos=(600,280),
                                           text="sticky", sticky=True).generate()

    # multi checkbox container with a label
    cb_label = pyguime.PyguimeTextbox(name="mylabel", text="my checkboxes", transparent_background=True).generate()
    checkbox_1 = pyguime.PyguimeCheckbox(name="checkbox1", text="check me").generate()
    checkbox_2 = pyguime.PyguimeCheckbox(name="checkbox2", text="second").generate()

    checkboxes=pyguime.PyguimeContainer(name="checkboxes", pos=(100, 100), auto_size=True, background=(128, 128, 128)).\
        add_object_linear(cb_label, vertical=True).\
        add_object_linear(checkbox_1, vertical=True).\
        add_object_linear(checkbox_2, vertical=True).\
        generate()
    #text = "check me", sticky = True).generate()

    # radio button
    radio_1 = pyguime.PyguimeCheckbox(name="radio1", text="rad 1", exclusive_group_id="radio1").generate()
    radio_2 = pyguime.PyguimeCheckbox(name="radio1", text="rad 2", exclusive_group_id="radio1", is_down=True).generate()

    radio_label = pyguime.PyguimeTextbox(name="mylabelradio", text="my radiobuttons", transparent_background=True).generate()
    radio_buttons = pyguime.PyguimeContainer(name="radiobuttons", pos=(300, 100), auto_size=True,
                                             background=(128, 128, 128)). \
        add_object_linear(radio_label, vertical=True). \
        add_object_linear(radio_1, vertical=True). \
        add_object_linear(radio_2, vertical=True). \
        generate()

    widgets = [ pyguime.PyguimeWidget(background=(255,255,0),name="rect1", pos=(500,100), size=(50, 100), click_callback=logic.sample_button_callback),
                pyguime.PyguimeWidget(name="image", pos=(200, 200), size=(50, 50), image="images/ball.png"),
                pyguime.PyguimeTextbox(name="keypad_text", pos=(300, 230), size=(100, 100), text='test'),
                ] + keypad_widgets + [ container ] + [ keypad ] + [ container2] + \
              [keypad2, button1, sticky_button1, checkboxes, radio_buttons ]
    main_loop(pyguime_screen, widgets)
     
     
if __name__=="__main__":

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)

    main()
