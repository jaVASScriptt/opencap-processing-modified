import json


class DataController:
    def __init__(self, analysis_type):
        self.analysis_type = analysis_type
        self.json_file_path = 'Data/parameters.json'  # Chemin fixe vers le fichier JSON
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

    def set(self, key, update_function):
        """Met à jour la valeur d'un paramètre par une fonction de mise à jour."""
        if key in self.parameters:
            new_value = update_function()
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
