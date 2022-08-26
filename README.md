# GitPython
GPS watch for Raspberry Pi Pico written by MicroPython<br>
1) Use ST7789 IPS display 240x240 SPI<br>
2) Use GY-GPS6MV2 for real time clock<br>

#SPI(1) default pins<br>
spi1_sck   = 10<br>
spi1_mosi  = 11<br>
spi1_miso  =  8     #not use<br>
st7789_res = 12<br>
st7789_dc  = 13<br>
uart-tx    = 0<br>
uart-rx    = 1<br>

<img src="images/GPS_watch_2.jpg" width=400><br>

Pico-RTC watch on Tufty2040 (new_clock.py)<br>
1) Use SPI7789 + Tufty 2040 320x240 Parallel<br>
2) RGB565 can be selected when PicoGraphics's RGB332 is unavailable
3) Use WiFi for weather information (option)<br>
4) 2 Access Points auto roaming on WiFi<br>
5) Dial face design is changeable<br><br>
<img src="images/TuftyWatch.jpg" width=400><br>

In case of Pico W, at least button-c(GPIO-7) may be provided.<br>
 - Back light control step by step<br>
 - Save and restore last time stamp<br>
 - Show current SSID connected<br>
 - Change dial face when backlight=0 <br>
<br>LILYGO running...<br>
https://www.facebook.com/100001708228622/videos/pcb.474901580820581/776638766871782<br>
LILYGO #SPI(0) fixed pins<br>
spi1_sck  = 2<br>
spi1_mosi = 3<br>
st7789_bl = 4<br>
st7789_cs = 5<br>
st7789_res= 0<br>
st7789_dc = 1<br>
