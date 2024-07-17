from InquirerPy import inquirer

from utils import *
import os


class DataController:
    def __init__(self):
        self.session_id = None
        self.trial_name = None
        self.motion_type = None
        self.time_window = None
        self.repetition = None
        self.case = None
        self.treadmill_speed = 0

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
        self.motion_type = self.get_user_selection(
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
    def get_user_selection(message, choices):
        print()
        res = inquirer.select(message=message, choices=choices).execute()
        print()
        return res

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
