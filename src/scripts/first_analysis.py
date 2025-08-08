import os
import pprint
from typing import Any

import pandas as pd
from packages.init_app import init_app
from packages.tools.data import ReportGenerator
from packages.tools.file import FileTools, FileUtils, PathUtils
from packages.tools.logger import log_function_call


def safe_get_path(tree: dict[str, Any], keys: list[str]) -> str | None:
    """
    Récupère un chemin (str) à partir d'une arborescence de dict imbriqués.
    Si le champ 'path' est une liste, retourne le premier élément (str),
    jamais la liste complète.
    """
    node: Any = tree
    for key in keys:
        if not isinstance(node, dict):
            return None
        node = node.get(key)
        if node is None:
            return None
        if isinstance(node, dict) and "children" in node:
            node = node["children"]
    if isinstance(node, dict):
        path = node.get("path")
        if isinstance(path, str):
            return path
        if (
            isinstance(path, list)
            and path
            and all(isinstance(p, str) for p in path)
        ):
            return path[0]
    if isinstance(node, str):
        return node
    return None


(
    PROJECT_STRUCTURE,
    DICT_APP,
    DICT_SCRIPT_CONFIG,
    LOGGER,
    CONST,
) = init_app(__file__)

pprint.pprint(PROJECT_STRUCTURE.get("docs"))


@log_function_call(LOGGER.get_logger())
def main() -> None:
    LOGGER.info("Démarrage du script first_analysis")

    raw_path = safe_get_path(PROJECT_STRUCTURE, ["data", "raw"])
    if not raw_path:
        LOGGER.error(
            "Impossible de déterminer le chemin raw data depuis la "
            "structure projet"
        )
        return

    data_file = os.path.join(raw_path, "games.csv")
    if not os.path.exists(data_file):
        LOGGER.error(f"Fichier de données introuvable : {data_file}")
        return

    try:
        df = pd.read_csv(data_file)
        LOGGER.info(
            f"Chargement du fichier CSV réussi "
            f"({data_file}) - {len(df)} lignes"
        )
    except Exception as e:
        LOGGER.error(f"Erreur lecture fichier CSV {data_file} : {e}")
        return

    html_path = safe_get_path(PROJECT_STRUCTURE, ["docs", "reports", "html"])
    if not html_path:
        LOGGER.error(
            "Impossible de déterminer le chemin HTML report depuis la "
            "structure projet"
        )
        return

    description_schema = None
    try:
        description_dir = safe_get_path(
            PROJECT_STRUCTURE, ["data", "describe"]
        )
        if not description_dir:
            raise ValueError("description_dir non trouvé")
        data_basename = os.path.splitext(os.path.basename(data_file))[0]
        description_file = os.path.join(
            description_dir, f"{data_basename}_describe.json"
        )

        if os.path.exists(description_file):
            description_schema = FileTools.load_from(description_file)
            LOGGER.info(
                f"Fichier description colonnes chargé : {description_file}"
            )
            desc_cols = (
                description_schema.get("columns")
                or description_schema.get("column_descriptions")
                or {}
            )
            for col in df.columns:
                desc_text = desc_cols.get(col, "")
                if desc_text:
                    LOGGER.info(
                        f"Description pour colonne '{col}': {desc_text}"
                    )
        else:
            LOGGER.info(
                f"Fichier description colonnes non trouvé : {description_file}"
            )
    except Exception as e:
        LOGGER.error(f"Erreur chargement description colonnes : {e}")

    try:
        report_template = PathUtils.get_config_param(
            "report_filename",
            DICT_SCRIPT_CONFIG,
            PROJECT_STRUCTURE,
            "docs",
            "reports",
            "html",
        )
    except KeyError:
        report_template = "{date:%Y%m%d%H%M}_{input}_report"

    try:
        report_extension = PathUtils.get_config_param(
            "report_filename_extension",
            DICT_SCRIPT_CONFIG,
            PROJECT_STRUCTURE,
            "docs",
            "reports",
            "html",
        )
    except KeyError:
        report_extension = "html"

    report_filename = FileUtils.format_report_filename(
        report_template, input_filename=data_file
    )

    if not report_filename.lower().endswith(f".{report_extension.lower()}"):
        report_filename += f".{report_extension}"

    output_path = os.path.join(html_path, report_filename)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    report_title = data_basename

    try:
        reporter = ReportGenerator(
            output_path,
            title=report_title,
            description_schema=description_schema,
        )
        reporter.generate(df)
        LOGGER.info(
            f"Rapport ydata-profiling généré dans {output_path}"
            f" avec titre '{report_title}'"
        )
    except Exception as e:
        LOGGER.error(f"Erreur génération rapport ydata {output_path} : {e}")

    LOGGER.info("Fin du script first_analysis")


if __name__ == "__main__":
    main()
