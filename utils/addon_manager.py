import os
import json

class AddonManager:
    def __init__(self):
        self.data_dir = "data"
        self.addon_file = os.path.join(self.data_dir, "addons.json")
        self.addons = self._load_addons()

    def _load_addons(self):
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
        
        if os.path.exists(self.addon_file):
            try:
                with open(self.addon_file, 'r') as f:
                    return json.load(f)
            except Exception:
                return {'vanilla': [], 'tbc': [], 'wotlk': []}
        return {'vanilla': [], 'tbc': [], 'wotlk': []}

    def _save_addons(self):
        try:
            with open(self.addon_file, 'w') as f:
                json.dump(self.addons, f, indent=4)
        except Exception as e:
            print(f"Erreur lors de la sauvegarde des addons: {e}")

    def get_addons(self, version):
        return self.addons.get(version, []) 