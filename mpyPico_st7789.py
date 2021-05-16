"""
MicroPython exercise
240x240 ST7789 SPI LCD
using MicroPython library:
https://github.com/russhughes/st7789py_mpy
"""
import uos, time, math, machine
from machine import Pin, SPI, UART
from lib import st7789py2 as st7789
from lib import read_8x16 as font1
from lib import read_16x32 as font2
import random
from micropython import const

#SPI(1) default pins
spi1_sck   = 10
spi1_mosi  = 11
spi1_miso  =  8     #not use
st7789_res = 12
st7789_dc  = 13
dump = Pin(15, Pin.IN, Pin.PULL_UP)
disp_width = const(240)
disp_height = const(240)
CENTER_X = const(disp_width//2)
CENTER_Y = disp_height//2
dbl_pi = math.pi * 2
doller = b'$'
col_base = [st7789.color565(0,0,255)] * 101
Watch_face = "Screenshot_clock4.bmp"

print(uos.uname())
spi1 = SPI(1, baudrate=62500000, polarity=1)
print(spi1)
disp = st7789.ST7789(spi1, disp_width, disp_width,
             reset=Pin(st7789_res, Pin.OUT),
             dc=Pin(st7789_dc, Pin.OUT),
             xstart=0, ystart=0, rotation=0)

disp.fill(st7789.BLACK)
disp.text(font2, "Hello!", 10, 10)
disp.text(font2, "RPi Pico", 10, 40)  #  or Micro:bit
disp.text(font2, "MicroPython", 10, 70)
disp.text(font1, "ST7789 SPI 240*240 IPS", 10, 110)
disp.text(font1, "https://github.com/", 10, 130)
disp.text(font1, "russhughes/st7789py_mpy", 10, 150)

for _ in range(2000):
    disp.pixel(random.randint(0, disp_width),
          random.randint(0, disp_height),
          st7789.color565(random.getrandbits(8),random.getrandbits(8),random.getrandbits(8)))

# Helper function to draw a circle from a given position with a given radius
def paint_circle (x0, y0, radius, col=st7789.color565(255, 255, 255)):
    for y in range(-radius, radius+1):
        for x in range(-radius, 1):
           if ((x * x) + (y * y) <= (radius * radius)):
               disp.fill_rect(x0+x, y0+y, abs(x*2), 1, col)
               break

def draw_circle(x0, y0, radius, col=st7789.color565(255, 255, 255)):
    for y in range(-radius, radius+1):
        yy = (y * y)//(radius*10)
        for x in range(-radius, 1):
           if ((x * x) + (y * y) <= (radius * radius)):
               disp.fill_rect(x0+x-yy//3, y0+y, yy+2, 1, col)
               disp.fill_rect(x0-x-yy, y0+y, yy+2, 1, col)
               break

def paint_fathand(cos, sin, color):
    dX = 2 if abs(cos) < abs(sin) else 0
    dY = 2 if abs(cos) > abs(sin) else 0
    if dX+dY==0:
        dX = dY = 2
    disp.line_ml( +cos, -sin, +dX, -dY, \
                 CENTER_X, CENTER_Y, color)

def draw_hands(old, new, hlen, col_new, col_old=None):
    cos_old = int(hlen*math.cos(dbl_pi*old/60)) if old else 0
    sin_old = int(hlen*math.sin(dbl_pi*old/60)) if old else 0
    cos_new = int(hlen*math.cos(dbl_pi*new/60))
    sin_new = int(hlen*math.sin(dbl_pi*new/60))
    col_old = open("/fonts/"+Watch_face,"rb") if Watch_face in uos.listdir("/fonts") else col_base
    disp.line_ml(+ cos_old, - sin_old, 0, 0, \
              CENTER_X, CENTER_Y, col_old)
    if hlen<100:
        paint_fathand(cos_old, sin_old, col_old)
    if type(col_old) is not list:
        col_old.close()
    if hlen<100 or old is None:
        paint_fathand(cos_new, sin_new, col_new)
    disp.line(CENTER_X + cos_new, CENTER_Y - sin_new, \
              CENTER_X, CENTER_Y, col_new)
    
if Watch_face not in uos.listdir("/fonts"):
    CENTER_Y -= 15
    draw_circle(CENTER_X, CENTER_Y, 104)
    draw_circle(CENTER_X, CENTER_Y, 102, st7789.color565(255, 0, 0))
    draw_circle(CENTER_X, CENTER_Y, 100, st7789.color565(0, 255, 0))
    paint_circle(CENTER_X, CENTER_Y, 98, st7789.color565(0, 0, 255))

def covrpt(yh, ov, n):
    xx = yh[n] if yh[n]<=ov[n] else yh[n]-ov[n] if n<3 else yh[n]-ov[n]-1
    if xx!=yh[n]:
        yh[n] = xx
        yh[n-1] += 1
        covrpt(yh ,ov, n-1)
    return yh
def carryover(yy_hh, ov=[99,12,31,23,59,59]):
    feb = 29 if yy_hh[0]%4==0 else 28
    ov[2] = 30 if yy_hh[1] in [4,6,9,11] else feb if yy_hh[1]==2 else 31
    covrpt(yy_hh, ov, 3)
    yy_hh[6] = week(yy_hh, feb) if yy_hh[6]==0 else 0
    return yy_hh
def week(yy, feb):
    days = (125+yy[0]+yy[0]//4+int("*033614625035"[yy[1]])+yy[2])
    wday = (days-1)%7 if feb==29 and yy[1]<3 else days%7
    return wday

internal_led = machine.Pin(25, machine.Pin.OUT)
def bitmap_thread():
    global col_base
    vw = 1    # 2nd threadで書く縦幅
    with open("/fonts/"+Watch_face,"rb") as bm:
        for l in range(1, disp_height-1, vw):
            col_base = bytes()
            for w in range(disp_width*vw):
                  if w%disp_width==0:
                      bm.seek(54+(disp_height-l)*disp_width*3)
                  bgr = bm.read(3)
                  rgb = st7789.color565((bgr[2],bgr[1],bgr[0]))
                  col_base += rgb.to_bytes(2, 'big')
            disp.set_window(0, l-1, disp_width-1, l-1+vw-1)
            disp.write(None, col_base)

dline = 214  # 日付時刻表示行の位置            
sec = min = hor = 75
omn = 0
if Watch_face in uos.listdir("/fonts"):
    bitmap_thread()
else:    
    for rd in range(0, 60, 5):
      draw_hands(None, rd, 104, st7789.color565(0, 0, 255))
      if rd==15:
        draw_hands(None, 75, 104, st7789.color565(255, 255, 255))

uart = UART(0, baudrate=9600, tx=None, rx=Pin(1), timeout=2000)
rxData = bytes()
rxData1 = bytes()
uart.readline()
if uart.readline()==None:
    print("GPSが応答していない可能性がある")
dt2 = []
# internal_led.toggle()
while True:
  while uart.any() > 0: 
     rxData1 = uart.read(1)
     Backup = bytes()
     if rxData1==doller and len(rxData)>0:
         if rxData[0:1]!=doller:
            print(rxData)
            rxData = doller
            continue
         rxData = rxData.decode('utf-8')
         if dump.value()==False:
            disp.text(font1, rxData[0:10], 24, dline)
            Backup = uart.read()
            print(rxData)
         if rxData.count(',')>6 \
            and rxData[1:6]=="GPRMC":
            UTC,Ua,Vert,VertM,Hori,HoriM,V,R,ddmmyy = \
                   rxData[7:].split(',')[0:9]
            if UTC=="" or len(ddmmyy)!=6:
                disp.text(font1, "Catching satellite...", 24, dline)
                print("衛星捕捉中・・・")
                rxData = doller
                continue
            if dt2==[]:
                print("衛星を捕捉しました")
            old = sec if sec>0 else 0
            wday = 0 if old==75 or old==59 else 8
            dt2 = carryover([int(ddmmyy[4:6]),int(ddmmyy[2:4]),int(ddmmyy[0:2]), \
                            int(UTC[0:2]) + 9,int(UTC[2:4]),int(UTC[4:6]),wday]) # +9-hours shift
            text1 = "20{:02d}.{:02d}.{:02d} {:02d}:{:02d}:{:02d}  "
            text2 = "N:{}°{}’ E:{}°{}’"
            ptext = text1.format(*dt2) + \
                        text2.format(Vert[0:2],Vert[2:4],Hori[0:3],Hori[3:5])
            print(ptext)
            sec = 75-dt2[5]
            if old==75 or old==59:
                disp.text(font1, " "+ptext[0:11], 36, dline)
                disp.text(font1,"SUNMONTUEWEDTHUFRISAT"[dt2[6]*3:dt2[6]*3+3]+("  "+str(dt2[2]))[-3:],173,110)
            disp.text(font1, ptext[10:20], 124, dline)
            omn = min if omn==0 else omn # not in a time 1S
            min = 75-dt2[4]
            draw_hands(old, sec, 100, st7789.color565(255, 0, 0))
            if old==73 or old==omn or (old==59 and 57<omn<62): 
                draw_hands(omn, min, 95, st7789.color565(255, 255, 255))
                omn = 0
            if old==70 or old==hor or (old==59 and 57<hor<62):
                ohr = hor if hor>0 else 0
                hor = 75-(dt2[3]%12)*5 -(dt2[4])//12
                draw_hands(ohr, hor, 75, st7789.color565(255, 255, 0))
            while True:
                rxData1 = uart.read(1)
                if rxData1==doller:
                    break
         rxData = bytes()
     rxData += rxData1 + Backup

print("終了")
