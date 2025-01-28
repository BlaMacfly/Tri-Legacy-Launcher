import os
import json
import logging
from datetime import datetime
from typing import Dict, Optional, Union
import sys

# Constantes
SUPPORTED_VERSIONS = {'vanilla', 'tbc', 'wotlk'}
DEFAULT_DATA_STRUCTURE = {
    'times': {version: 0 for version in SUPPORTED_VERSIONS},
    'last_used': {version: None for version in SUPPORTED_VERSIONS},
    'launches': {version: 0 for version in SUPPORTED_VERSIONS}
}

class GameTimeTracker:
    """
    Gère le suivi du temps de jeu pour différentes versions de World of Warcraft.
    
    Attributes:
        data_file (str): Nom du fichier de données
        data (dict): Données de temps de jeu
    """
    
    def __init__(self, data_file: str = "game_time.json"):
        """
        Initialise le tracker de temps de jeu.
        
        Args:
            data_file (str): Nom du fichier de données
        """
        # Déterminer le chemin de base selon que l'application est compilée ou non
        if getattr(sys, 'frozen', False):
            base_path = os.path.dirname(sys.executable)
        else:
            base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        self.data_dir = os.path.join(base_path, "data")
        self.data_file = os.path.join(self.data_dir, data_file)
        self.data = self.load_data()
        logging.info(f"GameTimeTracker initialisé avec le fichier: {self.data_file}")
        for version, time in self.data['times'].items():
            logging.info(f"{version}: {time}s")

    def _validate_version(self, version: str) -> bool:
        """
        Vérifie si la version est supportée.
        
        Args:
            version (str): Version à vérifier
            
        Returns:
            bool: True si la version est valide
        """
        if version not in SUPPORTED_VERSIONS:
            logging.error(f"Version non supportée: {version}")
            return False
        return True

    def _validate_data_structure(self, data: Dict) -> bool:
        """
        Vérifie si la structure des données est valide.
        
        Args:
            data (dict): Données à vérifier
            
        Returns:
            bool: True si la structure est valide
        """
        return (isinstance(data, dict) and 
                all(key in data for key in ['times', 'last_used', 'launches']) and
                all(version in data['times'] for version in SUPPORTED_VERSIONS) and
                all(version in data['last_used'] for version in SUPPORTED_VERSIONS) and
                all(version in data['launches'] for version in SUPPORTED_VERSIONS))

    def increment_launches(self, version: str) -> bool:
        """
        Incrémente le compteur de lancements pour une version.
        
        Args:
            version (str): Version du jeu
            
        Returns:
            bool: True si l'incrémentation a réussi
        """
        try:
            if not self._validate_version(version):
                return False
            
            if 'launches' not in self.data:
                self.data['launches'] = {v: 0 for v in SUPPORTED_VERSIONS}
            
            self.data['launches'][version] += 1
            logging.info(f"Lancement incrémenté pour {version}: total={self.data['launches'][version]}")
            self.save_data()
            return True
        except Exception as e:
            logging.error(f"Erreur lors de l'incrémentation des lancements pour {version}: {e}")
            return False

    def load_data(self) -> Dict:
        """
        Charge les données depuis le fichier.
        
        Returns:
            dict: Données chargées ou structure par défaut
        """
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                    logging.info(f"Données chargées depuis {self.data_file}")
                    if self._validate_data_structure(data):
                        return data
                    logging.warning("Structure de données invalide, utilisation de la structure par défaut")
            else:
                logging.info(f"Fichier {self.data_file} non trouvé, création de nouvelles données")
            return DEFAULT_DATA_STRUCTURE.copy()
        except Exception as e:
            logging.error(f"Erreur lors du chargement des données de temps de jeu : {e}")
            return DEFAULT_DATA_STRUCTURE.copy()

    def save_data(self) -> None:
        """Sauvegarde les données dans le fichier."""
        try:
            os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
            with open(self.data_file, 'w') as f:
                json.dump(self.data, f, indent=4)
            logging.info(f"Données sauvegardées dans {self.data_file}:")
            for version, time in self.data['times'].items():
                logging.info(f"{version}: {time}s, lancements: {self.data['launches'][version]}")
        except Exception as e:
            logging.error(f"Erreur lors de la sauvegarde des données de temps de jeu : {e}")

    def increment_time(self, version: str, seconds: Union[int, float]) -> bool:
        """
        Incrémente le temps de jeu pour une version.
        
        Args:
            version (str): Version du jeu
            seconds (Union[int, float]): Nombre de secondes à ajouter
            
        Returns:
            bool: True si l'incrémentation a réussi
        """
        try:
            if not self._validate_version(version) or not isinstance(seconds, (int, float)) or seconds <= 0:
                return False
                
            self.data['times'][version] += int(seconds)
            self.data['last_used'][version] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.save_data()
            return True
        except Exception as e:
            logging.error(f"Erreur lors de l'incrémentation du temps pour {version}: {e}")
            return False

    def get_time(self, version: str) -> int:
        """
        Récupère le temps total pour une version.
        
        Args:
            version (str): Version du jeu
            
        Returns:
            int: Temps total en secondes
        """
        try:
            if not self._validate_version(version):
                return 0
            return self.data['times'].get(version, 0)
        except Exception as e:
            logging.error(f"Erreur lors de la récupération du temps pour {version}: {e}")
            return 0

    def get_launches(self, version: str) -> int:
        """
        Récupère le nombre de lancements pour une version.
        
        Args:
            version (str): Version du jeu
            
        Returns:
            int: Nombre de lancements
        """
        try:
            if not self._validate_version(version):
                return 0
            return self.data.get('launches', {}).get(version, 0)
        except Exception as e:
            logging.error(f"Erreur lors de la récupération des lancements pour {version}: {e}")
            return 0

    def get_last_used(self, version: str) -> Optional[str]:
        """
        Récupère la dernière date d'utilisation pour une version.
        
        Args:
            version (str): Version du jeu
            
        Returns:
            Optional[str]: Date de dernière utilisation ou None
        """
        try:
            if not self._validate_version(version):
                return None
            return self.data['last_used'].get(version)
        except Exception as e:
            logging.error(f"Erreur lors de la récupération de la dernière utilisation pour {version}: {e}")
            return None

    def get_formatted_time(self, version: str) -> str:
        """
        Récupère le temps formaté pour une version.
        
        Args:
            version (str): Version du jeu
            
        Returns:
            str: Temps formaté (ex: "2h 30min")
        """
        try:
            if not self._validate_version(version):
                return "0h 0min"
            seconds = abs(int(self.get_time(version)))
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            formatted = f"{hours}h {minutes}min"
            logging.info(f"Temps formaté pour {version}: {formatted}")
            return formatted
        except Exception as e:
            logging.error(f"Erreur lors du formatage du temps pour {version}: {e}")
            return "0h 0min" 