import random
import time
import binascii

import hmac
import hashlib
import board
import busio
import threading
from digitalio import DigitalInOut, Direction, Pull
# from adafruit_pn532.i2c import PN532_I2C
# from adafruit_pn532.adafruit_pn532 import _COMMAND_TGGETDATA
# from adafruit_pn532.adafruit_pn532 import _COMMAND_TGSETDATA
from pn532pi import Pn532
from pn532pi import Pn532I2c

from keyDB import getSecretKeyByID

RESPONSE_OKAY = bytearray([0x90, 0x00])
RESPONSE_WAITING_USER_INPUT = bytearray([0x91, 0x00])
GET_KEYID = bytearray([0x00,  # CLA
                                        0xA4,  # INS
                                        0x04,  # P1
                                        0x00,  # P2
                                        0x07,  # Length of AID
                                        0xF0, 0x39, 0x41, 0x48, 0x14, 0x81, 0x01,  # AID defined on Android App
                                        0x00  # Le
                                        ])
GET_PASSCODE = bytearray([0x00,  # CLA
                                        0xA4,  # INS
                                        0x04,  # P1
                                        0x00,  # P2
                                        0x07,  # Length of AID
                                        0xF0, 0x39, 0x41, 0x48, 0x14, 0x81, 0x02,  # AID defined on Android App
                                        0x00  # Le
                                        ])
WRITE_RANDOM_NUMBER = bytearray([0x01, 0x2E])


def HMAC_SHA256(key, message):
    return hmac.new(key, message, hashlib.sha256).digest()


