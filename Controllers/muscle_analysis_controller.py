import sys

from InquirerPy import inquirer

from Controllers.analysis_utils import menu_analysis
from Controllers.data_controller import DataController
from Utils.utils import *
import os

from UtilsDynamicSimulations.OpenSimAD.utils_opensim_ad import processInputsOpenSimAD, plotResultsOpenSimAD
from UtilsDynamicSimulations.OpenSimAD.main_opensim_ad import run_tracking


class MuscleAnalysisController:
    def __init__(self):
        self.DataController = DataController("muscles_analysis")

        self.session_id = self.DataController.get('session_id')
        self.trial_name = self.DataController.get('trial_name')
        self.motion_type = self.DataController.get('motion_type')
        self.time_window = self.DataController.get('time_window')
        self.repetition = str(self.DataController.get('repetition'))
        self.case = self.DataController.get('case')
        self.treadmill_speed = self.DataController.get('treadmill_speed')
        self.contact_side = self.DataController.get('contact_side')

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

    @staticmethod
    def get_user_selection(message, choices):
        return get_user_selection(message, choices, display="Muscle Analysis")

    def initialize_contact_side(self):
        self.contact_side = self.get_user_selection(
            message="Select the contact side:",
            choices=["all", "right", "left"]
        )
        return self.contact_side

    def initialize_treadmill_speed(self):
        ask_if_treadmill_active = inquirer.confirm(
            message="Is the treadmill active?",
            default=True,
        ).execute()

        if ask_if_treadmill_active:
            print()
            self.treadmill_speed = inquirer.text(
                message="Please enter the time, the speed of the treadmill in m/s :",
                validate=lambda x: self.validate_time_input(x, 0.0)
            ).execute()
            print()

        return self.treadmill_speed

    def initialize_case(self):
        self.case = inquirer.text(
            message="Enter a name for this case to track different settings (recommendation: 0):",
            validate=lambda x: x != ""
        ).execute()
        return self.case

    def initialize_repetition(self):
        self.repetition = inquirer.text(
            message="Enter the repetition you want to take into account (0 is first)",
            validate=lambda x: x.isdigit()
        ).execute()
        return self.repetition

    def initialize_motion_type(self):
        self.motion_type = self.get_user_selection(
            message="Select a motion type:",
            choices=self.motion_types)
        return self.motion_type

    def initialize_trial_selection(self):
        self.trial_name = self.get_user_selection(
            message="Select a trial:",
            choices=get_trials_names_from_session(self.session_id))
        return self.trial_name

    def initialize_session_selection(self):
        ask_sessions = self.get_user_selection(
            message="Do you want to see your sessions or public sessions?",
            choices=["My sessions", "Public sessions", "All sessions", "Manual input"])
        self.handle_session_selection(ask_sessions)
        return self.session_id

    def handle_session_selection(self, selection):
        if selection == "Manual input":
            self.session_id = input("Enter the session id: ")
        else:
            self.sessions = get_sessions(is_public=self.get_public_status(selection))
            self.session_id = self.extract_session_id(
                self.get_user_selection(message="Select a session:", choices=self.sessions))

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

    @staticmethod
    def validate_time_input(input_str, higher_than):
        try:
            value = float(input_str)
            if value > higher_than:
                return value
            return False
        except Exception:
            return False

    def initialize_time_window(self):
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

        return [start_time, end_time]

    def start_analysis(self):
        self.DataController.display()

        if self.get_user_selection("Do you want to proceed with these settings?", ["Yes", "No"]) == "No":
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

        run_tracking(baseDir, dataFolder, self.session_id, settings, case=self.case,
                     solveProblem=solveProblem, analyzeResults=analyzeResults)

        plotResultsOpenSimAD(dataFolder, self.session_id, self.trial_name, settings, cases=[self.case])

    def setup(self):
        self.DataController.set("session_id", self.initialize_session_selection)
        self.DataController.set("trial_name", self.initialize_trial_selection)
        self.DataController.set("motion_type", self.initialize_motion_type)
        self.DataController.set("time_window", self.initialize_time_window)
        self.DataController.set("repetition", self.initialize_repetition)
        self.DataController.set("case", self.initialize_case)
        self.DataController.set("treadmill_speed", self.initialize_treadmill_speed)
        self.DataController.set("contact_side", self.initialize_contact_side)
        self.session_id = self.DataController.get("session_id")
        self.trial_name = self.DataController.get("trial_name")
        self.motion_type = self.DataController.get("motion_type")
        self.time_window = self.DataController.get("time_window")
        self.repetition = self.DataController.get("repetition")
        self.case = self.DataController.get("case")
        self.treadmill_speed = self.DataController.get("treadmill_speed")
        self.contact_side = self.DataController.get("contact_side")

    def modify_parameters(self):
        answer = self.get_user_selection("What do you want to modify?",
                                    ["Session", "Trial", "Motion type", "Time window",
                                     "Repetition", "Case", "Treadmill speed", "Contact side"])

        if answer == "Session":
            self.DataController.set("session_id", self.initialize_session_selection)
            self.session_id = self.DataController.get("session_id")

        elif answer == "Trial":
            self.DataController.set("trial_name", self.initialize_trial_selection)
            self.trial_name = self.DataController.get("trial_name")

        elif answer == "Motion type":
            self.DataController.set("motion_type", self.initialize_motion_type)
            self.motion_type = self.DataController.get("motion_type")

        elif answer == "Time window":
            self.DataController.set("time_window", self.initialize_time_window)
            self.time_window = self.DataController.get("time_window")

        elif answer == "Repetition":
            self.DataController.set("repetition", self.initialize_repetition)
            self.repetition = self.DataController.get("repetition")

        elif answer == "Case":
            self.DataController.set("case", self.initialize_case)
            self.case = self.DataController.get("case")

        elif answer == "Treadmill speed":
            self.DataController.set("treadmill_speed", self.initialize_treadmill_speed)
            self.treadmill_speed = self.DataController.get("treadmill_speed")

        elif answer == "Contact side":
            self.DataController.set("contact_side", self.initialize_contact_side)
            self.contact_side = self.DataController.get("contact_side")
