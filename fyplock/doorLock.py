import time
import board
import busio
import threading
from digitalio import DigitalInOut
from adafruit_pn532.i2c import PN532_I2C


class DoorLock:

    def __init__(self):
        print("Door lock is starting...")
        self.locked = True
        self.isShowStatus = False
        print("Setting up NFC reader...")
        self.i2c = busio.I2C(board.SCL, board.SDA)
        self.reset_pin = DigitalInOut(board.D6)
        self.req_pin = DigitalInOut(board.D12)
        self.irq_pin = DigitalInOut(board.D10)
        self.pn532 = PN532_I2C(self.i2c, debug=False, reset=self.reset_pin, req=self.req_pin, irq=self.irq_pin)
        self.ic, self.ver, self.rev, self.support = self.pn532.firmware_version
        # TODO: add try catch for pn532 not found
        print("Found PN532 with firmware version: {0}.{1}".format(self.ver, self.rev))
        self.pn532.SAM_configuration()
        # new thread to detect nfc card
        print("Starting NFC card detection thread...")
        self.nfc_thread = threading.Thread(target=self.detectKeyCard)
        self.nfc_thread.start()

    def lock(self):
        # TODO: lock the door and change status
        pass

    def unlock(self):
        # TODO: unlock the door and change status
        pass

    # status

    def show_door_lock_status(self):
        self.isShowStatus = True

    def hide_door_lock_status(self):
        self.isShowStatus = False

    def detectKeyCard(self):
        # while True:
        # #
        pass

    def detect_android_nfc_key(self):
        while True:
            self.pn532.listen_for_passive_target()
            uid = self.pn532.get_passive_target()
            if uid is None:
                continue
            print("Found card with UID:", [hex(i) for i in uid])
