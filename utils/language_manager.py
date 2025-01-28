import json
import os
import logging

class LanguageManager:
    def __init__(self):
        self.current_language = 'fr'  # Langue par défaut
        self.translations = {
            'fr': {
                'launch_button': 'Lancer {}',
                'game_time': 'Temps joué : {}',
                'options': 'Options',
                'settings': 'Paramètres',
                'addons': "Gestionnaire d'addons",
                'stats': 'Statistiques',
                'save': 'Sauvegarder',
                'cancel': 'Annuler',
                'browse': 'Parcourir',
                'vanilla_title': 'World of Warcraft Vanilla',
                'tbc_title': 'The Burning Crusade',
                'wotlk_title': 'Wrath of the Lich King',
                'path_vanilla': 'Chemin Vanilla (1.12.1):',
                'path_tbc': 'Chemin The Burning Crusade (2.4.3):',
                'path_wotlk': 'Chemin Wrath of the Lich King (3.3.5):',
                'settings_saved': 'Les paramètres ont été sauvegardés avec succès.',
                'error': 'Erreur',
                'game_running': 'Jeu en cours...',
                'open_addons': 'Ouvrir le dossier AddOns',
                'path_not_configured': 'Chemin non configuré pour {}',
                'configure_path': 'Configurer le chemin',
                'language': 'Langue',
                'file': 'Fichier',
                'tools': 'Outils',
                'quit': 'Quitter',
                'select_language': 'Sélectionnez votre langue',
                'launches_count': 'Nombre de lancements : {}',
                'last_used': 'Dernière utilisation : {}',
                'never_used': 'Jamais utilisé',
                'select_executable': "Sélectionner l'exécutable {}",
                'warning': 'Avertissement',
                'instance_warning': 'Une instance du launcher est déjà en cours d\'exécution.',
                'critical_error': 'Erreur critique',
                'error_occurred': 'Une erreur est survenue:',
                'close': 'Fermer',
                'description': 'Description :',
                'time': 'Heure : {}',
                'addon_manager': "Gestionnaire d'addons",
                'game_already_running': 'Le jeu est déjà en cours d\'exécution.',
                'invalid_path': 'Le chemin du jeu n\'est pas configuré ou invalide.\nVeuillez le configurer dans les paramètres.',
                'launch_error': 'Impossible de lancer le jeu:',
                'folder_error': 'Impossible d\'ouvrir le dossier:'
            },
            'en': {
                'launch_button': 'Launch {}',
                'game_time': 'Played time: {}',
                'options': 'Options',
                'settings': 'Settings',
                'addons': 'Addon Manager',
                'stats': 'Statistics',
                'save': 'Save',
                'cancel': 'Cancel',
                'browse': 'Browse',
                'vanilla_title': 'World of Warcraft Vanilla',
                'tbc_title': 'The Burning Crusade',
                'wotlk_title': 'Wrath of the Lich King',
                'path_vanilla': 'Vanilla Path (1.12.1):',
                'path_tbc': 'The Burning Crusade Path (2.4.3):',
                'path_wotlk': 'Wrath of the Lich King Path (3.3.5):',
                'settings_saved': 'Settings have been saved successfully.',
                'error': 'Error',
                'game_running': 'Game running...',
                'open_addons': 'Open AddOns folder',
                'path_not_configured': 'Path not configured for {}',
                'configure_path': 'Configure path',
                'language': 'Language',
                'file': 'File',
                'tools': 'Tools',
                'quit': 'Quit',
                'select_language': 'Select your language',
                'launches_count': 'Launch count: {}',
                'last_used': 'Last used: {}',
                'never_used': 'Never used',
                'select_executable': 'Select {} executable',
                'warning': 'Warning',
                'instance_warning': 'An instance of the launcher is already running.',
                'critical_error': 'Critical Error',
                'error_occurred': 'An error occurred:',
                'close': 'Close',
                'description': 'Description:',
                'time': 'Time: {}',
                'addon_manager': 'Addon Manager',
                'game_already_running': 'The game is already running.',
                'invalid_path': 'Game path is not configured or invalid.\nPlease configure it in settings.',
                'launch_error': 'Unable to launch game:',
                'folder_error': 'Unable to open folder:'
            },
            'es': {
                'launch_button': 'Iniciar {}',
                'game_time': 'Tiempo jugado: {}',
                'options': 'Opciones',
                'settings': 'Configuración',
                'addons': 'Gestor de Addons',
                'stats': 'Estadísticas',
                'save': 'Guardar',
                'cancel': 'Cancelar',
                'browse': 'Examinar',
                'path_vanilla': 'Ruta Vanilla (1.12.1):',
                'path_tbc': 'Ruta The Burning Crusade (2.4.3):',
                'path_wotlk': 'Ruta Wrath of the Lich King (3.3.5):',
                'settings_saved': 'La configuración se ha guardado correctamente.',
                'error': 'Error',
                'game_running': 'Juego en curso...',
                'open_addons': 'Abrir carpeta de AddOns',
                'path_not_configured': 'Ruta no configurada para {}',
                'configure_path': 'Configurar ruta',
                'language': 'Idioma',
                'file': 'Archivo',
                'tools': 'Herramientas',
                'quit': 'Salir',
                'select_language': 'Seleccione su idioma',
                'launches_count': 'Número de inicios: {}',
                'last_used': 'Último uso: {}',
                'never_used': 'Nunca usado',
                'select_executable': 'Seleccionar ejecutable de {}',
                'warning': 'Advertencia',
                'instance_warning': 'Ya se está ejecutando una instancia del launcher.',
                'critical_error': 'Error Crítico',
                'error_occurred': 'Ha ocurrido un error:',
                'close': 'Cerrar',
                'description': 'Descripción:',
                'time': 'Hora: {}',
                'addon_manager': 'Gestor de Addons',
                'game_already_running': 'El juego ya está en ejecución.',
                'invalid_path': 'La ruta del juego no está configurada o es inválida.\nPor favor, configúrela en los ajustes.',
                'launch_error': 'No se puede iniciar el juego:',
                'folder_error': 'No se puede abrir la carpeta:'
            },
            'de': {
                'launch_button': 'Starten {}',
                'game_time': 'Spielzeit: {}',
                'options': 'Optionen',
                'settings': 'Einstellungen',
                'addons': 'Addon-Manager',
                'stats': 'Statistiken',
                'save': 'Speichern',
                'cancel': 'Abbrechen',
                'browse': 'Durchsuchen',
                'path_vanilla': 'Vanilla-Pfad (1.12.1):',
                'path_tbc': 'The Burning Crusade-Pfad (2.4.3):',
                'path_wotlk': 'Wrath of the Lich King-Pfad (3.3.5):',
                'settings_saved': 'Einstellungen wurden erfolgreich gespeichert.',
                'error': 'Fehler',
                'game_running': 'Spiel läuft...',
                'open_addons': 'AddOns-Ordner öffnen',
                'path_not_configured': 'Pfad nicht konfiguriert für {}',
                'configure_path': 'Pfad konfigurieren',
                'language': 'Sprache',
                'file': 'Datei',
                'tools': 'Werkzeuge',
                'quit': 'Beenden',
                'select_language': 'Wählen Sie Ihre Sprache',
                'launches_count': 'Anzahl der Starts: {}',
                'last_used': 'Zuletzt verwendet: {}',
                'never_used': 'Nie verwendet',
                'select_executable': 'Wählen Sie die {}-Ausführungsdatei',
                'warning': 'Warnung',
                'instance_warning': 'Eine Instanz des Launchers läuft bereits.',
                'critical_error': 'Kritischer Fehler',
                'error_occurred': 'Ein Fehler ist aufgetreten:',
                'close': 'Schließen',
                'description': 'Beschreibung:',
                'time': 'Zeit: {}',
                'addon_manager': 'Addon-Manager',
                'game_already_running': 'Das Spiel läuft bereits.',
                'invalid_path': 'Spielpfad ist nicht konfiguriert oder ungültig.\nBitte konfigurieren Sie ihn in den Einstellungen.',
                'launch_error': 'Spiel kann nicht gestartet werden:',
                'folder_error': 'Ordner kann nicht geöffnet werden:'
            },
            'pt': {
                'launch_button': 'Iniciar {}',
                'game_time': 'Tempo jogado: {}',
                'options': 'Opções',
                'settings': 'Configurações',
                'addons': 'Gerenciador de Addons',
                'stats': 'Estatísticas',
                'save': 'Salvar',
                'cancel': 'Cancelar',
                'browse': 'Procurar',
                'path_vanilla': 'Caminho Vanilla (1.12.1):',
                'path_tbc': 'Caminho The Burning Crusade (2.4.3):',
                'path_wotlk': 'Caminho Wrath of the Lich King (3.3.5):',
                'settings_saved': 'Configurações foram salvas com sucesso.',
                'error': 'Erro',
                'game_running': 'Jogo em execução...',
                'open_addons': 'Abrir pasta de AddOns',
                'path_not_configured': 'Caminho não configurado para {}',
                'configure_path': 'Configurar caminho',
                'language': 'Idioma',
                'file': 'Arquivo',
                'tools': 'Ferramentas',
                'quit': 'Sair',
                'select_language': 'Selecione seu idioma',
                'launches_count': 'Número de inicializações: {}',
                'last_used': 'Último uso: {}',
                'never_used': 'Nunca usado',
                'select_executable': 'Selecionar executável {}',
                'warning': 'Aviso',
                'instance_warning': 'Uma instância do launcher já está em execução.',
                'critical_error': 'Erro Crítico',
                'error_occurred': 'Ocorreu um erro:',
                'close': 'Fechar',
                'description': 'Descrição:',
                'time': 'Hora: {}',
                'addon_manager': 'Gerenciador de Addons',
                'game_already_running': 'O jogo já está em execução.',
                'invalid_path': 'O caminho do jogo não está configurado ou é inválido.\nPor favor, configure nas configurações.',
                'launch_error': 'Não foi possível iniciar o jogo:',
                'folder_error': 'Não foi possível abrir a pasta:'
            }
        }
        self.load_language()

    def load_language(self):
        """Charge la langue depuis le fichier de configuration."""
        try:
            if os.path.exists('data/config.json'):
                with open('data/config.json', 'r') as f:
                    config = json.load(f)
                    if 'language' in config:
                        self.current_language = config['language']
            else:
                self.save_language()  # Crée le fichier avec la langue par défaut
        except Exception as e:
            logging.error(f"Erreur lors du chargement de la langue: {e}")

    def save_language(self):
        """Sauvegarde la langue dans le fichier de configuration."""
        try:
            config = {}
            if os.path.exists('data/config.json'):
                with open('data/config.json', 'r') as f:
                    config = json.load(f)
            
            config['language'] = self.current_language
            
            with open('data/config.json', 'w') as f:
                json.dump(config, f, indent=4)
        except Exception as e:
            logging.error(f"Erreur lors de la sauvegarde de la langue: {e}")

    def get_text(self, key, *args):
        """Récupère le texte traduit pour la clé donnée."""
        try:
            text = self.translations[self.current_language].get(key, key)
            if args:
                return text.format(*args)
            return text
        except Exception as e:
            logging.error(f"Erreur lors de la récupération du texte traduit: {e}")
            return key

    def set_language(self, language):
        """Change la langue courante."""
        if language in self.translations:
            self.current_language = language
            self.save_language()

    def get_available_languages(self):
        """Retourne un dictionnaire des langues disponibles."""
        return {
            'fr': 'Français',
            'en': 'English',
            'es': 'Español',
            'de': 'Deutsch',
            'pt': 'Português'
        } 