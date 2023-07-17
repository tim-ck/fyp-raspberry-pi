import keyboard
from doorLock import DoorLock
from os import system, name
from display import Display
from keyDB import KeyDB
def clear_screen():
    if name == 'nt':
        _ = system('cls')
    else:
        _ = system('clear')


class MainProgram:
    def __init__(self):
        print("Starting System...")
        self.keyDB = KeyDB()
        self.doorLock = DoorLock(self.keyDB)
        self.display = Display(self.doorLock)
        print("System started")

    def add_key(self):
        print("Add new key:")
        print("=====================")
        print("On your phone, open the app")
        print("go to \"Key Management\" page")
        print("click \"Generate Pin Code\"")
        print("Enter the pin code here")
        pinCode = input("Enter pin code: ")
        keyid, pinFromLock = self.keyDB.dhKeyExchange_addKey(int(pinCode))
        print("Enter key id and Pin to your phone")
        print("key id:", keyid)
        print("Pin:", pinFromLock)
        pass



    def manage_keys(self):
        print("Manage keys: ")
        print("=====================")
        print("1. add new key")
        print("2. main menu")
        option = input("Enter option: ")
        if option == "1":
            self.add_key()
        elif option == "2":
            self.main_menu()
        else:
            print("Invalid option")
            self.manage_keys()


    def main_menu(self):
        print("Welcome to FYP Project - Door Lock System")
        print("Please select an option:")
        print("1. manage keys")
        print("2. exit")
        option = input("Enter option: ")
        clear_screen()
        if option == "1":
            self.manage_keys()
        elif option == "2":
            print("not yet ready")
        else:
            print("Invalid option")
            self.main_menu()

    def main(self):
        self.main_menu()




mainProgram = MainProgram()
mainProgram.main()
