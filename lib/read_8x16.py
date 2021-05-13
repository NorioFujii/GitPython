"""read from vga_8x16.bin """
WIDTH = 8
HEIGHT = 16
FIRST = 0x00
LAST = 0xff
_FONT = bytearray(4096)

with open("/fonts/vga_8x16.bin", "rb") as fbm:
    _FONT = fbm.read()

FONT = memoryview(_FONT)
