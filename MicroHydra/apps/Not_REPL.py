# Version 0.02 Added better input handling for multiline inputs to allow my functions to be entered.
# For MicroPython on the M5 Cardputer
# Based on and intended for use with MicroHydra by echo-lalia
# https://github.com/echo-lalia/Cardputer-MicroHydra/tree/main
# I used Bing AI to help develope and debug this code so beware ;)
# Warning: The explicit intent of this to attempt to run whatever is put into the command line so be cautious
# Input is not sanitized at all but my coding might break before anything too bad happens... I hope

# Import necessary libraries and modules
from machine import Pin, SPI
from lib import st7789py as st7789
from lib import keyboard
from font import vga1_8x16 as font
import utime
import os
import time
from machine import RTC
import sys

# Constants
CMD_PREFIX = "CMD: "
RES_PREFIX = "RES: "
ERR_PREFIX = "ERR: "
DELAY_TIME = 20
display_width = 240
display_height = 135
font_width = 8
font_height = 16
max_chars_per_line = display_width // font_width
black = const(0)
white = const(65535)
display_lines = 7  # Define the display_lines variable
command_history = []
history_index = 0
scroll_x = 0

# Initialize display
spi = SPI(1, baudrate=40000000, sck=Pin(36), mosi=Pin(35), miso=None)
tft = st7789.ST7789(
    spi,
    display_height,
    display_width,
    reset=Pin(33, Pin.OUT),
    cs=Pin(37, Pin.OUT),
    dc=Pin(34, Pin.OUT),
    backlight=Pin(38, Pin.OUT),
    rotation=1,
    color_order=st7789.BGR
)

# Initialize keyboard
kb = keyboard.KeyBoard()

# Initialize variables
buffer = ""
current_line = ""
lines = []
x_offset = 0
y_offset = 0
display_x = x_offset
display_y = display_height - font_height


# Function to display text on the screen
def d_print(text, prefix=""):
    global display_x, display_y
    if text is None:
        text = "None"
    text = str(text)
    lines.extend([prefix + line for line in text.split('\n')])  # Add prefix to each line
    while len(lines) > display_lines:
        lines.pop(0)
    display_y = display_height - font_height * 2
    for line in reversed(lines):
        tft.fill_rect(0, display_y, display_width, font_height, black)
        display_x = x_offset
        for char in line:
            tft.text(font, char, display_x, display_y, white, black)
            display_x += font_width
        display_y -= font_height

# Function to handle the addition of characters
def add_character(char, display_char=None):
    global buffer, current_line, display_x, display_y
    buffer += char
    current_line += display_char if display_char else char
    if len(current_line) > max_chars_per_line:
        current_line = current_line[-1]
        display_y += font_height
        if display_y + font_height > display_height:
            display_y = y_offset
            tft.fill_rect(0, 0, display_width, display_height - font_height, black)
    tft.text(font, current_line[-1], display_x, display_y, white, black)
    display_x += len(char) * font_width
    if display_x + font_width > display_width:
        display_x = x_offset
        display_y += font_height
        if display_y + font_height > display_height:
            display_y = y_offset
            tft.fill_rect(0, 0, display_width, display_height - font_height, black)
# Function to handle the remove of characters
def remove_character():
    global buffer, current_line, display_x, display_y
    buffer = buffer[:-1]
    current_line = current_line[:-1]
    display_x -= font_width
    if display_x < 0:
        display_x = (max_chars_per_line - 1) * font_width
        display_y -= font_height
        if display_y < 0:
            display_y = display_height - font_height
    tft.fill_rect(display_x, display_y, font_width, font_height, black)

def execute_command():
    global buffer
    buffer = buffer.strip()
    if buffer:
        try:
            exec(buffer)
            result = None
            d_print(buffer, CMD_PREFIX)
            buffer = ""
            if result is not None:
                print(result)
                d_print(str(result), RES_PREFIX)
                buffer = '\n'
        except Exception as eval_error:
            error_message = f"Error evaluating code: {eval_error}"
            print(error_message, file=sys.stderr)  # Print to stderr for immediate display
            d_print(error_message, ERR_PREFIX)
            buffer = ''

# Main loop
while True:
    prev_pressed_keys = []
    while True:
        current_pressed_keys = kb.get_pressed_keys()
        if current_pressed_keys != prev_pressed_keys:
            for key in current_pressed_keys:
                if key == "GO": #The GO button on top is used to enter commands to allow for enter to be used for multiline input.
                    tft.fill_rect(0, display_height - font_height, display_width, font_height, black)
                    display_y = display_height - 2 * font_height
                    execute_command()
                    current_line = ""
                    display_y = display_height - font_height
                    display_x = x_offset
                    tft.fill_rect(0, display_height - font_height, display_width, font_height, black)
                elif key == "ENT": #this does not currently add a new line to the display but will function as one in a command. I think...
                    add_character('\n')
                elif key == "BSPC":
                    remove_character()
                elif key == "TAB":
                    add_character('    ', '····')  # Four spaces, four middle dots
                elif key == "RIGHT": # Working on side scrolling since to view the text off of the screen. 
                    #scroll_x += font_width
                    #tft.text(font, current_line[-1], display_x - scroll_x, display_y, white, black)
                    pass
                elif key == "LEFT":
                    #scroll_x = max(0, scroll_x - font_width)
                    #tft.text(font, current_line[-1], display_x - scroll_x, display_y, white, black)
                    pass
                elif key == "UP": #Need to add command history logic
                    #scroll_history = ...
                    pass
                elif key == "Down": #Need to add command history logic
                    #scroll_history = ...
                    pass
                
                elif key in ["F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9", "F10", "CTL", "OPT", "ALT"]:
                    pass  # Placeholders otherwise these would end up in the input line
                else:
                    if key == "SPC":
                        add_character(" ")
                    else:
                        add_character(key)
                #if current_line: #Broken side scrolling code
                    #tft.text(font, current_line[-1], display_x - scroll_x, display_y, white, black)
        prev_pressed_keys = current_pressed_keys
        utime.sleep_ms(DELAY_TIME)
    Pin(38, Pin.OUT).value(1)
