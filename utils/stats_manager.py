import os
import json
from datetime import datetime

class StatsManager:
    def __init__(self):
        self.data_dir = "data"
        self.stats_file = os.path.join(self.data_dir, "stats.json")
        self.stats = self._load_stats()

    def _load_stats(self):
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
        
        if os.path.exists(self.stats_file):
            try:
                with open(self.stats_file, 'r') as f:
                    return json.load(f)
            except Exception:
                return {'vanilla': {}, 'tbc': {}, 'wotlk': {}}
        return {'vanilla': {}, 'tbc': {}, 'wotlk': {}}

    def _save_stats(self):
        try:
            with open(self.stats_file, 'w') as f:
                json.dump(self.stats, f, indent=4)
        except Exception as e:
            print(f"Erreur lors de la sauvegarde des statistiques: {e}")

    def get_stats(self, version):
        return self.stats.get(version, {})

    def update_stats(self, version, session_time):
        if version not in self.stats:
            self.stats[version] = {
                'sessions': 0,
                'last_session': None,
                'total_time': 0
            }
        
        self.stats[version]['sessions'] = self.stats[version].get('sessions', 0) + 1
        self.stats[version]['last_session'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.stats[version]['total_time'] = self.stats[version].get('total_time', 0) + session_time
        self._save_stats()

    def get_launches(self, version):
        """Retourne le nombre de lancements pour une version donnée"""
        stats = self.get_stats(version)
        return stats.get('sessions', 0)

    def get_last_used(self, version):
        """Retourne la date de dernière utilisation pour une version donnée"""
        stats = self.get_stats(version)
        return stats.get('last_session', None)

    def get_total_time(self, version):
        """Retourne le temps total de jeu pour une version donnée"""
        stats = self.get_stats(version)
        return stats.get('total_time', 0) 