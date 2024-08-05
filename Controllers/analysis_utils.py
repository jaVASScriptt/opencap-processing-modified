from Utils.utils import *
import tkinter as tk
from tkinter import filedialog


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
                self.modify_parameters()
        elif choice == "Start an analysis":
            self.start_analysis()
        elif choice == "Home":
            break


def modify_output_folder():
    """Ouvre un explorateur de fichiers pour sélectionner un dossier."""
    root = tk.Tk()
    root.withdraw()  # Cache la fenêtre principale
    folder_selected = filedialog.askdirectory(title="Sélectionnez un dossier pour sauvegarder les résultats")
    if folder_selected:
        print(f"Dossier sélectionné : {folder_selected}")
        return folder_selected
    else:
        print("Aucun dossier sélectionné.")
