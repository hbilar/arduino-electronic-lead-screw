""" File to handle the logic side of the user interface, e.g. button
    callbacks """

import pyguime

textbox_values = {}


def keypad_button_callback(widget, pos):
    """ Callback for a specific number in a keypad """

    print(f"** Keypad callback: position = {pos}, widget = {widget}")

    if not (widget.data and widget.data.get('textbox_id', None)):
        print(f"*** ERROR: No 'textbox_id' in data dict for {widget}")
        return

    textbox_id = widget.data['textbox_id']
    cur_val = textbox_values.get(textbox_id, '')

    cur_val = cur_val + widget.data.get('character', '')

    print(f"Updating textbox {textbox_id} to {cur_val}")

    textbox_values[textbox_id] = cur_val


def sample_button_callback(widget, pos):
    """ Sample button callback that just prints stuff to stdout """

    print(f"** Button callback: position = {pos}, widget = {widget}")

    if isinstance(widget, pyguime.PyguimeTextbox):
        n = 0
        try:
            if widget.text:
                n = int(widget.text)
        except ValueError:
            pass

        widget.text = str(n + 1)