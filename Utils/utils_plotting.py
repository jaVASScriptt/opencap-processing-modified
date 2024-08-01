'''
    ---------------------------------------------------------------------------
    OpenCap processing: utils_plotting.py
    ---------------------------------------------------------------------------

    Copyright 2022 Stanford University and the Authors
    
    Author(s): Antoine Falisse, Scott Uhlrich
    
    Licensed under the Apache License, Version 2.0 (the "License"); you may not
    use this file except in compliance with the License. You may obtain a copy
    of the License at http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
'''
import os
import pandas as pd

import numpy as np
import matplotlib.pyplot as plt


def plot_dataframe(dataframes, x=None, y=[], xlabel=None, ylabel=None,
                   labels=None, title=None, xrange=None):
    # Handle case specific number of subplots.
    if not x and not y:
        nRow = int(np.ceil(np.sqrt(dataframes[0].shape[1] - 1)))
        nCol = int(np.ceil(np.sqrt(dataframes[0].shape[1] - 1)))
        if not xlabel:
            xlabel = list(dataframes[0].columns)[0]
        x = 'time'
        y = list(dataframes[0].columns)[1:]
    elif not x and y:
        nRow = int(np.ceil(np.sqrt(len(y))))
        nCol = int(np.ceil(np.sqrt(len(y))))
        if not xlabel:
            xlabel = list(dataframes[0].columns)[0]
        x = 'time'
    else:
        nRow = int(np.ceil(np.sqrt(len(y))))
        nCol = int(np.ceil(np.sqrt(len(y))))
        if not xlabel:
            xlabel = x
        if not ylabel:
            ylabel = y[0]
    if nRow >= len(y):
        nRow = 1
    nAxs = len(y)

    # Labels for legend.
    if not labels:
        labels = ['dataframe_' + str(i) for i in range(len(dataframes))]
    elif len(labels) != len(dataframes):
        print(
            "WARNING: The number of labels ({}) does not match the number of input dataframes ({})".format(len(labels),
                                                                                                           len(dataframes)))
        labels = ['dataframe_' + str(i) for i in range(dataframes)]

    if nCol == 1:  # Single plot.
        fig = plt.figure()
        color = iter(plt.cm.rainbow(np.linspace(0, 1, len(dataframes))))
        for c, dataframe in enumerate(dataframes):
            c_color = next(color)
            plt.plot(dataframe[x], dataframe[y], c=c_color, label=labels[c])
            if xrange is not None:
                plt.xlim(xrange)
    else:  # Multiple subplots.
        fig, axs = plt.subplots(nRow, nCol, sharex=True)
        for i, ax in enumerate(axs.flat):
            color = iter(plt.cm.rainbow(np.linspace(0, 1, len(dataframes))))
            if i < nAxs:
                for c, dataframe in enumerate(dataframes):
                    c_color = next(color)
                    ax.plot(dataframe[x], dataframe[y[i]], c=c_color, label=labels[c])
                    ax.set_title(y[i])
                    if xrange is not None:
                        plt.xlim(xrange)
            if i == 0:
                handles, labels = ax.get_legend_handles_labels()

    # Axis labels and legend.
    if nRow > 1 and nCol > 1:
        plt.setp(axs[-1, :], xlabel=xlabel)
        plt.setp(axs[:, 0], ylabel=ylabel)
        axs[0][0].legend(handles, labels)
    elif nRow == 1 and nCol > 1:
        plt.setp(axs[:, ], xlabel=xlabel)
        plt.setp(axs[0,], ylabel=ylabel)
        axs[0,].legend(handles, labels)
    else:
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.legend(labels)

    if nRow == 1 and nCol == 1:
        # Add figure title.
        if title:
            plt.title(title)
    else:
        # Add figure title.
        if title:
            fig.suptitle(title)
        # Align labels.        
        fig.align_ylabels()
        # Hidde empty subplots.
        nEmptySubplots = (nRow * nCol) - len(y)
        axs_flat = axs.flat
        for ax in (axs_flat[len(axs_flat) - nEmptySubplots:]):
            ax.set_visible(False)

    # Tight layout (should make figure big enough first).
    # fig.tight_layout()

    # Show plot (needed if running through terminal).
    plt.show()


