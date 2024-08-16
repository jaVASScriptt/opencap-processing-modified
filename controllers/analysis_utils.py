from utils.utils import *
import tkinter as tk
from tkinter import filedialog


def clear_terminal():
    os.system('cls' if os.name == 'nt' else 'clear')


def display_message(message):
    print()
    border = '*' * (len(message) + 4)
    print(border)
    print(f"* {message} *")
    print(border)
    print()


def menu_analysis(self):
    choices = ["data change", "Start an analysis", "Home"]
    while True:
        choice = self.get_user_selection("What do you want to do?", choices)
        if choice == "data change":
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


def download_trial(trial_id, folder, session_id=None):
    trial = get_trial_json(trial_id)
    if session_id is None:
        session_id = trial['session_id']

    os.makedirs(folder, exist_ok=True)

    # download model
    get_model_and_metadata(session_id, folder)

    # download trc and mot
    get_motion_data(trial_id, folder)

    return trial['name']


def get_periode_walk_run(session_id, trialName):
    from activity_analyses.gait_analysis import GaitAnalysis
    baseDir = os.path.join(os.getcwd(), '..')
    dataFolder = os.path.join(baseDir, 'data')
    n_gait_cycles = -1
    filter_frequency = 6
    sessionDir = os.path.join(dataFolder, session_id)

    right_times = GaitAnalysis(
        sessionDir, trialName, leg='r',
        lowpass_cutoff_frequency_for_coordinate_values=filter_frequency,
        n_gait_cycles=n_gait_cycles).get_coordinates_normalized_time()['mean']['time']
    left_times = GaitAnalysis(
        sessionDir, trialName, leg='l',
        lowpass_cutoff_frequency_for_coordinate_values=filter_frequency,
        n_gait_cycles=n_gait_cycles).get_coordinates_normalized_time()['mean']['time']

    time_min = min(right_times.min(), left_times.min())
    time_max = max(right_times.max(), left_times.max())

    return [time_min, time_max]
