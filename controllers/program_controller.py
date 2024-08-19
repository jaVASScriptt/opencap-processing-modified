import sys

from tools.utils import *

from controllers.gait_analysis_controller import GaitAnalysisController
from controllers.muscle_analysis_controller import MuscleAnalysisController


class ProgramLauncher:
    def __init__(self, program):
        self.mac = MuscleAnalysisController()
        self.gac = GaitAnalysisController()

    def menu(self):

        if not os.path.exists("data/sessions_info.json"):
            retrieves_and_sorts_sessions()

        choices = ["Muscle Analysis", "Gait Analysis", "Opencap data Recovery", "Disconnection", "Exit"]
        while True:
            clear_terminal()
            choice = get_user_selection("What do you want to do?", choices)
            if choice == "Muscle Analysis":
                self.mac.menu()
            elif choice == "Gait Analysis":
                self.gac.menu()
            elif choice == "Opencap data Recovery":
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
