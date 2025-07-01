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

# --- Non-blocking, echoing, cross-platform input with timeout ---
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
            # set raw mode and non-blocking
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
                    elif ch == '\x7f':  # backspace
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
            # restore settings
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            fcntl.fcntl(fd, fcntl.F_SETFL, old_flags)


class Game:
    """Encapsulates the hacking game logic and state."""

    def __init__(self, config):
        self.config = config
        self.is_blocking = False
        self.reset()

    def reset(self):
        """Reset game state to initial values."""
        self.step = 0
        self.errors = 0
        self.alarm = False
        self.start_time = None

    def print_intro(self):
        """Print the game introduction banner."""
        print("""
*** TERMINAL DE COFFRE-SYDNEY-S7E35810 ***
Tape 'help' pour voir les commandes disponibles.
""")

    def format_time(self, seconds):
        """Format seconds as MM:SS."""
        minutes = seconds // 60
        sec = seconds % 60
        return f"{int(minutes):02}:{int(sec):02}"

    def format_duration(self, seconds):
        """Format seconds as human readable duration."""
        if seconds < 60:
            return f"{seconds} secondes"
        if seconds % 60 == 0:
            return f"{seconds // 60} minutes"
        minutes = seconds // 60
        sec = seconds % 60
        return f"{minutes}m {sec}s"

    def play_alarm(self):
        """Play the alarm sound and countdown."""
        pygame.mixer.init()
        sound_path = os.path.join(base_path, "assets", "alarme.wav")
        alarm_sound = pygame.mixer.Sound(sound_path)
        channel = alarm_sound.play(-1)
        print("\nALAAAAAAARME !")
        for t in range(self.config.alarm_duration, 0, -1):
            print(f"  ... {t}")
            time.sleep(1)
        channel.stop()
        print("\n🚨 ALARME DÉCLENCHÉE 🚨")

    def show_help(self):
        """Display the help text for all non-hidden commands."""
        print("\nCommandes disponibles :")
        for cmd, data in self.config.all_commands():
            if not data.get("hidden", False):
                print(f"- {cmd} : {data.get('desc', '')}")
        print()

    def trigger_alarm(self):
        """Handle full alarm flow: play, block, reset."""
        self.is_blocking = True
        self.play_alarm()
        block = self.config.block_time_on_alarm
        print(
            f"\nLe terminal est bloqué pour {self.format_duration(block)}...")
        loading_bar(block)
        self.is_blocking = False
        self.reset()
        self.print_intro()

    def run(self):
        """Main game loop."""
        self.print_intro()
        while True:
            # Check global timer
            if self.start_time:
                elapsed = int(time.time() - self.start_time)
                remaining = max(self.config.global_timer - elapsed, 0)
                print(
                    f"Durée session restante : {self.format_time(remaining)}")
                if remaining == 0:
                    self.alarm = True

            # Determine input timeout
            timeout = self.config.inactivity_timeout if (
                not self.is_blocking and self.start_time and self.config.inactivity_timeout > 0
            ) else None
            cmd_raw = timed_input("> ", timeout)
            if cmd_raw is None:
                print("\nSession expirée pour cause d'inactivité.")
                time.sleep(2)
                os.system('cls' if os.name == 'nt' else 'clear')
                self.reset()
                self.print_intro()
                continue

            cmd = cmd_raw.strip().lower()
            if not self.start_time:
                self.start_time = time.time()

            # Always allowed commands
            if cmd == "help":
                self.show_help()
                continue
            if cmd == "agartha":
                result = admin_menu(os.path.join(base_path, "settings.json"))
                self.config.reload()
                if result == "reset":
                    print("\n*** TERMINAL RÉINITIALISÉ PAR L'ADMIN ***\n")
                    os.system('cls' if os.name == 'nt' else 'clear')
                    self.reset()
                    self.print_intro()
                continue
            if cmd == "reset":
                print("\n*** TERMINAL RÉINITIALISÉ ***\n")
                os.system('cls' if os.name == 'nt' else 'clear')
                self.reset()
                self.print_intro()
                continue

            # Alarm state
            if self.alarm:
                self.trigger_alarm()
                continue

            # Unknown command
            if cmd not in dict(self.config.all_commands()):
                print("Commande inconnue. Tape 'help' pour obtenir de l'aide.")
                self.errors += 1
                if self.errors >= self.config.max_errors:
                    self.trigger_alarm()
                continue

            # Command delay
            delay = self.config.delay_for(cmd)
            if delay > 0:
                self.is_blocking = True
                print(f"Traitement de la commande '{cmd}' en cours...")
                loading_bar(delay)
                self.is_blocking = False

            # Sequence validation
            expected = self.config.sequence[self.step]
            if cmd != expected:
                print(f"Commande incorrecte à ce stade ({cmd}).")
                self.errors += 1
                if self.errors >= self.config.max_errors:
                    self.trigger_alarm()
                continue

            # Correct command
            self.step += 1
            print(
                f"Commande acceptée ({cmd}). Progression : {self.step}/{len(self.config.sequence)}")
            if self.step == len(self.config.sequence):
                print("\n--- PIRATAGE RÉUSSI ---")
                print(f"Code à transmettre au MJ : {self.config.victory_code}")
                print(
                    f"(Les portes restent ouvertes pour : {self.format_duration(self.config.victory_display_time)})")
                self.is_blocking = True
                loading_bar(self.config.victory_display_time)
                self.is_blocking = False
                os.system('cls' if os.name == 'nt' else 'clear')
                self.reset()
                self.print_intro()


if __name__ == "__main__":
    Game(config).run()
