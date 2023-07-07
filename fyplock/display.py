import threading
import time
import board
import busio
import digitalio
from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306
import subprocess


class Display:
    def __init__(self, doorLock):
        print("Starting OLED display...")
        self.doorLock = doorLock
        self.oled_reset = digitalio.DigitalInOut(board.D4)
        self.WIDTH = 128
        self.HEIGHT = 64
        self.BORDER = 5
        self.LOOPTIME = 1.0
        self.i2c = board.I2C()
        self.oled = adafruit_ssd1306.SSD1306_I2C(self.WIDTH, self.HEIGHT, self.i2c, addr=0x3C, reset=self.oled_reset)
        self.oled.fill(0)
        self.oled.show()
        self.image = Image.new("1", (self.oled.width, self.oled.height))
        self.draw = ImageDraw.Draw(self.image)
        self.draw.rectangle((0, 0, self.oled.width, self.oled.height), outline=255, fill=255)
        self.font = ImageFont.truetype('PixelOperator.ttf', 16)
        self.draw.text((self.BORDER, self.BORDER), "Door Lock System", font=self.font, fill=0)
        self.oled.image(self.image)
        self.oled.show()
        thread = threading.Thread(target=self.display_loop)
        thread.start()
    def display_loop(self):
        while True:
            pass
            # TODO: display door lock status
            # check status [locked/attempted to unlock/unlocked]
            # """
            # Door Lock status: Locked
            # waiting to unlock
            # """
            # """
            # Door Lock status: Locked
            # Attemded to unlock:
            # We have sent numbers to your phohe. Tap &random_num to unlock
            # """
            # """
            # Door Lock status: Unlocked
            # the door will lock in 5 seconds
            # """


