import sys

from Controllers.gait_analysis_controller import GaitAnalysisController
from Controllers.muscle_analysis_controller import MuscleAnalysisController

from Utils.utils import *


class ProgramLauncher:
    def __init__(self, program):
        self.mac = MuscleAnalysisController()
        self.gac = GaitAnalysisController()

    def menu(self):

        if not os.path.exists("Data/sessions_info.json"):
            retrieves_and_sorts_sessions()

        choices = ["Muscle Analysis", "Gait Analysis", "Opencap Data Recovery", "Disconnection", "Exit"]
        while True:
            clear_terminal()
            choice = get_user_selection("What do you want to do?", choices)
            if choice == "Muscle Analysis":
                self.mac.menu()
            elif choice == "Gait Analysis":
                self.gac.menu()
            elif choice == "Opencap Data Recovery":
                retrieves_and_sorts_sessions()
            elif choice == "Disconnection":
                env_file_path = '.env'
                if os.path.exists(env_file_path):
                    os.remove(env_file_path)
                    print(f"File {env_file_path} has been deleted.")
                else:
                    print(f"File {env_file_path} not found.")
                sys.exit()
            elif choice == "Exit":
                break
