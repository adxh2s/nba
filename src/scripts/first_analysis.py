import os
import pprint

import pandas as pd
from modules.init_app import init_app
from modules.utils.data_tools import generate_report
from modules.utils.file_tools import (
    format_report_filename,
    get_config_param,
    get_node_path,
    load_from,
)
from modules.utils.logger_tools import log_function_call

PROJECT_STRUCTURE, DICT_APP, DICT_SCRIPT_CONFIG, LOGGER, CONST = init_app(
    __file__
)

# Debug structure docs pour vérification (à retirer en prod)
pprint.pprint(PROJECT_STRUCTURE.get("docs"))


@log_function_call(LOGGER)
def main():
    LOGGER.info("Démarrage du script first_analysis")

    try:
        raw_path = get_node_path(PROJECT_STRUCTURE, "data", "raw")
    except KeyError as e:
        LOGGER.error(f"Erreur accès path raw data : {e}")
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

    try:
        html_path = get_node_path(PROJECT_STRUCTURE, "docs", "reports", "html")
    except KeyError as e:
        LOGGER.error(f"Erreur accès path rapport HTML : {e}")
        return

    description_schema = None
    try:
        description_dir = get_node_path(PROJECT_STRUCTURE, "data", "describe")
        data_basename = os.path.splitext(os.path.basename(data_file))[0]
        description_file = os.path.join(
            description_dir, f"{data_basename}_describe.json"
        )

        if os.path.exists(description_file):
            description_schema = load_from(description_file)
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
        report_template = get_config_param(
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
        report_extension = get_config_param(
            "report_filename_extension",
            DICT_SCRIPT_CONFIG,
            PROJECT_STRUCTURE,
            "docs",
            "reports",
            "html",
        )
    except KeyError:
        report_extension = "html"

    report_filename = format_report_filename(
        report_template, input_filename=data_file
    )
    if not report_filename.lower().endswith(f".{report_extension.lower()}"):
        report_filename += f".{report_extension}"

    output_path = os.path.join(html_path, report_filename)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    report_title = data_basename

    try:
        generate_report(
            df,
            output_path,
            title=report_title,
            description_schema=description_schema,
        )
        LOGGER.info(
            f"Rapport ydata-profiling généré dans {output_path}"
            f"avec titre '{report_title}'"
        )
    except Exception as e:
        LOGGER.error(f"Erreur génération rapport ydata {output_path} : {e}")

    LOGGER.info("Fin du script first_analysis")


if __name__ == "__main__":
    main()
