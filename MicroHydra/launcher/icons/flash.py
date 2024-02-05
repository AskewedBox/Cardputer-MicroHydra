HEIGHT = 32
WIDTH = 32
COLORS = 2
BITS = 2048
BPP = 2
from esp32 import NVS
nvs = NVS("settings")
PALETTE = [nvs.get_i32("bg_color"),nvs.get_i32("ui_color")]
_bitmap =\
b'\x00\x55\x55\x55\x55\x55\x54\x00\x05\x55\x55\x55\x55\x55\x55\x50'\
b'\x15\x50\x00\x00\x00\x00\x05\x54\x15\x00\x00\x00\x00\x00\x00\x54'\
b'\x54\x00\x00\x00\x00\x00\x00\x15\x54\x00\x00\x00\x00\x00\x00\x15'\
b'\x50\x00\x00\x00\x00\x00\x00\x05\x50\x00\x00\x00\x00\x00\x00\x05'\
b'\x50\x00\x55\x55\x55\x55\x00\x05\x50\x00\x40\x00\x00\x01\x00\x05'\
b'\x50\x00\x45\x55\x55\x51\x00\x05\x50\x00\x45\x55\x55\x51\x00\x05'\
b'\x50\x00\x45\x55\x55\x51\x00\x05\x50\x00\x45\x55\x55\x51\x00\x05'\
b'\x50\x00\x45\x55\x55\x51\x00\x05\x50\x00\x45\x55\x55\x51\x00\x05'\
b'\x50\x00\x45\x55\x55\x51\x00\x05\x50\x00\x45\x55\x55\x51\x00\x05'\
b'\x50\x00\x45\x55\x55\x51\x00\x05\x50\x00\x45\x55\x55\x51\x00\x05'\
b'\x50\x00\x45\x55\x55\x51\x00\x05\x50\x00\x45\x55\x55\x51\x00\x05'\
b'\x50\x00\x40\x00\x00\x01\x00\x05\x50\x00\x55\x55\x55\x55\x00\x05'\
b'\x50\x00\x00\x00\x00\x00\x00\x05\x50\x00\x00\x00\x00\x00\x00\x05'\
b'\x54\x00\x00\x00\x00\x00\x00\x15\x54\x00\x00\x00\x00\x00\x00\x15'\
b'\x15\x00\x00\x00\x00\x00\x00\x54\x15\x50\x00\x00\x00\x00\x05\x54'\
b'\x05\x55\x55\x55\x55\x55\x55\x50\x00\x15\x55\x55\x55\x55\x55\x00'
BITMAP = memoryview(_bitmap)