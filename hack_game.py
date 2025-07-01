import time
import os
import sys
import pygame
from anims import loading_bar
from admin_panel import admin_menu
from config_manager import ConfigManager

# Initialize configuration manager
base_path = os.path.dirname(os.path.abspath(__file__))
config = ConfigManager(base_path)

# --- Global blocking flag to disable inactivity monitoring ---
is_blocking = False

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
    import termios, tty, fcntl
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

def format_time(seconds):
    """Format seconds as MM:SS."""
    minutes = seconds // 60
    sec = seconds % 60
    return f"{int(minutes):02}:{int(sec):02}"

def format_duration(seconds):
    """Format seconds as human readable duration."""
    if seconds < 60:
        return f"{seconds} seconds"
    if seconds % 60 == 0:
        return f"{seconds // 60} minutes"
    minutes = seconds // 60
    sec = seconds % 60
    return f"{minutes}m {sec}s"

def print_intro():
    """Print the game introduction banner."""
    print("""
*** COFFRE-SYDNEY-S7E35810 TERMINAL ***
Type 'help' to view available commands.
""")

def play_alarm():
    """Play the alarm sound and countdown."""
    pygame.mixer.init()
    sound_path = os.path.join(base_path, "assets", "alarme.wav")
    alarm_sound = pygame.mixer.Sound(sound_path)
    channel = alarm_sound.play(-1)  # Play in loop
    print("\nALAAAAAAARME !")
    for t in range(config.alarm_duration, 0, -1):
        print(f"  ... {t}")
        time.sleep(1)
    channel.stop()
    print("\n🚨 ALARM TRIGGERED 🚨")

def show_help():
    """Display the help text for all non-hidden commands."""
    print("\nAvailable commands:")
    for cmd, data in config.all_commands():
        if not data.get("hidden", False):
            print(f"- {cmd}: {data.get('desc', '')}")
    print()

def reset_game():
    """Reset game state to initial values."""
    return {"step": 0, "errors": 0, "alarm": False, "start_time": None}

def clear_screen():
    """Clear the console screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def main():
    global is_blocking
    game = reset_game()
    print_intro()

    while True:
        # Check global timer
        if game["start_time"]:
            elapsed = int(time.time() - game["start_time"])
            remaining = max(config.global_timer - elapsed, 0)
            print(f"Session time remaining: {format_time(remaining)}")
            if remaining == 0:
                game["alarm"] = True

        # Determine input timeout for inactivity
        if not is_blocking and game["start_time"] and config.inactivity_timeout > 0:
            timeout = config.inactivity_timeout
        else:
            timeout = None

        cmd_raw = timed_input("> ", timeout)
        if cmd_raw is None:
            print("\nSession expired due to inactivity.")
            time.sleep(2)
            clear_screen()
            game = reset_game()
            print_intro()
            continue

        cmd = cmd_raw.strip().lower()
        if not game["start_time"]:
            game["start_time"] = time.time()

        # Always allowed commands
        if cmd == "help":
            show_help()
            continue
        if cmd == "agartha":
            result = admin_menu(os.path.join(base_path, "settings.json"))
            config.reload()
            if result == "reset":
                print("\n*** TERMINAL RESET BY ADMIN ***\n")
                clear_screen()
                game = reset_game()
                print_intro()
            continue
        if cmd == "reset":
            print("\n*** TERMINAL RESET ***\n")
            clear_screen()
            game = reset_game()
            print_intro()
            continue

        # Alarm handling
        if game["alarm"]:
            is_blocking = True
            play_alarm()
            block_time = config.block_time_on_alarm
            print(f"\nTerminal locked for {format_duration(block_time)}...")
            loading_bar(block_time)
            is_blocking = False
            game = reset_game()
            print_intro()
            continue

        # Unknown command
        if cmd not in dict(config.all_commands()):
            print("Unknown command. Type 'help' for assistance.")
            game["errors"] += 1
            if game["errors"] >= config.max_errors:
                game["alarm"] = True
                is_blocking = True
                play_alarm()
                block_time = config.block_time_on_alarm
                print(f"\nTerminal locked for {format_duration(block_time)}...")
                loading_bar(block_time)
                is_blocking = False
                game = reset_game()
                print_intro()
            continue

        # Command delay
        delay = config.delay_for(cmd)
        if delay > 0:
            is_blocking = True
            print(f"Processing command '{cmd}'...")
            loading_bar(delay)
            is_blocking = False

        # Sequence validation
        expected = config.sequence[game["step"]]
        if cmd != expected:
            print(f"Incorrect command at this stage ({cmd}).")
            game["errors"] += 1
            if game["errors"] >= config.max_errors:
                game["alarm"] = True
                is_blocking = True
                play_alarm()
                block_time = config.block_time_on_alarm
                print(f"\nTerminal locked for {format_duration(block_time)}...")
                loading_bar(block_time)
                is_blocking = False
                clear_screen()
                game = reset_game()
                print_intro()
            continue

        # Correct command
        game["step"] += 1
        print(f"Command accepted ({cmd}). Progress: {game['step']}/{len(config.sequence)}")
        if game["step"] == len(config.sequence):
            print("\n--- HACK SUCCESSFUL ---")
            print(f"Code for GM: {config.victory_code}")
            print(f"(Doors remain open for: {format_duration(config.victory_display_time)})")
            is_blocking = True
            loading_bar(config.victory_display_time)
            is_blocking = False
            clear_screen()
            game = reset_game()
            print_intro()
            continue

if __name__ == "__main__":
    main()
