# data_allocator/config_handler.py

import os
import json

from data_allocator.constants import CONFIG_PATH
from data_allocator.exceptions import ConfigHandlerException

class ConfigHandler:
    def __init__(self, config_path=CONFIG_PATH):
        """
        Initialize and load configuration.
        """
        self._config = None
        self.config_path = config_path
        self.load_config(config_path=config_path)
        self.validate_paths()

    def load_config(self, config_path):
        """
        Loads the configuration from the specified CONFIG_PATH.
        """
        try:
            with open(config_path, "r") as file:
                self._config = json.load(file)
        except FileNotFoundError:
            raise FileNotFoundError(f"[ERROR] Configuration file '{CONFIG_PATH}' not found.")
        except json.JSONDecodeError:
            raise json.JSONDecodeError("[ERROR] Invalid JSON format in the configuration file {}.")

    def validate_paths(self):
        """
        Validates the mounted paths specified in the configuration.
        Checks if each path is accessible and is a mount point.
        """
        drives = self._config.get("drives", {})
        for name, path in drives.items():
            if not os.path.exists(path):
                raise ConfigHandlerException(f"Path '{path}' does not exist.")

    def get_drive_paths(self):
        """
        Returns the drive paths from the configuration.
        """
        return self._config.get("drives", {})

    def reload_config(self):
        """
        Reloads the configuration at runtime.
        """
        self.load_config(self.config_path)
        self.validate_paths()

