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



def main_loop(screen, widgets):

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
        screen.blit(gui_surface, (0, 0))
        pygame.display.flip()



 
# define a main function
def main():
     
    # create a screen to draw on
    screen = pyguime.setup_screen()


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
                                       data={'number': n},
                                       click_callback=logic.sample_button_callback
                                            )
        keypad_widgets.append(number)

    widgets = [ pyguime.PyguimeWidget(name="rect1", pos=(100,100), size=(50, 100), click_callback=logic.sample_button_callback),
                pyguime.PyguimeWidget(name="rect2", pos=(10,10), size=(10, 10), background=(128, 0, 0)),
                pyguime.PyguimeWidget(name="image", pos=(200, 200), size=(50, 50), image="images/ball.png")] + keypad_widgets



    main_loop(screen, widgets)
     
     
if __name__=="__main__":
    main()
