from ActivityAnalyses.gait_analysis import GaitAnalysis
from Controllers.analysis_utils import menu_analysis
from Utils.utils_plotting import plot_dataframe_with_shading, save_plots_to_excel, save_gait_metrics_to_excel
from Utils.utils import *
import os
import sys


class GaitAnalysisController:

    def __init__(self):

        self.analysis_folder = r"C:\Users\NNL_L\OneDrive\Documents\Tests"
        sys.path.append("../")
        sys.path.append("../ActivityAnalyses")

        # Paths
        self.baseDir = os.path.join(os.getcwd(), '..')
        self.dataFolder = os.path.join(self.baseDir, 'Data')

        # User-defined variables
        self.sessions_trials = [
            {'session_id': '1ef87bb0-774c-48f2-b1ff-61c008fffc3a', 'trial_name': 'marche'},
            {'session_id': 'b68b4507-edd3-44b3-9d1e-206dd784379a', 'trial_name': '6M_retour_course'},
            {'session_id': 'f726c45f-7db3-48ad-a22a-d7b491e23b30', 'trial_name': 'marchehigh2'}
        ]

        self.scalar_names = {'gait_speed', 'stride_length', 'step_width', 'cadence',
                             'single_support_time', 'double_support_time', 'step_length_symmetry'}

        self.n_gait_cycles = -1
        self.filter_frequency = 6
        self.AllGaitResults = {}

    def menu(self):
        menu_analysis(self)

    def start_analysis(self):

        question = "Here are all the settings you've configured:\n" \
                   "\n" \
                   "Sessions and trials:\n" \
                   + "\n".join(
            [f"Session {i + 1}: {self.sessions_trials[i]['session_id']} - {self.sessions_trials[i]['trial_name']}"
             for i in range(len(self.sessions_trials))]) + "\n" \
                                                           "\n" \
                                                           f"Results folder: {self.analysis_folder}\n" \
                                                           "\n" \
                                                           "Do you want to proceed with these settings?"

        if get_user_selection(question, ["Yes", "No"]) == "No":
            return

        sentence = "Please enter a name for the analysis : "

        analysis_name = inquirer.text(
            message=sentence,
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

            save_gait_metrics_to_excel(gaitResults, os.path.join(self.analysis_folder, f"{session_id}-{trial_name}",
                                                                 f'gait_metrics.xlsx'))

            plot_dataframe_with_shading(
                {f"{session_id}_{trial_name}": gaitResults},
                os.path.join(self.analysis_folder, f"{session_id}-{trial_name}"),
                leg=['r', 'l'],
                xlabel='% gait cycle',
                title='kinematics (m or deg)',
                legend_entries=['right', 'left']
            )

            self.AllGaitResults[f"{session_id}_{trial_name}"] = gaitResults
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
