from InquirerPy import inquirer

from Controllers.gait_analysis_controller import GaitAnalysisController
from Controllers.muscle_analysis_controller import MuscleAnalysisController

from Utils.utils import *


class ProgramLauncher:
    def __init__(self, program):
        self.mac = MuscleAnalysisController()
        self.gac = GaitAnalysisController()

    @staticmethod
    def display_message(message):
        border = '*' * (len(message) + 4)
        print(border)
        print(f"* {message} *")
        print(border)

    def menu(self):
        choices = ["Muscle Analysis", "Gait Analysis", "Opencap Data Recovery", "Disconnection", "Exit"]
        while True:
            choice = get_user_selection("What do you want to do?", choices)
            if choice == "Muscle Analysis":
                self.display_message("Muscle Analysis")
                self.mac.menu()
            elif choice == "Gait Analysis":
                self.display_message("Gait Analysis")
                self.gac.menu()
            elif choice == "Opencap Data Recovery":
                self.display_message("Opencap Data Recovery")
                retrieves_and_sorts_sessions()
            elif choice == "Disconnection":
                self.display_message("Disconnection")
            elif choice == "Exit":
                break
