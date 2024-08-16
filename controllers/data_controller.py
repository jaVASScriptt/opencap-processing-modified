import json
import os

import pandas as pd


class DataController:
    def __init__(self, analysis_type):
        self.analysis_type = analysis_type
        self.json_file_path = 'data/parameters.json'  # Chemin fixe vers le fichier JSON
        self.parameters = self.load_parameters()

    def load_parameters(self):
        with open(self.json_file_path, 'r') as file:
            data = json.load(file)
        return data.get(self.analysis_type, {})

    def display(self):
        print()
        print(f"Voici vos paramètres pour {self.analysis_type} :\n")
        for key, value in self.parameters.items():
            if isinstance(value, list):
                if not value:
                    print(f"{key}: []")
                else:
                    print(f"{key}:")
                    for item in value:
                        if isinstance(item, dict):
                            print("  - {")
                            for sub_key, sub_value in item.items():
                                print(f"    {sub_key}: {sub_value}")
                            print("    }")
                        else:
                            print(f"  - {item}")
                print()
            elif isinstance(value, dict):
                print(f"{key}: {{")
                for sub_key, sub_value in value.items():
                    print(f"  {sub_key}: {sub_value}")
                print("}")
                print()
            else:
                print(f"{key}: {value}\n")

    def get(self, key):
        """Récupère la valeur d'un paramètre par sa clé."""
        return self.parameters.get(key, None)

    def set(self, key, new_value):
        """Met à jour la valeur d'un paramètre par une fonction de mise à jour."""
        if key in self.parameters:
            self.parameters[key] = new_value
            self.save_parameters()

    def save_parameters(self):
        """Enregistre les paramètres mis à jour dans le fichier JSON."""
        with open(self.json_file_path, 'r+') as file:
            data = json.load(file)
            data[self.analysis_type] = self.parameters
            file.seek(0)
            json.dump(data, file, indent=4)
            file.truncate()

    def write_parameters_in_excel(self, output_file_path):
        """Écrit les paramètres d'un type d'analyse dans un fichier Excel."""
        df = pd.DataFrame(self.parameters.items(), columns=['Paramètre', 'Valeur'])
        df.to_excel(os.path.join(output_file_path, 'analysis_parameters.xlsx'), index=False)
