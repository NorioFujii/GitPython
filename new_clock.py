import uos, time, math, machine, rp2
import random, ujson
import jpegdec
from machine import Pin, PWM, SPI
from micropython import const
from lib.font_read16 import writeTXT
osname = uos.uname()[4]
City = "Haneda"
SSID = ""
button_c = Pin(9, Pin.IN, Pin.PULL_DOWN)
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
CENTER_X = const(disp_width//2)
CENTER_Y = disp_height//2
dbl_pi = math.pi * 2

class passPicoG():
    def __init__(self, obj):
        self.dispClass = obj
        self.pico = osname.find('Pico')>0
    def set_font(self,font):
        self.font = font
        display.set_font(font)
    def clear(self,col):
        if self.pico:
            self.dispClass.fill(col)
        else:
            self.dispClass.set_pen(col)
            self.dispClass.clear()
    def create_pen(self, r, g, b):
        if self.pico:
            return st7789.color565((r,g,b))
        else:
            return self.dispClass.create_pen(r,g,b)
    def pixel(self, x, y, col):
        if self.pico:
            self.dispClass.pixel(x,y,col)
        else:
            self.dispClass.set_pen(col)
            self.dispClass.pixel(x,y)
    def rectangle(self, x0, y0, xl, yl, col):
        if self.pico:
            if col==BLACK:
                return
            self.dispClass.fill_rect(x0, y0, xl, yl, col)
        else:
            self.dispClass.set_pen(col)
            self.dispClass.rectangle(x0, y0, xl, yl)
    def text(self, strg, x, y, col):
        if self.pico:
            self.dispClass.text(font1, strg, x, y, col)
        elif self.font=="bitmap8":
            self._text8(font1, strg, x, y, col)
        else:
            self.dispClass.set_pen(col)
            self.dispClass.text(strg, x, y, scale=2,spacing=1 )
    def update(self):
        if self.pico:
            return
        else:
            self.dispClass.update()
    def _text8(self, font, text, x0, y0, color, background=0):
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
def writeText(text,x,y,color=None):
    color = color if color else WHITE
    writeTXT(text,x,y,color=color,disp=display)
    display.update()

wlan = False
if osname.find('Pi Pico')>0:
    if osname.find('Pico W')>0:
        import network, socket
        from lib.set_WiFi import setWiFi
        wlan,SSID,apid = setWiFi(City,1)
#SPI(1) default pins
    spi1_sck   = 10
    spi1_mosi  = 11
    spi1_miso  =  8     #not use
    st7789_cs  =  6 
    st7789_res = 12
    st7789_dc  = 13
    if button_c.value():
      from picographics import PicoGraphics,DISPLAY_LCD_240X240,PEN_RGB332
      from pimoroni import Button
      from pimoroni_bus import SPIBus
      spibus = SPIBus(cs=6, dc=13, sck=10, mosi=11) # 17,16,18,19
      display = PicoGraphics(display=DISPLAY_LCD_240X240, bus=spibus, pen_type=PEN_RGB332)
      osname = "Pi Tufty fake"
      disp = passPicoG(display)
elif osname.find('Tufty 2040')>0:
    from picographics import PicoGraphics,DISPLAY_TUFTY_2040,PEN_RGB332 
    from pimoroni import Button
    display = PicoGraphics(display=DISPLAY_TUFTY_2040)
    disp = passPicoG(display)
else:
    uos.exit()
Watch_face = "Screenshot_clock1.bmp"
Watch_faceJ = "Screenshot_clock1.jpg"
Watch_faceB = "clock1.332" if osname.find('Tufty')>0 \
         else "clock1.565"
wkpos = (158,111)  # clock3:(173,110)
            
if osname.find('Pico')>0:
    from lib import st7789py2 as st7789
    from lib import read_8x16 as font1
    WHITE  = st7789.color565((255,255,255))
    BLACK  = st7789.color565((0, 0, 0))
    ORANGE = st7789.color565((200, 138, 30))
    YELLOW = st7789.color565((255, 216, 0))
    LITEYL = st7789.color565((200,200, 0))
    BLUE  = st7789.color565((116, 215, 238))
    CYAN  = st7789.color565((33, 177, 255))
    RED   = st7789.color565((209, 34, 41))
    j = False
    print (osname)
    spi1 = SPI(1, baudrate=62500000, polarity=1, miso=None)
    print(spi1)
    dispST = st7789.ST7789(spi1, disp_width, disp_height,
             reset=Pin(st7789_res, Pin.OUT),
             dc=Pin(st7789_dc, Pin.OUT),
             cs=Pin(st7789_cs, Pin.OUT),
             xstart=0, ystart=0, rotation=0)
    disp = passPicoG(dispST)
else:
    WIDTH, HEIGHT = display.get_bounds()
    display.set_backlight(0.6)
    disp.set_font("bitmap8")
#    display.set_clip(0, 0, disp_width, disp_height)
    j = jpegdec.JPEG(display)
# List of available pen colours, add more if necessary
    WHITE = display.create_pen(255, 255, 255)
    BLACK = display.create_pen(0, 0, 0)
    RED = display.create_pen(209, 34, 41)
    ORANGE = display.create_pen(246, 138, 30)
    YELLOW = display.create_pen(255, 216, 0)
    GREEN = display.create_pen(0, 121, 64)
    INDIGO = display.create_pen(36, 64, 142)
    VIOLET = display.create_pen(115, 41, 130)
    PINK = display.create_pen(255, 175, 200)
    BLUE = display.create_pen(116, 215, 238)
    LITEYL = display.create_pen(200,200, 0)
    MAGENTA = display.create_pen(255, 33, 140)
    CYAN = display.create_pen(33, 177, 255)
    col_base = [display.create_pen(0, 0, 255)] * 10
# Buttons
    button_a = Pin(7, Pin.IN, Pin.PULL_DOWN)
    button_b = Pin(8, Pin.IN, Pin.PULL_DOWN)
    button_c = Pin(9, Pin.IN, Pin.PULL_DOWN)
    button_up = Button(22, invert=False)
    button_down = Button(6, invert=False)
if osname.find('Pico')>0 or osname.find('fake')>0:
    STblank  = PWM(Pin(8, Pin.OUT))  # re-define
    STblank.freq(500)
    STblank.duty_u16(20000)
    BACKL = 20000
    if osname.find('fake')>0:
        WHITE = display.create_pen(220, 220, 255)
else:
    from lib import read_8x16 as font1
    BACKL = 0.5
    display.set_backlight(BACKL) 

blankSW = 1
set_clock = False
Cur = 4  # minute
# Button handling function
def button(pin):
    global set_clock, year, month, day, hour, minute, second, wd
    global newd, sec, min, hor, BACKL, blankSW, Cur, j
    if set_clock:
        return
    set_clock = True
    time.sleep(0.1)
    if pin.value() and pin==button_c:
        adjust = 0
        if osname.find('Tufty 2040')>0:
            adjust = -1 if button_down.read() else 0
            adjust = +1 if button_up.read() else adjust
            if adjust!=0:
                yy_hh = [year,month,day,hour,minute,second,0]
                yy_hh[Cur] += adjust
                year,month,day,hour,minute,second,wd = carryover(yy_hh)
                rtc.datetime((year, month, day, 0, hour, minute, second, 0))
                print('RTC is set now!')
                draw_clock(second)
                time.sleep(0.8)
                display.set_pen(BLACK)
                display.pixel_span(54,dline+16,15*9)
                set_clock = False
                return
        if year==2021:
            with open("stocktime.txt","r", encoding="utf-8") as stamp:
                strdate = stamp.read().split(",")
            yy_hh = []
            for x in strdate:
                yy_hh.append(int(x)) 
            year,month,day,hour,minute,second = yy_hh
            rtc.datetime((year, month, day, 0, hour, minute, second, 0))
            min = hor = 75
            newd = True
            draw_clock(second)
        else:
            yy_hh = [year,month,day,hour,minute+1,second,0]
            year,month,day,hour,minute,second,wd = carryover(yy_hh)
            text1 = "{:04d},{:02d},{:02d},{:02d},{:02d},{:02d}"
            ptext = text1.format(year,month,day,hour,minute,second)
            with open("stocktime.txt","w", encoding="utf-8") as stamp:
                stamp.write(ptext)
            if osname.find('Pico')>0 or osname.find('fake')>0:
                blankSW ^= 1
                BACKL = 65535 if BACKL<2000 else BACKL-2000  # 
                intnit = int(math.sin((BACKL/65536)*3.14)*65535)
                STblank.duty_u16(intnit)
    if osname.find('Pico')>0 or osname.find('fake')>0:
        set_clock = False
        return
    if pin.value() and pin==button_b:
        adjust = 0
        if button_down.read():
            adjust = -2000
        elif button_up.read():
            adjust = +2000
        if adjust!=0:
            BACKL1 = BACKL + adjust/20000
            BACKL=BACKL1 if 0<=BACKL1<=1.0 else BACKL
        else:
            blankSW ^= 1
            BACKL = 0.5 - 0.5*blankSW #20000 - 20000*blankSW
        display.set_backlight(BACKL) 

    if pin.value() and pin==button_a:
        adjust = Cur
        if button_down.read():
            adjust = adjust+1 if Cur<4 else 4
        elif button_up.read():
            adjust = adjust-1 if Cur>0 else 0
        Cur = adjust
        display.set_pen(BLACK)
        display.pixel_span(54,dline+16,Cur*8*3)
        display.set_pen(RED)
        display.pixel_span(54+Cur*8*3,dline+16,18)        
        display.set_pen(BLACK)
        display.pixel_span(72+Cur*8*3,dline+16,14*8-Cur*8*3)
        display.update()
    set_clock = False

def line_ml(self, cos, sin, ddx, ddy, x1, y1, colors):
        """
        Draw a single pixel colors line starting at x0, y0 and ending at x1, y1.
        """
        steep1 = abs(sin+ddy) > abs(cos+ddx)
        steep2 = abs(sin-ddy) > abs(cos-ddx)
        x0, y0 = x1+cos+ddx, y1+sin+ddy
        line_sl(disp, x0, y0, x1, y1, colors, steep1)
        if ddx==ddy==0:
            return
        x0, y0 = x1+cos-ddx, y1+sin-ddy
        line_sl(disp, x0, y0, x1, y1, colors, steep2)

def line_sl(self, x0, y0, x1, y1, colors, steep):
        if steep:
            x2, y2 = y0, x0
            x3, y3 = y1, x1
        else:
            x2, y2 = x0, y0
            x3, y3 = x1, y1
        if x2 > x3:
            x2, x3 = x3, x2
            y2, y3 = y3, y2
        dx = x3 - x2
        dy = abs(y3 - y2)
        err = dx // 2
        ystep = 1 if y2 < y3 else -1
        for x4 in range(x2, x3+1):
          if type(colors) is int:
              color = colors
          elif type(colors) is list:
              color = colors[x4 - x2] 
          else:
              vw = 2 if osname.find('Pico')>0 else 1
              if steep:
                  colors.seek((x4*disp_width+y2)*vw)
              else:
                  colors.seek((y2*disp_width+x4)*vw)
              color =int.from_bytes(colors.read(vw),'big') 
          if steep:
              self.pixel(y2, x4, color)
          else:
              self.pixel(x4, y2, color)
          err -= dy
          if err < 0:
                y2 += ystep
                err += dx

# Helper function to draw a circle from a given position with a given radius
def draw_circle(x0, y0, radius, col=0):
    if osname.find('Pico')>0:
      for y in range(-radius, radius+1):
        for x in range(-radius, 1):
           if ((x * x) + (y * y) <= (radius * radius)):
               dispST.fill_rect(x0+x, y0+y, abs(x*2), 1, col)
               break
    else:
        display.set_pen(col)
        display.circle(x0,y0, radius)

def paint_fathand(cos, sin, color):
    dX = 2 if abs(cos) < abs(sin) else 0
    dY = 2 if abs(cos) > abs(sin) else 0
    if dX+dY==0:
        dX = dY = 2
    line_ml(disp, +cos, -sin, +dX, -dY, \
                 CENTER_X, CENTER_Y, color)

def draw_hands(old, new, hlen, col_new, col_old=None):
    cos_old = int(hlen*math.cos(dbl_pi*old/60)) if old else 0
    sin_old = int(hlen*math.sin(dbl_pi*old/60)) if old else 0
    cos_new = int(hlen*math.cos(dbl_pi*new/60))
    sin_new = int(hlen*math.sin(dbl_pi*new/60))
    col_old = open("/img/"+Watch_faceB,"rb") if Watch_faceB in uos.listdir("/img") else col_base
    line_ml(disp, + cos_old, - sin_old, 0, 0, \
              CENTER_X, CENTER_Y, col_old)
    if hlen<100:
        paint_fathand(cos_old, sin_old, col_old)
    if type(col_old) is not list:
        col_old.close()
    if hlen<100 or old is None:
        paint_fathand(cos_new, sin_new, col_new)
    line_ml(disp, + cos_new, - sin_new, 0, 0, \
              CENTER_X, CENTER_Y, col_new)

def covrpt(yh, ov, n):
    xx = yh[n] if yh[n]<=ov[n] else yh[n]-ov[n] if n<3 else yh[n]-ov[n]-1
    if xx<0:
        yh[n] = ov[n]+1-xx
        yh[n-1] -= 1
    elif xx!=yh[n]:
        yh[n] = xx
        yh[n-1] += 1
    if n>1:
        covrpt(yh ,ov, n-1)
    return yh
def carryover(yy_hh, ov=[99,12,31,23,59,59]):
    feb = 29 if yy_hh[0]%4==0 else 28
    ov[2] = 30 if yy_hh[1] in [4,6,9,11] else feb if yy_hh[1]==2 else 31
    covrpt(yy_hh, ov, 4) # Check the upper of minute at count-up
    yy_hh[6] = week(yy_hh, feb) if yy_hh[6]==0 else 0
    return yy_hh
def week(yy, feb): # 124:MON start in a week
    days = (-2495+yy[0]+yy[0]//4+int("*033614625035"[yy[1]])+yy[2])
    wday = (days-1)%7 if feb==29 and yy[1]<3 else days%7
    return wday

def bitmap_thread():
   vw = 2 if osname.find('Pico')>0 else 1
   if Watch_faceB not in uos.listdir("/img"): 
      with open("/img/"+Watch_faceB,"wb") as b16:
        with open("/img/"+Watch_face,"rb") as bm:
           for l in range(1, disp_height-1):
              col_base = bytes()
              for w in range(disp_width):
                  if w%disp_width==0:
                      bm.seek(54+(disp_height-l)*disp_width*3)
                  bgr = bm.read(3)
                  rgb = disp.create_pen(bgr[2],bgr[1],bgr[0])
                  color = rgb.to_bytes(vw, 'big')
                  b16.write(color)
                  col_base += color
              if vw==2:
                  dispST.set_window(0, l-1, disp_width-1, l-1)
                  dispST.write(None, col_base)
   elif vw==2:
       with open("/img/"+Watch_faceB,"rb") as b16:
            dispST.set_window(0, 0, disp_width-1, 79)
            dispST.write(None, b16.read(480*80))
            dispST.set_window(0, 80,disp_width-1,159)
            dispST.write(None, b16.read(480*80))
            dispST.set_window(0,160,disp_width-1,239)
            dispST.write(None, b16.read(480*80))
   else:        
       disp.clear(BLACK)
       j.open_file("/img/"+Watch_faceJ)
       j.decode(0, 0, jpegdec.JPEG_SCALE_FULL)
       display.partial_update(0,0,239,239)
       writeText("<RTCによる時計>", 240, 6)
       writeText("ボタンUP", 240, 24)
       writeText("　＋（ABCと同時）", 240, 38)
       writeText("ボタンDOWN", 240, 52)
       writeText("　ー（ABCと同時）", 240, 66)
       writeText("ボタンA", 240, 80)
       writeText(" 調整日時分指定", 240, 94)
       writeText("ボタンB", 240, 108)
       writeText(" バックライト明暗", 240, 122)
       writeText("ボタンC", 240, 136)
       writeText(" 時刻調整・2前後", 240, 150)
       writeText("ボタンC単独", 240, 166)
       writeText(" 時刻保存・復元", 240, 180)

dline = 208  # 日付時刻表示行の位置            
sec = min = hor = 75
omn = 0
newd = True
rtc = machine.RTC()

def draw_clock(second):
    global sec,min,hor,omn,newd,oldText,j, wlan,jdtP,s,path,host
    old = sec if sec>0 else 0
    wday = 0 if newd else 8
    newd = False
    text1 = "{:04d}-{:02d}-{:02d} {:02d}.{:02d}.{:02d} "
    text2 = " N:{}°{}’ E:{}°{}’"
    text3 = "  {}°C {}%"
    ptext = text1.format(year,month,day,hour,minute,second)
    print(ptext)
    sec = 75-second
    disp.rectangle(40, dline, 180, 16, BLACK) 
    disp.text(ptext[0:20], 40, dline, WHITE) # 124
    if 56<sec<64 and not 57<min<63 or wday==0 or oldText!=ptext[8:10]:
        disp.rectangle(wkpos[0],wkpos[1], 49, 16, BLACK) 
        disp.text("MONTUEWEDTHUFRISATSUN"[wd*3:wd*3+3],wkpos[0],wkpos[1],WHITE)
        disp.text(("  "+str(day))[-3:],wkpos[0]+26,wkpos[1],WHITE)
    omn = min if omn==0 else omn # not in a time 1S
    min = 75-minute
    draw_hands(old, sec, 100, disp.create_pen(255, 0, 0))
    if 71<old<73 or old==omn or wday==0 or (58<old<60 and 57<omn<62): 
        draw_hands(omn, min, 95, WHITE)
        omn = 0
        if dline==208 and (wday==0 or min%15==0 and old==72):
            if wlan:
              s = socket.socket()
              try:
                s.connect(addr)
                s.send(bytes('GET /%s HTTP/1.1\r\nHost: %s\r\n\r\n' % (path, host), 'utf8'))
                recv = s.recv(1024).decode()
                if len(recv)>10:
                    print (recv)
                    jdtP = ujson.loads(recv[recv.find("{"):recv.find("}")+1])
              except:
                if not excgWiFi(apid):
                    wlan = False
                    
              s.close()
            disp.rectangle(36,dline+16,180, 16, BLACK) 
            mainL = jdtP['weather'].lower()
            colorJson = {'clear':ORANGE,'clouds':LITEYL,'rain':BLUE,'snow':WHITE,'mist':CYAN,'thunderstorm':YELLOW}
            toColor = colorJson[mainL] 
            if j:
                j.open_file("/img/"+mainL+".jpg")
                j.decode(0, 208, jpegdec.JPEG_SCALE_FULL)
                display.partial_update(0,208,39,239)
            else:
                with open("/img/"+mainL+".565","rb") as b16:
                    dispST.set_window(0, 208, 39, 239)
                    dispST.write(None, b16.read(80*32))

            disp.text(str(jdtP['temp'])+chr(0xb0)+"C "+str(jdtP['humidity'])+"% in "+City+"      ",36,dline+16,toColor)
            writeText("気圧："+str(jdtP['pressure'])+"hp",240,dline+16,color=toColor)
    if 68<old<70 or old==hor or wday==0 or (58<old<60 and 57<hor<62):
        ohr = hor if hor>0 else 0
        hor = 75-(hour%12)*5 - minute//12
        draw_hands(ohr, hor, 75, disp.create_pen(255, 255, 0))
        if wday==0 or oldText!=ptext[8:10]:
            oldText = ptext[8:10]
        if hor==min==75:
            newd = True
    disp.update()

def excgWiFi(ap_id):
    global wlan
    if not wlan.isconnected():
        ap_id = 2 if ap_id==1 else 1
        wlan,SSID,apid = setWiFi(City,ap_id)
        disp.rectangle(104, dline, 160, 24,BLACK) 
        disp.text(SSID+"     ",104,dline,WHITE)
        disp.update()
        time.sleep(10)
    return wlan.isconnected()

if not wlan:
    dline = 212 if not button_c.value() else dline
elif not wlan.isconnected() and wlan.status() >= 0:
    print("Waiting to connect:")
    disp.text("Connect to "+SSID,20,dline,WHITE)
    disp.update()
    time.sleep(5)
    if not excgWiFi(apid):
        wlan = False
        dline = 212

if Watch_face in uos.listdir("/img"):
    bitmap_thread()
    disp.rectangle(20, dline, 200, 24, BLACK) 
else:    
    CENTER_Y -= 15
    draw_circle(CENTER_X, CENTER_Y, 104)
    draw_circle(CENTER_X, CENTER_Y, 102, disp.create_pen(255, 0, 0))
    draw_circle(CENTER_X, CENTER_Y, 100, disp.create_pen(0, 255, 0))
    draw_circle(CENTER_X, CENTER_Y, 98, disp.create_pen(0, 0, 255))
    for rd in range(0, 60, 5):
      draw_hands(None, rd, 104, disp.create_pen(0, 0, 255))
      if rd==15:
        draw_hands(None, 75, 104, disp.create_pen(255, 255, 255))
s = 0
if wlan:
    print(SSID,end=" ")
    print(wlan.ifconfig())
    _, _, host, path = ("https://mori1-hakua.tokyo/cgi-bin/test/getTenki.cgi?"+City).split('/', 3)
    addr = socket.getaddrinfo(host, 80)[0][-1]
    _, _, host2 = ("http://date.jsontest.com").split('/', 3)
    addr2 = socket.getaddrinfo(host2, 80)[0][-1]
    disp.text("                          ",20,dline,WHITE)
    
year, month, day, wd, hour, minute, second, _ = rtc.datetime()
last_second = second
oldText = " s"
jdtP = {"city":"Haneda","weather":"Clouds","humidity":83,"temp":28.24,"pressure":1006}
jtmP = {}
# Register the button handling function with the buttons
if osname.find('Tufty 2040')>0:
    button_a.irq(trigger=Pin.IRQ_RISING, handler=button)
    button_b.irq(trigger=Pin.IRQ_RISING, handler=button)
button_c.irq(trigger=Pin.IRQ_RISING, handler=button)
while True:
   if wlan and (year==2021 or sec==min==45):
      s = socket.socket()
      try:
          s.connect(addr2)
          s.send(bytes('GET / HTTP/1.0\r\nHost: %s\r\n\r\n' % (host2), 'utf8'))
          recv = s.recv(1024).decode()
          print (recv)
          jtmP = ujson.loads(recv[recv.find("{"):recv.find("}")+1])
      except:
          if not excgWiFi(apid):
              wlan = False
              continue
      s.close()
      ddmmyy = jtmP['date']
      UTC = jtmP['time']
      bias = 9
      if UTC[0:2]=="12":
          if UTC[9:11]=="AM":
              UTC = "00"+UTC[2:]
      else:
          if UTC[9:11]=="PM":
              bias = 21
      year, month, day, hour, minute, second, wd = \
              carryover([int(ddmmyy[6:10]),int(ddmmyy[0:2]),int(ddmmyy[3:5]), \
                         int(UTC[0:2]) + bias,int(UTC[3:5]),int(UTC[6:8]),0])
      if not set_clock:
              set_clock = True
              rtc.datetime((year, month, day, 0, hour, minute, second, 0))
              print('RTC is set now!')
              set_clock = False
   else:
        year, month, day, wd, hour, minute, second, _ = rtc.datetime()
        if second == last_second:
            time.sleep(0.2)
            continue
   last_second = second
   draw_clock(second)
   time.sleep(0.1)