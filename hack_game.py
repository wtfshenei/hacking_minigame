import time
import json
import os
import pygame
from anims import loading_bar
from admin_panel import admin_menu

# --- Load settings and command data ---
base_path = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(base_path, "settings.json"), "r", encoding="utf-8") as f:
    settings = json.load(f)

with open(os.path.join(base_path, "commands.json"), "r", encoding="utf-8") as f:
    commands_data = json.load(f)

SEQUENCE = settings["sequence"]["value"]
MAX_ERRORS = settings["max_errors"]["value"]
ALARM_DURATION = settings["alarm_duration"]["value"]
GLOBAL_TIMER = settings["global_timer"]["value"]


def format_time(seconds):
    minutes = seconds // 60
    sec = seconds % 60
    return f"{int(minutes):02}:{int(sec):02}"


def print_intro():
    print("""\n*** TERMINAL DE PC-SYDNEY ***
Tape 'help' pour voir la liste des commandes disponibles.
""")


def play_alarm():
    pygame.mixer.init()
    sound_path = os.path.join(base_path, "assets", "alarme.wav")
    alarm_sound = pygame.mixer.Sound(sound_path)
    channel = alarm_sound.play(-1)  # -1 = infinite loop

    print("\nALAAAAAAARME !")
    duration = ALARM_DURATION
    for t in range(duration, 0, -1):
        print(f"  ... {t}")
        time.sleep(1)

    channel.stop()
    print("\n🚨 ALARME DÉCLENCHÉE 🚨")


def show_help():
    print("\nCommandes disponibles :")
    for cmd, data in commands_data["commands"].items():
        if not data.get("hidden", False):
            print(f"- {cmd} : {data['desc']}")
    print()


def reset_game():
    return {
        "step": 0,
        "errors": 0,
        "alarm": False,
        "start_time": None
    }


def reload_settings():
    with open(os.path.join(base_path, "settings.json"), "r", encoding="utf-8") as f:
        return json.load(f)


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


def main():
    global GLOBAL_TIMER, MAX_ERRORS, ALARM_DURATION, SEQUENCE
    game = reset_game()
    print_intro()

    while True:
        if game["start_time"]:
            elapsed = int(time.time() - game["start_time"])
            remaining = max(GLOBAL_TIMER - elapsed, 0)
            print(f"Durée session restante : {format_time(remaining)}")
            if remaining == 0:
                game["alarm"] = True

        cmd = input("> ").strip().lower()

        if not game["start_time"]:
            game["start_time"] = time.time()

        # Commands that should never count as errors or apply delay
        if cmd == "help":
            show_help()
            continue

        if cmd == "agartha":
            result = admin_menu(os.path.join(base_path, "settings.json"))
            settings = reload_settings()
            SEQUENCE = settings["sequence"]["value"]
            MAX_ERRORS = settings["max_errors"]["value"]
            ALARM_DURATION = settings["alarm_duration"]["value"]
            GLOBAL_TIMER = settings["global_timer"]["value"]
            if result == "reset":
                print("\n*** TERMINAL RÉINITIALISÉ PAR L'ADMIN ***\n")
                clear_screen()
                game = reset_game()
                print_intro()
            continue

        if cmd == "reset":
            print("\n*** TERMINAL RÉINITIALISÉ ***\n")
            clear_screen()
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
            print(f"Traitement de la commande '{cmd}' en cours...")
            loading_bar(delay)

        # Exceptions
        if cmd not in SEQUENCE or cmd != SEQUENCE[game["step"]]:
            if cmd not in ("help", "agartha", "reset"):
                print(f"Commande incorrecte à ce stade ({cmd}).")
                game["errors"] += 1
                if game["errors"] >= MAX_ERRORS:
                    game["alarm"] = True
                    play_alarm()
                    print("\nLe terminal va redémarrer...\n")
                    time.sleep(5)
                    clear_screen()
                    game = reset_game()
                    print_intro()
            continue

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
                clear_screen()
                game = reset_game()
                print_intro()
            continue


if __name__ == "__main__":
    main()
