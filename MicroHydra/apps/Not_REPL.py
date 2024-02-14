# Version 0.03 
# Now with multiline input, text input scroll, and colors.
# For MicroPython on the M5 Cardputer
# Based on and intended for use with MicroHydra by echo-lalia
# https://github.com/echo-lalia/Cardputer-MicroHydra/tree/main
# I used Bing AI to help develope and debug this code so beware ;)
# Warning: The explicit intent of this to attempt to run whatever is put into the command line so be cautious
# Input is not sanitized at all but my coding might break before anything too bad happens... I hope

# Use GO button to run commands no
# Enter key inserts a newline in the input
# F1 and F2 have predefined color themes but there is an issue where they don't work full with the panels that are new to V 0.03
# I am working to make they interface more dynamic for multiline or future imporvements
#		This may not be fully working yet, Sorry!
# To use command history hold fn and press up or down to scroll through.
# Now instead of wrapping the text at the end of the screen he text shifts to the left. Note, the left and right arrow do not scoll yet.
#    There is currently an issue with how the code redraws that prevents the new text from being displayed unless you press backspace. Sorry again!

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
display_lines = 7  # Define the display_lines variable
command_history = []
command_position = 0
error_message = None

# Initialize variables
buffer = ""
input_line = ""
current_line = ""
lines = []
x_offset = 0
y_offset = 0
display_x = x_offset
display_y = display_height - font_height


# Commodore64 Colors
black = const(0)
white = const(65535)
red = const(63488)
cyan = const(2047)
purple = const(63519)
green = const(2016)
blue = const(31)
yellow = const(65504)
orange = const(64512)
brown = const(48192)
light_red = const(63495)
dark_grey = const(31727)
grey = const(52735)
light_green = const(2111)
light_blue = const(2047)
light_grey = const(54245)

current_color = black # Add a global variable for the current color
font_color = white

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

class Panel:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.lines = []
        self.display_x = x
        self.display_y = y + height - font_height

    def add_line(self, line):
        self.lines.append(line)
        while len(self.lines) * font_height > self.height:
            if self.lines:  # Check if self.lines is not empty
                self.lines.pop(0)  # Remove the oldest line if there are too many

    def redraw(self):
        # Clear the panel
        tft.fill_rect(self.x, self.y, self.width, self.height, current_color)
        # Redraw the lines
        self.display_y = self.y + self.height - font_height
        for line in reversed(self.lines):
            draw_text(line, self.display_y, x_offset)
            self.display_y -= font_height

    def set_height(self, height):
        self.height = height
        self.display_y = self.y + height - font_height

    def set_y(self, y):
        self.y = y
        self.display_y = self.y + self.height - font_height

# Create two panels
history_panel = Panel(0, 0, display_width, display_height - font_height)
input_panel = Panel(0, display_height - font_height, display_width, font_height)

# Initialize keyboard
kb = keyboard.KeyBoard()

# Function to change the background color
def fill_cl(color):
    global current_color, display_y
    current_color = color
    tft.fill(color)
    old_display_y = display_y  # Save the current display_y
    redraw_text()  # Redraw the previous lines
    display_y = old_display_y  # Restore the saved display_y
    draw_text(current_line, display_y)  # Redraw the input line

# Function to change the font color
def font_cl(color):
    global font_color
    font_color = color
    
def draw_text(line, y, start_pos=0):
    global display_x
    tft.fill_rect(0, y, display_width, font_height, current_color)
    display_x = x_offset
    for char in line[start_pos:]:
        tft.text(font, char, display_x, y, font_color, current_color)
        display_x += font_width

def d_print(text, prefix=""):
    global display_y
    if text is None:
        text = "None"
    text = str(text)
    lines.extend([prefix + line for line in text.split('\n')])  # Add prefix to each line
    while len(lines) > display_lines:
        lines.pop(0)  # Remove the oldest line if there are too many
    display_y = display_height - font_height * 2
    for line in reversed(lines):
        draw_text(line, display_y)
        display_y -= font_height

def redraw_text():
    global lines, display_y
    display_y = display_height - font_height * 2
    for line in reversed(lines):
        draw_text(line, display_y)
        display_y -= font_height

def redraw_input_line():
    global display_x, display_y, input_line
    # Clear the input line
    tft.fill_rect(0, display_height - font_height, display_width, font_height, current_color)
    # Reset the display coordinates
    display_x = x_offset
    display_y = display_height - font_height
    # Redraw the input line
    for char in input_line:
        tft.text(font, char, display_x, display_y, font_color, current_color)
        display_x += font_width