def plot_dataframe_with_shading(AllGaitResults, analysis_folder, leg=None, xlabel=None, title=None,
                                legend_entries=None):
    # Initialiser le dictionnaire pour les données de tracé
    plot_data = {}

    # Déterminer les jambes (r ou l) en fonction des données
    legs = leg or ['r', 'l']

    # Couleurs distinctes pour chaque essai
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22',
              '#17becf']

    combined_data_right = {}
    combined_data_left = {}

    # Traiter chaque essai
    for trial_idx, trial_key in enumerate(AllGaitResults):
        session_id, trial_name = trial_key.split('_', 1)

        # Initialiser les dictionnaires pour les données de tracé
        plot_data_right = {}
        plot_data_left = {}

        # Extraire les données spécifiques au nom de scénario
        mean_dataframe_r = AllGaitResults[trial_key]['curves_r']['mean']
        sd_dataframe_r = AllGaitResults[trial_key]['curves_r']['sd']
        mean_dataframe_l = AllGaitResults[trial_key]['curves_l']['mean']
        sd_dataframe_l = AllGaitResults[trial_key]['curves_l']['sd']

        mean_dataframe = [mean_dataframe_r, mean_dataframe_l]
        sd_dataframe = [sd_dataframe_r, sd_dataframe_l]

        columns = [col for col in mean_dataframe[0].columns if col not in ['time', '_beta', 'mtp']]

        if legs[0] == 'r':
            columns = [col for col in columns if not col.endswith('_l')]
        elif legs[0] == 'l':
            columns = [col for col in columns if not col.endswith('_r')]

        # Accumuler les données pour chaque colonne
        for column in columns:
            if column not in combined_data_right:
                combined_data_right[column] = []
                combined_data_left[column] = []

            for j, (mean_df, sd_df) in enumerate(zip(mean_dataframe, sd_dataframe)):
                col = column[:-2] + '_' + legs[j] if (
                        legs and (column.endswith('_r') or column.endswith('_l'))) else column
                if col not in mean_df.columns:
                    continue

                # Calculer la durée totale et normaliser le temps en pourcentage
                total_time = mean_df['time'].max()
                min_time = mean_df['time'].min()
                time_percentage = 100 * (mean_df['time'] - min_time) / (total_time - min_time)

                mean_values = mean_df[col]

                if legs[j] == 'r':
                    combined_data_right[column].append(
                        (mean_df['time'], time_percentage, mean_values, trial_name, colors[trial_idx]))
                    plot_data_right[column] = (mean_df['time'], time_percentage, mean_values)
                else:
                    combined_data_left[column].append(
                        (mean_df['time'], time_percentage, mean_values, trial_name, colors[trial_idx]))
                    plot_data_left[column] = (mean_df['time'], time_percentage, mean_values)

        # Ajouter les données au dictionnaire de résultats
        plot_data[trial_key] = [plot_data_right, plot_data_left]

    # Créer un seul graphique
    num_columns = len(columns)
    num_rows = (num_columns + 3) // 4

    fig, axes = plt.subplots(num_rows, 4, figsize=(12, 8))
    axes = axes.flatten()

    # Accumulateur pour les handles et labels de la légende
    handles = []
    labels = []

    for i, column in enumerate(columns):
        row, col_idx = divmod(i, 4)
        ax = axes[i]

        # Afficher les données de la jambe droite
        for time, time_percentage, mean_values, trial_name, color in combined_data_right[column]:
            line, = ax.plot(time_percentage, mean_values, color=color, label=f'{trial_name} (right)')
            if f'{trial_name} (right)' not in labels:
                handles.append(line)
                labels.append(f'{trial_name} (right)')

        # Afficher les données de la jambe gauche
        for time, time_percentage, mean_values, trial_name, color in combined_data_left[column]:
            line, = ax.plot(time_percentage, mean_values, color=color, linestyle='--', label=f'{trial_name} (left)')
            if f'{trial_name} (left)' not in labels:
                handles.append(line)
                labels.append(f'{trial_name} (left)')

        ax.set_xlabel(xlabel if row == num_rows - 1 else None, fontsize=12)
        ax.set_ylabel(column, fontsize=12)
        ax.tick_params(axis='both', which='major', labelsize=10)

    for i in range(num_columns, num_rows * 4):
        fig.delaxes(axes[i])

    if title:
        fig.suptitle(title)

    # Afficher la légende une seule fois en bas à droite
    fig.legend(handles, labels, loc='lower right', fontsize=8)

    plt.tight_layout()
    plt.show()

    plt.savefig(os.path.join(analysis_folder, f"plot.png"), dpi=300)

    print("")
    print("Plot saved as 'plot.png'.")
    print("")

    return plot_data


