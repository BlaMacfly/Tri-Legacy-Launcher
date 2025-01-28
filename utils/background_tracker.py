import threading
import time
import psutil
import logging
from datetime import datetime, timedelta

class BackgroundTracker:
    def __init__(self, game_tracker):
        self.game_tracker = game_tracker
        self.tracking_threads = {}
        self.lock = threading.Lock()
        logging.info("BackgroundTracker initialisé")

    def start_tracking(self, version, process):
        try:
            # Arrêter le suivi existant si nécessaire
            self.stop_tracking(version)
            
            # Créer un nouvel événement d'arrêt pour ce thread
            stop_event = threading.Event()
            
            thread = threading.Thread(
                target=self._monitor_game_process,
                args=(version, process, stop_event),
                daemon=True
            )
            
            with self.lock:
                self.tracking_threads[version] = {
                    'thread': thread,
                    'start_time': datetime.now(),
                    'last_update': datetime.now(),
                    'process': process,
                    'accumulated_time': 0,
                    'stop_event': stop_event
                }
            
            thread.start()
            logging.info(f"Démarrage du suivi pour {version}")
            
        except Exception as e:
            logging.error(f"Erreur lors du démarrage du suivi pour {version}: {e}")

    def stop_tracking(self, version):
        try:
            thread_info = None
            with self.lock:
                if version in self.tracking_threads:
                    thread_info = self.tracking_threads[version]
            
            if thread_info:
                # Signaler l'arrêt au thread
                thread_info['stop_event'].set()
                
                # Attendre la fin du thread avec un timeout
                thread_info['thread'].join(timeout=2)
                
                # Sauvegarder le temps final
                self._save_final_time(version, thread_info)
                
                # Supprimer les informations du thread
                with self.lock:
                    if version in self.tracking_threads:
                        del self.tracking_threads[version]
                
                logging.info(f"Arrêt du suivi pour {version}")
                
        except Exception as e:
            logging.error(f"Erreur lors de l'arrêt du suivi pour {version}: {e}")

    def _save_final_time(self, version, thread_info):
        try:
            # Lors de la fermeture, on ne sauvegarde que le temps déjà accumulé
            # sans ajouter le temps écoulé depuis la dernière mise à jour
            if thread_info['accumulated_time'] > 0:
                logging.info(f"Temps final sauvegardé pour {version}: {thread_info['accumulated_time']} secondes")
        except Exception as e:
            logging.error(f"Erreur lors de la sauvegarde finale du temps pour {version}: {e}")

    def stop(self):
        try:
            # Copier la liste des versions pour éviter les modifications pendant l'itération
            versions = list(self.tracking_threads.keys())
            
            # Arrêter chaque thread individuellement
            for version in versions:
                self.stop_tracking(version)
                
            logging.info("Arrêt de tous les suivis")
        except Exception as e:
            logging.error(f"Erreur lors de l'arrêt général: {e}")

    def _monitor_game_process(self, version, process, stop_event):
        try:
            pid = process.pid
            while not stop_event.is_set():
                try:
                    # Vérifier si le processus existe toujours
                    if not psutil.pid_exists(pid):
                        logging.info(f"Processus {version} (PID: {pid}) terminé")
                        break
                    
                    # Vérifier si le processus est toujours WoW
                    try:
                        proc = psutil.Process(pid)
                        if not proc.name().lower().startswith('wow'):
                            logging.info(f"Processus {version} (PID: {pid}) n'est plus WoW")
                            break
                    except psutil.NoSuchProcess:
                        logging.info(f"Processus {version} (PID: {pid}) n'existe plus")
                        break
                    
                    thread_info = None
                    with self.lock:
                        if version in self.tracking_threads:
                            thread_info = self.tracking_threads[version]
                    
                    if thread_info:
                        current_time = datetime.now()
                        last_update = thread_info.get('last_update', thread_info['start_time'])
                        elapsed_seconds = int((current_time - last_update).total_seconds())
                        
                        if elapsed_seconds >= 10:  # Mise à jour toutes les 10 secondes
                            with self.lock:
                                if version in self.tracking_threads:
                                    thread_info['accumulated_time'] += elapsed_seconds
                                    thread_info['last_update'] = current_time
                                    self.game_tracker.increment_time(version, elapsed_seconds)
                                    logging.info(f"Temps mis à jour pour {version}: +{elapsed_seconds}s, total accumulé={thread_info['accumulated_time']}s")
                    
                    time.sleep(1)  # Vérification toutes les secondes
                    
                except psutil.NoSuchProcess:
                    logging.info(f"Processus {version} (PID: {pid}) n'existe plus")
                    break
                except Exception as e:
                    logging.error(f"Erreur dans la boucle de suivi pour {version}: {e}")
                    break
                
        except Exception as e:
            logging.error(f"Erreur dans le moniteur de processus pour {version}: {e}")
        finally:
            try:
                # Nettoyage final
                thread_info = None
                with self.lock:
                    if version in self.tracking_threads:
                        thread_info = self.tracking_threads[version]
                        del self.tracking_threads[version]
                
                if thread_info:
                    self._save_final_time(version, thread_info)
                    logging.info(f"Nettoyage final pour {version}")
            except Exception as e:
                logging.error(f"Erreur lors du nettoyage final pour {version}: {e}") 