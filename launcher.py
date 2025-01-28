import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import subprocess
import threading
import time
import os
from PIL import Image, ImageTk
import pygame
import sys
import psutil
import json
import logging
from datetime import datetime, timedelta
import shutil
from utils import (
    GameTimeTracker, 
    SettingsManager, 
    StatsManager, 
    AddonManager,
    BackgroundTracker,
    LanguageManager,
    is_wow_running
)

class SoundManager:
    def __init__(self):
        self.sounds = {}
        try:
            if getattr(sys, 'frozen', False):
                base_path = sys._MEIPASS
            else:
                base_path = os.path.dirname(os.path.abspath(__file__))

            sound_files = {
                'toggle': os.path.join(base_path, 'Sounds', 'toggle.mp3'),
                'launch': os.path.join(base_path, 'Sounds', 'launch.mp3')
            }

            for sound_name, sound_path in sound_files.items():
                if os.path.exists(sound_path):
                    self.sounds[sound_name] = sound_path
        except Exception as e:
            print(f"Erreur lors de l'initialisation du gestionnaire de sons: {e}")

    def play(self, sound_name):
        try:
            if sound_name in self.sounds:
                sound = pygame.mixer.Sound(self.sounds[sound_name])
                sound.play()
        except Exception as e:
            print(f"Erreur lors de la lecture du son {sound_name}: {e}")

class EventNotification(tk.Toplevel):
    def __init__(self, parent, title, time, description=None, version=None):
        super().__init__(parent)
        
        # Configuration de base de la fenêtre
        self.title(f"Tri-Legacy - {parent.language_manager.get_text('notification')}")
        self.geometry("400x250")
        self.configure(bg=parent.colors['frame_bg'])
        
        # Rendre la fenêtre non redimensionnable et toujours au premier plan
        self.resizable(False, False)
        self.attributes('-topmost', True)
        
        # Centrer la fenêtre
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'+{x}+{y}')
        
        # Frame principal
        main_frame = tk.Frame(self, bg=parent.colors['frame_bg'], padx=20, pady=20)
        main_frame.pack(fill='both', expand=True)
        
        # Version (si disponible)
        if version:
            version_label = tk.Label(main_frame,
                                   text=f"Version: {version.upper()}",
                                   font=('Morpheus', 12),
                                   bg=parent.colors['frame_bg'],
                                   fg=parent.colors['gold'])
            version_label.pack(pady=(0, 10))
        
        # Titre de l'événement
        title_label = tk.Label(main_frame,
                             text=title,
                             font=('Morpheus', 14, 'bold'),
                             bg=parent.colors['frame_bg'],
                             fg=parent.colors['text'],
                             wraplength=350)
        title_label.pack(pady=(0, 10))
        
        # Heure de l'événement
        time_label = tk.Label(main_frame,
                            text=parent.language_manager.get_text('time', time),
                            font=('Morpheus', 12),
                            bg=parent.colors['frame_bg'],
                            fg=parent.colors['text'])
        time_label.pack(pady=(0, 10))
        
        # Description (si disponible)
        if description:
            desc_label = tk.Label(main_frame,
                                text=description,
                                font=('Morpheus', 10),
                                bg=parent.colors['frame_bg'],
                                fg=parent.colors['text'],
                                wraplength=350)
            desc_label.pack(pady=(0, 10))
        
        # Bouton de fermeture
        close_button = tk.Button(main_frame,
                               text=parent.language_manager.get_text('close'),
                               command=self.destroy,
                               font=('Morpheus', 10),
                               bg=parent.colors['button_bg'],
                               fg=parent.colors['text'],
                               activebackground=parent.colors['button_active_bg'],
                               activeforeground=parent.colors['text'])
        close_button.pack(pady=(10, 0))

class NotificationWindow:
    def __init__(self, parent, title, event_data, colors):
        self.window = tk.Toplevel(parent)
        self.window.title(f"Tri-Legacy - {parent.language_manager.get_text('notification')}")
        self.window.geometry("400x300")
        self.window.configure(bg=colors['frame_bg'])
        
        # Rendre la fenêtre non redimensionnable
        self.window.resizable(False, False)
        
        # Toujours au premier plan
        self.window.attributes('-topmost', True)
        
        # Frame principal avec marge
        main_frame = tk.Frame(self.window, bg=colors['frame_bg'])
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Titre de l'événement
        title_label = tk.Label(main_frame,
                             text=event_data['title'],
                             font=('Morpheus', 14, 'bold'),
                             bg=colors['frame_bg'],
                             fg=colors['gold'],
                             wraplength=350)
        title_label.pack(pady=(0, 10))
        
        # Heure de l'événement
        time_label = tk.Label(main_frame,
                            text=parent.language_manager.get_text('time', event_data['time']),
                            font=('Morpheus', 12),
                            bg=colors['frame_bg'],
                            fg=colors['text'])
        time_label.pack(pady=5)
        
        # Description (si disponible)
        if 'description' in event_data and event_data['description'].strip():
            desc_frame = tk.Frame(main_frame, bg=colors['frame_bg'])
            desc_frame.pack(fill='both', expand=True, pady=10)
            
            desc_label = tk.Label(desc_frame,
                                text=parent.language_manager.get_text('description'),
                                font=('Morpheus', 12, 'bold'),
                                bg=colors['frame_bg'],
                                fg=colors['gold'])
            desc_label.pack(anchor='w')
            
            desc_text = tk.Label(desc_frame,
                               text=event_data['description'],
                               font=('Morpheus', 10),
                               bg=colors['frame_bg'],
                               fg=colors['text'],
                               justify=tk.LEFT,
                               wraplength=350)
            desc_text.pack(fill='both', expand=True)
        
        # Bouton pour fermer
        close_button = tk.Button(main_frame,
                               text=parent.language_manager.get_text('close'),
                               command=self.window.destroy,
                               bg=colors['button_bg'],
                               fg=colors['gold'],
                               activebackground=colors['button_hover'],
                               activeforeground=colors['gold'],
                               font=('Morpheus', 10))
        close_button.pack(pady=10)
        
        # Centrer la fenêtre sur l'écran
        self.center_window()
        
        # Auto-destruction après 30 secondes
        self.window.after(30000, self.window.destroy)
    
    def center_window(self):
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() - width) // 2
        y = (self.window.winfo_screenheight() - height) // 2
        self.window.geometry(f"+{x}+{y}")

