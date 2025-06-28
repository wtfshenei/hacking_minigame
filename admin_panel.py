import json
import os


def load_settings(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_settings(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)


def admin_menu(settings_path):
    settings = load_settings(settings_path)
    while True:
        print("\n=== MENU ADMINISTRATEUR ===")
        print("1. Modifier les réglages")
        print("2. Réinitialiser la session de piratage")
        print("3. Quitter")
        choice = input("> ").strip()
        if choice == "1":
            edit_settings(settings, settings_path)
        elif choice == "2":
            confirm = input(
                "Confirmer le reset de la session ? (oui/non) : ").lower()
            if confirm == "oui":
                return "reset"
        elif choice == "3":
            break
        else:
            print("Choix invalide.")


def edit_settings(settings, path):
    keys = list(settings.keys())
    while True:
        print("\n--- Réglages ---")
        for idx, key in enumerate(keys, 1):
            desc = settings[key].get("desc", key)
            val = settings[key]["value"]
            print(f"{idx}. {desc} (actuel: {val})")
        print(f"{len(keys)+1}. Retour")

        choice = input("> ").strip()
        if not choice.isdigit():
            print("Entrée invalide.")
            continue
        choice = int(choice)
        if choice == len(keys) + 1:
            break
        if 1 <= choice <= len(keys):
            key = keys[choice - 1]
            new_val = input(f"Nouvelle valeur pour '{key}' : ").strip()
            try:
                val = int(new_val) if new_val.isdigit() else new_val
                settings[key]["value"] = val
                save_settings(path, settings)
                print("Valeur mise à jour.")
            except Exception as e:
                print(f"Erreur lors de la mise à jour : {e}")
        else:
            print("Choix invalide.")
