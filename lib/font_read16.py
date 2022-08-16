import uos, sys, binascii
from micropython import const
TEXT_NORMAL = const(1)
_BIT7 = const(0x80)
_BIT6 = const(0x40)
_BIT5 = const(0x20)
_BIT4 = const(0x10)
_BIT3 = const(0x08)
_BIT2 = const(0x04)
_BIT1 = const(0x02)
_BIT0 = const(0x01)
disp_width = const(240)
disp_height = const(240)
yoko = 94
tate = 12
fontL = 84
img = [[0 for x in range(yoko)] for y in range(tate)]
# kanjiL = [[0 for x in range(yoko*2)] for y in range(2)]
kanjiL = ""
last_seek = -1
last_eye = 0
# BMPデータを取り込む
if uos.uname()[4].find('Tufty 2040')>0:
    fbm = open("/fonts/k8x12L_jisx0208_r.bmp", "rb")
# headerとpadding zero を取り除いたBitmapファイル

# 文字列の入力と変換
def dispUTF(strg, x, y, color, disp=None, rot=None):
    global img, kanjiL, last_seek, last_eye
    strg1 = bytes(strg,'utf-8') if type(strg) is str else strg
    strg2 = ""
    if strg1[0]==0:  # 半角の時、全角に
        i = strg1[1]+0x20
        strg1 = chr(strg1[1]).encode()
        strg2 = "ff" + ('%02x' % (i^0xC0 if i&0x80 else i^0x40)) 
    elif 0xc2<=strg1[0]<=0xdf:
        strg2 = ('%02x' % (strg1[0]&0x1f)>>2) \
              + ('%02x' % (((strg1[0]&0x1f)<<6)|(strg1[1]&0x3f))%256)
    elif 0xe0<=strg1[0]<=0xef:
        strg2 = ('%02x' % ((strg1[0]&0x0f)<<4 | (strg1[1]&0x3f)>>2)) \
              + ('%02x' % ((strg1[1]<<6)&0xff | strg1[2]&0x3f))
    with open("/fonts/JIS16_tbl.txt", "rb") as ftx:
        # UTF-16(BE) BOM付きで９４字／行にcr改行されたFontファイル
        dmy = ftx.read(2)
        i = last_eye
        j = -1
        k = 0
        key = strg2  # '%02x%02x' % (strg1[0],strg1[1])
        z = kanjiL.find(key)
        if z >= 0 and z % 4 == 0:
            j = z // 4
        else:
            for i in range(fontL): # 一定長の読み込みを続ける
                kanjiL = str(binascii.hexlify(ftx.read(yoko*2+2)),'utf-8')
                z = kanjiL.find(key)
                if z < 0 or z & 1 > 0:
                    n = kanjiL[0:yoko*4].find("000d")
                    if n != -1:
                        k += 1
                        dmy = ftx.read(n//2 + 2) # 4バイト文字以降は捨てる
                    continue
                j = z // 4
                break
            if j==-1:
                print('Kanji Not found',key,'from',strg)
                return
            last_eye = i + k
    print(strg1.decode(), last_eye, j, k, key)
    new_seek = tate*(fontL-last_eye-1)*yoko
    if last_seek != new_seek:
        last_seek = new_seek
        fbm.seek(new_seek)
        for zz in range(tate):
            img[11-zz] = fbm.read(yoko)
    dots = ""
    fontw = 8
#    tate  = 12
    for q in range(tate) :
        c = img[q][j]
        for r in range(0, fontw) :
            dots += ("●●" if (c & (0x80 >> r))==0 else "　")
            if disp:
                pos = r * TEXT_NORMAL
                disp.set_pen(color if (c & (0x80 >> r))==0 else 0)
                disp.pixel_span(x+pos,y+q,TEXT_NORMAL)
        dots += "\n"
    if not disp:
        print(dots)

def writeTXT(strg, x, y, color=None, disp=None, rot=None):
    strg1 = strg.encode() if len("日本語")==3 else bytes(strg, 'utf-8')
    skip=0
    for i in range(len(strg1)):
        if (skip>0):
            skip -= 1
            continue
        code=ord(strg1[i:i+1]) & 0xFF
        if (code<=0x1F):
            if (code==0) :
                break
        elif (code<=0x7F):
            dispUTF(chr(0x00)+chr(code), x,y,color , disp=disp, rot=rot)
        elif (code & 0xe0)==0xe0:
            dispUTF(strg1[i:i+3], x,y,color , disp=disp, rot=rot)
            skip = 2
        elif (code & 0xc0)==0xc0:
            dispUTF(strg1[i:i+2], x,y,color , disp=disp, rot=rot)
            skip = 1
        x += TEXT_NORMAL*8

def text8(display, font, text, x0, y0, color, background=0):
        """
        Internal method to write characters with width of 8 and
        heights of 16.

        Args:
            font (module): font module to use
            text (str): text to write
            x0 (int): column to start drawing at
            y0 (int): row to start drawing at
            color (int): 332 encoded color to use for characters
            background (int): 332 encoded color to use for background
        """
        for char in text:
            ch = ord(char)
            if not (font.FIRST <= ch < font.LAST
                    and x0+font.WIDTH <= disp_width
                    and y0+font.HEIGHT <= disp_height):
                continue
            idx = (ch-font.FIRST)*font.HEIGHT
            for y in range(font.HEIGHT):
                    display.set_pen(color if font.FONT[idx] & _BIT7 else background)
                    display.pixel(x0+0,y0+y)
                    display.set_pen(color if font.FONT[idx] & _BIT6 else background)
                    display.pixel(x0+1,y0+y)
                    display.set_pen(color if font.FONT[idx] & _BIT5 else background)
                    display.pixel(x0+2,y0+y)
                    display.set_pen(color if font.FONT[idx] & _BIT4 else background)
                    display.pixel(x0+3,y0+y)
                    display.set_pen(color if font.FONT[idx] & _BIT3 else background)
                    display.pixel(x0+4,y0+y)
                    display.set_pen(color if font.FONT[idx] & _BIT2 else background)
                    display.pixel(x0+5,y0+y)
                    display.set_pen(color if font.FONT[idx] & _BIT1 else background)
                    display.pixel(x0+6,y0+y)
                    display.set_pen(color if font.FONT[idx] & _BIT0 else background)
                    display.pixel(x0+7,y0+y)
                    idx += 1
            x0 += font.WIDTH