def check_single_instance():
    try:
        current_pid = os.getpid()
        for proc in psutil.process_iter(['name', 'pid']):
            try:
                if proc.info['name'] == 'Tri-Legacy Launcher.exe' and proc.pid != current_pid:
                    try:
                        old_process = psutil.Process(proc.pid)
                        old_process.terminate()
                        old_process.wait(timeout=3)
                    except (psutil.NoSuchProcess, psutil.TimeoutExpired):
                        pass
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return True
    except Exception as e:
        logging.error(f"Erreur lors de la vérification d'instance unique: {e}")
        return False

def ensure_required_folders():
    """Vérifie et crée les dossiers requis pour l'application et copie les fichiers nécessaires."""
    required_folders = ['assets', 'data', 'Sounds']
    base_path = os.path.dirname(os.path.abspath(__file__)) if not getattr(sys, 'frozen', False) else os.path.dirname(sys.executable)
    
    for folder in required_folders:
        folder_path = os.path.join(base_path, folder)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
            logging.info(f"Dossier créé : {folder_path}")
    
    # Copier les sons par défaut
    default_sounds = {
        'toggle': 'toggle.mp3',
        'launch': 'launch.mp3'
    }
    
    sounds_path = os.path.join(base_path, 'Sounds')
    for sound_name, sound_file in default_sounds.items():
        target_path = os.path.join(sounds_path, sound_file)
        if not os.path.exists(target_path):
            try:
                if getattr(sys, 'frozen', False):
                    # Si l'application est compilée, extraire les sons depuis sys._MEIPASS
                    source_path = os.path.join(sys._MEIPASS, 'Sounds', sound_file)
                else:
                    # En développement, utiliser le chemin relatif
                    source_path = os.path.join('Sounds', sound_file)
                
                if os.path.exists(source_path):
                    shutil.copy2(source_path, target_path)
                    logging.info(f"Son copié : {sound_file}")
            except Exception as e:
                logging.error(f"Erreur lors de la copie du son {sound_file}: {e}")

