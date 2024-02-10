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
lines = []
display_lines = 7
x_offset = 0
y_offset = 0
x = x_offset
y = display_height - font_height

# Function to display text on the screen
def d_print(text):
    global x, y
    if text is None:
        text = "None"
    text = str(text)
    lines.append(text)
    while len(lines) > display_lines:
        lines.pop(0)
    y = display_height - font_height*2
    for line in reversed(lines):
        tft.fill_rect(0, y, display_width, font_height, black)
        x = x_offset
        for char in line:
            tft.text(font, char, x, y, white, black)
            x += font_width
        y -= font_height

# Main loop
while True:
    prev_keys = []
    current_line = ""
    while True:
        pressed_keys = kb.get_pressed_keys()
        if pressed_keys != prev_keys:
            for key in pressed_keys:
                if key == "ENT":
                    tft.fill_rect(0, display_height - font_height, display_width, font_height, black)
                    y = display_height - 2 * font_height
                    x = x_offset
                    buffer = buffer.strip()
                    if buffer:
                        d_print(CMD_PREFIX + buffer)
                        try:
                            if "=" in buffer:
                                exec(buffer)
                                result = None
                            else:
                                result = eval(buffer)
                            buffer = ""
                            if result is not None:
                                print(result)
                                y = display_height - font_height
                                x = x_offset
                                d_print(RES_PREFIX + str(result))
                                buffer = '\n'
                        except Exception as e:
                            print(f"Error evaluating code: {e}")
                            d_print(ERR_PREFIX + f"Error evaluating code: {e}")
                            buffer = ''
                            print("here")
                    current_line = ""
                    y = display_height - font_height
                    x = x_offset
                    tft.fill_rect(0, display_height - font_height, display_width, font_height, black)
                elif key == "BSPC":
                    buffer = buffer[:-1]
                    current_line = current_line[:-1]
                    x -= font_width
                    if x < 0:
                        x = (max_chars_per_line - 1) * font_width
                        y -= font_height
                        if y < 0:
                            y = display_height - font_height
                    tft.fill_rect(x, y, font_width, font_height, black)
                else:
                    if key == "SPC":
                        buffer += " "
                        current_line += " "
                    else:
                        buffer += key
                        current_line += key
                    if len(current_line) > max_chars_per_line:
                        current_line = key
                        y += font_height
                        if y + font_height > display_height:
                            y = y_offset
                            tft.fill_rect(0, 0, display_width, display_height - font_height, black)
                    tft.text(font, current_line[-1], x, y, white, black)
                    x += font_width
                    if x + font_width > display_width:
                        x = x_offset
                        buffer += '\n'
                        y += font_height
                        if y + font_height > display_height:
                            y = y_offset
                            tft.fill_rect(0, 0, display_width, display_height - font_height, black)
        prev_keys = pressed_keys
        utime.sleep_ms(DELAY_TIME)
    Pin(38, Pin.OUT).value(1)