def add_character(char, display_char=None):
    global buffer, input_line, display_x, display_y, x_offset
    if char == '\n':
        # If the key is 'ENT', add the current input line to the panel's lines and create a new input line
        buffer += char
        # Increase the height of the input panel and decrease the height of the history panel
        input_panel.set_height(input_panel.height + font_height)
        history_panel.set_height(history_panel.height - font_height)
        # Adjust the y starting points of the panels
        history_panel.set_y(display_height - input_panel.height - history_panel.height)  # Set the y starting point of the history panel to the top of the input panel
        input_panel.set_y(display_height - input_panel.height)  # Keep the y starting point of the input panel at the bottom of the display
        # Add the current input line to the panel's lines
        input_panel.add_line(input_line)
        input_line = ""
        # Reset the horizontal offset
        x_offset = 0
        
    else:
        buffer += char
        input_line += display_char if display_char else char
        if len(input_line) * font_width > display_width:
            # If the text goes off the right edge of the screen, decrease the horizontal offset and redraw the line
            x_offset = int(len(input_line) - display_width/font_width)+8
        else:
            if input_panel.lines:  # Check if input_panel.lines is not empty
                input_panel.lines[-1] = input_line  # Update the last line of the input panel
            else:
                input_panel.lines.append(input_line)  # Add the line to the input panel
    input_panel.redraw()  # Redraw the input panel
    
# Update the remove_character function to remove characters from the input panel
def remove_character():
    global buffer, input_line, display_x, display_y
    if buffer:
        buffer = buffer[:-1]
    if input_line:
        input_line = input_line[:-1]
    if input_panel.lines:
        input_panel.lines[-1] = input_line  # Update the last line of the input panel
    input_panel.redraw()  # Redraw the input panel

def execute_command():
    global buffer, error_message, x_offset
    error_message = None  # Reset the error message at the start of each command execution
    buffer = buffer.strip() # Also stips newlines so executing enter does not add a new line.Still in work
    if buffer:
        command_history.append(buffer)
        command_position = len(command_history)  # Set the position to the end of the history
        # Add the command to the history panel and decrease its height
        #history_panel.add_line(buffer)
        history_panel.set_height(history_panel.height - input_panel.height + font_height)
        input_line = ""
        input_panel.lines = []
        input_panel.set_height(font_height)
        input_panel.y = display_height - input_panel.height  # Reset the y starting point of the input panel
        # Reset the horizontal offset
        x_offset = 0
        history_panel.redraw()  # Redraw the history panel
        input_panel.redraw()  # Redraw the input panel    
        d_print(buffer, CMD_PREFIX)
        try:           
            # Check if buffer is a valid Python command
            # Add the command to the history when it's executed
            compiled = compile(buffer, '<string>', 'exec')
            result = exec(compiled)
            # If the command returns a result, display it
            if result is not None:
                lines.append(buffer)
                d_print(str(result), RES_PREFIX)
            while len(lines) > display_lines:
                lines.pop(0)  # Remove the oldest line if there are too many
        except Exception as eval_error:
            # If an error occurs, store the error message and display it
            error_message = f"Error evaluating code: {eval_error}"
            #d_print("Code Error")
            d_print(error_message, ERR_PREFIX)
            # Add the command to the history and display it
            while len(lines) > display_lines:
                lines.pop(0)  # Remove the oldest line if there are too many
        finally:
            buffer = ''  # Always clear the buffer, even if an error occurred
        
# Main loop
while True:
    prev_pressed_keys = []
    current_line = ""
    while True:      
        current_pressed_keys = kb.get_pressed_keys()
        if current_pressed_keys != prev_pressed_keys:
            for key in current_pressed_keys:
                if key == "GO":
                    # When the GO key is pressed, execute the command in the buffer
                    execute_command()
                    # Clear the input line and reset the display coordinates
                    
                    input_line = ""
                    redraw_input_line()
                    input_panel.lines = []  # Clear the input panel
                    input_panel.redraw()  # Redraw the input panel 
                elif key == "ENT": #this does not currently add a new line to the display but will function as one in a command. I think...
                    add_character('\n')
                    redraw_input_line()
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
                elif key == "DOWN": #Need to add command history logic
                    if command_position > 0:
                        command_position -= 1
                        buffer = command_history[command_position]
                        input_line = buffer  # Update input_line
                        input_panel.lines = [buffer]  # Update the input panel
                        input_panel.redraw()  # Redraw the input panel
                elif key == "UP": #Need to add command history logic
                    if command_position < len(command_history) - 1:
                        command_position += 1
                        buffer = command_history[command_position]
                        input_line = buffer  # Update input_line
                        input_panel.lines = [buffer]  # Update the input panel
                        input_panel.redraw()  # Redraw the input panel
                elif key == "F1": #Need to add command history logic
                    fill_cl(blue)
                    font_cl(white)               
                elif key == "F2": #Need to add command history logic
                    fill_cl(black)
                    font_cl(green) 
                elif key in ["F3", "F4", "F5", "F6", "F7", "F8", "F9", "F10", "CTL", "OPT", "ALT"]:
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
