import keyboard
from doorLock import DoorLock
from os import system, name
from display import Display

def clear_screen():
    if name == 'nt':
        _ = system('cls')
    else:
        _ = system('clear')


class MainProgram:
    def __init__(self):
        print("Starting System...")
        self.doorLock = DoorLock()
        self.display = Display(self.doorLock)
        print("System started")

    def add_key(self):
        print("Add new key:")
        print("Enter key id to your phone:{:d}".format(self.random_number))
        print("Enter id from ur phone")

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