class DoorLock:

    def __init__(self):
        print("Door lock is starting...")
        self.locked = True
        self.attempted_to_unlock = False
        self.failed_to_unlock = False
        self.error_message = ""
        self.random_number = -1
        self.maxTimeSendRandomNumber = 5
        self.max_time_to_wait_for_passcode = 30
        self.max_time_for_unlock = 30
        self.timeBeforeAttemdExpired = 0
        self.time_before_lock = 0

        print("Setting up NFC reader...")
        self.PN532_I2C = Pn532I2c(1)
        self.nfc = Pn532(self.PN532_I2C)
        self.nfc.begin()
        versiondata = self.nfc.getFirmwareVersion()
        if not versiondata:
            print("Didn't find PN53x board")
            raise RuntimeError("Didn't find PN53x board")
        print("Found chip PN5 {:#x} Firmware ver. {:d}.{:d}".format((versiondata >> 24) & 0xFF,
                                                                    (versiondata >> 16) & 0xFF,
                                                                    (versiondata >> 8) & 0xFF))
        self.nfc.SAMConfig()
        print("Starting NFC card detection thread...")
        self.nfc_thread = threading.Thread(target=self.detect_android_nfc_key)
        self.nfc_thread.start()

    def reset_door_lock_status(self):
        self.locked = True
        self.attempted_to_unlock = False
        self.failed_to_unlock = False
        self.error_message = ""

    def lock(self):
        self.locked = True
        pass

    def unlock(self):
        self.locked = False
        self.time_before_lock = self.max_time_for_unlock
        while(self.time_before_lock > 0):
            self.time_before_lock -= 1
            time.sleep(1.5)
        self.lock()

    def authenticate_failed(self, error_message):
        for i in range(5):
            self.failed_to_unlock = True
            self.error_message = error_message
            time.sleep(1.5)
        self.reset_door_lock_status()

    def wait_for_passcode(self, secret_key):
        self.attempted_to_unlock = True
        self.timeBeforeAttemdExpired = self.max_time_to_wait_for_passcode
        while self.timeBeforeAttemdExpired > 0:
            self.timeBeforeAttemdExpired -= 1
            print("waiting for passcode: " + str(self.timeBeforeAttemdExpired))
            success, response = self.nfc.inDataExchange(GET_PASSCODE)
            if success and len(response) == 4:
                print("response: " + str(response))
                print("responseLength: {:d}".format(len(response)))
                if response == HMAC_SHA256(secret_key, self.random_number):
                    self.unlock()
                    return
                else:
                    self.authenticate_failed("incorrect passcode")
                    return
            time.sleep(1.5)
        self.authenticate_failed("time expired")

    def start_a_fake_challenge(self):
        for i in range(1, 6):
            print("sending random number to android app for " + str(i) + " time")
            # //WRITE_RANDOM_NUMBER + random_number
            apdu = WRITE_RANDOM_NUMBER + bytearray(self.random_number.to_bytes(1, byteorder='big'))
            success, response = self.nfc.inDataExchange(apdu)
            if (success):
                print("response: " + str(response))
                print("responseLength: {:d}".format(len(response)))
                if response == RESPONSE_OKAY:
                    self.timeBeforeAttemdExpired = self.max_time_to_wait_for_passcode
                    while self.timeBeforeAttemdExpired > 0:
                        self.timeBeforeAttemdExpired -= 1
                        print("[fake]waiting for passcode: " + str(self.timeBeforeAttemdExpired))
                        success, response = self.nfc.inDataExchange(GET_PASSCODE)
                        # response length should be 4 bytes
                        if success and len(response) == 4:
                            print("response: " + str(response))
                            print("responseLength: {:d}".format(len(response)))
                            self.authenticate_failed("incorrect passcode")
                            return
                        time.sleep(1.5)
                    self.authenticate_failed("time expired")
                    return
        self.authenticate_failed("failed to send challenge number")

    def generate_three_bytearray_with_random_order(self):
        first_byte = random.randint(0, 255)
        second_byte = random.randint(0, 255)
        third_byte = self.random_number
        random.shuffle([first_byte, second_byte, third_byte])
        print("array: " + str(first_byte) + " " + str(second_byte) + " " + str(third_byte))
        return bytearray(first_byte.to_bytes(1, byteorder='big')) + \
            bytearray(second_byte.to_bytes(1, byteorder='big')) + \
            bytearray(third_byte.to_bytes(1, byteorder='big'))

    def start_a_challenge(self, secret_key):
        for i in range(1,6):
            print("sending random number to android app for " + str(i) + " time")
            # //WRITE_RANDOM_NUMBER + random_number
            apdu = WRITE_RANDOM_NUMBER + self.generate_three_bytearray_with_random_order()
            success, response = self.nfc.inDataExchange(apdu)
            if (success):
                print("responseLength: {:d}".format(len(response)))
                print("response: " + str(response))
                if response == RESPONSE_OKAY:
                    self.wait_for_passcode(secret_key)
                    return
        self.authenticate_failed("failed to send challenge number")


    def authenticate(self, keyID):
        is_key_exist, secret_key = getSecretKeyByID(keyID)
        self.random_number = random.randint(0, 255)
        self.locked = True
        if not is_key_exist:
            print("key not exist")
            self.start_a_fake_challenge()
        else:
            print("key exist")
            self.start_a_challenge(secret_key)

    def detect_android_nfc_key(self):
        print("detecting android nfc key...")
        while True:
            self.reset_door_lock_status()
            success = self.nfc.inListPassiveTarget()
            if (success):
                # RTD_TEXT
                select_apdu = GET_KEYID
                success, response = self.nfc.inDataExchange(select_apdu)
                if (success):
                    print(select_apdu)
                    print("responseLength: Apdu {:d}", len(response))
                    print("response: " + str(response))
                    keyID = response[0:4]
                    self.authenticate(keyID)
                else:
                    print("Failed sending SELECT AID")
            else:
                print("Didn't find anything!")
            time.sleep(1.5)

    # status list: locked, failed_to_unlock, attempted_to_unlock
    def getStatusString(self):
        displayString = []
        if not self.locked:
            displayString.append("Door Lock status: ")
            displayString.append("Unlocked")
            displayString.append("the door will lock in " + str(self.time_before_lock) + "seconds")
            return displayString
        if self.failed_to_unlock:
            displayString.append("Door Lock status: ")
            displayString.append("Failed to unlock")
            if self.error_message != "":
                displayString.append("ERROR: " + self.error_message)
            return displayString
        if self.locked:
            displayString.append("Door Lock status: ")
            if self.attempted_to_unlock:
                displayString.append("Attemded to unlock")
                displayString.append("seconds left: " + str(self.timeBeforeAttemdExpired))
                displayString.append("Tap " + str(self.random_number) + " on your phone")
                displayString.append("and tap the nfc reader to authenticat")
            else:
                displayString.append("Locked")
                displayString.append("waiting to unlock")
            return displayString
        return "Welcome to the Door Lock System!"
