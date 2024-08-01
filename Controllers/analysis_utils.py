from Utils.utils import *


def menu_analysis(self):
    choices = ["Data change", "Start an analysis", "Home"]
    while True:
        choice = get_user_selection("What do you want to do?", choices)
        if choice == "Data change":
            data_choices = ["Full setup", "Select an element to change"]
            data_choice = get_user_selection("What do you want to do?", data_choices)
            if data_choice == "Full setup":
                self.setup()
            elif data_choice == "Select an element to change":
                print("Select an element to change")
        elif choice == "Start an analysis":
            self.start_analysis()
        elif choice == "Home":
            break