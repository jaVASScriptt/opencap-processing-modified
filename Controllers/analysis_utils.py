from Utils.utils import *
import tkinter as tk
from tkinter import filedialog


def clear_terminal():
    os.system('cls' if os.name == 'nt' else 'clear')


def display_message(message):
    border = '*' * (len(message) + 4)
    print(border)
    print(f"* {message} *")
    print(border)
    print()


def menu_analysis(self):
    choices = ["Data change", "Start an analysis", "Home"]
    while True:
        choice = self.get_user_selection("What do you want to do?", choices)
        if choice == "Data change":
            data_choices = ["Full setup", "Select an element to change"]
            data_choice = self.get_user_selection("What do you want to do?", data_choices)
            if data_choice == "Full setup":
                self.setup()
            elif data_choice == "Select an element to change":
                self.modify_parameters()
        elif choice == "Start an analysis":
            self.start_analysis()
        elif choice == "Home":
            break


def modify_output_folder():
    """Ouvre un explorateur de fichiers pour sélectionner un dossier."""
    root = tk.Tk()
    root.withdraw()  # Cache la fenêtre principale
    folder_selected = filedialog.askdirectory(title="Select a folder to save the results")
    print()
    if folder_selected:
        print(f"Selected folder : {folder_selected}")
        print()
        return folder_selected
    else:
        print("No folders selected.")
        print()
        return None