def save_plots_to_excel(plot_data, analysis_folder):
    # Crée le dossier principal 'results_excels' s'il n'existe pas
    if not os.path.exists('results_excels'):
        os.makedirs('results_excels')

    for trial_key, data_list in plot_data.items():
        session_id, trial_name = trial_key.split('_', 1)
        trial_dir = os.path.join(analysis_folder, f"{session_id}-{trial_name}")

        # Crée un sous-dossier pour chaque essai s'il n'existe pas
        if not os.path.exists(trial_dir):
            os.makedirs(trial_dir)

        # On suppose qu'il y a deux éléments dans data_list: [plot_data_right, plot_data_left]
        plot_data_right, plot_data_left = data_list

        # Enregistre les fichiers Excel dans le sous-dossier correspondant
        for plot_data, suffix in zip([plot_data_right, plot_data_left], ['right', 'left']):
            filename = os.path.join(trial_dir, f'plots_{suffix}.xlsx')
            with pd.ExcelWriter(filename, engine='xlsxwriter') as writer:
                df = pd.DataFrame()

                # Ajoute toutes les colonnes de données à une seule feuille
                for column, data in plot_data.items():
                    time, time_percentage, values = data

                    # Crée des colonnes pour le temps absolu et le pourcentage
                    df['time'] = time
                    df['percent trial'] = time_percentage
                    df[column] = values

                # Écriture des données dans une seule feuille Excel
                df.to_excel(writer, sheet_name='Sheet1', index=False)

    print("")
    print(f"Excel files saved in 'results_excels' folder.")
    print("")


def save_gait_metrics_to_excel(gaitResults, filename):
    # Créer un DataFrame pour les métriques du pied droit

    parent = os.path.dirname(filename)
    if not os.path.exists(parent):
        os.makedirs(parent)

    right_metrics = {
        'Metric': [],
        'Value': [],
        'Units': []
    }
    for key, value in gaitResults['scalars_r'].items():
        right_metrics['Metric'].append(key)
        right_metrics['Value'].append(round(value['value'], 2))
        right_metrics['Units'].append(value['units'])

    df_right = pd.DataFrame(right_metrics)

    # Créer un DataFrame pour les métriques du pied gauche
    left_metrics = {
        'Metric': [],
        'Value': [],
        'Units': []
    }
    for key, value in gaitResults['scalars_l'].items():
        left_metrics['Metric'].append(key)
        left_metrics['Value'].append(round(value['value'], 2))
        left_metrics['Units'].append(value['units'])

    df_left = pd.DataFrame(left_metrics)

    # Enregistrer les DataFrames dans un fichier Excel
    with pd.ExcelWriter(filename) as writer:
        df_right.to_excel(writer, sheet_name='Right Foot Metrics', index=False)
        df_left.to_excel(writer, sheet_name='Left Foot Metrics', index=False)

    print("")
    print(f"Gait metrics saved to {filename}")
