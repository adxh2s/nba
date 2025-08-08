import json
import os
from typing import Any

import yaml


class FileTools:
    """
    Utilities for loading and saving JSON and YAML files.
    """

    @staticmethod
    def load_json(filepath: str) -> dict[str, Any]:
        """
        Load JSON file.

        Args:
            filepath: Path to JSON file.

        Returns:
            Parsed content as a dict.
        """
        with open(filepath, encoding="utf-8") as f:
            return json.load(f)

    @staticmethod
    def load_yaml(filepath: str) -> dict[str, Any]:
        """
        Load YAML file.

        Args:
            filepath: Path to YAML file.

        Returns:
            Parsed content as a dict.
        """
        with open(filepath, encoding="utf-8") as f:
            return yaml.safe_load(f)

    @staticmethod
    def load_from(filepath: str) -> dict[str, Any]:
        """
        Load JSON or YAML file based on extension.

        Args:
            filepath: Path to configuration file.

        Returns:
            Parsed content as dict.

        Raises:
            FileNotFoundError: If file does not exist.
            ValueError: If extension is unsupported.
        """
        if not os.path.isfile(filepath):
            raise FileNotFoundError(f"File not found: {filepath}")

        ext = os.path.splitext(filepath)[1].lower()
        if ext == ".json":
            return FileTools.load_json(filepath)
        if ext in {".yaml", ".yml"}:
            return FileTools.load_yaml(filepath)
        raise ValueError(f"Unsupported file extension: {ext}")

    @staticmethod
    def save_json(data: dict, filepath: str) -> None:
        """
        Save dict to JSON file.

        Args:
            data: Data to save.
            filepath: Output file path.
        """
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    @staticmethod
    def save_yaml(data: dict, filepath: str) -> None:
        """
        Save dict to YAML file.

        Args:
            data: Data to save.
            filepath: Output file path.
        """
        with open(filepath, "w", encoding="utf-8") as f:
            yaml.dump(data, f)
