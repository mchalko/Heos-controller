from machine import Pin
import led
from led import Led
from button import Button
import time
import network
import socket
import ure
"""
class ConnManager(object):
    def __init__(self, configFile, ap_ssid = "ReCo", ap_password = "12345678"):
        self.config = configFile
        self.ssid = ap_ssid
        self.password = ap_password
    def __connectLan(self):
        return False
    def __connectWifi(self):
        return False
    def connect(self):
        return self.__connectLan() or self.__connectWifi() # try both, prefer lan
    def createAP(self):
        return False
    
class HeosManager(object):
    def __init__(self, configFile):
        self.configFile = conFile
    
class ConfManager(object):
    def __init__(self, lanFile, heosFile, port = 80):
        self.connConf = lanFile
        self.heosConf = heosFile
        self.port = port
    def listen(self):
        pass

"""
#create buttons 
buttons = (Button(23), Button(5), Button(23), Button(5), Button(13), Button(12))
#btn_volUp, btn_volDown, btn_1, btn_2, btn_3, btn_4 = buttons
#create leds
leds = (Led(23), Led(15), Led(4), Led(17), Led(18), Led(5), Led(16), Led(2))
#led_volUp, led_volDown, led_3, led_4, led_5, led_6, led_7 = leds

#FILE_HEOS = "config_heos"
#FILE_LAN = "config_lan"

#lanMngr = ConnManager(FILE_LAN)
#heosMngr = HeosManager(FILE_HEOS)

def onPress():
    print("press")
def onSPress():
    print("shortpress")
def onRelease():
    print("release")
def onLPress():
    print("longPress")
def onHold():
    print("hold")
"""        
def error():
    led_controller.setBlinkFunction(LedController.blinkError, 1000)
    while True:
        led_controller.update()
"""
"""
#### Program start
if any(b.isPressed() for b in buttons): # if any button is pressed enter config mode
    led_controller.setBlinkFunction(led_controller.blinkConfig)
    lanMngr.createAP()
    configMngr = ConfManager(lanFile = FILE_LAN, heosFile = FILE_HEOS)
    while True: 
        configMngr.listen()
        led_controller.update()


led_controller.setBlinkFunction(led_controller.blinkConnecting)
while True:
    led_controller.update()
    for button in buttons: 
        button.update()
"""
for button in buttons:
        button.on_press(onPress)
        button.on_shortpress(onSPress)
        button.on_longpress(onLPress)
        button.on_hold(onHold)
        button.on_release(onRelease())

while True:
    led.blink_connecting(leds)
    for b in buttons :
        b.update()

