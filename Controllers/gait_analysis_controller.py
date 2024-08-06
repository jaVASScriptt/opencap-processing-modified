from ActivityAnalyses.gait_analysis import GaitAnalysis
from Controllers.analysis_utils import menu_analysis, modify_output_folder
from Controllers.data_controller import DataController
from Utils.utils_plotting import plot_dataframe_with_shading, save_plots_to_excel, save_gait_metrics_to_excel
from Utils.utils import *
import os
import sys


class GaitAnalysisController:

    def __init__(self):

        sys.path.append("../")
        sys.path.append("../ActivityAnalyses")

        # Paths
        self.baseDir = os.path.join(os.getcwd(), '..')
        self.dataFolder = os.path.join(self.baseDir, 'Data')

        self.DataController = DataController('gait_analysis')

        self.sessions_trials = self.DataController.get('sessions_trials')
        self.analysis_folder = self.DataController.get('analysis_folder')

        self.scalar_names = {'gait_speed', 'stride_length', 'step_width', 'cadence',
                             'single_support_time', 'double_support_time', 'step_length_symmetry'}

        self.n_gait_cycles = -1
        self.filter_frequency = 6
        self.AllGaitResults = {}

    def menu(self):
        menu_analysis(self)

    @staticmethod
    def get_user_selection(message, choices):
        return get_user_selection(message, choices, display="Gait Analysis")

    def start_analysis(self):

        self.DataController.display()

        if self.get_user_selection("Do you want to proceed with these settings?", ["Yes", "No"]) == "No":
            return

        analysis_name = inquirer.text(
            message="Please enter a name for the analysis : ",
            validate=lambda x: len(x) > 0
        ).execute()

        self.analysis_folder = os.path.join(self.analysis_folder, analysis_name)
        os.makedirs(self.analysis_folder, exist_ok=True)

        for session_trial in self.sessions_trials:
            session_id = session_trial['session_id']
            trial_name = session_trial['trial_name']

            trial_id = get_trial_id(session_id, trial_name)
            sessionDir = os.path.join(self.dataFolder, session_id)

            trialName = download_trial(trial_id, sessionDir, session_id=session_id)

            print('\n')

            try:
                gait_r = GaitAnalysis(
                    sessionDir, trialName, leg='r',
                    lowpass_cutoff_frequency_for_coordinate_values=self.filter_frequency,
                    n_gait_cycles=self.n_gait_cycles)
                gait_l = GaitAnalysis(
                    sessionDir, trialName, leg='l',
                    lowpass_cutoff_frequency_for_coordinate_values=self.filter_frequency,
                    n_gait_cycles=self.n_gait_cycles)

                gaitResults = {'scalars_r': gait_r.compute_scalars(self.scalar_names),
                               'curves_r': gait_r.get_coordinates_normalized_time(),
                               'scalars_l': gait_l.compute_scalars(self.scalar_names),
                               'curves_l': gait_l.get_coordinates_normalized_time()}

                print(f'\nRight foot gait metrics for session "{session_id}", trial "{trial_name}":')
                print('-----------------')
                for key, value in gaitResults['scalars_r'].items():
                    rounded_value = round(value['value'], 2)
                    print(f"{key}: {rounded_value} {value['units']}")

                print(f'\nLeft foot gait metrics for session "{session_id}", trial "{trial_name}":')
                print('-----------------')
                for key, value in gaitResults['scalars_l'].items():
                    rounded_value = round(value['value'], 2)
                    print(f"{key}: {rounded_value} {value['units']}")

                save_gait_metrics_to_excel(gaitResults,
                                           os.path.join(self.analysis_folder, f"{session_id}-{trial_name}", f'gait_metrics.xlsx'))

                plot_dataframe_with_shading(
                    {f"{session_id}_{trial_name}": gaitResults},
                    os.path.join(self.analysis_folder, f"{session_id}-{trial_name}"),
                    leg=['r', 'l'],
                    xlabel='% gait cycle',
                    title='kinematics (m or deg)',
                    legend_entries=['right', 'left']
                )

                self.AllGaitResults[f"{session_id}_{trial_name}"] = gaitResults

            except Exception as e:
                print()
                print(f"Error during gait analysis of {session_id}, {trial_name} : {e}")
                continue

        self.plot_and_save_results()

    def plot_and_save_results(self):

        plot_data = plot_dataframe_with_shading(
            self.AllGaitResults,
            self.analysis_folder,
            leg=['r', 'l'],
            xlabel='% gait cycle',
            title='kinematics (m or deg)',
            legend_entries=['right', 'left']
        )

        save_plots_to_excel(plot_data, self.analysis_folder)

    def setup(self):
        self.DataController.set('analysis_folder', modify_output_folder)
        self.DataController.set('sessions_trials', self.modify_sessions_trials)
        self.analysis_folder = self.DataController.get('analysis_folder')
        self.sessions_trials = self.DataController.get('sessions_trials')

    def modify_parameters(self):
        answer = self.get_user_selection("What do you want to modify?", ["Output folder", "Sessions Trials"])

        match answer:
            case "Output folder":
                self.DataController.set('analysis_folder', modify_output_folder)
                self.analysis_folder = self.DataController.get('analysis_folder')
            case "Sessions Trials":
                self.DataController.set('sessions_trials', self.modify_sessions_trials)
                self.sessions_trials = self.DataController.get('sessions_trials')

    def modify_sessions_trials(self):
        ask_sessions = self.get_user_selection(
            message="Do you want to see your sessions or public sessions?",
            choices=["My sessions", "Public sessions", "All sessions", "Manual input"]
        )
        trials = []
        removed = False

        while True:
            if not removed:
                trial = self.handle_trial_selection(ask_sessions)
                if trial:
                    already_in_list = False
                    for t in trials:
                        if t['session_id'] == trial[0] and t['trial_name'] == trial[1]:
                            already_in_list = True
                    if not already_in_list:
                        trials.append({'session_id': trial[0], 'trial_name': trial[1]})
                    else:
                        print("This trial is already in the list.")
                        print()

            print("Current sessions and trials:")
            for trial in trials:
                print(f"{trial['trial_name']} from session {trial['session_id']}")
            print()

            question = self.get_user_selection("What do you want to do?",
                                          ["Add another trial", "Remove a trial", "Continue"])

            if question == "Remove a trial":
                li = [f"{trial['trial_name']} from session {trial['session_id']}" for trial in trials]
                trial_to_remove = self.get_user_selection("Select a trial to remove:", choices=li)
                session_id, trial_name = self.extract_session_info(trial_to_remove)
                trials = [trial for trial in trials
                          if trial['session_id'] != session_id
                          or trial['trial_name'] != trial_name]
                removed = True

            elif question == "Add another trial":
                removed = False
            elif question == "Continue":
                print()
                print("Trials modified successfully.")
                print()
                break

        return trials

    def handle_trial_selection(self, selection):
        if selection == "Manual input":
            session_id = input("Enter the session id: ")
        else:
            sessions = get_sessions(is_public=self.get_public_status(selection))
            selected_session = self.get_user_selection(message="Select a session:", choices=sessions)
            session_id = selected_session.split(" (")[1].split(")")[0]

        selected_trial = self.get_user_selection(message="Select a trial:",
                                            choices=get_trials_names_from_session(session_id))
        print(f"Selected trial: {selected_trial} from session {session_id}")
        print("\n")

        return session_id, selected_trial

    @staticmethod
    def get_public_status(selection):
        if selection == "My sessions":
            return False
        elif selection == "Public sessions":
            return True
        return None

    @staticmethod
    def extract_session_info(session_string):
        try:
            session_id = session_string.split(" from session ")[1]
            trial_name = session_string.split(" from session ")[0]
            return session_id, trial_name
        except IndexError:
            return None, None
