import time
import binascii

import board
import busio
import threading
from digitalio import DigitalInOut, Direction, Pull
# from adafruit_pn532.i2c import PN532_I2C
# from adafruit_pn532.adafruit_pn532 import _COMMAND_TGGETDATA
# from adafruit_pn532.adafruit_pn532 import _COMMAND_TGSETDATA
from pn532pi import Pn532
from pn532pi import Pn532I2c

def printString(data1):
    out = ''
    for x in range(len(data1)):
        out += '%02x' % data1[x]
    return out


class DoorLock:

    def __init__(self):
        print("Door lock is starting...")
        self.locked = True
        self.attempted_to_unlock = False
        self.maxUnlockTime = 5
        self.timeBeforeLock = 0
        print("Setting up NFC reader...")
        # self.i2c = busio.I2C(board.SCL, board.SDA)
        # self.reset_pin = DigitalInOut(board.D6)
        # self.req_pin = DigitalInOut(board.D12)
        # self.irq_pin = DigitalInOut(board.D10)
        # self.pn532 = PN532_I2C(self.i2c, debug=False, reset=self.reset_pin, req=self.req_pin, irq=self.irq_pin)
        # self.ic, self.ver, self.rev, self.support = self.pn532.firmware_version
        # # TODO: add try catch for pn532 not found
        # print("Found PN532 with firmware version: {0}.{1}".format(self.ver, self.rev))
        # self.pn532.SAM_configuration()
        # ========
        self.PN532_I2C = Pn532I2c(1)
        self.nfc = Pn532(self.PN532_I2C)
        self.nfc.begin()
        versiondata = self.nfc.getFirmwareVersion()
        if not versiondata:
            print("Didn't find PN53x board")
            raise RuntimeError("Didn't find PN53x board")  # halt
            # Got ok data, print it out!
        print("Found chip PN5 {:#x} Firmware ver. {:d}.{:d}".format((versiondata >> 24) & 0xFF,
                                                                    (versiondata >> 16) & 0xFF,
                                                                    (versiondata >> 8) & 0xFF))
        self.nfc.SAMConfig()

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
            success = self.nfc.inListPassiveTarget()
            if (success):
                # RTD_TEXT
                selectApdu = bytearray([0x00,  # CLA
                                        0xA4,  # INS
                                        0x04,  # P1
                                        0x00,  # P2
                                        0x07,  # Length of AID
                                        0xF0, 0x39, 0x41, 0x48, 0x14, 0x81, 0x01,  # AID defined on Android App
                                        0x00  # Le
                                        ])
                success, response = self.nfc.inDataExchange(selectApdu)
                if (success):
                    print(selectApdu)
                    print("responseLength: Apdu {:d}", len(response))
                    print(binascii.hexlify(response))

                    while (success):
                        selectApdu = bytearray(b"Hello from Arduino")
                        success, response = self.nfc.inDataExchange(selectApdu)
                        if (success):
                            print("responseLength: {:d}", len(response))
                            print(binascii.hexlify(response))
                        else:
                            print("disconnected")
                else:
                    print("Failed sending SELECT AID")
            else:
                print("Didn't find anything!")
            time.sleep(0.5)

            # uid = self.pn532.read_passive_target(timeout=0.5)
            # print(".")
            # # Try again if no card is available.
            # if uid is not None:
            #     print("Found card with UID:", [hex(i) for i in uid])
            #     # apdu create
            #     apdu = [0x00, 0xA4, 0x04, 0x00, 0x07, 0xF0, 0x39, 0x41, 0x48, 0x14, 0x81, 0x00, 0x00]
            #     # aid = A0000010000112
            #     print(apdu)
            #     # select apdu command AID
            #     sendData = self.pn532.call_function(_COMMAND_TGSETDATA, params=apdu)
            #     result = self.pn532.call_function(_COMMAND_TGGETDATA, 255)
            #     print(result)
            #     apdu = printString(result)
            #     print(apdu)
            #     continue



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
