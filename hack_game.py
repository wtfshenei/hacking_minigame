import time
import json
import os
from anims import loading_bar

# --- Load settings and command data ---
base_path = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(base_path, "settings.json"), "r", encoding="utf-8") as f:
    settings = json.load(f)

with open(os.path.join(base_path, "commands.json"), "r", encoding="utf-8") as f:
    commands_data = json.load(f)

SEQUENCE = settings["sequence"]
MAX_ERRORS = settings["max_errors"]
ALARM_DURATION = settings["alarm_duration"]


def print_intro():
    print("""\n*** TERMINAL DE PIRATAGE ***
Tape 'help' pour voir la liste des commandes disponibles.
""")


def play_alarm():
    print("\nALAAAAAAARME !")
    for t in range(ALARM_DURATION, 0, -1):
        print(f"  ... {t}")
        time.sleep(1)
    print("\n🚨 ALARME DÉCLENCHÉE 🚨")


def show_help():
    print("\nCommandes disponibles :")
    for cmd, data in commands_data["commands"].items():
        print(f"- {cmd} : {data['desc']}")
    print()


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

        # Commands that should never count as errors or apply delay
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
            print("Commande inconnue. Tape 'help' pour obtenir de l'aide.")
            game["errors"] += 1
            if game["errors"] >= MAX_ERRORS:
                game["alarm"] = True
                play_alarm()
                print("\nLe terminal va redémarrer...\n")
                time.sleep(5)
                game = reset_game()
                print_intro()
            continue

        # Apply delay on all known commands (even wrong ones)
        delay = commands_data["commands"][cmd].get("delay", 0)
        if delay > 0:
            print(f"Traitement de la commande '{cmd}'...")
            loading_bar(delay)

        # Check if it's the correct command in the sequence
        if cmd == SEQUENCE[game["step"]]:
            game["step"] += 1
            print(
                f"Commande acceptée ({cmd}). Progression : {game['step']}/{len(SEQUENCE)}")
            if game["step"] == len(SEQUENCE):
                print("\n--- PIRATAGE RÉUSSI ---")
                print("QR Code généré : murder_clue.png")
                print("Réinitialisation dans 10 secondes...")
                time.sleep(10)
                game = reset_game()
                print_intro()
            continue

        # Wrong but valid command
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
