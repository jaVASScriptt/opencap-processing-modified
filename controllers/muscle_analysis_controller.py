import os
import sys

from tools.utils import *

from controllers.analysis_utils import menu_analysis, modify_output_folder, get_periode_walk_run
from controllers.data_controller import DataController
from utils_dynamic_simulations.opensim_ad.main_opensim_ad import run_tracking
from utils_dynamic_simulations.opensim_ad.utils_opensim_ad import processInputsOpenSimAD, plotResultsOpenSimAD


class MuscleAnalysisController:
    def __init__(self):
        self.DataController = DataController("muscles_analysis")

        self.session_id = self.DataController.get('session_id')
        self.trial_name = self.DataController.get('trial_name')
        self.motion_type = self.DataController.get('motion_type')
        self.time_window = self.DataController.get('time_window')
        self.repetition = int(self.DataController.get('repetition'))
        self.case = self.DataController.get('case')
        self.treadmill_speed = self.DataController.get('treadmill_speed')
        self.contact_side = self.DataController.get('contact_side')
        self.ipopt_tolerance = self.DataController.get('ipopt_tolerance')
        self.mesh_density = self.DataController.get('mesh_density')
        self.baseDir = os.getcwd()

        self.output_folder = self.DataController.get('output_folder') \
            if self.DataController.get('output_folder') \
            else os.path.join(self.baseDir, 'data')
        self.DataController.set('output_folder', self.output_folder)

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
    def get_user_selection(message, choices=None, type=None, validate=None):
        return get_user_selection(message, choices, type, "Muscle Analysis", validate)

    def initialize_contact_side(self):
        self.contact_side = self.get_user_selection(
            message="Select the contact side:",
            choices=["all", "right", "left"]
        )
        self.DataController.set("contact_side", self.contact_side)

    def initialize_treadmill_speed(self):
        ask_if_treadmill_active = self.get_user_selection(
            message="Is the treadmill active?",
            type="confirm"
        )

        if ask_if_treadmill_active:
            self.treadmill_speed = self.get_user_selection(
                message="Please enter the speed of the treadmill in m/s : ",
                type="input",
                validate=lambda x: self.validate_time_input(x, 0.0)
            )

        self.DataController.set("treadmill_speed", self.treadmill_speed)

    def initialize_case(self):
        self.case = self.get_user_selection(
            message="Enter a name for this case to track different settings (recommendation: 0): ",
            type="input",
            validate=lambda x: x != ""
        )

        self.DataController.set("case", self.case)

    def initialize_motion_type(self):
        self.motion_type = self.get_user_selection(
            message="Select a motion type:",
            choices=self.motion_types)
        self.DataController.set("motion_type", self.motion_type)

    def initialize_session_selection(self):
        ask_sessions = self.get_user_selection(
            message="Do you want to see your sessions or public sessions?",
            choices=["My sessions", "Public sessions", "All sessions", "Manual input"])
        self.handle_session_selection(ask_sessions)
        self.DataController.set("session_id", self.session_id)

        self.trial_name = self.get_user_selection(
            message="Select a trial:",
            choices=get_trials_names_from_session(self.session_id))
        self.DataController.set("trial_name", self.trial_name)


    def initialize_complexity(self):
        complexity = self.get_user_selection(
            message="Select the complexity of the model "
                    "(the higher it is, the more precise it is, but the slower it is) :",
            choices=["1", "2", "3", "4 (recommended)", "5", "6", "7", "8", "9", "10 (not recommended)", "Manual input"]
        )

        if complexity == "Manual input":
            self.ipopt_tolerance = self.get_user_selection(
                message="Enter the tolerance (1-4):",
                type="input",
                validate=lambda x: x.isdigit() and 1 <= int(x) <= 4
            )

            self.mesh_density = self.get_user_selection(
                message="Enter the mesh density of the model (10-100):",
                type="input",
                validate=lambda x: x.isdigit() and 10 <= int(x) <= 100
            )

        else:
            complexity = int(complexity[0])
            self.ipopt_tolerance = int(complexity * 0.3 + 1)
            self.mesh_density = complexity * 10

        self.DataController.set("ipopt_tolerance", self.ipopt_tolerance)
        self.DataController.set("mesh_density", self.mesh_density)

    def handle_session_selection(self, selection):
        if selection == "Manual input":
            self.session_id = self.get_user_selection("Enter the session id:", type="input")
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

    def initialize_time_settings(self):

        list_choices = ["Enter a time window", "all the trial (not recommended)"]

        if self.motion_type in ['sit_to_stand', 'squats']:
            list_choices.append("Automatic repetition Detection (Beta)")
        elif self.motion_type in ['walking', 'running', 'my_periodic_running', 'running_torque_driven',
                                  'walking_formulation1']:
            list_choices.append("Automatic Time Window Detection (Beta)")

        choice = self.get_user_selection(
            message="What do you want to do?",
            choices=list_choices
        )

        if choice == "all the trial (not recommended)":
            self.time_window = []
            self.DataController.set("time_window", self.time_window)
            return
        elif choice == "Choose a repetition":
            self.repetition = self.get_user_selection(
                "Enter a specific repetition", type="input",
                validate=lambda x: x.isdigit()
            )

            self.repetition = int(self.repetition)

            self.DataController.set("repetition", self.repetition)
            self.time_window = []
            self.DataController.set("time_window", self.time_window)
            return
        elif choice == "Automatic Time Window Detection (Beta)":
            self.time_window = get_periode_walk_run(self.session_id, self.trial_name)
            self.DataController.set("time_window", self.time_window)

            print()
            print(f"Time window detected : {self.time_window}")
            print()
            return
        else:
            start_time_input = self.get_user_selection(
                message="Enter the start time of the time window (ex: 0.1) : ",
                type="input",
                validate=lambda x: self.validate_time_input(x, 0.0)
            )
            start_time = float(start_time_input)

            end_time_input = self.get_user_selection(
                message="Enter the end time of the time window (ex: 0.1), which must be greater than the start time : ",
                type="input",
                validate=lambda x: self.validate_time_input(x, start_time)
            )
            end_time = float(end_time_input)

            self.time_window = [start_time, end_time]
            self.DataController.set("time_window", self.time_window)

    def initialize_output_folder(self):
        self.output_folder = modify_output_folder()
        self.DataController.set("output_folder", self.output_folder)

    def start_analysis(self):
        self.DataController.display()

        if self.get_user_selection("Do you want to proceed with these settings?", ["Yes", "No"]) == "No":
            return

        analysis_name = self.get_user_selection("Please enter a name for the analysis : ", type="input",
                                                validate=lambda x: len(x) > 0)

        output_folder = os.path.join(self.output_folder, analysis_name)

        opensimADDir = os.path.join(self.baseDir, 'utils_dynamic_simulations', 'opensim_ad')
        sys.path.append(self.baseDir)
        sys.path.append(opensimADDir)

        solveProblem = True
        analyzeResults = True

        settings = processInputsOpenSimAD(self.baseDir, output_folder, self.session_id, self.trial_name,
                                          self.motion_type, self.time_window, self.repetition,
                                          self.treadmill_speed, self.contact_side, self.mesh_density,
                                          self.ipopt_tolerance)

        run_tracking(self.baseDir, output_folder, self.session_id, settings, case=self.case,
                     solveProblem=solveProblem, analyzeResults=analyzeResults)

        plotResultsOpenSimAD(output_folder, self.session_id, self.trial_name, settings,
                             cases=[self.case], output_dir=output_folder)

        self.DataController.write_parameters_in_excel(output_folder)

    def setup(self):
        self.initialize_session_selection()
        self.initialize_motion_type()
        self.initialize_time_settings()
        self.initialize_case()
        self.initialize_treadmill_speed()
        self.initialize_contact_side()
        self.initialize_complexity()
        self.initialize_output_folder()

    def modify_parameters(self):
        answer = self.get_user_selection("What do you want to modify??",
                                         ["Trial", "Motion type", "Time settings", "Case", "Treadmill speed",
                                          "Contact side", "Complexity", "Output folder"])

        match answer:
            case "Trial":
                self.initialize_session_selection()
            case "Motion type":
                self.initialize_motion_type()
            case "Time settings":
                self.initialize_time_settings()
            case "Case":
                self.initialize_case()
            case "Treadmill speed":
                self.initialize_treadmill_speed()
            case "Contact side":
                self.initialize_contact_side()
            case "Complexity":
                self.initialize_complexity()
            case "Output folder":
                self.initialize_output_folder()
