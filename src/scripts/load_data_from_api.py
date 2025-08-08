import sys
from pathlib import Path

from packages.init_app import AppInitializer
from packages.tools.api import LoadDataFromApi
from packages.tools.file import FileTools
from packages.tools.logger import log_function_call


def main() -> int:
    """
    Point d'entrée : initialise l'application, charge configs et logger,
    et lance l'extraction API.

    Returns:
        int: 0 en cas de succès, autre valeur sinon.
    """
    try:
        script_path = Path(__file__).resolve()
        app_init = AppInitializer(str(script_path))
        (
            project_structure,
            dict_app,
            dict_script_config,
            logger,
            config_constants,
        ) = app_init.initialize()

        ft = FileTools()

        cfg_path = dict_script_config.get(
            "api_config_path",
            dict_app.get(
                "default_api_config_path", "conf/load_data_from_api.json"
            ),
        )
        conf_dir = project_structure.get("conf", {}).get("path", "")
        if conf_dir and not Path(cfg_path).is_absolute():
            cfg_path = str(Path(conf_dir) / cfg_path)

        loader = LoadDataFromApi(cfg_path, ft)

        # Pour éviter "cannot assign to method",
        # on crée une nouvelle méthode décorée
        decorated_run = log_function_call(logger.get_logger())(loader.run)

        logger.info("Starting LoadDataFromApi run()")
        decorated_run()
        logger.info("LoadDataFromApi run() completed successfully")

        return 0

    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
