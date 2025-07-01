import json
import os

class ConfigManager:
    """
    Load and manage settings.json and commands.json.
    Usage:
        config = ConfigManager(base_path)
        seq = config.sequence
        delay = config.delay_for('cmd')
        config._settings[...] = ...
        config.save_settings()
        config.reload()
    """
    def __init__(self, base_path):
        self.settings_path = os.path.join(base_path, "settings.json")
        self.commands_path = os.path.join(base_path, "commands.json")
        self.reload()

    def reload(self):
        with open(self.settings_path, 'r', encoding='utf-8') as f:
            self._settings = json.load(f)
        with open(self.commands_path, 'r', encoding='utf-8') as f:
            self._commands = json.load(f)

    @property
    def sequence(self):
        seq = self._settings.get("sequence", {}).get("value")
        return seq if isinstance(seq, list) else [seq]

    @property
    def max_errors(self):
        return self._settings.get("max_errors", {}).get("value", 0)

    @property
    def alarm_duration(self):
        return self._settings.get("alarm_duration", {}).get("value", 0)

    @property
    def global_timer(self):
        return self._settings.get("global_timer", {}).get("value", 0)

    @property
    def block_time_on_alarm(self):
        return self._settings.get("block_time_on_alarm", {}).get("value", 0)

    @property
    def victory_display_time(self):
        return self._settings.get("victory_code_display_time", {}).get("value", 0)

    @property
    def victory_code(self):
        return self._settings.get("victory_code", {}).get("value", "")

    @property
    def inactivity_timeout(self):
        return self._settings.get("inactivity_timeout", {}).get("value", 0)

    def delay_for(self, cmd):
        return self._commands.get("commands", {}).get(cmd, {}).get("delay", 0)

    def all_commands(self):
        return self._commands.get("commands", {}).items()

    def save_settings(self):
        with open(self.settings_path, 'w', encoding='utf-8') as f:
            json.dump(self._settings, f, indent=2, ensure_ascii=False)

    def save_commands(self):
        with open(self.commands_path, 'w', encoding='utf-8') as f:
            json.dump(self._commands, f, indent=2, ensure_ascii=False)
