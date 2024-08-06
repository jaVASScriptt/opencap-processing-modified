from Controllers.gait_analysis_controller import GaitAnalysisController
from Controllers.muscle_analysis_controller import MuscleAnalysisController

from Utils.utils import *


class ProgramLauncher:
    def __init__(self, program):
        self.mac = MuscleAnalysisController()
        self.gac = GaitAnalysisController()

    def menu(self):
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
                print("You have been disconnected.")
            elif choice == "Exit":
                break
