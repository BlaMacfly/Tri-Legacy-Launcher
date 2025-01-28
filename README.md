# Tri-Legacy Launcher

Un lanceur moderne et élégant pour World of Warcraft, supportant plusieurs versions du jeu (Vanilla, TBC, WotLK).

## Fonctionnalités

- Support multi-versions :
  - World of Warcraft Vanilla (1.12.1)
  - The Burning Crusade (2.4.3)
  - Wrath of the Lich King (3.3.5)
- Interface moderne et intuitive
- Gestion des addons pour chaque version
- Suivi du temps de jeu et des statistiques
- Support multilingue (FR, EN, ES, DE, PT)
- Effets sonores pour une meilleure expérience utilisateur
- Thème sombre élégant

## Installation

1. Téléchargez la dernière version depuis la page [Releases](https://github.com/BlaMacfly/Tri-Legacy-Launcher/releases)
2. Extrayez l'archive dans le dossier de votre choix
3. Lancez `Tri-Legacy Launcher.exe`

## Configuration requise

- Windows 10/11
- Python 3.10+ (pour le développement)
- World of Warcraft (versions correspondantes installées)

## Développement

Pour configurer l'environnement de développement :

```bash
# Cloner le dépôt
git clone https://github.com/BlaMacfly/Tri-Legacy-Launcher.git
cd Tri-Legacy-Launcher

# Créer un environnement virtuel
python -m venv .venv
.venv\Scripts\activate

# Installer les dépendances
pip install -r requirements.txt
```

## Compilation

Pour créer l'exécutable :

```bash
pyinstaller --onefile --noconsole --add-data "assets;assets" --add-data "Sounds;Sounds" --add-data "data;data" --name "Tri-Legacy Launcher" launcher.py
```

## Structure du projet

```
Tri-Legacy-Launcher/
├── assets/           # Images et ressources graphiques
├── data/            # Fichiers de données
├── Sounds/          # Effets sonores
├── utils/           # Modules utilitaires
├── launcher.py      # Point d'entrée principal
└── requirements.txt # Dépendances Python
```

## Contribution

Les contributions sont les bienvenues ! N'hésitez pas à :
1. Fork le projet
2. Créer une branche pour votre fonctionnalité
3. Commiter vos changements
4. Pousser vers la branche
5. Ouvrir une Pull Request

## Licence

Ce projet est sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

## Auteur

- BlaMacfly - Développeur principal

## Remerciements

- La communauté World of Warcraft
- Les contributeurs du projet 