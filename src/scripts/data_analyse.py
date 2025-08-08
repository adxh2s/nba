import argparse
import logging
import os
import pprint
from typing import Any

import pandas as pd
from packages.init_app import init_app
from packages.tools.data import DataTransformer, DataValidator, ReportGenerator
from packages.tools.file import FileTools, FileUtils, PathUtils
from packages.tools.logger import log_function_call


class DataAnalysisApp:
    """
    Classe principale pour l'analyse de données.

    Initialise la configuration, charge les données,
    enrichit et valide le DataFrame,
    puis génère un rapport de profilage.
    """

    def __init__(self) -> None:
        (
            self.project_structure,
            self.dict_app,
            self.dict_script_config,
            self.logger,
            self.const,
        ) = init_app(__file__)

        # Debug : affichage sommaire de la structure projet
        # (supprimer en production)
        pprint.pprint(self.project_structure.get("docs"))

    @log_function_call(logging.getLogger())
    def run(self, data_filename: str) -> None:
        """
        Exécution principale de l’application d’analyse.

        Args:
            data_filename (str): Nom du fichier CSV à analyser.
        """
        self.logger.info("Démarrage du script data_analyse")

        df = self._load_data(data_filename)
        if df is None:
            return

        description_schema = self._load_description(df, data_filename)

        output_path = self._prepare_report_path(data_filename)

        # Utilisation correcte de DataTransformer sans description_schema
        transformer = DataTransformer(fields=list(df.columns))
        records = df.to_dict(orient="records")
        # conversion de type
        records_str_keys = [
            {str(k): v for k, v in record.items()} for record in records
        ]
        transformed_records = transformer.transform(records_str_keys)

        df_enriched = pd.DataFrame(transformed_records)

        validator = DataValidator(required_fields=[])
        if not validator.validate(transformed_records):
            self.logger.error(
                "Validation des données échouée. Rapport non généré."
            )
            return

        self._generate_report(
            df_enriched, output_path, data_filename, description_schema
        )

        self.logger.info("Fin du script data_analyse")

    def _load_data(self, data_filename: str) -> pd.DataFrame | None:
        """
        Charge les données CSV.

        Args:
            data_filename (str): Nom du fichier CSV.

        Returns:
            pd.DataFrame ou None si erreur.
        """
        try:
            raw_path = PathUtils.get_node_path(
                self.project_structure, "data", "raw"
            )
        except KeyError as e:
            self.logger.error(f"Erreur accès path raw data : {e}")
            return None

        data_file = os.path.join(raw_path, data_filename)
        if not os.path.isfile(data_file):
            self.logger.error(f"Fichier de données introuvable : {data_file}")
            return None

        try:
            df = pd.read_csv(data_file)
            self.logger.info(
                f"Chargement du fichier CSV réussi ({data_file}) - "
                f"{len(df)} lignes"
            )
            return df
        except (FileNotFoundError, pd.errors.ParserError) as e:
            self.logger.error(f"Erreur lecture fichier CSV {data_file} : {e}")
            return None

    def _load_description(
        self, df: pd.DataFrame, data_filename: str
    ) -> dict[str, Any] | None:
        """
        Charge la description des colonnes si disponible.

        Args:
            df (pd.DataFrame): DataFrame chargé.
            data_filename (str): Nom fichier CSV.

        Returns:
            dict ou None si non disponible ou erreur.
        """
        try:
            description_dir = PathUtils.get_node_path(
                self.project_structure, "data", "describe"
            )
        except KeyError as e:
            self.logger.error(f"Erreur accès path description colonnes : {e}")
            return None

        data_basename = os.path.splitext(os.path.basename(data_filename))[0]
        description_file = FileUtils.build_file_path(
            description_dir, f"{data_basename}_describe", "json"
        )

        if os.path.isfile(description_file):
            try:
                description_schema = FileTools.load_from(description_file)
                self.logger.info(
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
                        self.logger.debug(
                            f"Description pour colonne '{col}': {desc_text}"
                        )

                return description_schema
            except Exception as e:
                self.logger.error(
                    f"Erreur chargement description colonnes : {e}"
                )
                return None
        else:
            self.logger.info(
                f"Fichier description colonnes non trouvé : {description_file}"
            )
            return None

    def _prepare_report_path(self, data_filename: str) -> str:
        """
        Prépare le chemin complet du fichier rapport à générer.

        Args:
            data_filename (str): Nom fichier CSV initial.

        Returns:
            str: Chemin complet du rapport.
        """
        try:
            html_path = PathUtils.get_node_path(
                self.project_structure, "docs", "reports", "html"
            )
        except KeyError as e:
            self.logger.error(f"Erreur accès path rapport HTML : {e}")
            html_path = "reports/html"  # chemin fallback

        try:
            report_template = PathUtils.get_config_param(
                "report_filename",
                self.dict_script_config,
                self.project_structure,
                "docs",
                "reports",
                "html",
            )
        except KeyError:
            report_template = "{date:%Y%m%d%H%M}_{input}_report"

        try:
            report_extension = PathUtils.get_config_param(
                "report_filename_extension",
                self.dict_script_config,
                self.project_structure,
                "docs",
                "reports",
                "html",
            )
        except KeyError:
            report_extension = "html"

        report_filename = FileUtils.format_report_filename(
            report_template, input_filename=data_filename
        )
        if not report_filename.lower().endswith(
            f".{report_extension.lower()}"
        ):
            report_filename += f".{report_extension}"

        output_path = os.path.join(html_path, report_filename)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        return output_path

    def _generate_report(
        self,
        df_enriched: pd.DataFrame,
        output_path: str,
        data_basename: str,
        description_schema: dict[str, Any] | None,
    ) -> None:
        """
        Génère le rapport de profilage ydata-profiling.

        Args:
            df_enriched (pd.DataFrame): DataFrame enrichi.
            output_path (str): Chemin du rapport de sortie.
            data_basename (str): Nom de base du fichier source.
            description_schema (dict | None): Description des colonnes.
        """
        try:
            reporter = ReportGenerator(
                output_path,
                title=data_basename,
                description_schema=description_schema,
            )
            reporter.generate(df_enriched)
            self.logger.info(
                f"Rapport ydata-profiling généré dans {output_path} "
                f"avec titre '{data_basename}'"
            )
        except Exception as e:
            self.logger.error(
                f"Erreur génération rapport ydata {output_path} : {e}"
            )


def main(data_filename: str) -> None:
    """
    Point d'entrée principal exécutant l'application.

    Args:
        data_filename: Nom du fichier CSV à analyser.
    """
    app = DataAnalysisApp()
    app.run(data_filename)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Script d'analyse de données")
    parser.add_argument(
        "--data-file",
        type=str,
        required=True,
        help="Nom du fichier CSV à analyser",
    )
    args = parser.parse_args()

    if not args.data_file:
        parser.print_help()
    else:
        main(args.data_file)
