import time
import board
import busio
import threading
from digitalio import DigitalInOut, Direction, Pull
from adafruit_pn532.i2c import PN532_I2C
# get data from adpu android hce
# from adafruit_pn532.adafruit_pn532 import COMMAND_TGGETDATA
# from adafruit_pn532.adafruit_pn532 import COMMAND_TGSETDATA
import pn532pi.nfc as nfc
import ndef
class DoorLock:

    def __init__(self):
        print("Door lock is starting...")
        self.locked = True
        self.attempted_to_unlock = False
        self.maxUnlockTime = 5
        self.timeBeforeLock = 0
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
        self.nfc_thread = threading.Thread(target=self.detect_android_nfc_key)
        self.nfc_thread.start()

    def lock(self):
        # TODO: lock the door and change status
        pass

    def unlock(self):
        # TODO: unlock the door and change status
        pass

    def detectKeyCard(self):
        # while True:
        # #
        pass

    def detect_android_nfc_key(self):
        print("detecting android nfc key...")
        while True:
            self.pn532.listen_for_passive_target()
            uid = self.pn532.get_passive_target()
            if uid is None:
                print("card not found")
                continue
            print("Found card with UID:", [hex(i) for i in uid])
    #             #         send adpu command to android phone
    #             uid = self.pn532.read_passive_target()
    #             print(".", end="")
    #             if uid is not None:
    #                 break
    #         print("")
    #
    #         print("Found card with UID:", [hex(i) for i in uid])
    #         print("Authenticating block 4 ...")
    #         cardApdu = [0x00, 0xA4, 0x04, 0x00, 0x07, 0xA0, 0x00, 0x00, 0x10, 0x00, 0x01,
    #                     0x12, 0x00]  # select apdu command AID "0xA0000010000112"
    #
    #     def sendAPDU(self, apdu):
    #         sendData = self.pn532.call_function(COMMAND_TGSETDATA, params=apdu)
    #
    #     def getAPDU(self):
    #         result = self.pn532.call_function(COMMAND_TGGETDATA, 255)
    #         print(result)
    #         apdu = nfc.Apdu.from_buffer(result)
    #         return apdu

    def getStatusString(self):
        displayString = []
        if not self.locked:
            displayString.append("Door Lock status: ")
            displayString.append("Unlocked")
            displayString.append("the door will lock in " + self.timeBeforeLock + "seconds")
            return displayString
        if self.locked:
            displayString.append("Door Lock status: ")
            if self.attempted_to_unlock:
                displayString.append("Attemded to unlock")
                displayString.append("Tap &random_num to unlock")
            else:
                displayString.append("Locked")
                displayString.append("waiting to unlock")
            return displayString
        return "Welcome to the Door Lock System!"
