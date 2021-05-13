"""read from vga_16x32.bin """
WIDTH = 16
HEIGHT = 32
FIRST = 0
LAST = 255
_FONT = bytearray()

with open("/fonts/vga_16x32.bin", "rb") as fbm:
    _FONT = fbm.read()

FONT = memoryview(_FONT)
