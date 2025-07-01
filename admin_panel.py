import os
from config_manager import ConfigManager

# Initialize the configuration manager
# base_path is used by ConfigManager to locate JSON files
base_path = os.path.dirname(os.path.abspath(__file__))
config = ConfigManager(base_path)


def admin_menu(settings_path):
    """
    Display the administrator menu and return 'reset' if the session should be reset.
    """
    while True:
        print("\n=== MENU ADMINISTRATEUR ===")
        print("1. Modifier les réglages")
        print("2. Modifier les temps de délai des commandes")
        print("3. Réinitialiser la session de hack")
        print("4. Quitter")
        choice = input("> ").strip()
        if choice == "1":
            edit_settings()
        elif choice == "2":
            edit_command_delays()
        elif choice == "3":
            confirm = input(
                "Confirmer la réinitialisation de la session ? (oui/non) : ").lower()
            if confirm == "oui":
                return "reset"
        elif choice == "4":
            break
        else:
            print("Choix invalide.")


def edit_settings():
    """
    Allow the administrator to edit general settings.
    """
    keys = list(config._settings.keys())
    while True:
        print("\n--- Réglages ---")
        for idx, key in enumerate(keys, 1):
            desc = config._settings[key].get("desc", key)
            val = config._settings[key]["value"]
            print(f"{idx}. {desc} (actuel : {val})")
        print(f"{len(keys)+1}. Retour")

        choice = input("> ").strip()
        if not choice.isdigit():
            print("Entrée invalide.")
            continue
        idx = int(choice)
        if idx == len(keys) + 1:
            break
        if 1 <= idx <= len(keys):
            key = keys[idx - 1]
            # Special handling for 'sequence'
            if key == "sequence":
                new_seq = input(
                    f"Entrez les commandes séparées par des virgules pour '{key}' : ").strip()
                seq_list = [cmd.strip()
                            for cmd in new_seq.split(",") if cmd.strip()]
                config._settings[key]["value"] = seq_list
            else:
                new_val = input(f"Nouvelle valeur pour '{key}' : ").strip()
                if new_val.isdigit():
                    config._settings[key]["value"] = int(new_val)
                else:
                    try:
                        config._settings[key]["value"] = float(new_val)
                    except ValueError:
                        config._settings[key]["value"] = new_val
            config.save_settings()
            config.reload()
            print("Valeur mise à jour.")
        else:
            print("Choix invalide.")


def edit_command_delays():
    """
    Allow the administrator to edit the delay for each command.
    """
    commands = config._commands.get("commands", {})
    keys = list(commands.keys())
    while True:
        print("\n--- Délais des commandes ---")
        for idx, cmd in enumerate(keys, 1):
            desc = commands[cmd].get("desc", cmd)
            delay = commands[cmd].get("delay", 0)
            print(f"{idx}. {cmd} : {desc} (délai actuel : {delay}s)")
        print(f"{len(keys)+1}. Retour")

        choice = input("> ").strip()
        if not choice.isdigit():
            print("Entrée invalide.")
            continue
        idx = int(choice)
        if idx == len(keys) + 1:
            break
        if 1 <= idx <= len(keys):
            cmd_key = keys[idx - 1]
            new_delay = input(
                f"Nouveau délai (en secondes) pour '{cmd_key}' : ").strip()
            if new_delay.isdigit():
                commands[cmd_key]["delay"] = int(new_delay)
                config.save_commands()
                config.reload()
                print("Délai mis à jour.")
            else:
                print("Veuillez entrer un entier valide.")
        else:
            print("Choix invalide.")
