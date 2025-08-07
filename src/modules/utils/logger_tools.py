import logging
import os
from datetime import datetime

from .file_tools import is_path_in_root


def init_logger(
    log_dir, app_name, script_name, log_ext="log", project_root=None
):
    """
    Initialise et configure un logger Python qui écrit dans un fichier
    avec encodage UTF-8.

    Args:
        log_dir (str): Répertoire où écrire le fichier log.
        app_name (str): Nom de l'application (nom du logger).
        script_name (str): Nom du script pour nom fichier log.
        log_ext (str): Extension du fichier log (par défaut "log").
        project_root (str, optional): Racine projet pour valider
        que les chemins sont dans le périmètre.

    Returns:
        logging.Logger: Logger Python configuré pour écrire dans
        un fichier UTF-8.

    Raises:
        RuntimeError: Si les chemins fournis (log_dir ou log_path)
        ne sont pas dans la racine projet.
    """
    # Vérifier que dossier logs est dans périmètre racine projet
    if project_root and not is_path_in_root(log_dir, project_root):
        raise RuntimeError(
            f"Dossier logs {log_dir} hors du périmètre racine {project_root}"
        )

    os.makedirs(log_dir, exist_ok=True)

    # Construire nom complet fichier log avec date, app et script
    date_str = datetime.now().strftime("%Y%m%d")
    log_filename = f"{date_str}_{app_name}_{script_name}.{log_ext}"
    log_path = os.path.join(log_dir, log_filename)

    # Vérifier que fichier log sera dans périmètre racine projet
    if project_root and not is_path_in_root(log_path, project_root):
        raise RuntimeError(
            f"Fichier log {log_path} hors du périmètre racine {project_root}"
        )

    # Création logger ou récupération si déjà existant
    logger = logging.getLogger(app_name)
    logger.setLevel(logging.INFO)

    # Supprimer les handlers existants pour éviter duplication de logs
    if logger.hasHandlers():
        logger.handlers.clear()

    # Handler fichier avec encodage UTF-8
    # pour éviter problème caractères spéciaux
    file_handler = logging.FileHandler(log_path, mode="a", encoding="utf-8")
    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)

    # Optionnel : Ajouter un handler console pour sorties standard
    # (peut être commenté ou paramétré)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    logger.info(f"Logger initialisé : {log_path}")

    return logger


def log_function_call(logger):
    """
    Décorateur générateur pour logger le début et la fin d'une fonction.

    Args:
        logger (logging.Logger): Logger à utiliser.

    Usage:
        @log_function_call(logger)
        def ma_fonction():
            pass
    """

    def decorator(func):
        import time
        from functools import wraps

        @wraps(func)
        def wrapper(*args, **kwargs):
            logger.info(f"Début de la fonction '{func.__name__}'")
            start_time = time.time()
            result = func(*args, **kwargs)
            elapsed = time.time() - start_time
            logger.info(
                f"Fin de la fonction '{func.__name__}' (durée {elapsed:.2f}s)"
            )
            return result

        return wrapper

    return decorator
