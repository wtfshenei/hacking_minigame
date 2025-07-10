# HACKING MINIGAME

[FR 🇫🇷](#fr---description-du-jeu) | [ENG 🇬🇧](#eng---game-description)

---

## 📌 FR — Description du jeu

### 🎮 Présentation

Ce mini-jeu de hacking simule un terminal dans lequel le joueur doit découvrir la **bonne séquence de commandes** pour réussir à "pirater" un coffre sécurisé.  
Le jeu introduit des mécaniques de pression, d’erreur et de temps pour renforcer l'immersion.

### ⚙️ Fonctionnalités principales

- ✅ **Séquence personnalisable** via `settings.json`
- ⏳ **Temps global** limité pour réussir le piratage
- ❌ **Déclenchement d’une alarme** après un nombre d’erreurs défini
- 🔐 **Blocage du terminal** pendant un certain temps en cas d'échec
- 🕒 **Affichage du code de victoire** pour une durée limitée
- 🔇 **Gestion de l’inactivité** avec timeout dynamique
- 🎵 **Alarme sonore** (fichier `alarme.wav` dans le dossier `assets`)
- 📊 **Commandes avec délai d'exécution**, pour ajouter du stress
- 🧠 **Commandes cachées**, invisibles dans l’aide (`help`)
- 👨‍💼 **Commande admin secrète** (`agartha`) pour :
  - Modifier dynamiquement les réglages
  - Réinitialiser une session
  - Modifier le code de victoire
- 🎲 **Script de shuffle** (`shuffle_commands.py`) pour réordonner aléatoirement les commandes

---

### 🗃️ Structure des fichiers

| Fichier               | Rôle |
|-----------------------|------|
| `hack_game.py`        | Cœur du jeu, logique principale |
| `settings.json`       | Fichier de configuration des règles (timer, erreurs, etc.) |
| `commands.json`       | Liste des commandes possibles et leurs métadonnées |
| `admin_panel.py`      | Menu admin accessible via la commande `agartha` |
| `anims.py`            | Gestion des animations dans le terminal |
| `console.py`          | Fonctions transverses (input avec timeout, clear, intro) |
| `config_manager.py`   | Outils de lecture/écriture propre des fichiers JSON |
| `shuffle_commands.py` | Script pour mélanger l’ordre des commandes visibles |
| `assets/alarme.wav`   | Son de l’alarme en cas d’échec |

---

### 🛠️ Personnalisation via `settings.json`

Exemples de réglages modifiables :

```json
{
  "max_errors": {
    "value": 3,
    "desc": "Nombre maximal d'erreurs avant déclenchement de l'alarme"
  },
  "global_timer": {
    "value": 180,
    "desc": "Temps total (en secondes) avant échec automatique"
  },
  "victory_code": {
    "value": "S3CURE-42",
    "desc": "Code à transmettre au MJ en cas de réussite"
  }
}
```

---

## 🧠 Conseils pour MJ

- Le MJ peut accéder au menu admin (`agartha`) **directement dans le terminal** pour adapter la difficulté ou remettre à zéro une session.
- Le code de victoire n’est affiché que pendant X secondes — prévoir de le noter rapidement.
- Pour rendre chaque session unique, pensez à réordonner les commandes via `shuffle_commands.py`.
- Lancer le jeu en ouvrant un terminal et taper `python hack_game.py`.

---

## ENG — Game Description

### 🎮 Overview

This hacking minigame simulates a secure terminal that the player must break into by discovering the correct **sequence of commands**.  
It features stress mechanics such as timers, execution delays, errors, and sound alarms.

### ⚙️ Main Features

- ✅ **Customizable sequence** through `settings.json`
- ⏳ **Global timer** to increase pressure
- ❌ **Alarm** triggered after too many mistakes
- 🔐 **Terminal lockout** on failure (custom duration)
- 🕒 **Victory code displayed** for a limited time
- 🔇 **Inactivity detection** with timeout
- 🎵 **Alarm sound** (`alarme.wav` in `assets`)
- 📊 **Command execution delay** per command
- 🧠 **Hidden commands**, not shown in `help`
- 👨‍💼 **Secret admin command** (`agartha`) allows:
  - Dynamic settings editing
  - Session reset
  - Manual victory code edit
- 🎲 **Command shuffle script** (`shuffle_commands.py`) to randomize visible command order

---

### 🗃️ File Structure

| File                   | Description |
|------------------------|-------------|
| `hack_game.py`         | Main game logic |
| `settings.json`        | Rules configuration (timers, max errors, etc.) |
| `commands.json`        | Command definitions with metadata |
| `admin_panel.py`       | Admin menu, triggered by the `agartha` command |
| `anims.py`             | Loading and visual terminal animations |
| `console.py`           | Terminal intro, clear screen, timeout input |
| `config_manager.py`    | Utilities for reading/writing config JSONs |
| `shuffle_commands.py`  | Script to shuffle visible command order |
| `assets/alarme.wav`    | Alarm sound played on failure |

---

### 🛠️ Example `settings.json`

```json
{
  "max_errors": {
    "value": 3,
    "desc": "Maximum number of errors before triggering the alarm"
  },
  "global_timer": {
    "value": 180,
    "desc": "Total time (in seconds) before the session fails"
  },
  "victory_code": {
    "value": "S3CURE-42",
    "desc": "Code displayed on success"
  }
}
```

---

### 🧠 Tips for Game Masters

- The GM can enter the secret `agartha` command in terminal to tweak game settings at any moment.
- The victory code is displayed only for a limited duration — be quick to write it down.
- Use `shuffle_commands.py` to make each run more unpredictable.
- Start the game by opening a terminal and typing `python hack_game.py`.

---
