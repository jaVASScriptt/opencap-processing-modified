import sys

from InquirerPy import inquirer

from Controllers.analysis_utils import menu_analysis
from Utils.utils import *
import os

from UtilsDynamicSimulations.OpenSimAD.utils_opensim_ad import processInputsOpenSimAD, plotResultsOpenSimAD
from UtilsDynamicSimulations.OpenSimAD.main_opensim_ad import run_tracking


class MuscleAnalysisController:
    def __init__(self):
        self.session_id = None
        self.trial_name = None
        self.motion_type = None
        self.time_window = None
        self.repetition = None
        self.case = None
        self.treadmill_speed = 0
        self.contact_side = 'all'

        self.motion_types = [
            'squats',
            'sit_to_stand',
            'jumping',
            'walking',
            'drop_jump',
            'running',
            'my_periodic_running',
            'running_torque_driven',
            'other',
            'walking_formulation1'
        ]

        self.sessions = []

    def menu(self):
        menu_analysis(self)

    def user_wants_to_update_data(self):
        return get_user_selection(
            message="Do you want to download the new data from opencap? (This may take 1-3 minutes)",
            choices=["Yes", "No"]) == "Yes"

    def initialize_session_selection(self):
        ask_sessions = get_user_selection(
            message="Do you want to see your sessions or public sessions?",
            choices=["My sessions", "Public sessions", "All sessions", "Manual input"])
        self.handle_session_selection(ask_sessions)

    def handle_session_selection(self, selection):
        if selection == "Manual input":
            self.session_id = input("Enter the session id: ")
        else:
            self.sessions = get_sessions(is_public=self.get_public_status(selection))
            self.session_id = self.extract_session_id(
                get_user_selection(message="Select a session:", choices=self.sessions))

    @staticmethod
    def get_public_status(selection):
        if selection == "My sessions":
            return False
        elif selection == "Public sessions":
            return True
        return None

    @staticmethod
    def extract_session_id(session_string):
        return session_string.split(" (")[1].split(")")[0]

    def setup(self):
        self.initialize_session_selection()
        trials = get_trials_names_from_session(self.session_id)
        self.trial_name = get_user_selection(message="Select a trial:", choices=trials)
        self.motion_type = get_user_selection(
            message="Select a motion type:",
            choices=self.motion_types)
        self.ask_for_time_window()
        self.case = inquirer.text(
            message="Enter a name for this case to track different settings (recommendation: 0):",
            validate=lambda x: x != ""
        ).execute()
        self.get_treadmill_speed()

    def get_treadmill_speed(self):
        ask_if_threadmill_active = inquirer.confirm(
            message="Is the treadmill active?",
            default=True,
        ).execute()

        if ask_if_threadmill_active:
            print()
            self.treadmill_speed = inquirer.text(
                message="Please enter the time, the speed of the treadmill in m/s :",
                validate=lambda x: self.validate_time_input(x, 0.0)
            ).execute()
            print()

    @staticmethod
    def validate_time_input(input_str, higher_than):
        try:
            value = float(input_str)
            if value > higher_than:
                return value
            return False
        except Exception:
            return False

    def ask_for_time_window(self):
        print()
        want_time_window = inquirer.confirm(
            message="Do you want to enter a time window? It's highly recommended to speed up the computation.",
            default=True,
        ).execute()
        print()

        if not want_time_window:

            if self.motion_type in ['sit_to_stand', 'squats']:
                print()
                want_repetition = inquirer.confirm(
                    message="Your choice of type of motion allows us to automatically split repetitions, "
                            "do you want to choose one?",
                    default=True,
                ).execute()
                print()

                if not want_repetition:
                    self.time_window = []
                    return

                else:
                    print()
                    self.repetition = inquirer.text(
                        message="Enter the repetition you want to take into account (0 is first)",
                        validate=lambda x: x.isdigit()
                    ).execute()
                    print()

                    return
            else:
                self.time_window = []
                return

        print()
        start_time_input = inquirer.text(
            message="Enter the start time of the repetition (ex: 0.1)",
            validate=lambda x: self.validate_time_input(x, 0.0)
        ).execute()
        print()
        start_time = float(start_time_input)

        print()
        end_time_input = inquirer.text(
            message="Enter the end time of the repetition (ex: 0.1), which must be greater than the start time "
                    "and we recommend that the total time is lower than 2 sec :",
            validate=lambda x: self.validate_time_input(x, start_time)
        ).execute()
        print()
        end_time = float(end_time_input)

        self.time_window = [start_time, end_time]

    def start_analysis(self):

        question = "Here are all the settings you've configured:\n" \
                   f"\n" \
                   f"Session id: {self.session_id}\n" \
                   f"Trial name: {self.trial_name}\n" \
                   f"Motion type: {self.motion_type}\n" \
                   f"Time window: {self.time_window}\n" \
                   f"Repetition: {self.repetition}\n" \
                   f"Treadmill speed: {self.treadmill_speed}\n" \
                   f"Contact side: {self.contact_side}\n" \
                   f"Case: {self.case}\n" \
                   f"\n" \
                   "Do you want to proceed with these settings?"

        if get_user_selection(question, ["Yes", "No"]) == "No":
            return

        baseDir = os.getcwd()
        opensimADDir = os.path.join(baseDir, 'UtilsDynamicSimulations', 'OpenSimAD')
        sys.path.append(baseDir)
        sys.path.append(opensimADDir)

        solveProblem = True
        analyzeResults = True

        dataFolder = os.path.join(baseDir, 'Data')

        settings = processInputsOpenSimAD(baseDir, dataFolder, self.session_id, self.trial_name,
                                          self.motion_type, self.time_window, self.repetition,
                                          self.treadmill_speed, self.contact_side)

        # %% Simulation.
        run_tracking(baseDir, dataFolder, self.session_id, settings, case=self.case,
                     solveProblem=solveProblem, analyzeResults=analyzeResults)

        # %% Plots.
        plotResultsOpenSimAD(dataFolder, self.session_id, self.trial_name, settings, cases=[self.case])
