import logging
import sys


import attr
import pygame


sys.path.insert(0, '../libraries/')
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
    logging.info(f"EXAMPLE BUTTON PRESSED: {widget}")


def main_loop(pyguime_screen, widgets):

    gui_surface = pygame.Surface((pyguime_screen.width, pyguime_screen.height)).convert()
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
                logging.debug(f"event.key:  {event.key}")

                if event.key == pygame.K_ESCAPE:
                    logging.info("Quitting...")
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

    # Draw a simple textbox on the screen (not inside a container)
    textbox = pyguime.PyguimeTextbox(text="Random little textbox",
                                     pos=(10, 200), size=(130, 50),
                                     font_colour=(255,0,0),
                                     transparent_background=True)

    container2 = pyguime.PyguimeContainer(name="container2", pos=(300,250), size=(200,200))
    container2.add(pyguime.PyguimeWidget(name="c1", pos=(10, 20), size=(30, 50), background=(128,255,0)))
    container2.add(pyguime.PyguimeTextbox(name="t1", pos=(50, 0), size=(150, 20), font_size=18, font_colour=(0,0, 255), text="my container"))

    # Keypad for entering decimal numbers
    keypad = pyguime.PyguimeKeypad(name="keypad1", pos=(300, 0), size=(110, 200), background=(50, 50, 50))
    keypad.add_textbox(initial_text="textbox", size=(keypad.size[0], 30),
                       font_size=30, font_colour=(255, 0, 128)).\
        generate(pos=(0, 50), font_colour=(255, 0, 255))

    # A normal button
    button1 = pyguime.PyguimeButton(name="button1", pos=(450,10), click_callback=example_button_callback,
                                    text="normal button").generate()

    # A sticky button that stays pressed when released
    sticky_button1 = pyguime.PyguimeButton(name="sticky_button1", pos=(450,100),
                                           text="sticky", sticky=True).generate()

    # Container with checkboxes with a label
    cb_label = pyguime.PyguimeTextbox(name="mylabel", text="my checkboxes", transparent_background=True).generate()
    checkbox_1 = pyguime.PyguimeCheckbox(name="checkbox1", text="check me").generate()
    checkbox_2 = pyguime.PyguimeCheckbox(name="checkbox2", text="second").generate()
    checkboxes=pyguime.PyguimeContainer(name="checkboxes", pos=(10, 10), auto_size=True, background=(128, 128, 128)).\
        add_object_linear(cb_label).\
        add_object_linear(checkbox_1).\
        add_object_linear(checkbox_2).\
        generate()

    # radio buttons
    radio_1 = pyguime.PyguimeCheckbox(name="radio1", text="rad 1", exclusive_group_id="radio1").generate()
    radio_2 = pyguime.PyguimeCheckbox(name="radio1", text="rad 2", exclusive_group_id="radio1", is_down=True).generate()
    radio_label = pyguime.PyguimeTextbox(name="mylabelradio", text="my radiobuttons", transparent_background=True).generate()
    radio_buttons = pyguime.PyguimeContainer(name="radiobuttons", pos=(150, 10), auto_size=True,
                                             background=(128, 128, 128)). \
        add_object_linear(radio_label). \
        add_object_linear(radio_1). \
        add_object_linear(radio_2). \
        generate()


    # yellow rectangle
    rect1 = pyguime.PyguimeWidget(background=(255,255,0), name="rect1", pos=(10,270), size=(50, 100), click_callback=logic.sample_button_callback)

    # the pygame ball as an image
    ball = pyguime.PyguimeWidget(name="image", pos=(200, 200), size=(50, 50), image="images/ball.png")

    # make a list of widgets (and define some new widgets...)
    widgets = [ rect1, ball, textbox , keypad , container2 ,
               button1, sticky_button1, checkboxes, radio_buttons ]

    # call main loop
    main_loop(pyguime_screen, widgets)


if __name__=="__main__":

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)

    main()
