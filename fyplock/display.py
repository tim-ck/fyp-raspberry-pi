import threading
import time
from os import system, name

import board
import busio
import digitalio
from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306
import subprocess
def clear_screen():
    if name == 'nt':
        _ = system('cls')
    else:
        _ = system('clear')

class Display:
    def __init__(self, doorLock):
        print("Starting OLED display...")
        # clear
        self.doorLock = doorLock
        # self.oled_reset = digitalio.DigitalInOut(board.D4)
        # self.WIDTH = 128
        # self.HEIGHT = 64
        # self.BORDER = 5
        # self.LOOPTIME = 0.2
        # self.i2c = board.I2C()
        # self.oled = adafruit_ssd1306.SSD1306_I2C(self.WIDTH, self.HEIGHT, self.i2c, addr=0x3C, reset=self.oled_reset)
        # self.oled.fill(0)
        # self.oled.show()
        # self.image = Image.new("1", (self.oled.width, self.oled.height))
        # self.draw = ImageDraw.Draw(self.image)
        # self.draw.rectangle((0, 0, self.oled.width, self.oled.height), outline=255, fill=255)
        # self.font = ImageFont.truetype('PixelOperator.ttf', 16)
        # self.draw.rectangle((0, 0, self.oled.width, self.oled.height), outline=0, fill=0)
        # self.draw.text((self.BORDER, self.BORDER), "Door Lock System", font=self.font, fill=255)
        # self.oled.image(self.image)
        # self.oled.show()
        thread = threading.Thread(target=self.display_loop)
        thread.start()
    def display_loop(self):
        while True:
            # clear_screen()
            # doorLockStatusString = self.doorLock.getStatusString()
            # for i in range(len(doorLockStatusString)):
            #     print(doorLockStatusString[i])
            time.sleep(0.5)
            #
            # self.draw.rectangle((0, 0, self.oled.width, self.oled.height), outline=0, fill=0)
            # doorLockStatusString = self.doorLock.getStatusString()
            # for i in range(len(doorLockStatusString)):
            #     self.draw.text((0, 16*i), doorLockStatusString[i], font=self.font, fill=255)
            # self.oled.image(self.image)
            # self.oled.show()
            # time.sleep(self.LOOPTIME)



