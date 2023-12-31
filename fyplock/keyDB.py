import json

from numpy import random


def getSecretKeyByID(id):
    return True, 123


class KeyDB:
    # keyList is json obj
    # [{
    #  "keyid": 123,
    #  "secretKey": 123},
    #  {
    #  "keyid": 123,
    #  "secretKey": 123}]
    keyList = []

    p = 23
    g = 5

    def __init__(self):
        # if keyList.json does not exist, create one
        try:
            with open("keyList.json", "r") as f:
                self.keyList = json.load(f)
        except FileNotFoundError:
            with open("keyList.json", "w") as f:
                json.dump(self.keyList, f)

    def dhKeyExchange_addKey(self, pinFromPhone):
        A = pinFromPhone
        b = random.randint(1, 255)
        pinFromLock = (self.g ** b) % self.p
        secret_key = (pinFromPhone ** b) % self.p
        # generate a unique keyid with 9 digits
        keyid = random.randint(100000000, 999999999)
        while self.isKeyIDExist(keyid):
            keyid = random.randint(100000000, 999999999)
        self.keyList.append({"keyid": keyid, "secretKey": secret_key})
        self.saveKeyListAsJsonFile()
        return keyid, pinFromLock

    def saveKeyListAsJsonFile(self):
        with open("keyList.json", "w") as f:
            json.dump(self.keyList, f)

    def isKeyIDExist(self, keyid):
        for key in self.keyList:
            if key["keyid"] == keyid:
                return True
        return False

    def getSecretKeyByID(self, keyid):
        for key in self.keyList:
            if key["keyid"] == keyid:
                return True, key["secretKey"]
        return False, 0
