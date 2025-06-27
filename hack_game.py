import time
import json
import os

# --- Chargement des fichiers ---
base_path = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(base_path, "settings.json"), "r", encoding="utf-8") as f:
    settings = json.load(f)

with open(os.path.join(base_path, "commands.json"), "r", encoding="utf-8") as f:
    commands_data = json.load(f)

SEQUENCE = settings["sequence"]
MAX_ERRORS = settings["max_errors"]
ALARM_DURATION = settings["alarm_duration"]


def print_intro():
    print("""\n*** TERMINAL DE PC-SYDNEY ***
Tape \033[1mhelp\033[0m pour la liste des commandes disponibles.
""")


def play_alarm():
    print("\nALAAAAAAAAARME !")
    for t in range(ALARM_DURATION, 0, -1):
        print(f"  ... {t}")
        time.sleep(1)
    print("\n🚨 ALARME DÉCLENCHÉE 🚨")


def show_help():
    print("\nCommandes disponibles :")
    for cmd, desc in commands_data["commands"].items():
        print(f"- {cmd} : {desc}")


def reset_game():
    return {
        "step": 0,
        "errors": 0,
        "alarm": False
    }


def main():
    game = reset_game()
    print_intro()

    while True:
        cmd = input("> ").strip().lower()

        if cmd == "help":
            show_help()
            continue

        if cmd == "reset":
            print("\n*** TERMINAL RÉINITIALISÉ ***\n")
            game = reset_game()
            print_intro()
            continue

        if game["alarm"]:
            play_alarm()
            print("\nLe terminal va redémarrer...\n")
            time.sleep(5)
            game = reset_game()
            print_intro()
            continue

        if cmd not in commands_data["commands"]:
            print("Commande inconnue. Tape 'help' si besoin.")
            game["errors"] += 1
            if game["errors"] >= MAX_ERRORS:
                game["alarm"] = True
                play_alarm()
                print("\nLe terminal va redémarrer...\n")
                time.sleep(5)
                game = reset_game()
                print_intro()
            continue

        if cmd == SEQUENCE[game["step"]]:
            game["step"] += 1
            print(
                f"Commande acceptée ({cmd}). Progression : {game['step']}/{len(SEQUENCE)}")
            if game["step"] == len(SEQUENCE):
                print("\n--- HACK RÉUSSI ---")
                print("QR Code généré : murder_clue.png")
                print("Réinitialisation dans 10 secondes...")
                time.sleep(10)
                game = reset_game()
                print_intro()
            continue

        print(f"Commande incorrecte à ce stade ({cmd}).")
        game["errors"] += 1
        if game["errors"] >= MAX_ERRORS:
            game["alarm"] = True
            play_alarm()
            print("\nLe terminal va redémarrer...\n")
            time.sleep(5)
            game = reset_game()
            print_intro()


if __name__ == "__main__":
    main()
