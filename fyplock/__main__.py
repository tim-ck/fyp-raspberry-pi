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

    def hide_door_lock_status(self):
        # self.doorLock.hide_door_lock_status()
        if mainProgram == None:
            print("mainProgram is None")
            return
        mainProgram.main_menu()

    def show_door_lock_status(self):
        print("Door lock status: (press x to back to main menu)")
        print("=====================")
        # self.doorLock.show_door_lock_status()

    def manage_keys(self):
        print("Manage keys: (press x to back to main menu)")
        print("=====================")
        # keyboard.add_hotkey('x', self.hide_door_lock_status)
        print("1. add new key")
        print("2. remove key")
        option = input("Enter option: ")
        if option == "1":
            self.add_key()
        if option == "2":
            self.remove_key()

    def main_menu(self):
        print("Welcome to FYP Project - Door Lock System")
        print("Please select an option:")
        print("1. recent door lock status record")
        print("2. manage keys")
        print("3. exit")
        option = input("Enter option: ")
        clear_screen()
        if option == "1":
            self.show_door_lock_status()
        if option == "2":
            self.manage_keys()
        else:
            print("Invalid option")
            self.main_menu()

    def main(self):
        self.main_menu()


mainProgram = MainProgram()
mainProgram.main()
