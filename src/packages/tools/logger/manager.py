from __future__ import annotations

import logging
import os
from datetime import datetime

from packages.tools.file.path_utils import PathUtils


class LoggerManager:
    """
    Manage la création et la configuration d'un logger Python
    avec écriture dans un fichier UTF-8 et sortie console.

    Le logger utilise la bibliothèque standard `logging`,
    avec format personnalisé pour date, niveau et message.

    Attributes:
        log_dir (str): Répertoire où écrire les fichiers logs.
        app_name (str): Nom de l’application (utilisé dans le nom de fichier).
        script_name (str): Nom du script (utilisé dans le nom de fichier).
        log_ext (str): Extension du fichier log (défaut: 'log').
        project_root (str | None): Racine du projet pour contrôle des chemins.
        logger (logging.Logger): Instance logger configurée.
    """

    def __init__(
        self,
        log_dir: str,
        app_name: str,
        script_name: str,
        log_ext: str = "log",
        project_root: str | None = None,
    ):
        """
        Initialise LoggerManager et configure le logger.

        Args:
            log_dir (str): Répertoire de stockage des logs.
            app_name (str): Nom de l'application (pour nom fichier log).
            script_name (str): Nom du script (pour nom fichier log).
            log_ext (str, optional): Extension du fichier log. Defaults to
            "log".
            project_root (str | None, optional): Racine du projet pour valider
            chemin. Defaults to None.
        """
        self.log_dir = log_dir
        self.app_name = app_name
        self.script_name = script_name
        self.log_ext = log_ext
        self.project_root = project_root
        self.logger = self._init_logger()

    def _init_logger(self) -> logging.Logger:
        """
        Initialise et configure un logger avec handlers fichier et console.

        Vérifie que le chemin du dossier log et du fichier log sont
        sous la racine projet si définie.

        Returns:
            logging.Logger: Logger configuré.

        Raises:
            RuntimeError: Si log_dir ou log_path sont hors du projet root.
        """
        if self.project_root and not PathUtils.is_path_in_root(
            self.log_dir, self.project_root
        ):
            raise RuntimeError(
                f"Log directory {self.log_dir} outside project root "
                f"{self.project_root}"
            )

        os.makedirs(self.log_dir, exist_ok=True)

        date_str = datetime.now().strftime("%Y%m%d")
        filename = (
            f"{date_str}_{self.app_name}_{self.script_name}.{self.log_ext}"
        )
        log_path = os.path.join(self.log_dir, filename)

        if self.project_root and not PathUtils.is_path_in_root(
            log_path, self.project_root
        ):
            raise RuntimeError(
                f"Log file {log_path} outside project root {self.project_root}"
            )

        logger = logging.getLogger(self.app_name)
        logger.setLevel(logging.INFO)

        # Supprime les handlers existants pour éviter doublons
        if logger.hasHandlers():
            logger.handlers.clear()

        formatter = logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        # Handler fichier UTF-8
        file_handler = logging.FileHandler(log_path, encoding="utf-8")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        # Handler console
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        logger.info(f"Logger initialized: {log_path}")

        return logger

    def get_logger(self) -> logging.Logger:
        """
        Retourne l'instance logger configurée.

        Returns:
            logging.Logger: Logger configuré.
        """
        return self.logger

    def info(self, message: str) -> None:
        """
        Log un message au niveau INFO.

        Args:
            message (str): Message à logger.
        """
        self.logger.info(message)

    def debug(self, message: str) -> None:
        """
        Log un message au niveau DEBUG.

        Args:
            message (str): Message à logger.
        """
        self.logger.debug(message)

    def warning(self, message: str) -> None:
        """
        Log un message au niveau WARNING.

        Args:
            message (str): Message à logger.
        """
        self.logger.warning(message)

    def error(self, message: str) -> None:
        """
        Log un message au niveau ERROR.

        Args:
            message (str): Message à logger.
        """
        self.logger.error(message)
