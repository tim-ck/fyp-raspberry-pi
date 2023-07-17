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

waiting_for_user_input = bytearray([0x00, 0x00, 0x00, 0x00])

unlock_success = bytearray([0x00,  # CLA
                            0xA4,  # INS
                            0x04,  # P1
                            0x00,  # P2
                            0x07,  # Length of AID
                            0xF0, 0x39, 0x41, 0x48, 0x14, 0x81, 0x03,  # AID defined on Android App
                            0x00  # Le
                            ])

unlock_failed = bytearray([0x00,  # CLA
                           0xA4,  # INS
                           0x04,  # P1
                           0x00,  # P2
                           0x07,  # Length of AID
                           0xF0, 0x39, 0x41, 0x48, 0x14, 0x81, 0x04,  # AID defined on Android App
                           0x00  # Le
                           ])


def intToBytes(number):
    return number.to_bytes(4, "big")


def HMAC_SHA256(key, message):
    return hmac.new(intToBytes(key), intToBytes(message), hashlib.sha256).digest()


def printBytes(bytes):
    #     print as 0x..
    for byte in bytes:
        print(hex(byte), end=" ")
    print()


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

    def sendUnlockStatusToAndroid(self, isUnlock):
        if isUnlock:
            cmd = unlock_success
        else:
            cmd = unlock_failed
        for i in range(5):
            success = self.nfc.readPassiveTargetID(0, timeout=250)
            if success:
                success, response = self.nfc.inDataExchange(cmd)
                if success and response == RESPONSE_OKAY:
                    return

    def lock(self):
        self.locked = True
        pass

    def unlock(self):
        self.locked = False
        self.time_before_lock = self.max_time_for_unlock
        threading.Thread(target=self.sendUnlockStatusToAndroid(True)).start()
        while (self.time_before_lock > 0):
            self.time_before_lock -= 1
            time.sleep(1.1)
        self.lock()

    def authenticate_failed(self, error_message):
        threading.Thread(target=self.sendUnlockStatusToAndroid(False)).start()
        for i in range(5):
            self.failed_to_unlock = True
            self.error_message = error_message
            time.sleep(1.1)
        self.reset_door_lock_status()

    def wait_for_passcode(self, secret_key):
        self.attempted_to_unlock = True
        self.timeBeforeAttemdExpired = self.max_time_to_wait_for_passcode
        correctAnswer = HMAC_SHA256(secret_key, self.random_number)
        while self.timeBeforeAttemdExpired > 0:
            self.timeBeforeAttemdExpired -= 1
            print("waiting for passcode: " + str(self.timeBeforeAttemdExpired))
            success, response = self.nfc.readPassiveTargetID(0, timeout=250)
            if success:
                success, response = self.nfc.inDataExchange(GET_PASSCODE)
                print("success: " + str(success))
                if success:
                    print("response: ")
                    printBytes(response)
                    print("responseLength: {:d}".format(len(response)))
                    if success and response == waiting_for_user_input:
                        time.sleep(1)
                        continue
                    if response == correctAnswer:
                        self.unlock()
                        return
                    else:
                        self.authenticate_failed("incorrect passcode")
                        print("expected: ")
                        print("secret_key: " + str(secret_key))
                        print("random_number: " + str(self.random_number))
                        printBytes(HMAC_SHA256(secret_key, self.random_number))
                        return
        self.authenticate_failed("time expired")

    def start_a_fake_challenge(self):
        for i in range(1, 6):
            print("sending random number to android app for " + str(i) + " time")
            # //WRITE_RANDOM_NUMBER + random_number
            apdu = WRITE_RANDOM_NUMBER + bytearray(self.random_number.to_bytes(1, byteorder='big'))
            success, response = self.nfc.inDataExchange(apdu)
            if (success):
                print("response: ")
                printBytes(response)
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
                        time.sleep(1.1)
                    self.authenticate_failed("time expired")
                    return
        self.authenticate_failed("failed to send challenge number")

    def generate_three_bytearray_with_random_order(self):
        first_byte = random.randint(0, 255)
        second_byte = random.randint(0, 255)
        third_byte = self.random_number
        random.shuffle([first_byte, second_byte, third_byte])
        print("generate_three_bytearray_with_random_order: " + str(first_byte) + " " + str(second_byte) + " " + str(
            third_byte))
        return bytearray([first_byte, second_byte, third_byte])

    def start_a_challenge(self, secret_key):
        for i in range(1, 6):
            print("sending random number to android app for " + str(i) + " time")
            apdu = WRITE_RANDOM_NUMBER + self.generate_three_bytearray_with_random_order()
            print("apdu: " + str(apdu))
            success, response = self.nfc.inDataExchange(apdu)
            if (success):
                print("responseLength: {:d}".format(len(response)))
                print("response: ")
                printBytes(response)
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
            success, response = self.nfc.readPassiveTargetID(0, timeout=250)
            if (success):
                success = self.nfc.inListPassiveTarget()
                if not success:
                    continue
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
                    time.sleep(1.1)
            else:
                print("Didn't find anything!")

    # status list: locked, failed_to_unlock, attempted_to_unlock
    def getStatusString(self):
        displayString = []
        if not self.locked:
            displayString.append("Door Lock status: ")
            displayString.append("Unlocked")
            displayString.append("the door will lock in:")
            displayString.append(str(self.time_before_lock))
            return displayString
        if self.failed_to_unlock:
            displayString.append("Door Lock status: ")
            displayString.append("Failed to unlock")
            if self.error_message != "":
                displayString.append("ERROR: " + self.error_message)
            return displayString
        if self.locked:
            if self.attempted_to_unlock:
                displayString.append("~~~"+str(self.random_number)+"~~~")
                displayString.append("Tap " + str(self.random_number) + " on the phone")
                displayString.append("and tap nfc reader")
                displayString.append("seconds left: " + str(self.timeBeforeAttemdExpired))
            else:
                displayString.append("Door Lock status: ")
                displayString.append("Locked")
                displayString.append("waiting to unlock")
            return displayString
        return "Welcome to the Door Lock System!"
