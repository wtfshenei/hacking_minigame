import time
import json
import os
import sys

# Non-blocking, echoing, cross-platform input with timeout
try:
    import msvcrt

    def timed_input(prompt, timeout):
        sys.stdout.write(prompt)
        sys.stdout.flush()
        input_str = ''
        start = time.time()
        while True:
            if msvcrt.kbhit():
                char = msvcrt.getwch()
                if char in ('\r', '\n'):
                    sys.stdout.write('\n')
                    return input_str
                elif char == '\b':
                    if input_str:
                        input_str = input_str[:-1]
                        sys.stdout.write('\b \b')
                else:
                    input_str += char
                    sys.stdout.write(char)
                sys.stdout.flush()
            if timeout is not None and time.time() - start >= timeout:
                sys.stdout.write('\n')
                return None
            time.sleep(0.1)
except ImportError:
    import termios
    import tty
    import fcntl

    def timed_input(prompt, timeout):
        sys.stdout.write(prompt)
        sys.stdout.flush()
        input_str = ''
        start = time.time()
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        old_flags = fcntl.fcntl(fd, fcntl.F_GETFL)
        try:
            tty.setcbreak(fd)
            fcntl.fcntl(fd, fcntl.F_SETFL, old_flags | os.O_NONBLOCK)
            while True:
                try:
                    ch = sys.stdin.read(1)
                except (IOError, OSError):
                    ch = ''
                if ch:
                    if ch in ('\n', '\r'):
                        sys.stdout.write('\n')
                        return input_str
                    elif ch == '\x7f':
                        if input_str:
                            input_str = input_str[:-1]
                            sys.stdout.write('\b \b')
                    else:
                        input_str += ch
                        sys.stdout.write(ch)
                    sys.stdout.flush()
                if timeout is not None and time.time() - start >= timeout:
                    sys.stdout.write('\n')
                    return None
                time.sleep(0.1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            fcntl.fcntl(fd, fcntl.F_SETFL, old_flags)

import pygame
from anims import loading_bar
from admin_panel import admin_menu

# --- Global blocking flag to disable inactivity monitoring ---
is_blocking = False

# --- Load settings and command data ---
base_path = os.path.dirname(os.path.abspath(__file__))


def load_settings():
    with open(os.path.join(base_path, "settings.json"), "r", encoding="utf-8") as f:
        return json.load(f)


def load_commands():
    with open(os.path.join(base_path, "commands.json"), "r", encoding="utf-8") as f:
        return json.load(f)


settings = load_settings()
commands_data = load_commands()


def apply_settings():
    global SEQUENCE, MAX_ERRORS, ALARM_DURATION, GLOBAL_TIMER
    global BLOCK_TIME_ON_ALARM, VICTORY_DISPLAY_TIME, VICTORY_CODE, INACTIVITY_TIMEOUT, commands_data
    seq_val = settings["sequence"]["value"]
    SEQUENCE = seq_val if isinstance(seq_val, list) else [seq_val]
    MAX_ERRORS = settings["max_errors"]["value"]
    ALARM_DURATION = settings["alarm_duration"]["value"]
    GLOBAL_TIMER = settings["global_timer"]["value"]
    BLOCK_TIME_ON_ALARM = settings["block_time_on_alarm"]["value"]
    VICTORY_DISPLAY_TIME = settings["victory_code_display_time"]["value"]
    VICTORY_CODE = settings["victory_code"]["value"]
    INACTIVITY_TIMEOUT = settings["inactivity_timeout"]["value"]
    # Reload commands data to apply any delay modifications
    commands_data = load_commands()


apply_settings()


def format_time(seconds):
    minutes = seconds // 60
    sec = seconds % 60
    return f"{int(minutes):02}:{int(sec):02}"


def format_duration(seconds):
    if seconds < 60:
        return f"{seconds} secondes"
    if seconds % 60 == 0:
        return f"{seconds // 60} minutes"
    minutes = seconds // 60
    sec = seconds % 60
    return f"{minutes}m {sec}s"


def print_intro():
    print("""
*** TERMINAL DE COFFRE-SYDNEY-S7E35810 ***
Tape 'help' pour voir la liste des commandes disponibles.
""")


def play_alarm():
    pygame.mixer.init()
    sound_path = os.path.join(base_path, "assets", "alarme.wav")
    alarm_sound = pygame.mixer.Sound(sound_path)
    channel = alarm_sound.play(-1)
    print("\nALAAAAAAARME !")
    for t in range(ALARM_DURATION, 0, -1):
        print(f"  ... {t}")
        time.sleep(1)
    channel.stop()
    print("\n🚨 ALARME DÉCLÉNCHÉE 🚨")


def show_help():
    print("\nCommandes disponibles :")
    for cmd, data in commands_data["commands"].items():
        if not data.get("hidden", False):
            print(f"- {cmd} : {data['desc']}")
    print()


def reset_game():
    return {"step": 0, "errors": 0, "alarm": False, "start_time": None}


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


def main():
    global is_blocking, settings
    game = reset_game()
    print_intro()

    while True:
        # Check global timer
        if game["start_time"]:
            elapsed = int(time.time() - game["start_time"])
            remaining = max(GLOBAL_TIMER - elapsed, 0)
            print(f"Durée session restante : {format_time(remaining)}")
            if remaining == 0:
                game["alarm"] = True

        # Input with inactivity timeout
        if not is_blocking and game["start_time"] and INACTIVITY_TIMEOUT > 0:
            timeout = INACTIVITY_TIMEOUT
        else:
            timeout = None
        cmd_raw = timed_input("> ", timeout)
        if cmd_raw is None:
            print("\n Session expirée pour cause d'inactivité.")
            time.sleep(2)
            clear_screen()
            game = reset_game()
            print_intro()
            continue

        cmd = cmd_raw.strip().lower()
        if not game["start_time"]:
            game["start_time"] = time.time()

        # Always-allowed commands
        if cmd == "help":
            show_help()
            continue
        if cmd == "agartha":
            result = admin_menu(os.path.join(base_path, "settings.json"))
            settings = load_settings()
            apply_settings()
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

        # Alarm state
        if game["alarm"]:
            is_blocking = True
            play_alarm()
            print(
                f"\nLe terminal est bloqué pour {format_duration(BLOCK_TIME_ON_ALARM)}...")
            loading_bar(BLOCK_TIME_ON_ALARM)
            is_blocking = False
            game = reset_game()
            print_intro()
            continue

        # Unknown command
        if cmd not in commands_data["commands"]:
            print("Commande inconnue. Tape 'help' pour obtenir de l'aide.")
            game["errors"] += 1
            if game["errors"] >= MAX_ERRORS:
                game["alarm"] = True
                is_blocking = True
                play_alarm()
                print(
                    f"\nLe terminal est bloqué pour {format_duration(BLOCK_TIME_ON_ALARM)}...")
                loading_bar(BLOCK_TIME_ON_ALARM)
                is_blocking = False
                game = reset_game()
                print_intro()
            continue

        # Command delay
        delay = commands_data["commands"][cmd].get("delay", 0)
        if delay > 0:
            is_blocking = True
            print(f"Traitement de la commande '{cmd}' en cours...")
            loading_bar(delay)
            is_blocking = False

        # Sequence validation
        if cmd != SEQUENCE[game["step"]]:
            print(f"Commande incorrecte à ce stade ({cmd}).")
            game["errors"] += 1
            if game["errors"] >= MAX_ERRORS:
                game["alarm"] = True
                is_blocking = True
                play_alarm()
                print(
                    f"\nLe terminal est bloqué pour {format_duration(BLOCK_TIME_ON_ALARM)}...")
                loading_bar(BLOCK_TIME_ON_ALARM)
                is_blocking = False
                clear_screen()
                game = reset_game()
                print_intro()
            continue

        # Correct command
        game["step"] += 1
        print(
            f"Commande acceptée ({cmd}). Progression : {game['step']}/{len(SEQUENCE)}")
        if game["step"] == len(SEQUENCE):
            print("\n--- PIRATAGE RÉUSSI ---")
            print(f"Code à transmettre au MJ : {VICTORY_CODE}")
            print(
                f"(Portes ouvertes: {format_duration(VICTORY_DISPLAY_TIME)})")
            is_blocking = True
            loading_bar(VICTORY_DISPLAY_TIME)
            is_blocking = False
            clear_screen()
            game = reset_game()
            print_intro()
            continue


if __name__ == "__main__":
    main()
