import os

from packages.tools.file.io_utils import FileTools
from packages.tools.file.path_utils import PathUtils
from packages.tools.logger.manager import LoggerManager
from packages.tools.messages.i18n import setup_i18n
from packages.tools.messages.message_service import MessageService


class AppInitializer:
    """
    Initialise la structure projet, configurations globales et logger,
    avec cache pour réutilisation.
    """

    _cache: dict[str, object] = {}

    def __init__(
        self,
        script_path: str,
        project_structure_path: str | None = None,
        root_dir_name: str | None = None,
        language: str | None = None,
    ):
        if not script_path:
            raise ValueError("Le paramètre script_path est obligatoire")

        self.project_structure: dict = {}
        self.dict_app: dict = {}
        self.dict_script_config: dict = {}
        self.logger: LoggerManager | None = None
        self.config_constants: dict = {}

        self.script_path = os.path.abspath(script_path)
        self.project_structure_path = project_structure_path
        self.root_dir_name = root_dir_name or "nba"

        # Setup i18n _ function with language (list)
        self._ = setup_i18n(languages=[language] if language else None)
        self.message_service = MessageService()

    def expose_constants_from_dict(self, d: dict) -> None:
        for key, value in d.items():
            self.config_constants[key.upper()] = value

    def initialize(self) -> tuple[dict, dict, dict, LoggerManager, dict]:
        if self._cache:
            if not self.logger:
                raise RuntimeError("Logger non initialisé dans cache")
            return (
                self.project_structure,
                self.dict_app,
                self.dict_script_config,
                self.logger,
                self.config_constants,
            )

        project_root = PathUtils.find_project_root(
            self.script_path,
            self.root_dir_name,
        )

        ps_path = (
            self.project_structure_path
            or PathUtils.find_project_structure(project_root)
        )

        if self.project_structure_path and not PathUtils.is_path_in_root(
            ps_path, project_root
        ):
            raise RuntimeError(
                f"project_structure.yaml {ps_path} "
                f"outside project root {project_root}"
            )

        loaded_yaml = FileTools.load_from(ps_path)

        root_meta = loaded_yaml.get("root", {})
        if not root_meta:
            raise RuntimeError("Missing 'root' key in project_structure.yaml")

        self.expose_constants_from_dict(root_meta)

        root_name = root_meta.get("name")
        if not root_name:
            raise RuntimeError("Missing 'root.name' in project_structure.yaml")

        project_root = PathUtils.find_project_root(self.script_path, root_name)

        if not os.path.exists(project_root):
            raise FileNotFoundError(f"Project root not found: {project_root}")

        raw_structure = root_meta.get("structure", {})
        if not raw_structure:
            raise RuntimeError(
                "Key 'structure' missing or empty in 'root' "
                "of project_structure.yaml"
            )

        self.project_structure = PathUtils.build_project_tree(
            project_root, raw_structure
        )

        app_config_path: str | None = None
        app_name = root_meta.get("app_name")
        if app_name:
            conf_node = self.project_structure.get("conf", {})
            if isinstance(conf_node, dict):
                conf_dir = conf_node.get("path")
            else:
                conf_dir = None
            if conf_dir:
                candidate_path = os.path.join(conf_dir, f"{app_name}.json")
                if os.path.exists(
                    candidate_path
                ) and PathUtils.is_path_in_root(candidate_path, project_root):
                    app_config_path = candidate_path

        if app_config_path:
            self.dict_app = FileTools.load_from(app_config_path)
            self.expose_constants_from_dict(self.dict_app)
        else:
            self.dict_app = {}

        script_name = os.path.splitext(os.path.basename(self.script_path))[0]
        conf_file_ext = self.dict_app.get("conf_file_extension", "json")
        conf_script_dir = self.dict_app.get("conf")
        if not conf_script_dir:
            conf_node = self.project_structure.get("conf", {})
            if isinstance(conf_node, dict):
                conf_script_dir = conf_node.get("path")
            else:
                conf_script_dir = None

        script_conf_path: str | None = None
        if conf_script_dir:
            candidate_script_path = os.path.join(
                conf_script_dir, f"{script_name}.{conf_file_ext}"
            )
            if os.path.exists(
                candidate_script_path
            ) and PathUtils.is_path_in_root(
                candidate_script_path, project_root
            ):
                script_conf_path = candidate_script_path

        if script_conf_path:
            self.dict_script_config = FileTools.load_from(script_conf_path)
        else:
            self.dict_script_config = {}

        log_node = self.project_structure.get("logs", {})
        if isinstance(log_node, dict):
            log_dir = self.dict_app.get("log") or log_node.get("path")
        else:
            log_dir = self.dict_app.get("log")

        if not log_dir:
            log_dir = os.path.join(project_root, "logs")

        log_ext = self.dict_app.get("log_file_extension", "log")

        self.logger = LoggerManager(
            log_dir,
            app_name or "app",
            script_name,
            log_ext,
            project_root,
        )

        self._cache.update(
            {
                "project_structure": self.project_structure,
                "dict_app": self.dict_app,
                "dict_script_config": self.dict_script_config,
                "logger": self.logger,
                "config_constants": self.config_constants,
            }
        )

        # Exemple : affichage d'un message traduit d'init app
        self.logger.info(self.message_service.get_message("init_app_success"))

        return (
            self.project_structure,
            self.dict_app,
            self.dict_script_config,
            self.logger,
            self.config_constants,
        )


def init_app(
    script_path: str, language: str | None = None
) -> tuple[dict, dict, dict, LoggerManager, dict]:
    """
    Usine facilitant l'initialisation pour importer et démarrer rapidement.

    Args:
        script_path: chemin du script appelant, obligatoire.
        language: code langue ISO (ex: 'fr' ou 'en'), optionnel.

    Returns:
        tuple: project_structure, dict_app, dict_script_config,
            LoggerManager instance, config_constants
    """
    if not script_path:
        raise ValueError("Le paramètre script_path est obligatoire")

    initializer = AppInitializer(script_path, language=language)
    return initializer.initialize()