def main():
    if not check_single_instance():
        messagebox.showwarning(
            LanguageManager().get_text('warning'),
            LanguageManager().get_text('instance_warning')
        )
        sys.exit(0)

    if getattr(sys, 'frozen', False):
        app_dir = os.path.dirname(sys.executable)
    else:
        app_dir = os.path.dirname(os.path.abspath(__file__))

    log_file = os.path.join(app_dir, 'launcher.log')
    logging.basicConfig(
        filename=log_file,
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    try:
        ensure_required_folders()  # Vérification des dossiers requis
        pygame.init()
        pygame.mixer.init()
        root = tk.Tk()
        app = TriLegacyLauncher(root)
        app.run()
    except Exception as e:
        logging.critical(f"Erreur critique: {e}", exc_info=True)
        messagebox.showerror(
            LanguageManager().get_text('critical_error'),
            f"{LanguageManager().get_text('error_occurred')}\n\n{str(e)}"
        )
    finally:
        try:
            pygame.mixer.quit()
            pygame.quit()
        except:
            pass
        logging.info("Application terminée")

class WindowManager:
    def __init__(self, parent, title, geometry, theme_colors):
        self.window = tk.Toplevel(parent)
        self.window.title(title)
        self.window.geometry(geometry)
        self.window.resizable(False, False)
        self.window.configure(bg=theme_colors['frame_bg'])
        self.window.transient(parent)
        self.window.grab_set()
        
        # Forcer la fenêtre au premier plan
        self.window.lift()
        self.window.focus_force()
        
        if os.path.exists("assets/logo.ico"):
            self.window.iconbitmap("assets/logo.ico")
        
        # Centrer la fenêtre
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - (width // 2)
        y = parent.winfo_y() + (parent.winfo_height() // 2) - (height // 2)
        self.window.geometry(f"+{x}+{y}")

class TriLegacyLauncher:
    def __init__(self, root):
        self.root = root
        
        # Définition d'une seule palette de couleurs
        self.colors = {
            'bg': '#0A0A0A',
            'frame_bg': '#151515',
            'button_bg': '#1A1A1A',
            'button_hover': '#252525',
            'gold': '#FFD700',
            'text': '#FFFFFF'
        }
        
        # Initialisation du dictionnaire des processus en cours
        self.running_processes = {}
        
        # Configuration de la fenêtre principale
        self.root.configure(bg=self.colors['bg'])
        self.root.geometry("1200x800")
        self.root.resizable(False, False)  # Empêche le redimensionnement
        self.root.title("Tri-Legacy")
        
        # Chargement des icônes
        try:
            if getattr(sys, 'frozen', False):
                base_path = sys._MEIPASS
            else:
                base_path = os.path.dirname(os.path.abspath(__file__))
            
            # Icône principale
            icon_path = os.path.join(base_path, 'assets', 'logo.ico')
            icon_small_path = os.path.join(base_path, 'assets', 'logosmall.ico')
            
            if os.path.exists(icon_path):
                self.root.iconbitmap(default=icon_path)
                # Pour la barre des tâches Windows
                if os.name == 'nt':
                    try:
                        import ctypes
                        myappid = 'trilegacy.launcher.1.0'
                        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
                        if os.path.exists(icon_small_path):
                            self.root.iconbitmap(icon_small_path)
                    except Exception as e:
                        logging.warning(f"Impossible de définir l'icône de la barre des tâches: {e}")
            else:
                logging.warning(f"Icône introuvable: {icon_path}")
        except Exception as e:
            logging.warning(f"Impossible de charger l'icône: {e}")
        
        # Initialisation des gestionnaires
        self.load_managers()
        
        # Création de l'interface
        self.setup_interface()
        
        # Configuration de la fermeture
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Centrer la fenêtre
        self.center_window()
        
        # Démarrer la mise à jour de l'interface
        self.update_ui()

        self.sound_manager = SoundManager()
        self.language_manager = LanguageManager()

    def load_managers(self):
        """Initialise les différents gestionnaires."""
        try:
            # Création du dossier data s'il n'existe pas
            if not os.path.exists('data'):
                os.makedirs('data')

            # Initialisation des gestionnaires
            self.settings_manager = SettingsManager()
            self.game_tracker = GameTimeTracker()
            self.stats_manager = StatsManager()
            self.addon_manager = AddonManager()
            self.language_manager = LanguageManager()
            
            # Initialisation du tracker en arrière-plan
            self.background_tracker = BackgroundTracker(self.game_tracker)

        except Exception as e:
            logging.error(f"Erreur lors de l'initialisation des gestionnaires: {e}")
            messagebox.showerror(
                self.language_manager.get_text('error') if hasattr(self, 'language_manager') else "Erreur",
                str(e)
            )

    def setup_interface(self):
        """Configure l'interface principale."""
        try:
            # Chargement de l'image de fond
            if getattr(sys, 'frozen', False):
                base_path = sys._MEIPASS
            else:
                base_path = os.path.dirname(os.path.abspath(__file__))
            
            bg_path = os.path.join(base_path, 'assets', 'background.jpg')
            if os.path.exists(bg_path):
                bg_image = Image.open(bg_path)
                # Redimensionner l'image à la taille de la fenêtre
                bg_image = bg_image.resize((1200, 800), Image.Resampling.LANCZOS)
                self.bg_photo = ImageTk.PhotoImage(bg_image)
                
                # Création d'un canvas pour le fond
                self.bg_canvas = tk.Canvas(self.root, width=1200, height=800, highlightthickness=0)
                self.bg_canvas.pack(fill='both', expand=True)
                self.bg_canvas.create_image(0, 0, image=self.bg_photo, anchor='nw')

                # Frame principale sur le canvas
                self.main_frame = tk.Frame(self.bg_canvas, bg=self.colors['bg'])
                self.main_frame.place(relx=0.5, rely=0.5, anchor='center')
            else:
                # Fallback si l'image n'existe pas
                self.main_frame = tk.Frame(self.root, bg=self.colors['bg'])
                self.main_frame.pack(expand=True, padx=20, pady=20)

            # Configuration des menus
            self.setup_menus()

            # Style des boutons
            button_style = {
                'font': ('Morpheus', 12),
                'bg': self.colors['button_bg'],
                'fg': self.colors['gold'],
                'width': 30,
                'height': 2,
                'relief': 'flat',
                'bd': 0
            }

            # Titre
            title_label = tk.Label(self.main_frame, 
                                text="Tri-Legacy Launcher",
                                font=('Morpheus', 24, 'bold'),
                                fg=self.colors['gold'],
                                bg=self.colors['bg'])
            title_label.pack(pady=(0, 40))

            # Création des boutons pour chaque version
            versions = [
                ("vanilla", "World of Warcraft Vanilla"),
                ("tbc", "The Burning Crusade"),
                ("wotlk", "Wrath of the Lich King")
            ]

            for version, title in versions:
                frame = tk.Frame(self.main_frame, bg=self.colors['bg'])
                frame.pack(pady=10)

                # Bouton de lancement
                launch_button = tk.Button(frame,
                                        text=self.language_manager.get_text('launch_button', version.title()),
                                        command=lambda v=version: self.launch_game(v),
                                        **button_style)
                launch_button.pack()

                # Effet de survol pour le bouton de lancement
                launch_button.bind('<Enter>', lambda e, b=launch_button: b.configure(bg=self.colors['button_hover']))
                launch_button.bind('<Leave>', lambda e, b=launch_button: b.configure(bg=self.colors['button_bg']))

                # Label pour le temps de jeu
                time_label = tk.Label(frame,
                                    text=self.language_manager.get_text('game_time', "0h 0min"),
                                    font=('Segoe UI', 10),
                                    bg=self.colors['bg'],
                                    fg=self.colors['gold'])
                time_label.pack(pady=5)

            # Bouton Options avec son
            options_button = tk.Button(self.main_frame,
                                    text=self.language_manager.get_text('options'),
                                    command=lambda: [self.sound_manager.play('toggle'), self.open_settings()],
                                    **button_style)
            options_button.pack(pady=20)

            # Effet de survol pour le bouton options
            options_button.bind('<Enter>', lambda e: options_button.configure(bg=self.colors['button_hover']))
            options_button.bind('<Leave>', lambda e: options_button.configure(bg=self.colors['button_bg']))

        except Exception as e:
            logging.error(f"Erreur lors de la configuration de l'interface: {e}")
            # Fallback en cas d'erreur
            self.main_frame = tk.Frame(self.root, bg=self.colors['bg'])
            self.main_frame.pack(expand=True, padx=20, pady=20)

    def setup_menus(self):
        """Configure la barre de menus."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # Menu Fichier
        file_menu = tk.Menu(menubar, tearoff=0, bg=self.colors['frame_bg'], fg=self.colors['text'])
        menubar.add_cascade(label=self.language_manager.get_text('file'), menu=file_menu)
        file_menu.add_command(label=self.language_manager.get_text('settings'), 
                            command=lambda: [self.sound_manager.play('toggle'), self.open_settings()])
        file_menu.add_separator()
        file_menu.add_command(label=self.language_manager.get_text('quit'), 
                            command=lambda: [self.sound_manager.play('toggle'), self.on_closing()])

        # Menu Outils
        tools_menu = tk.Menu(menubar, tearoff=0, bg=self.colors['frame_bg'], fg=self.colors['text'])
        menubar.add_cascade(label=self.language_manager.get_text('tools'), menu=tools_menu)
        tools_menu.add_command(label=self.language_manager.get_text('addons'), 
                             command=lambda: [self.sound_manager.play('toggle'), self.open_addon_manager()])
        tools_menu.add_command(label=self.language_manager.get_text('stats'), 
                             command=lambda: [self.sound_manager.play('toggle'), self.open_stats()])

    def launch_game(self, version):
        """Lance le jeu spécifié."""
        try:
            # Vérifier si le jeu est déjà en cours d'exécution
            if version in self.running_processes and self.running_processes[version]['process'].poll() is None:
                messagebox.showinfo(
                    self.language_manager.get_text('information'),
                    self.language_manager.get_text('game_already_running')
                )
                return

            # Récupérer le chemin du jeu
            game_path = self.settings_manager.get_path(version)
            if not game_path or not os.path.exists(game_path):
                messagebox.showerror(
                    self.language_manager.get_text('error'),
                    self.language_manager.get_text('invalid_path')
                )
                return

            # Lancer le jeu
            process = subprocess.Popen([game_path])
            self.running_processes[version] = {
                'process': process,
                'start_time': datetime.now()
            }
            
            # Incrémenter le compteur de lancements dans game_tracker
            self.game_tracker.increment_launches(version)
            
            # Mettre à jour les statistiques avec un temps initial de 0
            self.stats_manager.update_stats(version, 0)

            # Démarrer le suivi du processus
            self.background_tracker.start_tracking(version, process)

            # Jouer le son de lancement
            self.sound_manager.play('launch')

        except Exception as e:
            messagebox.showerror(
                self.language_manager.get_text('error'),
                f"{self.language_manager.get_text('launch_error')}\n{str(e)}"
            )

    def update_ui(self):
        try:
            # Récupérer tous les frames des versions (en ignorant le titre et le bouton options)
            version_frames = [frame for frame in self.main_frame.winfo_children() 
                             if isinstance(frame, tk.Frame)][:3]  # Les 3 premiers frames sont pour les versions
            
            for version, frame in zip(['vanilla', 'tbc', 'wotlk'], version_frames):
                launch_button = frame.winfo_children()[0]  # Premier widget: bouton de lancement
                time_label = frame.winfo_children()[1]     # Deuxième widget: label de temps
                
                if version in self.running_processes:
                    process_info = self.running_processes[version]
                    if process_info['process'].poll() is not None or not is_wow_running(process_info['process'].pid):
                        # Processus terminé
                        logging.info(f"Processus {version} terminé, mise à jour des statistiques")
                        
                        # Calculer le temps final
                        end_time = datetime.now()
                        elapsed = int((end_time - process_info['start_time']).total_seconds())
                        
                        # Mettre à jour les statistiques une seule fois
                        self.stats_manager.update_stats(version, elapsed)
                        
                        # Supprimer le processus de la liste
                        del self.running_processes[version]
                        
                        # Mettre à jour l'affichage avec le temps sauvegardé uniquement
                        formatted_time = self.game_tracker.get_formatted_time(version)
                        time_label.config(text=self.language_manager.get_text('game_time', formatted_time))
                        launch_button.config(
                            text=self.language_manager.get_text('launch_button', version.upper()),
                            state=tk.NORMAL,
                            bg=self.colors['button_bg']
                        )
                    else:
                        # Jeu en cours, mise à jour du temps
                        current_time = datetime.now()
                        elapsed = int((current_time - process_info['start_time']).total_seconds())
                        # Calculer le temps total : temps sauvegardé + temps de la session en cours non encore sauvegardé
                        saved_time = self.game_tracker.get_time(version)
                        # Le temps sauvegardé par le BackgroundTracker (par tranches de 10 secondes)
                        saved_session_time = (elapsed // 10) * 10
                        # Le temps restant non encore sauvegardé (moins de 10 secondes)
                        unsaved_time = elapsed - saved_session_time
                        total_time = saved_time + unsaved_time
                        hours = total_time // 3600
                        minutes = (total_time % 3600) // 60
                        formatted_time = f"{hours}h {minutes}min"
                        time_label.config(text=self.language_manager.get_text('game_time', formatted_time))
                        launch_button.config(
                            text=self.language_manager.get_text('game_running'),
                            state=tk.DISABLED,
                            bg=self.colors['button_hover']
                        )
                else:
                    # Jeu non lancé, afficher uniquement le temps sauvegardé
                    formatted_time = self.game_tracker.get_formatted_time(version)
                    time_label.config(text=self.language_manager.get_text('game_time', formatted_time))
                    launch_button.config(
                        text=self.language_manager.get_text('launch_button', version.upper()),
                        state=tk.NORMAL,
                        bg=self.colors['button_bg']
                    )
        except Exception as e:
            logging.error(f"Erreur lors de la mise à jour de l'interface: {e}")
        finally:
            # Mettre à jour toutes les secondes
            self.root.after(1000, self.update_ui)

    def get_version_number(self, version):
        """Retourne le numéro de version pour chaque version du jeu."""
        version_numbers = {
            'vanilla': '1.12.1',
            'tbc': '2.4.3',
            'wotlk': '3.3.5'
        }
        return version_numbers.get(version, '')

    def run(self):
        try:
            self.root.mainloop()
        except Exception as e:
            logging.error(f"Erreur dans la boucle principale: {e}", exc_info=True)
            raise

    def create_settings_content(self, window):
        """Crée le contenu de la fenêtre des paramètres."""
        main_frame = tk.Frame(window, bg=self.colors['bg'])
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Style des labels et des entrées
        label_style = {
            'font': ('Morpheus', 12),
            'bg': self.colors['bg'],
            'fg': self.colors['text']
        }

        # Style des boutons
        button_style = {
            'font': ('Morpheus', 10),
            'bg': self.colors['button_bg'],
            'fg': self.colors['gold'],
            'activebackground': self.colors['button_hover'],
            'activeforeground': self.colors['gold'],
            'width': 10,
            'relief': 'ridge',
            'bd': 1
        }

        # Sélecteur de langue
        language_frame = tk.Frame(main_frame, bg=self.colors['bg'])
        language_frame.pack(fill='x', pady=5)
        
        language_label = tk.Label(language_frame, text=self.language_manager.get_text('language'), **label_style)
        language_label.pack(side='left', padx=(0, 10))
        
        self.language_var = tk.StringVar(value=self.language_manager.current_language)
        language_menu = ttk.Combobox(language_frame, 
                                   textvariable=self.language_var,
                                   values=list(self.language_manager.get_available_languages().keys()),
                                   state='readonly',
                                   width=10)
        language_menu.pack(side='left')
        
        # Afficher le nom complet de la langue dans le menu déroulant
        def language_selected(event):
            selected = self.language_var.get()
            self.language_manager.set_language(selected)
            # Mettre à jour les textes de l'interface immédiatement
            self.update_interface_texts()
            # Forcer la mise à jour de l'interface
            self.root.update_idletasks()
            # Mettre à jour les fenêtres ouvertes
            for window in self.root.winfo_children():
                if isinstance(window, tk.Toplevel):
                    if 'stats' in window.title().lower():
                        window.title(self.language_manager.get_text('stats'))
                        self.update_stats_window(window)
                    elif 'addon' in window.title().lower():
                        window.title(self.language_manager.get_text('addon_manager'))
                        self.update_addon_window(window)
                    elif 'settings' in window.title().lower():
                        window.title(self.language_manager.get_text('settings'))
                        self.update_settings_window(window)
        
        language_menu.bind('<<ComboboxSelected>>', language_selected)

        # Chemins des jeux
        paths = [
            (f"Chemin Vanilla (1.12.1):", 'vanilla'),
            (f"Chemin The Burning Crusade (2.4.3):", 'tbc'),
            (f"Chemin Wrath of the Lich King (3.3.5):", 'wotlk')
        ]

        self.path_entries = {}
        
        for label_text, version in paths:
            frame = tk.Frame(main_frame, bg=self.colors['bg'])
            frame.pack(fill='x', pady=5)
            
            label = tk.Label(frame, text=label_text, **label_style)
            label.pack(side='left', padx=(0, 10))
            
            entry = tk.Entry(frame, width=50, bg=self.colors['frame_bg'], fg=self.colors['text'],
                           insertbackground=self.colors['text'])
            entry.pack(side='left', padx=(0, 10))
            current_path = self.settings_manager.get_path(version)
            if current_path:
                entry.insert(0, current_path)
            self.path_entries[version] = entry
            
            browse_btn = tk.Button(frame, text=self.language_manager.get_text('browse'),
                                 command=lambda v=version: self.browse_path(v),
                                 **button_style)
            browse_btn.pack(side='left')

        # Frame pour les boutons Sauvegarder et Annuler
        button_frame = tk.Frame(main_frame, bg=self.colors['bg'])
        button_frame.pack(side='bottom', pady=20)

        save_btn = tk.Button(button_frame, text=self.language_manager.get_text('save'),
                           command=lambda: [self.sound_manager.play('toggle'), self.save_settings()], **button_style)
        save_btn.pack(side='left', padx=10)

        cancel_btn = tk.Button(button_frame, text=self.language_manager.get_text('cancel'),
                            command=lambda: [self.sound_manager.play('toggle'), window.destroy()], **button_style)
        cancel_btn.pack(side='left', padx=10)

    def browse_path(self, version):
        """Ouvre une boîte de dialogue pour sélectionner le chemin du jeu."""
        path = filedialog.askopenfilename(
            title=self.language_manager.get_text('select_executable', version.upper()),
            filetypes=[("Executable", "*.exe")]
        )
        if path:
            self.path_entries[version].delete(0, tk.END)
            self.path_entries[version].insert(0, path)

    def save_settings(self):
        """Sauvegarde les paramètres."""
        try:
            # Sauvegarde des chemins
            for version, entry in self.path_entries.items():
                path = entry.get().strip()
                self.settings_manager.set_path(version, path)
            
            # Sauvegarde de la langue
            selected_language = self.language_var.get()
            if selected_language:
                self.language_manager.set_language(selected_language)
            
            messagebox.showinfo(self.language_manager.get_text('settings'), 
                              self.language_manager.get_text('settings_saved'))
            self.root.focus_force()  # Remet le focus sur la fenêtre principale
        except Exception as e:
            messagebox.showerror(self.language_manager.get_text('error'), 
                               str(e))

    def create_addon_manager_content(self, window):
        # Réduire la taille de la fenêtre
        window.geometry("600x600")
        
        # Créer un canvas avec barre de défilement
        canvas = tk.Canvas(window, bg=self.colors['frame_bg'], width=580)
        scrollbar = ttk.Scrollbar(window, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.colors['frame_bg'])

        # Configurer le canvas
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas_frame = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        
        # Configurer la liaison entre le canvas et la scrollbar
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Ajuster la largeur du frame au canvas
        def configure_frame(event):
            canvas.itemconfig(canvas_frame, width=event.width)
        canvas.bind('<Configure>', configure_frame)

        # Placer le canvas et la barre de défilement
        canvas.pack(side="left", fill="both", expand=True, padx=10)
        scrollbar.pack(side="right", fill="y")

        # Créer le contenu dans le frame défilable
        main_frame = tk.Frame(scrollable_frame, bg=self.colors['frame_bg'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=20)

        # En-tête avec bordure dorée
        header_frame = tk.Frame(main_frame, 
                              bg=self.colors['frame_bg'],
                              highlightbackground=self.colors['gold'],
                              highlightthickness=1)
        header_frame.pack(fill='x', pady=(0, 20))
        
        header = tk.Label(header_frame,
                         text=self.language_manager.get_text('addons'),
                         font=('Morpheus', 24, 'bold'),
                         bg=self.colors['frame_bg'],
                         fg=self.colors['gold'])
        header.pack(pady=10)

        # Style des boutons
        button_style = {
            'font': ('Morpheus', 12),
            'bg': self.colors['button_bg'],
            'fg': self.colors['gold'],
            'activebackground': self.colors['button_hover'],
            'activeforeground': self.colors['gold'],
            'width': 30,  # Réduire la largeur des boutons
            'pady': 10,
            'cursor': 'hand2',
            'relief': 'ridge',
            'bd': 2
        }

        # Création des sections pour chaque version
        versions = [
            ('Vanilla (1.12.1)', 'vanilla'),
            ('The Burning Crusade (2.4.3)', 'tbc'),
            ('Wrath of the Lich King (3.3.5)', 'wotlk')
        ]

        for title, version in versions:
            # Frame avec bordure dorée pour chaque version
            version_frame = tk.Frame(main_frame, 
                                   bg=self.colors['frame_bg'],
                                   highlightbackground=self.colors['gold'],
                                   highlightthickness=1)
            version_frame.pack(fill='x', pady=10, padx=5)
            
            # Titre de la version
            version_title = tk.Label(version_frame,
                                   text=title,
                                   font=('Morpheus', 16, 'bold'),
                                   bg=self.colors['frame_bg'],
                                   fg=self.colors['gold'])
            version_title.pack(pady=(10, 5))
            
            path = self.settings_manager.get_path(version)
            if path and os.path.exists(path):
                addon_path = os.path.join(os.path.dirname(path), 'Interface', 'AddOns')
                
                # Frame pour le chemin avec fond légèrement différent
                path_frame = tk.Frame(version_frame, 
                                    bg=self.colors['button_bg'],
                                    padx=10, 
                                    pady=5)
                path_frame.pack(fill='x', padx=10, pady=5)
                
                # Icône ou symbole pour le dossier
                folder_icon = tk.Label(path_frame,
                                     text="📁",
                                     font=('Segoe UI Emoji', 12),
                                     bg=self.colors['button_bg'],
                                     fg=self.colors['text'])
                folder_icon.pack(side='left', padx=(0, 5))
                
                # Chemin du dossier
                path_label = tk.Label(path_frame,
                                    text=addon_path,
                                    font=('Morpheus', 10),
                                    bg=self.colors['button_bg'],
                                    fg=self.colors['text'])
                path_label.pack(side='left', fill='x', expand=True)
                
                # Bouton pour ouvrir le dossier
                btn = tk.Button(version_frame,
                              text=self.language_manager.get_text('open_addons'),
                              command=lambda p=addon_path: [self.sound_manager.play('toggle'), self.open_addon_folder(p)],
                              **button_style)
                btn.pack(pady=10)
                
                # Effet de survol pour le bouton
                def on_enter(e, button):
                    button.config(bg=self.colors['button_hover'])
                
                def on_leave(e, button):
                    button.config(bg=self.colors['button_bg'])
                
                btn.bind('<Enter>', lambda e, b=btn: on_enter(e, b))
                btn.bind('<Leave>', lambda e, b=btn: on_leave(e, b))
            else:
                # Message d'erreur avec icône
                error_frame = tk.Frame(version_frame, bg=self.colors['frame_bg'])
                error_frame.pack(pady=10)
                
                error_icon = tk.Label(error_frame,
                                    text="⚠️",
                                    font=('Segoe UI Emoji', 14),
                                    bg=self.colors['frame_bg'],
                                    fg='red')
                error_icon.pack(side='left', padx=5)
                
                error_label = tk.Label(error_frame,
                                     text=self.language_manager.get_text('path_not_configured', title),
                                     font=('Morpheus', 12),
                                     bg=self.colors['frame_bg'],
                                     fg='red')
                error_label.pack(side='left')
                
                # Bouton pour ouvrir les paramètres
                settings_btn = tk.Button(version_frame,
                                       text=self.language_manager.get_text('configure_path'),
                                       command=lambda: [self.sound_manager.play('toggle'), self.open_settings()],
                                       **button_style)
                settings_btn.pack(pady=10)
                
                # Effet de survol pour le bouton des paramètres
                settings_btn.bind('<Enter>', lambda e, b=settings_btn: on_enter(e, b))
                settings_btn.bind('<Leave>', lambda e, b=settings_btn: on_leave(e, b))

        # Configurer le défilement avec la molette de la souris
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind_all("<MouseWheel>", _on_mousewheel)

    def open_addon_folder(self, path):
        try:
            if not os.path.exists(path):
                os.makedirs(path)
            if os.path.exists(path):
                if sys.platform == 'win32':
                    os.startfile(path)
                else:
                    subprocess.run(['xdg-open', path])
        except Exception as e:
            messagebox.showerror(
                self.language_manager.get_text('error'),
                f"{self.language_manager.get_text('folder_error')}\n{str(e)}"
            )

    def open_stats(self):
        """Ouvre la fenêtre des statistiques."""
        window = WindowManager(self.root, self.language_manager.get_text('stats'), "400x600", self.colors)
        self.create_stats_content(window.window)

    def create_stats_content(self, window):
        """Crée le contenu de la fenêtre des statistiques."""
        main_frame = tk.Frame(window, bg=self.colors['bg'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Titre
        title_label = tk.Label(main_frame,
                             text=self.language_manager.get_text('stats'),
                             font=('Morpheus', 24, 'bold'),
                             bg=self.colors['bg'],
                             fg='#FFD700')
        title_label.pack(pady=(0, 30))

        # Versions des jeux avec leurs traductions
        versions = [
            (self.language_manager.get_text('vanilla_title'), "vanilla"),
            (self.language_manager.get_text('tbc_title'), "tbc"),
            (self.language_manager.get_text('wotlk_title'), "wotlk")
        ]

        for name, version in versions:
            # Titre de la version
            version_label = tk.Label(main_frame,
                                   text=name,
                                   font=('Morpheus', 16, 'bold'),
                                   bg=self.colors['bg'],
                                   fg='#FFD700')
            version_label.pack(pady=(20, 10), anchor='w')

            # Frame pour les statistiques
            stats_frame = tk.Frame(main_frame, bg=self.colors['bg'])
            stats_frame.pack(fill='x', padx=10)

            # Temps de jeu
            total_time = self.game_tracker.get_time(version)  # Utiliser uniquement le temps du game_tracker
            hours = total_time // 3600
            minutes = (total_time % 3600) // 60
            time_text = f"{hours}h {minutes}min"

            time_label = tk.Label(stats_frame,
                                text=self.language_manager.get_text('game_time', time_text),
                                font=('Segoe UI', 12),
                                bg=self.colors['bg'],
                                fg='white')
            time_label.pack(anchor='w', pady=2)

            # Nombre de lancements
            launches = self.game_tracker.get_launches(version)  # Utiliser les lancements du game_tracker
            launches_label = tk.Label(stats_frame,
                                    text=self.language_manager.get_text('launches_count', launches),
                                    font=('Segoe UI', 12),
                                    bg=self.colors['bg'],
                                    fg='white')
            launches_label.pack(anchor='w', pady=2)

            # Dernière utilisation
            if version in self.running_processes:
                last_used = self.language_manager.get_text('game_running')
            else:
                last_used = self.stats_manager.get_last_used(version)
                if last_used:
                    last_used = datetime.strptime(last_used, "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y à %H:%M")
                else:
                    last_used = self.language_manager.get_text('never_used')

            last_used_label = tk.Label(stats_frame,
                                     text=self.language_manager.get_text('last_used', last_used),
                                     font=('Segoe UI', 12),
                                     bg=self.colors['bg'],
                                     fg='white')
            last_used_label.pack(anchor='w', pady=(2, 10))

    def open_addon_manager(self):
        """Ouvre la fenêtre du gestionnaire d'addons."""
        window = WindowManager(self.root, self.language_manager.get_text('addon_manager'), "800x600", self.colors)
        self.create_addon_manager_content(window.window)

    def open_settings(self):
        """Ouvre la fenêtre des paramètres."""
        window = WindowManager(self.root, self.language_manager.get_text('settings'), "800x500", self.colors)
        self.create_settings_content(window.window)

    def center_window(self):
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() - width) // 2
        y = (self.root.winfo_screenheight() - height) // 2
        self.root.geometry(f"+{x}+{y}")

    def on_closing(self):
        """Gère la fermeture propre de l'application."""
        try:
            # Sauvegarder le temps de jeu pour tous les processus en cours
            current_time = datetime.now()
            for version, process_info in list(self.running_processes.items()):
                if process_info['process'].poll() is None:
                    elapsed = int((current_time - process_info['start_time']).total_seconds())
                    self.game_tracker.increment_time(version, elapsed)
                    process_info['process'].terminate()

            # Arrêter le tracker en arrière-plan
            self.background_tracker.stop()
            
            # Détruire la fenêtre principale
            self.root.destroy()
            
        except Exception as e:
            logging.error(f"Erreur lors de la fermeture de l'application: {e}")
            self.root.destroy()

    def update_interface_texts(self):
        """Met à jour tous les textes de l'interface avec la langue sélectionnée de manière dynamique."""
        try:
            def update_widget_text(widget):
                """Met à jour récursivement le texte de tous les widgets."""
                if isinstance(widget, (tk.Button, tk.Label)):
                    current_text = widget.cget('text')
                    
                    # Mise à jour des textes spécifiques
                    if 'temps joué' in current_text.lower() or 'game time' in current_text.lower():
                        version = None
                        for v in ['vanilla', 'tbc', 'wotlk']:
                            if v.upper() in current_text.upper():
                                version = v
                                break
                        if version:
                            total_time = self.game_tracker.get_time(version)
                            hours = total_time // 3600
                            minutes = (total_time % 3600) // 60
                            time_text = f"{hours}h {minutes}min"
                            widget.config(text=self.language_manager.get_text('game_time', time_text))
                    
                    # Mise à jour des boutons de lancement
                    elif any(f"LANCER {v.upper()}" in current_text.upper() for v in ['vanilla', 'tbc', 'wotlk']):
                        for v in ['vanilla', 'tbc', 'wotlk']:
                            if v.upper() in current_text.upper():
                                if v in self.running_processes:
                                    widget.config(text=self.language_manager.get_text('game_running'))
                                else:
                                    widget.config(text=self.language_manager.get_text('launch_button', v.upper()))
                    
                    # Mise à jour des autres textes
                    elif current_text.lower() in ['options', 'settings', 'addons', 'stats']:
                        widget.config(text=self.language_manager.get_text(current_text.lower()))
                
                # Parcours récursif des widgets enfants
                for child in widget.winfo_children():
                    update_widget_text(child)
            
            # Mise à jour des menus
            menubar = self.root.config('menu')[4]
            menubar.entryconfigure(0, label=self.language_manager.get_text('file'))
            menubar.entryconfigure(1, label=self.language_manager.get_text('tools'))
            
            # Mise à jour du menu Fichier
            file_menu = menubar.winfo_children()[0]
            file_menu.entryconfigure(0, label=self.language_manager.get_text('settings'))
            file_menu.entryconfigure(2, label=self.language_manager.get_text('quit'))
            
            # Mise à jour du menu Outils
            tools_menu = menubar.winfo_children()[1]
            tools_menu.entryconfigure(0, label=self.language_manager.get_text('addons'))
            tools_menu.entryconfigure(1, label=self.language_manager.get_text('stats'))
            
            # Mise à jour récursive de tous les widgets
            update_widget_text(self.root)
            
            # Mise à jour des fenêtres ouvertes
            for window in self.root.winfo_children():
                if isinstance(window, tk.Toplevel):
                    if 'stats' in window.title().lower():
                        window.title(self.language_manager.get_text('stats'))
                        self.update_stats_window(window)
                    elif 'addon' in window.title().lower():
                        window.title(self.language_manager.get_text('addon_manager'))
                        self.update_addon_window(window)
                    elif 'settings' in window.title().lower():
                        window.title(self.language_manager.get_text('settings'))
                        self.update_settings_window(window)
            
            # Forcer la mise à jour de l'interface
            self.root.update_idletasks()

        except Exception as e:
            logging.error(f"Erreur lors de la mise à jour des textes de l'interface: {e}")

    def update_stats_window(self, window):
        """Met à jour les textes de la fenêtre des statistiques."""
        try:
            main_frame = window.winfo_children()[0]
            
            # Mise à jour du titre
            title_label = main_frame.winfo_children()[0]
            title_label.config(text=self.language_manager.get_text('stats'))
            
            # Mise à jour des statistiques pour chaque version
            versions = ['vanilla', 'tbc', 'wotlk']
            for i, version in enumerate(versions):
                stats_frame = main_frame.winfo_children()[i * 4 + 1:i * 4 + 5]  # 4 widgets par version
                
                # Mise à jour des labels
                for widget in stats_frame:
                    if isinstance(widget, tk.Label):
                        if 'temps joué' in widget.cget('text').lower():
                            total_time = self.game_tracker.get_time(version)
                            hours = total_time // 3600
                            minutes = (total_time % 3600) // 60
                            time_text = f"{hours}h {minutes}min"
                            widget.config(text=self.language_manager.get_text('game_time', time_text))
                        elif 'lancements' in widget.cget('text').lower():
                            launches = self.game_tracker.get_launches(version)
                            widget.config(text=self.language_manager.get_text('launches_count', launches))
                        elif 'dernière utilisation' in widget.cget('text').lower():
                            if version in self.running_processes:
                                last_used = self.language_manager.get_text('game_running')
                            else:
                                last_used = self.stats_manager.get_last_used(version)
                                if last_used:
                                    last_used = datetime.strptime(last_used, "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y à %H:%M")
                                else:
                                    last_used = self.language_manager.get_text('never_used')
                            widget.config(text=self.language_manager.get_text('last_used', last_used))

        except Exception as e:
            logging.error(f"Erreur lors de la mise à jour de la fenêtre des statistiques: {e}")

    def update_addon_window(self, window):
        """Met à jour les textes de la fenêtre des addons."""
        try:
            main_frame = window.winfo_children()[0]
            
            # Mise à jour des textes pour chaque version
            for widget in main_frame.winfo_children():
                if isinstance(widget, tk.Label):
                    if widget.cget('text') == 'Addon Manager':
                        widget.config(text=self.language_manager.get_text('addon_manager'))
                elif isinstance(widget, tk.Button):
                    if 'open' in widget.cget('text').lower():
                        widget.config(text=self.language_manager.get_text('open_addons'))
                    elif 'configure' in widget.cget('text').lower():
                        widget.config(text=self.language_manager.get_text('configure_path'))

        except Exception as e:
            logging.error(f"Erreur lors de la mise à jour de la fenêtre des addons: {e}")

    def update_settings_window(self, window):
        """Met à jour les textes de la fenêtre des paramètres."""
        try:
            main_frame = window.winfo_children()[0]
            
            # Mise à jour des labels et boutons
            for widget in main_frame.winfo_children():
                if isinstance(widget, tk.Label):
                    if 'language' in widget.cget('text').lower():
                        widget.config(text=self.language_manager.get_text('language'))
                    elif 'path' in widget.cget('text').lower():
                        if 'vanilla' in widget.cget('text').lower():
                            widget.config(text=self.language_manager.get_text('path_vanilla'))
                        elif 'tbc' in widget.cget('text').lower():
                            widget.config(text=self.language_manager.get_text('path_tbc'))
                        elif 'wotlk' in widget.cget('text').lower():
                            widget.config(text=self.language_manager.get_text('path_wotlk'))
                elif isinstance(widget, tk.Button):
                    if 'browse' in widget.cget('text').lower():
                        widget.config(text=self.language_manager.get_text('browse'))
                    elif 'save' in widget.cget('text').lower():
                        widget.config(text=self.language_manager.get_text('save'))
                    elif 'cancel' in widget.cget('text').lower():
                        widget.config(text=self.language_manager.get_text('cancel'))

        except Exception as e:
            logging.error(f"Erreur lors de la mise à jour de la fenêtre des paramètres: {e}")

    def change_language(self, language, window=None):
        """Change la langue de l'interface."""
        try:
            # Changer la langue dans le gestionnaire de langue
            self.language_manager.set_language(language)
            
            # Récupérer la barre de menu
            menubar = self.root.config('menu')[4]
            
            # Mise à jour du menu Fichier
            file_menu = menubar.winfo_children()[0]
            file_menu.entryconfigure(0, label=self.language_manager.get_text('settings'))
            file_menu.entryconfigure(2, label=self.language_manager.get_text('quit'))
            
            # Mise à jour du menu Outils
            tools_menu = menubar.winfo_children()[1]
            tools_menu.entryconfigure(0, label=self.language_manager.get_text('addons'))
            tools_menu.entryconfigure(1, label=self.language_manager.get_text('stats'))
            
            # Mise à jour des labels des menus
            menubar.entryconfigure(0, label=self.language_manager.get_text('file'))
            menubar.entryconfigure(1, label=self.language_manager.get_text('tools'))
            menubar.entryconfigure(2, label=language.upper())

            # Mise à jour des boutons de lancement et labels de temps
            versions = ['vanilla', 'tbc', 'wotlk']
            for i, version in enumerate(versions):
                # Récupérer le frame correspondant à la version (en sautant le titre)
                frame = self.main_frame.winfo_children()[i + 1]
                
                # Récupérer le bouton de lancement et le label de temps
                launch_button = frame.winfo_children()[0]  # Premier widget dans le frame
                time_label = frame.winfo_children()[1]     # Deuxième widget dans le frame
                
                # Mise à jour du bouton de lancement
                if version in self.running_processes:
                    launch_button.config(text=self.language_manager.get_text('game_running'))
                else:
                    launch_button.config(text=self.language_manager.get_text('launch_button', version.upper()))
                
                # Mise à jour du label de temps
                total_time = self.game_tracker.get_time(version)
                hours = total_time // 3600
                minutes = (total_time % 3600) // 60
                time_text = f"{hours}h {minutes}min"
                time_label.config(text=self.language_manager.get_text('game_time', time_text))
            
            # Mise à jour du bouton Options (dernier widget dans main_frame)
            options_button = self.main_frame.winfo_children()[-1]
            options_button.config(text=self.language_manager.get_text('options'))
            
            # Fermer la fenêtre de sélection de langue si elle existe
            if window:
                window.destroy()
            
            # Forcer la mise à jour de l'interface
            self.root.update_idletasks()
            
        except Exception as e:
            logging.error(f"Erreur lors du changement de langue: {e}")

if __name__ == "__main__":
    main() 