import time
import os
import sys
import pygame
from anims import loading_bar
from admin_panel import admin_menu
from config_manager import ConfigManager
from console import timed_input, clear_screen, print_intro

# Initialize configuration manager
base_path = os.path.dirname(os.path.abspath(__file__))
config = ConfigManager(base_path)


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
        print("\n🚨 ALARME DÉCLÉNCHÉE 🚨")

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
        clear_screen()
        self.reset()
        print_intro()

    def run(self):
        """Main game loop."""
        print_intro()
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
                clear_screen()
                self.reset()
                print_intro()
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
                    clear_screen()
                    self.reset()
                    print_intro()
                continue
            if cmd == "reset":
                print("\n*** TERMINAL RÉINITIALISÉ ***\n")
                clear_screen()
                self.reset()
                print_intro()
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
                clear_screen()
                self.reset()
                print_intro()


if __name__ == "__main__":
    Game(config).run()
