from InquirerPy import inquirer

from utils import *
import os


class DataController:
    def __init__(self):
        self.session_id = None
        self.trial_name = None
        self.motion_type = None
        self.session_type = None
        self.sessions_types = ['treadmill', 'overground', 'other']

        self.motion_types_overground = [
            'squats',
            'sit_to_stand',
            'jumping',
            'walking',
            'drop_jump'
        ]

        self.motion_types_treadmill = [
            'walking',
            'running',
            'my_periodic_running',
            'running_torque_driven'
        ]

        self.motion_types_other = [
            'other',
            'walking_formulation1'
        ]

        self.sessions = []

    def collect_data(self):
        if not os.path.exists("sessions_info.json") or self.user_wants_to_update_data():
            retrieves_and_sorts_sessions()

    def user_wants_to_update_data(self):
        return self.get_user_selection(
            message="Do you want to download the new data from opencap? (This may take 1-3 minutes)",
            choices=["Yes", "No"]) == "Yes"

    def initialize_session_selection(self):
        ask_sessions = self.get_user_selection(
            message="Do you want to see your sessions or public sessions?",
            choices=["My sessions", "Public sessions", "All sessions", "Manual input"])
        self.handle_session_selection(ask_sessions)

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

    def setup(self):
        self.collect_data()
        self.initialize_session_selection()
        trials = get_trials_names_from_session(self.session_id)
        self.trial_name = self.get_user_selection(message="Select a trial:", choices=trials)
        self.session_type = self.get_user_selection(message="Select a session type:", choices=self.sessions_types)
        self.motion_type = self.get_user_selection(
            message="Select a motion type:",
            choices=self.motion_types_overground if self.session_type == 'overground'
            else self.motion_types_treadmill if self.session_type == 'treadmill'
            else self.motion_types_other)

    @staticmethod
    def get_user_selection(message, choices):
        print()
        res = inquirer.select(message=message, choices=choices).execute()
        print()
        return res
