import os
import json

class SettingsManager:
    def __init__(self):
        self.data_dir = "data"
        self.settings_file = os.path.join(self.data_dir, "settings.json")
        self.settings = self._load_settings()

    def _load_settings(self):
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
        
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r') as f:
                    return json.load(f)
            except Exception:
                return {'paths': {'vanilla': '', 'tbc': '', 'wotlk': ''}}
        return {'paths': {'vanilla': '', 'tbc': '', 'wotlk': ''}}

    def save_settings(self):
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f, indent=4)
        except Exception as e:
            print(f"Erreur lors de la sauvegarde des paramètres: {e}")

    def get_path(self, version):
        return self.settings['paths'].get(version, '')

    def set_path(self, version, path):
        if 'paths' not in self.settings:
            self.settings['paths'] = {}
        self.settings['paths'][version] = path
        self.save_settings() 