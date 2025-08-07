import inspect
import os

from .utils.file_tools import (
    build_project_tree,
    find_project_root,
    find_project_structure,
    is_path_in_root,
    load_from,
)
from .utils.logger_tools import init_logger

PROJECT_STRUCTURE = {}
DICT_APP = {}
DICT_SCRIPT_CONFIG = {}
LOGGER = None
CONFIG_CONSTANTS = {}
_cache = {}


def expose_constants_from_dict(d):
    """
    Expose les clés du dictionnaire `d` en constantes globales en majuscules.

    Args:
        d (dict): Dictionnaire source.
    """
    global CONFIG_CONSTANTS
    for key, value in d.items():
        CONFIG_CONSTANTS[key.upper()] = value


def init_app(
    script_path=None, project_structure_path=None, root_dir_name=None
):
    """
    Initialise la configuration de l'application en chargeant la structure
    Projet YAML et, si besoin, la configuration applicative spécifique.

    Args:
        script_path (str, optional): Chemin absolu du script appelant.
        Si None, déduit automatiquement.
        project_structure_path (str, optional): Chemin vers
        project_structure.yaml.
        Si None, cherche par défaut.
        root_dir_name (str, optional): Nom du dossier racine du projet.
        Si None, pris depuis YAML.

    Returns:
        tuple: (PROJECT_STRUCTURE, DICT_APP, DICT_SCRIPT_CONFIG, LOGGER,
        CONFIG_CONSTANTS)

    Raises:
        RuntimeError, FileNotFoundError: En cas d'erreur de configuration.
    """
    global \
        PROJECT_STRUCTURE, \
        DICT_APP, \
        DICT_SCRIPT_CONFIG, \
        LOGGER, \
        CONFIG_CONSTANTS

    # Retour du cache si déjà initialisé
    if _cache:
        return (
            _cache["project_structure"],
            _cache["dict_app"],
            _cache["dict_script_config"],
            _cache["logger"],
            _cache["config_constants"],
        )

    # Déterminer chemin script appelant si non fourni
    if script_path is None:
        caller_frame = inspect.stack()[1]
        script_path = caller_frame.filename

    # Valeur par défaut temporaire pour localiser la racine et YAML
    if root_dir_name is None:
        root_dir_name = "nba"

    # Trouver racine provisoire pour localiser project_structure.yaml
    project_root = find_project_root(script_path, root_dir_name)

    # Localiser le fichier YAML de structure
    ps_path = project_structure_path or find_project_structure(project_root)
    if project_structure_path and not is_path_in_root(ps_path, project_root):
        raise RuntimeError(
            f"project_structure.yaml {ps_path} hors périmètre {project_root}"
        )

    # Charger YAML via load_from
    loaded_yaml = load_from(ps_path)

    # Extraire la métadonnée racine 'root'
    root_meta = loaded_yaml.get("root", {})
    if not root_meta:
        raise RuntimeError("La clé 'root' est absente dans le YAML")

    # Exposer constantes globales depuis root
    expose_constants_from_dict(root_meta)

    # Récupérer le nom réel de la racine projet (root.name)
    root_name = root_meta.get("name")
    if not root_name:
        raise RuntimeError(
            "Le champ 'root.name' doit être défini dans le YAML"
        )

    # Redéfinir la racine projet à partir de root.name
    project_root = find_project_root(script_path, root_name)
    if not os.path.exists(project_root):
        raise FileNotFoundError(f"Racine projet introuvable : {project_root}")

    # Extraire la structure projet dans root.structure
    raw_structure = root_meta.get("structure", {})
    if not raw_structure:
        raise RuntimeError(
            "La clé 'structure' est absente ou vide dans 'root' du YAML"
        )

    # Construire l’arborescence complète avec chemins, métadonnées, enfants
    PROJECT_STRUCTURE = build_project_tree(project_root, raw_structure)

    # Chargement de la configuration applicative spécifique
    # (paramètres métier)
    app_config_path = None
    app_name = root_meta.get("app_name")
    if app_name:
        conf_node = PROJECT_STRUCTURE.get("conf", {})
        conf_dir = (
            conf_node.get("path") if isinstance(conf_node, dict) else None
        )
        if conf_dir:
            candidate_path = os.path.join(conf_dir, f"{app_name}.json")
            if os.path.exists(candidate_path) and is_path_in_root(
                candidate_path, project_root
            ):
                app_config_path = candidate_path

    if app_config_path:
        DICT_APP = load_from(app_config_path)
        expose_constants_from_dict(DICT_APP)
    else:
        DICT_APP = {}

    # Configuration spécifique au script appelant (chargée si possible)
    script_name = os.path.splitext(os.path.basename(script_path))[0]
    conf_file_ext = DICT_APP.get("conf_file_extension", "json")
    conf_script_dir = DICT_APP.get("conf")
    if not conf_script_dir:
        # Par défaut, prendre dossier conf dans la structure
        conf_node = PROJECT_STRUCTURE.get("conf", {})
        conf_script_dir = (
            conf_node.get("path") if isinstance(conf_node, dict) else None
        )

    script_conf_path = None
    if conf_script_dir:
        candidate_script_path = os.path.join(
            conf_script_dir, f"{script_name}.{conf_file_ext}"
        )
        if os.path.exists(candidate_script_path) and is_path_in_root(
            candidate_script_path, project_root
        ):
            script_conf_path = candidate_script_path

    if script_conf_path:
        DICT_SCRIPT_CONFIG = load_from(script_conf_path)
    else:
        DICT_SCRIPT_CONFIG = {}

    # Initialisation du logger
    log_node = PROJECT_STRUCTURE.get("logs", {})
    log_dir = (
        DICT_APP.get("log")
        or log_node.get("path")
        or os.path.join(project_root, "logs")
    )
    log_ext = DICT_APP.get("log_file_extension", "log")

    LOGGER = init_logger(
        log_dir, app_name or "app", script_name, log_ext, project_root
    )

    # Mise en cache des données pour réutilisation
    _cache.update(
        {
            "project_structure": PROJECT_STRUCTURE,
            "dict_app": DICT_APP,
            "dict_script_config": DICT_SCRIPT_CONFIG,
            "logger": LOGGER,
            "config_constants": CONFIG_CONSTANTS,
        }
    )

    return (
        PROJECT_STRUCTURE,
        DICT_APP,
        DICT_SCRIPT_CONFIG,
        LOGGER,
        CONFIG_CONSTANTS,
    )
